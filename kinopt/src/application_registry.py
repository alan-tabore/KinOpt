"""Discover supported analyses and describe their editable parameters."""

import numpy as np

from kinopt.src import isoconversional_methods
from kinopt.src import optimization
from kinopt.src.model_metadata import (
    kinetic_model_metadata,
    kinetic_model_names,
)
from kinopt.src.optimization_runner import LOG_SPACE_LEAST_SQUARES


def get_functions_for_isoconversional_method():
    return [
        name
        for name in dir(isoconversional_methods)
        if name.startswith("isoconversional_analysis")
        and callable(getattr(isoconversional_methods, name))
    ]


def get_parameters_for_isoconversional_method(name):
    function = getattr(isoconversional_methods, name, None)
    if function is None:
        return []
    return function.__code__.co_varnames[:function.__code__.co_argcount]


def get_functions_for_kinetics():
    return tuple(
        list(kinetic_model_names(kind))
        for kind in ("rate", "vitrification", "coupling", "tg")
    )


def _model_parameters(kind, name):
    metadata = kinetic_model_metadata(kind, name)
    return () if metadata is None else metadata.function_parameters


def get_parameters_for_rate(name):
    return _model_parameters("rate", name)


def get_parameters_for_vitrification(name):
    return _model_parameters("vitrification", name)


def get_parameters_for_coupling(name):
    return _model_parameters("coupling", name)


def get_parameters_for_tg(name):
    return _model_parameters("tg", name)


def get_functions_for_optimization():
    global_methods = ["basinhopping", "differential_evolution", "shgo"]
    local_methods = [
        LOG_SPACE_LEAST_SQUARES,
        "Nelder-Mead",
        "CG",
        "BFGS",
        "L-BFGS-B",
    ]
    costs = [
        name
        for name in dir(optimization)
        if name.startswith("rss") and callable(getattr(optimization, name))
    ]
    return global_methods, local_methods, costs


_OPTIMIZATION_PARAMETERS = {
    LOG_SPACE_LEAST_SQUARES: {
        "jac": {"type": list, "optional": False},
        "max_nfev": {"type": int, "optional": False},
        "ftol": {"type": float, "optional": True},
        "xtol": {"type": float, "optional": True},
        "gtol": {"type": float, "optional": True},
        "bounds": {"type": "sequence", "optional": False},
    },
    "Nelder-Mead": {
        "disp": {"type": bool, "optional": True},
        "maxiter": {"type": int, "optional": False},
        "maxfev": {"type": int, "optional": True},
        "return_all": {"type": bool, "optional": True},
        "xatol": {"type": float, "optional": True},
        "fatol": {"type": float, "optional": True},
        "adaptive": {"type": bool, "optional": True},
        "bounds": {"type": "sequence", "optional": True},
    },
    "CG": {
        "disp": {"type": bool, "optional": True},
        "jac": {"type": list, "optional": True},
        "maxiter": {"type": int, "optional": False},
        "gtol": {"type": float, "optional": True},
        "norm": {"type": float, "optional": True},
        "eps": {"type": float, "optional": True},
        "return_all": {"type": bool, "optional": True},
    },
    "BFGS": {
        "disp": {"type": bool, "optional": True},
        "jac": {"type": list, "optional": True},
        "maxiter": {"type": int, "optional": False},
        "gtol": {"type": float, "optional": True},
        "norm": {"type": float, "optional": True},
        "eps": {"type": float, "optional": True},
        "return_all": {"type": bool, "optional": True},
        "xrtol": {"type": float, "optional": True},
    },
    "L-BFGS-B": {
        "disp": {"type": bool, "optional": True},
        "jac": {"type": list, "optional": True},
        "maxcor": {"type": int, "optional": True},
        "maxfun": {"type": int, "optional": True},
        "maxiter": {"type": int, "optional": False},
        "iprint": {"type": int, "optional": True},
        "maxls": {"type": int, "optional": True},
        "ftol": {"type": float, "optional": True},
        "gtol": {"type": float, "optional": True},
        "eps": {"type": float, "optional": True},
        "bounds": {"type": "sequence", "optional": True},
    },
    "basinhopping": {
        "disp": {"type": bool, "optional": True},
        "niter": {"type": int, "optional": False},
        "T": {"type": float, "optional": True},
        "stepsize": {"type": float, "optional": True},
        "interval": {"type": int, "optional": True},
        "niter_success": {"type": int, "optional": True},
        "target_accept_rate": {"type": float, "optional": True},
        "stepwise_factor": {"type": float, "optional": True},
    },
    "differential_evolution": {
        "disp": {"type": bool, "optional": True},
        "strategy": {"type": "strategy", "optional": True},
        "maxiter": {"type": int, "optional": False},
        "popsize": {"type": int, "optional": True},
        "tol": {"type": float, "optional": True},
        "mutation": {"type": float, "optional": True},
        "recombination": {"type": float, "optional": True},
        "polish": {"type": bool, "optional": True},
        "init": {"type": "init", "optional": True},
        "atol": {"type": float, "optional": True},
        "updating": {"type": "updating", "optional": True},
        "workers": {"type": int, "optional": False},
        "vectorized": {"type": bool, "optional": True},
        "bounds": {"type": "sequence", "optional": False},
    },
    "shgo": {
        "n": {"type": int, "optional": False},
        "iters": {"type": int, "optional": False},
        "sampling_method": {"type": "sampling_method", "optional": True},
        "workers": {"type": int, "optional": True},
        "bounds": {"type": "sequence", "optional": False},
    },
}


def get_parameters_for_optimization(name):
    return _OPTIMIZATION_PARAMETERS.get(name, {})


def get_parameters_for_rss(name):
    function = getattr(optimization, name, None)
    if function is None:
        return []
    arguments = function.__code__.co_varnames[1:function.__code__.co_argcount]
    excluded = {
        "x",
        "experimental_rate",
        "rate_law",
        "experimental_args_for_rate",
        "number_of_parameters_to_optimize_for_rate",
        "vitrification",
        "vitrification_law",
        "experimental_args_for_vitrification",
        "number_of_parameters_to_optimize_for_vitrification",
        "coupling_law",
        "experimental_args_for_coupling",
        "tg_law",
        "experimental_args_for_tg",
        "tg_args",
        "rss_to_use_args",
    }
    return [argument for argument in arguments if argument not in excluded]


def get_main_args_dict_and_options_dict(main_args_dict, method_dict):
    keys_to_move = [key for key in method_dict if key in main_args_dict]
    for key in keys_to_move:
        main_args_dict[key] = method_dict.pop(key)
    return main_args_dict, method_dict


def pad_arrays(array_list, fill_value=np.nan):
    """Pad arrays in a list to match the longest array."""
    maximum = max(len(values) for values in array_list)
    return np.asarray(
        [
            np.pad(
                values,
                (0, maximum - len(values)),
                constant_values=fill_value,
            )
            for values in array_list
        ]
    )
