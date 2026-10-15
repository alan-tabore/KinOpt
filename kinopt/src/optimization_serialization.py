"""Versioned JSON serialization for optimization run configurations."""

import json
from typing import Any, Callable, Dict, Iterable, Mapping, Optional

import numpy as np
from scipy import optimize as scipy_optimize

from kinopt.src import kinetic_models
from kinopt.src import optimization
from kinopt.src.optimization_runner import OptimizationRunConfig
from kinopt.src.optimization_runner import LOG_SPACE_LEAST_SQUARES


SCHEMA_VERSION = 2

_COST_FUNCTIONS = {
    "rss_standard",
    "rss_mean",
    "rss_relative",
    "rss_increase_of_small_extents_impact",
    "rss_increase_of_small_rates_impact_with_zones",
}
_RATE_LAWS = {
    "rate_for_nth_order",
    "rate_for_autocatalytic",
    "rate_for_kamal",
}
_VITRIFICATION_LAWS = {
    "vitrification_WLF_rate",
    "vitrification_WLF_rate_no_reaction_below_Tg",
}
_COUPLING_LAWS = {"coupling_harmonic_mean", "coupling_product"}
_TG_LAWS = {"tg_diBennedetto"}
_GLOBAL_METHODS = {"basinhopping", "differential_evolution", "shgo"}
_LOCAL_METHODS = {
    LOG_SPACE_LEAST_SQUARES,
    "Nelder-Mead",
    "CG",
    "BFGS",
    "L-BFGS-B",
}


def _registered_name(
    function: Optional[Callable[..., Any]],
    module: Any,
    allowed_names: Iterable[str],
    label: str,
) -> Optional[str]:
    if function is None:
        return None
    name = getattr(function, "__name__", None)
    if name not in allowed_names or getattr(module, name, None) is not function:
        raise ValueError(f"Cannot serialize unregistered {label}: {function!r}")
    return name


def _resolve_function(
    name: Optional[str],
    module: Any,
    allowed_names: Iterable[str],
    label: str,
) -> Optional[Callable[..., Any]]:
    if name is None:
        return None
    if name not in allowed_names:
        raise ValueError(f"Unknown {label}: {name!r}")
    function = getattr(module, name, None)
    if not callable(function):
        raise ValueError(f"Unavailable {label}: {name!r}")
    return function


