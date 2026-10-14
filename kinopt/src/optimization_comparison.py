"""Comparable diagnostics for completed kinetic model optimizations."""

from dataclasses import dataclass
import hashlib
import math

import numpy as np

from kinopt.src import optimization


@dataclass(frozen=True)
class FitComparison:
    """Model error recalculated independently from the solver objective."""

    rmse: float
    sample_count: int
    dataset_fingerprint: str


def _experimental_rate(config):
    values = np.asarray(config.experimental_rate, dtype=np.float64)
    if values.size == 0:
        raise ValueError("Cannot compare an empty experimental rate series.")
    if not np.all(np.isfinite(values)):
        raise ValueError("Experimental rates must be finite for comparison.")
    return np.ascontiguousarray(values)


def dataset_fingerprint(config):
    """Identify jobs that use the same ordered experimental rate series."""
    values = _experimental_rate(config)
    digest = hashlib.sha256()
    digest.update(str(values.shape).encode("ascii"))
    digest.update(values.astype("<f8", copy=False).tobytes())
    return digest.hexdigest()


def compare_fit(config, parameters):
    """Return an unweighted rate RMSE for one fitted parameter vector."""
    experimental_rate = _experimental_rate(config)
    model_rate = np.asarray(
        optimization.model(
            np.asarray(parameters, dtype=float),
            config.rate_law,
            config.experimental_args_for_rate,
            config.rate_parameter_count,
            config.vitrification_law,
            config.experimental_args_for_vitrification,
            config.vitrification_parameter_count,
            config.coupling_law,
            config.experimental_args_for_coupling,
            config.tg_law,
            config.experimental_args_for_tg,
            config.tg_args,
        ),
        dtype=float,
    )
    if model_rate.shape != experimental_rate.shape:
        raise ValueError(
            "The model and experimental rates must have the same shape."
        )
    if not np.all(np.isfinite(model_rate)):
        raise ValueError("The model rates must be finite for comparison.")
    residuals = model_rate - experimental_rate
    rmse = float(np.sqrt(np.mean(np.square(residuals))))
    if not math.isfinite(rmse):
        raise ValueError("The comparison RMSE is not finite.")
    return FitComparison(
        rmse=rmse,
        sample_count=experimental_rate.size,
        dataset_fingerprint=dataset_fingerprint(config),
    )
