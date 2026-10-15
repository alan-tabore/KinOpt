"""Comparable diagnostics for completed kinetic model optimizations."""

from dataclasses import dataclass
from collections import defaultdict
import hashlib
import math
from typing import Optional

import numpy as np

from kinopt.src import optimization
from kinopt.src.optimization_validation import (
    experiment_slices,
    fitted_parameter_metadata,
)


@dataclass(frozen=True)
class ExperimentFit:
    """Fit error for one imported experiment and its role in the run."""

    index: int
    sample_count: int
    rmse: float
    role: str


@dataclass(frozen=True)
class FitComparison:
    """Model error recalculated independently from the solver objective."""

    rmse: float
    sample_count: int
    dataset_fingerprint: str
    overall_rmse: float
    validation_rmse: Optional[float]
    experiment_fits: tuple


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
    overall_rmse: float
    validation_rmse: Optional[float]
    training_sample_count: int
    validation_sample_count: int
    experiment_fits: tuple


@dataclass(frozen=True)
class ParameterStability:
    """Spread of one fitted parameter across a multi-start group."""

    index: int
    name: str
    unit: str
    minimum: float
    median: float
    maximum: float
    relative_range: float


@dataclass(frozen=True)
class MultiStartSummary:
    """Aggregate stability indicators for one persisted multi-start group."""

    group_identifier: str
    group_name: str
    seed: Optional[int]
    total_count: int
    completed_count: int
    comparable_count: int
    converged_count: int
    best_job_identifier: Optional[str]
    best_job_name: Optional[str]
    best_rmse: Optional[float]
    median_rmse: Optional[float]
    maximum_relative_parameter_range: Optional[float]
    parameter_stability: tuple
    message: str


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
    digest.update(str(tuple(config.experiment_lengths)).encode("ascii"))
    if config.training_mask is not None:
        digest.update(np.asarray(config.training_mask, dtype=np.uint8).tobytes())
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
    overall_rmse = float(np.sqrt(np.mean(np.square(residuals))))
    training_mask = (
        np.ones(experimental_rate.size, dtype=bool)
        if config.training_mask is None
        else np.asarray(config.training_mask, dtype=bool)
    )
    validation_mask = ~training_mask
    rmse = float(np.sqrt(np.mean(np.square(residuals[training_mask]))))
    validation_rmse = (
        None
        if not np.any(validation_mask)
        else float(np.sqrt(np.mean(np.square(residuals[validation_mask]))))
    )
    experiment_fits = []
    for index, experiment_slice in enumerate(experiment_slices(config)):
        experiment_residuals = residuals[experiment_slice]
        experiment_training = training_mask[experiment_slice]
        role = (
            "validation"
            if not np.any(experiment_training)
            else "fit" if np.all(experiment_training) else "mixed"
        )
        experiment_fits.append(
            ExperimentFit(
                index=index,
                sample_count=experiment_residuals.size,
                rmse=float(
                    np.sqrt(np.mean(np.square(experiment_residuals)))
                ),
                role=role,
            )
        )
    mean_absolute_error = float(np.mean(np.abs(residuals)))
    mean_residual = float(np.mean(residuals))
    maximum_absolute_error = float(np.max(np.abs(residuals)))
    indicators = (
        rmse,
        mean_absolute_error,
        mean_residual,
        maximum_absolute_error,
        overall_rmse,
    )
    if validation_rmse is not None:
        indicators += (validation_rmse,)
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
        overall_rmse=overall_rmse,
        validation_rmse=validation_rmse,
        training_sample_count=int(np.count_nonzero(training_mask)),
        validation_sample_count=int(np.count_nonzero(validation_mask)),
        experiment_fits=tuple(experiment_fits),
    )


def compare_fit(config, parameters):
    """Return an unweighted rate RMSE for one fitted parameter vector."""
    diagnostics = diagnose_fit(config, parameters)
    return FitComparison(
        rmse=diagnostics.rmse,
        sample_count=diagnostics.training_sample_count,
        dataset_fingerprint=dataset_fingerprint(config),
        overall_rmse=diagnostics.overall_rmse,
        validation_rmse=diagnostics.validation_rmse,
        experiment_fits=diagnostics.experiment_fits,
    )


