"""Run a configured optimization without depending on the graphical interface."""

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional, Tuple
import time

import numpy as np
from scipy.optimize import OptimizeResult


class OptimizationCancelled(Exception):
    """Stop an optimization cooperatively from a solver callback."""


def _freeze(value: Any) -> Any:
    """Copy mutable configuration values into read-only equivalents."""
    if isinstance(value, np.ndarray):
        frozen = np.array(value, copy=True)
        frozen.setflags(write=False)
        return frozen
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    try:
        return deepcopy(value)
    except (TypeError, ValueError):
        # Functions and some SciPy objects are intentionally shared. They are
        # treated as services, not as mutable configuration values.
        return value


def _thaw(value: Any) -> Any:
    """Return private mutable values that a SciPy solver may modify."""
    if isinstance(value, np.ndarray):
        return np.array(value, copy=True)
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_thaw(item) for item in value)
    if isinstance(value, frozenset):
        return set(_thaw(item) for item in value)
    try:
        return deepcopy(value)
    except (TypeError, ValueError):
        return value


@dataclass(frozen=True)
class OptimizationRunConfig:
    """Immutable snapshot of everything needed by one optimization run."""

    cost_function: Callable[..., float]
    initial_guess: np.ndarray
    global_method: str
    global_optimizer: Optional[Callable[..., OptimizeResult]]
    global_options: Optional[Mapping[str, Any]]
    local_method: str
    local_optimizer: Optional[Callable[..., OptimizeResult]]
    local_options: Optional[Mapping[str, Any]]
    experimental_rate: np.ndarray
    rate_law: Optional[Callable[..., np.ndarray]]
    experimental_args_for_rate: Tuple[Any, ...]
    rate_parameter_count: int
    vitrification_law: Optional[Callable[..., np.ndarray]]
    experimental_args_for_vitrification: Tuple[Any, ...]
    vitrification_parameter_count: int
    coupling_law: Optional[Callable[..., np.ndarray]]
    experimental_args_for_coupling: Tuple[Any, ...]
    tg_law: Optional[Callable[..., np.ndarray]]
    experimental_args_for_tg: Tuple[Any, ...]
    tg_args: Optional[Tuple[float, ...]]
    cost_function_args: Tuple[Any, ...]
    experimental_args_for_cost_function: Tuple[Any, ...]
    max_iterations: int

    def __post_init__(self) -> None:
        if not self.global_method and not self.local_method:
            raise ValueError("Select at least one optimization method.")
        if self.global_method and self.global_optimizer is None:
            raise ValueError("The selected global optimizer is not available.")
        if self.local_method and self.local_optimizer is None:
            raise ValueError("The selected local optimizer is not available.")
        if self.max_iterations <= 0:
            raise ValueError("The iteration budget must be a positive integer.")

        fields_to_freeze = (
            "initial_guess",
            "global_options",
            "local_options",
            "experimental_rate",
            "experimental_args_for_rate",
            "experimental_args_for_vitrification",
            "experimental_args_for_coupling",
            "experimental_args_for_tg",
            "tg_args",
            "cost_function_args",
            "experimental_args_for_cost_function",
        )
        for field_name in fields_to_freeze:
            object.__setattr__(self, field_name, _freeze(getattr(self, field_name)))


@dataclass(frozen=True)
class OptimizationRunResult:
    """Solver result and elapsed wall-clock time for one run."""

    result: OptimizeResult
    elapsed_seconds: float


def _objective_arguments(config: OptimizationRunConfig) -> Tuple[Any, ...]:
    return (
        _thaw(config.experimental_rate),
        config.rate_law,
        _thaw(config.experimental_args_for_rate),
        config.rate_parameter_count,
        config.vitrification_law,
        _thaw(config.experimental_args_for_vitrification),
        config.vitrification_parameter_count,
        config.coupling_law,
        _thaw(config.experimental_args_for_coupling),
        config.tg_law,
        _thaw(config.experimental_args_for_tg),
        _thaw(config.tg_args),
        *_thaw(config.experimental_args_for_cost_function),
        *_thaw(config.cost_function_args),
    )


def run_optimization(
    config: OptimizationRunConfig,
    callback: Optional[Callable[..., Any]] = None,
    is_cancelled: Optional[Callable[[], bool]] = None,
    clock: Callable[[], float] = time.perf_counter,
) -> OptimizationRunResult:
    """Execute one configured SciPy optimization and return its result."""
    cancellation_requested = is_cancelled or (lambda: False)
    if cancellation_requested():
        raise OptimizationCancelled()

    global_options = _thaw(config.global_options or {})
    local_options = _thaw(config.local_options or {})
    objective_args = _objective_arguments(config)
    initial_guess = _thaw(config.initial_guess)

    if config.global_method:
        global_options["callback"] = callback
    elif callback is not None:
        local_options["callback"] = callback

    started_at = clock()
    if config.global_method == "basinhopping":
        local_options["args"] = objective_args
        global_options["minimizer_kwargs"] = local_options
        result = config.global_optimizer(
            config.cost_function,
            initial_guess,
            **global_options,
        )
    elif config.global_method in {"differential_evolution", "shgo"}:
        try:
            bounds = global_options.pop("bounds")
        except KeyError as error:
            raise ValueError(
                f"{config.global_method} requires parameter bounds."
            ) from error
        global_options["args"] = objective_args
        if config.global_method == "shgo":
            global_options["minimizer_kwargs"] = local_options
        result = config.global_optimizer(
            config.cost_function,
            bounds,
            **global_options,
        )
    elif config.global_method:
        raise ValueError(f"Unsupported global optimizer: {config.global_method}")
    else:
        local_options["args"] = objective_args
        result = config.local_optimizer(
            config.cost_function,
            initial_guess,
            **local_options,
        )

    elapsed_seconds = clock() - started_at
    if cancellation_requested():
        raise OptimizationCancelled()
    if not np.all(np.isfinite(result.x)) or not np.isfinite(result.fun):
        raise ValueError("Optimization returned non-finite parameters or cost.")
    return OptimizationRunResult(result=result, elapsed_seconds=elapsed_seconds)