def _json_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_json_value(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return _json_value(value.item())
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError(f"Unsupported configuration value: {value!r}")


def _argument_tuple(values: Any, label: str) -> tuple:
    if not isinstance(values, list):
        raise ValueError(f"{label} must be a JSON array.")
    arguments = []
    for value in values:
        if isinstance(value, list):
            arguments.append(np.asarray(value))
        else:
            arguments.append(value)
    return tuple(arguments)


def _validate_model_selection(rate_law, vitrification_law, coupling_law, tg_law):
    if rate_law is None and vitrification_law is None:
        raise ValueError("At least one rate or vitrification law is required.")
    if coupling_law is not None and (
        rate_law is None or vitrification_law is None
    ):
        raise ValueError("A coupling law requires rate and vitrification laws.")
    if rate_law is not None and vitrification_law is not None:
        if coupling_law is None:
            raise ValueError(
                "A coupling law is required with rate and vitrification laws."
            )
    if vitrification_law is not None and tg_law is None:
        raise ValueError("A vitrification law requires a Tg law.")


def config_to_dict(config: OptimizationRunConfig) -> Dict[str, Any]:
    """Return a JSON-compatible, versioned representation of a run."""
    global_method = config.global_method or None
    if global_method is not None:
        if global_method not in _GLOBAL_METHODS:
            raise ValueError(f"Cannot serialize global method: {global_method!r}")
        if getattr(scipy_optimize, global_method) is not config.global_optimizer:
            raise ValueError("The global optimizer does not match its method name.")
    elif config.global_optimizer is not None:
        raise ValueError("A global optimizer requires a global method name.")

    local_method = config.local_method or None
    if local_method is not None:
        if local_method not in _LOCAL_METHODS:
            raise ValueError(f"Cannot serialize local method: {local_method!r}")
        expected_optimizer = (
            scipy_optimize.least_squares
            if local_method == LOG_SPACE_LEAST_SQUARES
            else scipy_optimize.minimize
        )
        if config.local_optimizer is not expected_optimizer:
            raise ValueError(
                "The local optimizer does not match its method name."
            )
    elif config.local_optimizer is not None:
        raise ValueError("A local optimizer requires a local method name.")

    cost_function_name = _registered_name(
        config.cost_function,
        optimization,
        _COST_FUNCTIONS,
        "cost function",
    )
    if cost_function_name is None:
        raise ValueError("A cost function is required.")
    rate_law_name = _registered_name(
        config.rate_law, kinetic_models, _RATE_LAWS, "rate law"
    )
    vitrification_law_name = _registered_name(
        config.vitrification_law,
        kinetic_models,
        _VITRIFICATION_LAWS,
        "vitrification law",
    )
    coupling_law_name = _registered_name(
        config.coupling_law,
        kinetic_models,
        _COUPLING_LAWS,
        "coupling law",
    )
    tg_law_name = _registered_name(
        config.tg_law, kinetic_models, _TG_LAWS, "Tg law"
    )
    _validate_model_selection(
        rate_law_name,
        vitrification_law_name,
        coupling_law_name,
        tg_law_name,
    )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "cost_function": cost_function_name,
        "initial_guess": _json_value(config.initial_guess),
        "global_method": global_method,
        "global_options": _json_value(config.global_options),
        "local_method": local_method,
        "local_options": _json_value(config.local_options),
        "experimental_rate": _json_value(config.experimental_rate),
        "rate_law": rate_law_name,
        "experimental_args_for_rate": _json_value(
            config.experimental_args_for_rate
        ),
        "rate_parameter_count": config.rate_parameter_count,
        "vitrification_law": vitrification_law_name,
        "experimental_args_for_vitrification": _json_value(
            config.experimental_args_for_vitrification
        ),
        "vitrification_parameter_count": config.vitrification_parameter_count,
        "coupling_law": coupling_law_name,
        "experimental_args_for_coupling": _json_value(
            config.experimental_args_for_coupling
        ),
        "tg_law": tg_law_name,
        "experimental_args_for_tg": _json_value(
            config.experimental_args_for_tg
        ),
        "tg_args": _json_value(config.tg_args),
        "cost_function_args": _json_value(config.cost_function_args),
        "experimental_args_for_cost_function": _json_value(
            config.experimental_args_for_cost_function
        ),
        "max_iterations": config.max_iterations,
        "experiment_lengths": list(config.experiment_lengths),
        "training_mask": _json_value(config.training_mask),
    }
    # Enforce standard JSON now so invalid NaN or infinite values fail before
    # the payload reaches persistent storage.
    json.dumps(payload, allow_nan=False)
    return payload


