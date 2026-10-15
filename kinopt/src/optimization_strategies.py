"""Measured optional strategies that preserve a final full-data fit."""

from dataclasses import replace
import math

import numpy as np

from kinopt.src.optimization_runner import (
    LOG_SPACE_LEAST_SQUARES,
    OptimizationProgress,
    OptimizationRunResult,
    run_optimization,
)
from kinopt.src.optimization_validation import experiment_slices


def representative_subsample_mask(config, fraction=0.25, minimum_points=3):
    """Select evenly distributed fitting points within every experiment."""
    if not 0 < fraction < 1:
        raise ValueError("The exploratory fraction must be between 0 and 1.")
    if isinstance(minimum_points, bool) or minimum_points < 2:
        raise ValueError("At least two exploratory points are required.")
    original = (
        np.ones(np.asarray(config.experimental_rate).size, dtype=bool)
        if config.training_mask is None
        else np.asarray(config.training_mask, dtype=bool)
    )
    selected = np.zeros_like(original)
    for experiment_slice in experiment_slices(config):
        indices = np.flatnonzero(original[experiment_slice]) + experiment_slice.start
        if indices.size == 0:
            continue
        count = min(
            indices.size,
            max(minimum_points, int(math.ceil(indices.size * fraction))),
        )
        positions = np.unique(
            np.rint(np.linspace(0, indices.size - 1, count)).astype(int)
        )
        selected[indices[positions]] = True
    if not np.any(selected):
        raise ValueError("The exploratory subset contains no fitting data.")
    if np.array_equal(selected, original):
        raise ValueError(
            "The dataset is too small for the requested exploratory subset."
        )
    return selected


def _exploratory_config(config, fraction, budget_fraction, minimum_points):
    budget = max(1, int(math.ceil(config.max_iterations * budget_fraction)))
    local_options = dict(config.local_options or {})
    if config.local_method == LOG_SPACE_LEAST_SQUARES:
        local_options["max_nfev"] = budget
    else:
        solver_options = dict(local_options.get("options") or {})
        solver_options["maxiter"] = budget
        local_options["options"] = solver_options
    return replace(
        config,
        local_options=local_options,
        max_iterations=budget,
        training_mask=representative_subsample_mask(
            config,
            fraction,
            minimum_points,
        ),
    )


def run_exploratory_then_full(
    config,
    fraction=0.25,
    budget_fraction=0.25,
    minimum_points=3,
    *,
    runner=run_optimization,
    is_cancelled=None,
    progress_callback=None,
):
    """Explore a representative subset, then always refine on all fitting data."""
    if config.global_method:
        raise ValueError("Two-stage fitting currently supports local solvers only.")
    if not 0 < budget_fraction <= 1:
        raise ValueError("The exploratory budget fraction must be above 0 and at most 1.")
    exploratory_config = _exploratory_config(
        config,
        fraction,
        budget_fraction,
        minimum_points,
    )
    exploratory_kwargs = {"is_cancelled": is_cancelled}
    if progress_callback is not None:
        exploratory_kwargs["progress_callback"] = progress_callback
    exploratory = runner(exploratory_config, **exploratory_kwargs)
    full_config = replace(
        config,
        initial_guess=np.asarray(exploratory.result.x, dtype=float),
    )
    evaluation_offset = int(getattr(exploratory.result, "nfev", 0) or 0)

    def full_progress(progress):
        progress_callback(
            OptimizationProgress(
                evaluations=evaluation_offset + progress.evaluations,
                best_cost=progress.best_cost,
                elapsed_seconds=(
                    exploratory.elapsed_seconds + progress.elapsed_seconds
                ),
                estimated_remaining_seconds=progress.estimated_remaining_seconds,
                best_parameters=progress.best_parameters,
            )
        )

    full_kwargs = {"is_cancelled": is_cancelled}
    if progress_callback is not None:
        full_kwargs["progress_callback"] = full_progress
    final = runner(full_config, **full_kwargs)
    final.result.exploratory_parameters = np.asarray(
        exploratory.result.x,
        dtype=float,
    )
    final.result.exploratory_cost = float(exploratory.result.fun)
    final.result.exploratory_elapsed_seconds = float(
        exploratory.elapsed_seconds
    )
    final.result.exploratory_fraction = float(fraction)
    return OptimizationRunResult(
        result=final.result,
        elapsed_seconds=(
            exploratory.elapsed_seconds + final.elapsed_seconds
        ),
    )