def _maximum_relative_parameter_range(completed_jobs):
    parameter_vectors = [
        np.asarray(job.result.parameters, dtype=float)
        for job in completed_jobs
    ]
    if len(parameter_vectors) < 2:
        return None
    lengths = {values.size for values in parameter_vectors}
    if len(lengths) != 1 or not all(
        np.all(np.isfinite(values)) for values in parameter_vectors
    ):
        return None
    matrix = np.vstack(parameter_vectors)
    scale = np.max(np.abs(matrix), axis=0)
    ranges = np.ptp(matrix, axis=0)
    relative_ranges = np.divide(
        ranges,
        scale,
        out=np.zeros_like(ranges),
        where=scale > 0,
    )
    return float(np.max(relative_ranges))


def _parameter_stability(completed_jobs):
    if len(completed_jobs) < 2:
        return ()
    lengths = {len(job.result.parameters) for job in completed_jobs}
    if len(lengths) != 1:
        return ()
    matrix = np.vstack(
        [np.asarray(job.result.parameters, dtype=float) for job in completed_jobs]
    )
    if not np.all(np.isfinite(matrix)):
        return ()
    metadata = fitted_parameter_metadata(completed_jobs[0].config)
    stability = []
    for index in range(matrix.shape[1]):
        values = matrix[:, index]
        scale = float(np.max(np.abs(values)))
        relative_range = 0.0 if scale == 0 else float(np.ptp(values) / scale)
        parameter = metadata[index] if index < len(metadata) else None
        stability.append(
            ParameterStability(
                index=index,
                name=(
                    parameter.label
                    if parameter is not None
                    else f"Parameter {index + 1}"
                ),
                unit="" if parameter is None else parameter.unit,
                minimum=float(np.min(values)),
                median=float(np.median(values)),
                maximum=float(np.max(values)),
                relative_range=relative_range,
            )
        )
    return tuple(stability)


def summarize_multistart_groups(jobs):
    """Summarize convergence, fit quality, and parameter spread by group."""
    grouped = defaultdict(list)
    for job in jobs:
        if job.group_kind == "multi_start" and job.group_identifier:
            grouped[job.group_identifier].append(job)

    summaries = []
    ordered_groups = sorted(
        grouped.values(),
        key=lambda group: min(job.position for job in group),
    )
    for group in ordered_groups:
        ordered = sorted(group, key=lambda job: job.position)
        completed = [
            job
            for job in ordered
            if job.status.value == "completed" and job.result is not None
        ]
        measurements = []
        unavailable_count = 0
        for job in completed:
            try:
                measurements.append(
                    (job, compare_fit(job.config, job.result.parameters))
                )
            except (TypeError, ValueError, FloatingPointError):
                unavailable_count += 1

        fingerprints = {
            comparison.dataset_fingerprint
            for _, comparison in measurements
        }
        message = ""
        comparable = measurements
        if len(fingerprints) > 1:
            comparable = []
            message = "The group contains different measured datasets."
        elif unavailable_count:
            message = (
                f"Fit metrics unavailable for {unavailable_count} "
                "completed run(s)."
            )

        ranked = sorted(
            comparable,
            key=lambda item: (item[1].rmse, item[0].position),
        )
        best_job = ranked[0][0] if ranked else None
        rmse_values = [comparison.rmse for _, comparison in ranked]
        parameter_stability = _parameter_stability(completed)
        summaries.append(
            MultiStartSummary(
                group_identifier=ordered[0].group_identifier,
                group_name=ordered[0].group_name or "Multi-start",
                seed=ordered[0].group_seed,
                total_count=len(ordered),
                completed_count=len(completed),
                comparable_count=len(ranked),
                converged_count=sum(
                    job.result.solver_success is True for job in completed
                ),
                best_job_identifier=(
                    None if best_job is None else best_job.identifier
                ),
                best_job_name=None if best_job is None else best_job.name,
                best_rmse=None if not rmse_values else min(rmse_values),
                median_rmse=(
                    None if not rmse_values else float(np.median(rmse_values))
                ),
                maximum_relative_parameter_range=(
                    _maximum_relative_parameter_range(completed)
                ),
                parameter_stability=parameter_stability,
                message=message,
            )
        )
    return tuple(summaries)
