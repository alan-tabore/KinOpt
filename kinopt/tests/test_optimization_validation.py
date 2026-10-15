"""Validate holdout construction and parameter review warnings."""

from dataclasses import replace

import numpy as np

from kinopt.src.optimization_validation import (
    assess_parameters,
    validation_experiment_index,
    with_validation_experiment,
)


def test_complete_experiment_is_reserved_for_validation(serializable_config):
    config = replace(serializable_config, experiment_lengths=(1, 2))

    holdout = with_validation_experiment(config, 1)

    np.testing.assert_array_equal(holdout.training_mask, [True, False, False])
    assert validation_experiment_index(holdout) == 1


def test_parameter_assessment_names_values_and_solver_bound(serializable_config):
    config = replace(
        serializable_config,
        local_options={
            "method": "L-BFGS-B",
            "bounds": ((1e5, 1e10), (1e3, 2e5), (0.1, 5.0)),
        },
    )

    assessments = assess_parameters(config, [1e5, 60000.0, 1.5])

    assert [assessment.name for assessment in assessments] == ["A₁", "E₁", "n"]
    assert assessments[0].unit == "s^-1"
    assert "lower bound" in assessments[0].warning
    assert assessments[1].warning == ""