def config_from_dict(payload: Mapping[str, Any]) -> OptimizationRunConfig:
    """Rebuild an immutable run configuration from a versioned payload."""
    if not isinstance(payload, Mapping):
        raise ValueError("The optimization configuration must be a JSON object.")
    schema_version = payload.get("schema_version")
    if schema_version not in {1, SCHEMA_VERSION}:
        raise ValueError(
            "Unsupported optimization configuration schema: "
            f"{payload.get('schema_version')!r}"
        )

    global_method = payload.get("global_method") or ""
    if global_method and global_method not in _GLOBAL_METHODS:
        raise ValueError(f"Unknown global method: {global_method!r}")
    local_method = payload.get("local_method") or ""
    if local_method and local_method not in _LOCAL_METHODS:
        raise ValueError(f"Unknown local method: {local_method!r}")

    try:
        cost_function = _resolve_function(
            payload["cost_function"],
            optimization,
            _COST_FUNCTIONS,
            "cost function",
        )
        if cost_function is None:
            raise ValueError("A cost function is required.")
        rate_law = _resolve_function(
            payload["rate_law"], kinetic_models, _RATE_LAWS, "rate law"
        )
        vitrification_law = _resolve_function(
            payload["vitrification_law"],
            kinetic_models,
            _VITRIFICATION_LAWS,
            "vitrification law",
        )
        coupling_law = _resolve_function(
            payload["coupling_law"],
            kinetic_models,
            _COUPLING_LAWS,
            "coupling law",
        )
        tg_law = _resolve_function(
            payload["tg_law"], kinetic_models, _TG_LAWS, "Tg law"
        )
        _validate_model_selection(
            rate_law,
            vitrification_law,
            coupling_law,
            tg_law,
        )
        return OptimizationRunConfig(
            cost_function=cost_function,
            initial_guess=np.asarray(payload["initial_guess"], dtype=float),
            global_method=global_method,
            global_optimizer=(
                getattr(scipy_optimize, global_method)
                if global_method else None
            ),
            global_options=payload["global_options"],
            local_method=local_method,
            local_optimizer=(
                scipy_optimize.least_squares
                if local_method == LOG_SPACE_LEAST_SQUARES
                else scipy_optimize.minimize if local_method else None
            ),
            local_options=payload["local_options"],
            experimental_rate=np.asarray(
                payload["experimental_rate"], dtype=float
            ),
            rate_law=rate_law,
            experimental_args_for_rate=_argument_tuple(
                payload["experimental_args_for_rate"],
                "Rate-law experimental arguments",
            ),
            rate_parameter_count=int(payload["rate_parameter_count"]),
            vitrification_law=vitrification_law,
            experimental_args_for_vitrification=_argument_tuple(
                payload["experimental_args_for_vitrification"],
                "Vitrification experimental arguments",
            ),
            vitrification_parameter_count=int(
                payload["vitrification_parameter_count"]
            ),
            coupling_law=coupling_law,
            experimental_args_for_coupling=_argument_tuple(
                payload["experimental_args_for_coupling"],
                "Coupling experimental arguments",
            ),
            tg_law=tg_law,
            experimental_args_for_tg=_argument_tuple(
                payload["experimental_args_for_tg"],
                "Tg experimental arguments",
            ),
            tg_args=(
                None
                if payload["tg_args"] is None
                else tuple(float(value) for value in payload["tg_args"])
            ),
            cost_function_args=tuple(payload["cost_function_args"]),
            experimental_args_for_cost_function=_argument_tuple(
                payload["experimental_args_for_cost_function"],
                "Cost-function experimental arguments",
            ),
            max_iterations=int(payload["max_iterations"]),
            experiment_lengths=tuple(
                int(value) for value in payload.get("experiment_lengths", ())
            ),
            training_mask=(
                None
                if payload.get("training_mask") is None
                else np.asarray(payload["training_mask"], dtype=bool)
            ),
        )
    except KeyError as error:
        raise ValueError(
            f"Missing optimization configuration field: {error.args[0]}"
        ) from error
    except (TypeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith(
            (
                "Unknown ",
                "Unavailable ",
                "Select ",
                "The iteration ",
                "At least ",
                "A cost ",
                "A coupling ",
                "A vitrification ",
            )
        ):
            raise
        raise ValueError(f"Invalid optimization configuration: {error}") from error


def serialize_config(config: OptimizationRunConfig) -> str:
    """Serialize a configuration as compact, deterministic JSON."""
    return json.dumps(
        config_to_dict(config),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def deserialize_config(serialized: str) -> OptimizationRunConfig:
    """Deserialize JSON while rejecting non-standard numeric constants."""
    try:
        payload = json.loads(
            serialized,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"Invalid numeric constant: {value}")
            ),
        )
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid optimization configuration JSON: {error}") from error
    return config_from_dict(payload)
