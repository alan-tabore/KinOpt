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


@dataclass(frozen=True)
class FitDiagnostics:
    """Pointwise model errors and understandable aggregate indicators."""

    measured_rate: np.ndarray
    model_rate: np.ndarray
    residuals: np.ndarray
    rmse: float
    mean_absolute_error: float
    mean_residual: float
    maximum_absolute_error: float
    sample_count: int


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


def diagnose_fit(config, parameters):
    """Recalculate pointwise rate residuals and common error indicators."""
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
    mean_absolute_error = float(np.mean(np.abs(residuals)))
    mean_residual = float(np.mean(residuals))
    maximum_absolute_error = float(np.max(np.abs(residuals)))
    indicators = (
        rmse,
        mean_absolute_error,
        mean_residual,
        maximum_absolute_error,
    )
    if not all(math.isfinite(value) for value in indicators):
        raise ValueError("The fit diagnostics are not finite.")

    arrays = []
    for values in (experimental_rate, model_rate, residuals):
        frozen = np.ascontiguousarray(values, dtype=np.float64)
        frozen.setflags(write=False)
        arrays.append(frozen)
    return FitDiagnostics(
        measured_rate=arrays[0],
        model_rate=arrays[1],
        residuals=arrays[2],
        rmse=rmse,
        mean_absolute_error=mean_absolute_error,
        mean_residual=mean_residual,
        maximum_absolute_error=maximum_absolute_error,
        sample_count=experimental_rate.size,
    )


def compare_fit(config, parameters):
    """Return an unweighted rate RMSE for one fitted parameter vector."""
    diagnostics = diagnose_fit(config, parameters)
    return FitComparison(
        rmse=diagnostics.rmse,
        sample_count=diagnostics.sample_count,
        dataset_fingerprint=dataset_fingerprint(config),
    )
