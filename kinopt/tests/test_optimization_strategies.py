"""Validate optional representative-data exploration strategies."""

from dataclasses import replace

import numpy as np
from scipy.optimize import OptimizeResult

from kinopt.src.optimization_runner import OptimizationRunResult
from kinopt.src.optimization_strategies import (
    representative_subsample_mask,
    run_exploratory_then_full,
)


def test_representative_mask_keeps_each_experiment_and_existing_holdout(
    serializable_config,
):
    config = replace(
        serializable_config,
        experimental_rate=np.tile(serializable_config.experimental_rate, 2),
        experimental_args_for_rate=(
            np.tile(serializable_config.experimental_args_for_rate[0], 2),
            np.tile(serializable_config.experimental_args_for_rate[1], 2),
        ),
        experiment_lengths=(3, 3),
        training_mask=np.array([True, True, True, False, False, False]),
    )

    mask = representative_subsample_mask(config, 0.5, minimum_points=2)

    assert np.count_nonzero(mask[:3]) == 2
    assert not np.any(mask[3:])
    assert mask[0] and mask[2]


def test_two_stage_strategy_refines_full_config_from_exploratory_result(
    serializable_config,
):
    calls = []

    def runner(config, is_cancelled=None):
        calls.append(config)
        parameters = (
            np.array([9e7, 58000.0, 1.45])
            if len(calls) == 1
            else np.array([1e8, 60000.0, 1.5])
        )
        return OptimizationRunResult(
            OptimizeResult(x=parameters, fun=float(2 - len(calls))),
            elapsed_seconds=float(len(calls)),
        )

    outcome = run_exploratory_then_full(
        replace(serializable_config, experiment_lengths=(3,)),
        fraction=0.5,
        minimum_points=2,
        runner=runner,
    )

    assert len(calls) == 2
    assert np.count_nonzero(calls[0].training_mask) == 2
    np.testing.assert_array_equal(calls[1].initial_guess, [9e7, 58000.0, 1.45])
    assert calls[1].training_mask is None
    assert outcome.elapsed_seconds == 3.0
    assert outcome.result.exploratory_cost == 1.0
