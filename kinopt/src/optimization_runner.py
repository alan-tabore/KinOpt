"""Run a configured optimization without depending on the graphical interface."""

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional, Tuple
import time

import numpy as np
from scipy.optimize import OptimizeResult

from kinopt.src import optimization


LOG_SPACE_LEAST_SQUARES = "least_squares_log"
GRADIENT_LOCAL_METHODS = frozenset({"CG", "BFGS", "L-BFGS-B"})


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
    experiment_lengths: Tuple[int, ...] = ()
    training_mask: Optional[np.ndarray] = None
    exploratory_fraction: Optional[float] = None
    exploratory_budget_fraction: float = 0.25

    def __post_init__(self) -> None:
        if not self.global_method and not self.local_method:
            raise ValueError("Select at least one optimization method.")
        if self.global_method and self.global_optimizer is None:
            raise ValueError("The selected global optimizer is not available.")
        if self.local_method and self.local_optimizer is None:
            raise ValueError("The selected local optimizer is not available.")
        if self.global_method and self.local_method == LOG_SPACE_LEAST_SQUARES:
            raise ValueError(
                "Run log-space least squares without a global optimizer."
            )
        if self.max_iterations <= 0:
            raise ValueError("The iteration budget must be a positive integer.")

        sample_count = np.asarray(self.experimental_rate).size
        lengths = tuple(int(length) for length in self.experiment_lengths)
        if lengths and (
            any(length <= 0 for length in lengths)
            or sum(lengths) != sample_count
        ):
            raise ValueError(
                "Experiment lengths must be positive and cover every rate value."
            )
        object.__setattr__(self, "experiment_lengths", lengths)
        if self.training_mask is not None:
            mask = np.asarray(self.training_mask, dtype=bool)
            if mask.ndim != 1 or mask.size != sample_count:
                raise ValueError(
                    "The training mask must select the experimental rate series."
                )
            if not np.any(mask):
                raise ValueError("The training mask must keep at least one value.")
            if np.all(mask):
                raise ValueError(
                    "Omit the training mask when every value is used for fitting."
                )
            object.__setattr__(self, "training_mask", mask)
        if self.exploratory_fraction is not None:
            if self.global_method:
                raise ValueError(
                    "Two-stage fitting currently supports local solvers only."
                )
            if not 0 < float(self.exploratory_fraction) < 1:
                raise ValueError(
                    "The exploratory fraction must be between 0 and 1."
                )
        if not 0 < float(self.exploratory_budget_fraction) <= 1:
            raise ValueError(
                "The exploratory budget fraction must be above 0 and at most 1."
            )

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
            "training_mask",
        )
        for field_name in fields_to_freeze:
            object.__setattr__(self, field_name, _freeze(getattr(self, field_name)))


@dataclass(frozen=True)
class OptimizationRunResult:
    """Solver result and elapsed wall-clock time for one run."""

    result: OptimizeResult
    elapsed_seconds: float


@dataclass(frozen=True)
class OptimizationProgress:
    """Portable progress sample emitted while an objective is evaluated."""

    evaluations: int
    best_cost: float
    elapsed_seconds: float
    estimated_remaining_seconds: Optional[float]
    best_parameters: Tuple[float, ...]


class _ProgressReporter:
    def __init__(self, callback, clock, started_at, budget):
        self.callback = callback
        self.clock = clock
        self.started_at = started_at
        self.budget = budget
        self.evaluations = 0
        self.best_cost = np.inf
        self.best_parameters = ()
        self.last_emitted_at = -np.inf

    def observe(self, cost, parameters, evaluations=None, force=False):
        if evaluations is None:
            self.evaluations += 1
        else:
            self.evaluations = max(self.evaluations, int(evaluations))
        numeric_cost = float(cost)
        improved = np.isfinite(numeric_cost) and numeric_cost < self.best_cost
        if improved:
            self.best_cost = numeric_cost
            self.best_parameters = tuple(
                float(value) for value in np.asarray(parameters, dtype=float)
            )
        if self.callback is None or not np.isfinite(self.best_cost):
            return
        now = self.clock()
        if not force and self.evaluations > 1 and now - self.last_emitted_at < 0.25:
            return
        elapsed = max(0.0, now - self.started_at)
        remaining = None
        if 1 < self.evaluations < self.budget:
            remaining = elapsed * (
                self.budget - self.evaluations
            ) / self.evaluations
        self.callback(
            OptimizationProgress(
                evaluations=self.evaluations,
                best_cost=self.best_cost,
                elapsed_seconds=elapsed,
                estimated_remaining_seconds=remaining,
                best_parameters=self.best_parameters,
            )
        )
        self.last_emitted_at = now


