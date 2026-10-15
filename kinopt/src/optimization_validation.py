"""Holdout configuration and parameter-plausibility helpers."""

from dataclasses import dataclass, replace
from typing import Optional

import numpy as np

from kinopt.src.model_metadata import kinetic_model_metadata


@dataclass(frozen=True)
class ParameterAssessment:
    """One fitted value with its name, unit, and any review warning."""

    index: int
    name: str
    unit: str
    value: float
    warning: str


def experiment_slices(config):
    """Return stable point slices for each experiment in a run config."""
    sample_count = np.asarray(config.experimental_rate).size
    lengths = config.experiment_lengths or (sample_count,)
    if any(length <= 0 for length in lengths) or sum(lengths) != sample_count:
        raise ValueError("Experiment lengths do not cover the measured rates.")
    slices = []
    start = 0
    for length in lengths:
        slices.append(slice(start, start + length))
        start += length
    return tuple(slices)


def with_validation_experiment(config, experiment_index):
    """Return a config fitted on every experiment except the selected one."""
    slices = experiment_slices(config)
    if len(slices) < 2:
        raise ValueError("Holdout validation requires at least two experiments.")
    if isinstance(experiment_index, bool) or not 0 <= experiment_index < len(slices):
        raise ValueError("The validation experiment index is out of range.")
    mask = np.ones(np.asarray(config.experimental_rate).size, dtype=bool)
    mask[slices[experiment_index]] = False
    return replace(config, training_mask=mask)


def validation_experiment_index(config) -> Optional[int]:
    """Return the wholly reserved experiment, if the mask defines one."""
    if config.training_mask is None:
        return None
    mask = np.asarray(config.training_mask, dtype=bool)
    held_out = []
    for index, experiment_slice in enumerate(experiment_slices(config)):
        values = mask[experiment_slice]
        if not np.any(values):
            held_out.append(index)
        elif not np.all(values):
            return None
    return held_out[0] if len(held_out) == 1 else None


def fitted_parameter_metadata(config):
    """Return central metadata in the same order as fitted parameters."""
    selected = []
    for kind, function in (
        ("rate", config.rate_law),
        ("vitrification", config.vitrification_law),
        ("coupling", config.coupling_law),
    ):
        if function is None:
            continue
        metadata = kinetic_model_metadata(kind, function.__name__)
        if metadata is not None:
            selected.extend(metadata.parameters)
    return tuple(selected)


def _configured_bounds(config, parameter_count):
    for options in (config.local_options, config.global_options):
        if not options:
            continue
        bounds = options.get("bounds")
        if bounds is None:
            continue
        array = np.asarray(bounds, dtype=float)
        if array.shape == (parameter_count, 2):
            return array
    return None


def assess_parameters(config, parameters, boundary_tolerance=0.01):
    """Flag nonfinite, nonpositive, out-of-reference, or boundary values."""
    values = np.asarray(parameters, dtype=float)
    metadata = fitted_parameter_metadata(config)
    bounds = _configured_bounds(config, values.size)
    assessments = []
    for index, value in enumerate(values):
        parameter = metadata[index] if index < len(metadata) else None
        name = parameter.label if parameter is not None else f"Parameter {index + 1}"
        unit = parameter.unit if parameter is not None else ""
        warnings = []
        if not np.isfinite(value):
            warnings.append("value is not finite")
        else:
            if parameter is not None:
                lower_reference = (
                    None
                    if parameter.lower_bound is None
                    else float(parameter.lower_bound)
                )
                upper_reference = (
                    None
                    if parameter.upper_bound is None
                    else float(parameter.upper_bound)
                )
                if lower_reference is not None and value < lower_reference:
                    warnings.append("below KinOpt's illustrative reference range")
                if upper_reference is not None and value > upper_reference:
                    warnings.append("above KinOpt's illustrative reference range")
            if bounds is not None:
                lower, upper = bounds[index]
                span = upper - lower
                if np.isfinite(span) and span > 0:
                    if value - lower <= boundary_tolerance * span:
                        warnings.append("at or near the solver's lower bound")
                    if upper - value <= boundary_tolerance * span:
                        warnings.append("at or near the solver's upper bound")
        assessments.append(
            ParameterAssessment(
                index=index,
                name=name,
                unit=unit,
                value=float(value),
                warning="; ".join(warnings),
            )
        )
    return tuple(assessments)