def _objective_arguments(config: OptimizationRunConfig) -> Tuple[Any, ...]:
    training_mask = config.training_mask

    def training_value(value):
        thawed = _thaw(value)
        if training_mask is None:
            return thawed
        if isinstance(thawed, np.ndarray):
            if thawed.ndim > 0 and thawed.shape[0] == training_mask.size:
                return thawed[training_mask]
            return thawed
        if (
            isinstance(thawed, (tuple, list))
            and config.experiment_lengths
            and len(thawed) == len(config.experiment_lengths)
            and all(
                isinstance(item, np.ndarray)
                and item.ndim > 0
                and item.shape[0] == length
                for item, length in zip(thawed, config.experiment_lengths)
            )
        ):
            selected = []
            start = 0
            for item, length in zip(thawed, config.experiment_lengths):
                experiment_mask = training_mask[start:start + length]
                if np.all(experiment_mask):
                    selected.append(item)
                elif np.any(experiment_mask):
                    selected.append(item[experiment_mask])
                start += length
            return tuple(selected)
        return thawed

    return (
        training_value(config.experimental_rate),
        config.rate_law,
        tuple(training_value(value) for value in config.experimental_args_for_rate),
        config.rate_parameter_count,
        config.vitrification_law,
        tuple(
            training_value(value)
            for value in config.experimental_args_for_vitrification
        ),
        config.vitrification_parameter_count,
        config.coupling_law,
        tuple(
            training_value(value)
            for value in config.experimental_args_for_coupling
        ),
        config.tg_law,
        tuple(training_value(value) for value in config.experimental_args_for_tg),
        _thaw(config.tg_args),
        *tuple(
            training_value(value)
            for value in config.experimental_args_for_cost_function
        ),
        *_thaw(config.cost_function_args),
    )


def _log_space_bounds(bounds: Any, initial_guess: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Validate physical bounds and convert them to base-10 log space."""
    if bounds is None:
        raise ValueError("Log-space least squares requires parameter bounds.")
    pairs = np.asarray(bounds, dtype=float)
    expected_shape = (initial_guess.size, 2)
    if pairs.shape != expected_shape:
        raise ValueError(
            "Log-space least squares requires one lower and upper bound "
            f"for each parameter; expected {expected_shape[0]} pairs."
        )
    lower, upper = pairs.T
    if not np.all(np.isfinite(pairs)):
        raise ValueError("Log-space least-squares bounds must be finite.")
    if np.any(lower <= 0) or np.any(upper <= 0):
        raise ValueError("Log-space least-squares bounds must be strictly positive.")
    if np.any(lower >= upper):
        raise ValueError("Each lower parameter bound must be below its upper bound.")
    if not np.all(np.isfinite(initial_guess)) or np.any(initial_guess <= 0):
        raise ValueError(
            "Log-space least-squares starting values must be strictly positive."
        )
    if np.any(initial_guess < lower) or np.any(initial_guess > upper):
        raise ValueError(
            "Every starting value must lie inside its least-squares bounds."
        )
    return np.log10(lower), np.log10(upper)


def _run_log_space_least_squares(
    config: OptimizationRunConfig,
    objective_args: Tuple[Any, ...],
    local_options: Mapping[str, Any],
    callback: Optional[Callable[..., Any]],
    cancellation_requested: Callable[[], bool],
    progress_reporter: _ProgressReporter,
) -> OptimizeResult:
    """Fit positive physical parameters in a numerically balanced log space."""
    options = dict(local_options)
    bounds = options.pop("bounds", None)
    initial_guess = np.asarray(_thaw(config.initial_guess), dtype=float)
    lower, upper = _log_space_bounds(bounds, initial_guess)
    transformed_initial_guess = np.log10(initial_guess)
    options.setdefault("x_scale", "jac")
    options.setdefault("method", "trf")
    requested_jacobian = options.pop("jac", "2-point")
    use_analytic_jacobian = (
        requested_jacobian == "auto"
        and optimization.has_analytic_jacobian_for_least_squares(
            initial_guess.size,
            config.rate_law,
            config.rate_parameter_count,
            config.vitrification_law,
            config.vitrification_parameter_count,
            config.coupling_law,
            config.tg_law,
        )
    )
    residual_weights = optimization.least_squares_residual_weights(
        config.cost_function,
        objective_args[0],
        *objective_args[12:],
    )
    prepared_rate_data = (
        optimization.prepare_analytic_rate_data(
            config.rate_law,
            objective_args[2],
        )
        if use_analytic_jacobian
        else None
    )
    residual_evaluations = [0]
    analytic_jacobian_evaluations = [0]
    kinetic_evaluations = [0]
    best_squared_norm = [np.inf]
    cached_transformed_parameters = [None]
    cached_physical_parameters = [None]
    cached_residuals = [None]
    cached_jacobian = [None]

    def evaluate_analytic_model(transformed_parameters):
        if (
            cached_transformed_parameters[0] is None
            or not np.array_equal(
                transformed_parameters,
                cached_transformed_parameters[0],
            )
        ):
            kinetic_evaluations[0] += 1
            physical_parameters = np.power(10.0, transformed_parameters)
            residuals, physical_jacobian = (
                optimization.analytic_residuals_and_jacobian_for_least_squares(
                    physical_parameters,
                    config.cost_function,
                    *objective_args,
                    residual_weights=residual_weights,
                    prepared_rate_data=prepared_rate_data,
                )
            )
            log_space_derivative = np.log(10.0) * physical_parameters
            cached_transformed_parameters[0] = np.array(
                transformed_parameters,
                copy=True,
            )
            cached_physical_parameters[0] = physical_parameters
            cached_residuals[0] = residuals
            cached_jacobian[0] = (
                physical_jacobian * log_space_derivative[np.newaxis, :]
            )
        return (
            cached_physical_parameters[0],
            cached_residuals[0],
            cached_jacobian[0],
        )

    def residual_function(transformed_parameters):
        if cancellation_requested():
            raise OptimizationCancelled()
        residual_evaluations[0] += 1
        if use_analytic_jacobian:
            physical_parameters, residuals, _ = evaluate_analytic_model(
                transformed_parameters
            )
        else:
            kinetic_evaluations[0] += 1
            physical_parameters = np.power(10.0, transformed_parameters)
            residuals = optimization.residuals_for_least_squares(
                physical_parameters,
                config.cost_function,
                *objective_args,
                residual_weights=residual_weights,
            )
        squared_norm = float(np.dot(residuals, residuals))
        progress_reporter.observe(
            squared_norm,
            physical_parameters,
            evaluations=residual_evaluations[0],
        )
        if callback is not None and squared_norm < best_squared_norm[0]:
            best_squared_norm[0] = squared_norm
            callback(physical_parameters)
        return residuals

    if use_analytic_jacobian:
        def jacobian_function(transformed_parameters):
            if cancellation_requested():
                raise OptimizationCancelled()
            analytic_jacobian_evaluations[0] += 1
            _, _, jacobian = evaluate_analytic_model(
                transformed_parameters
            )
            return jacobian

        options["jac"] = jacobian_function
        jacobian_source = optimization.analytic_jacobian_source(
            config.rate_law
        )
    else:
        options["jac"] = (
            "2-point" if requested_jacobian == "auto" else requested_jacobian
        )
        jacobian_source = (
            options["jac"] if isinstance(options["jac"], str) else "custom"
        )

    result = config.local_optimizer(
        residual_function,
        transformed_initial_guess,
        bounds=(lower, upper),
        **options,
    )
    residual_vector = np.asarray(result.fun, dtype=float)
    result.x = np.power(10.0, result.x)
    result.residuals = residual_vector
    result.fun = float(config.cost_function(result.x, *objective_args))
    result.residual_evaluations = residual_evaluations[0]
    result.analytic_jacobian_evaluations = analytic_jacobian_evaluations[0]
    result.kinetic_evaluations = kinetic_evaluations[0]
    result.jacobian_source = jacobian_source
    return result


def run_optimization(
    config: OptimizationRunConfig,
    callback: Optional[Callable[..., Any]] = None,
    is_cancelled: Optional[Callable[[], bool]] = None,
    progress_callback: Optional[Callable[[OptimizationProgress], Any]] = None,
    clock: Callable[[], float] = time.perf_counter,
) -> OptimizationRunResult:
    """Execute one configured SciPy optimization and return its result."""
    cancellation_requested = is_cancelled or (lambda: False)
    if cancellation_requested():
        raise OptimizationCancelled()

    def solver_callback(*args, **kwargs):
        if cancellation_requested():
            raise OptimizationCancelled()
        if callback is not None:
            return callback(*args, **kwargs)
        return None

    global_options = _thaw(config.global_options or {})
    local_options = _thaw(config.local_options or {})
    objective_args = _objective_arguments(config)
    initial_guess = _thaw(config.initial_guess)
    started_at = clock()
    progress_reporter = _ProgressReporter(
        progress_callback,
        clock,
        started_at,
        config.max_iterations,
    )

    def tracked_objective(parameters, *args):
        value = config.cost_function(parameters, *args)
        progress_reporter.observe(value, parameters)
        return value

    minimize_objective = tracked_objective
    minimize_jacobian_source = None
    analytic_gradient_evaluations = [0]

    can_use_selected_local_method = config.global_method in {
        "",
        "basinhopping",
        "shgo",
    }
    requested_jacobian = local_options.get("jac")
    if (
        can_use_selected_local_method
        and config.local_method in GRADIENT_LOCAL_METHODS
        and requested_jacobian == "auto"
    ):
        use_analytic_gradient = (
            optimization.has_analytic_gradient_for_minimize(
                config.cost_function,
                np.asarray(initial_guess).size,
                config.rate_law,
                config.rate_parameter_count,
                config.vitrification_law,
                config.vitrification_parameter_count,
                config.coupling_law,
                config.tg_law,
            )
        )
        if use_analytic_gradient:
            residual_weights = optimization.least_squares_residual_weights(
                config.cost_function,
                objective_args[0],
                *objective_args[12:],
            )
            prepared_rate_data = optimization.prepare_analytic_rate_data(
                config.rate_law,
                objective_args[2],
            )
            cached_parameters = [None]
            cached_cost = [None]
            cached_gradient = [None]

            def evaluate_cost_and_gradient(parameters):
                if (
                    cached_parameters[0] is None
                    or not np.array_equal(parameters, cached_parameters[0])
                ):
                    cost, gradient = (
                        optimization.analytic_cost_and_gradient_for_minimize(
                            parameters,
                            config.cost_function,
                            *objective_args,
                            residual_weights=residual_weights,
                            prepared_rate_data=prepared_rate_data,
                        )
                    )
                    cached_parameters[0] = np.array(parameters, copy=True)
                    cached_cost[0] = cost
                    cached_gradient[0] = gradient
                    progress_reporter.observe(cost, parameters)
                return cached_cost[0], cached_gradient[0]

            def analytic_objective(parameters, *unused_args):
                cost, _ = evaluate_cost_and_gradient(parameters)
                return cost

            def analytic_gradient(parameters, *unused_args):
                if cancellation_requested():
                    raise OptimizationCancelled()
                analytic_gradient_evaluations[0] += 1
                _, gradient = evaluate_cost_and_gradient(parameters)
                return gradient

            local_options["jac"] = analytic_gradient
            minimize_jacobian_source = optimization.analytic_jacobian_source(
                config.rate_law
            )
            if not config.global_method:
                minimize_objective = analytic_objective
        else:
            local_options["jac"] = None
            minimize_jacobian_source = "2-point"

    callback_required = callback is not None or is_cancelled is not None
    if config.global_method and callback_required:
        global_options["callback"] = solver_callback
    elif callback_required and config.local_method != LOG_SPACE_LEAST_SQUARES:
        local_options["callback"] = solver_callback

    if config.global_method == "basinhopping":
        local_options["args"] = objective_args
        global_options["minimizer_kwargs"] = local_options
        result = config.global_optimizer(
            tracked_objective,
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
            tracked_objective,
            bounds,
            **global_options,
        )
    elif config.global_method:
        raise ValueError(f"Unsupported global optimizer: {config.global_method}")
    elif config.local_method == LOG_SPACE_LEAST_SQUARES:
        result = _run_log_space_least_squares(
            config,
            objective_args,
            local_options,
            callback,
            cancellation_requested,
            progress_reporter,
        )
    else:
        local_options["args"] = objective_args
        result = config.local_optimizer(
            minimize_objective,
            initial_guess,
            **local_options,
        )

    if minimize_jacobian_source is not None:
        result.jacobian_source = minimize_jacobian_source
        result.analytic_gradient_evaluations = (
            analytic_gradient_evaluations[0]
        )

    elapsed_seconds = clock() - started_at
    progress_reporter.observe(
        result.fun,
        result.x,
        evaluations=getattr(result, "nfev", None),
        force=True,
    )
    if cancellation_requested():
        raise OptimizationCancelled()
    if not np.all(np.isfinite(result.x)) or not np.all(np.isfinite(result.fun)):
        raise ValueError("Optimization returned non-finite parameters or cost.")
    return OptimizationRunResult(result=result, elapsed_seconds=elapsed_seconds)
