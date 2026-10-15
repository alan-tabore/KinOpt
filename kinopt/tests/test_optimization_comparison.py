"""Validate solver-independent fit comparisons."""

from dataclasses import replace

import numpy as np
import pytest
from scipy.optimize import OptimizeResult

from kinopt.src import optimization
from kinopt.src.optimization_comparison import (
    compare_fit,
    dataset_fingerprint,
    diagnose_fit,
    summarize_multistart_groups,
)
from kinopt.src.optimization_queue import JobStatus, OptimizationQueue
from kinopt.src.optimization_runner import OptimizationRunResult


def test_rmse_is_recalculated_from_model_predictions(serializable_config):
    parameters = np.array([7e7, 57000., 1.2])
    predicted = optimization.model(
        parameters,
        serializable_config.rate_law,
        serializable_config.experimental_args_for_rate,
        serializable_config.rate_parameter_count,
        serializable_config.vitrification_law,
        serializable_config.experimental_args_for_vitrification,
        serializable_config.vitrification_parameter_count,
        serializable_config.coupling_law,
        serializable_config.experimental_args_for_coupling,
        serializable_config.tg_law,
        serializable_config.experimental_args_for_tg,
        serializable_config.tg_args,
    )
    expected = np.sqrt(
        np.mean(np.square(predicted - serializable_config.experimental_rate))
    )

    comparison = compare_fit(serializable_config, parameters)

    assert comparison.rmse == pytest.approx(expected)
    assert comparison.sample_count == 3


def test_fit_diagnostics_explain_pointwise_model_errors(serializable_config):
    parameters = np.array([7e7, 57000., 1.2])
    diagnostics = diagnose_fit(serializable_config, parameters)

    expected_residuals = (
        diagnostics.model_rate - serializable_config.experimental_rate
    )
    np.testing.assert_allclose(diagnostics.residuals, expected_residuals)
    assert diagnostics.rmse == pytest.approx(
        np.sqrt(np.mean(np.square(expected_residuals)))
    )
    assert diagnostics.mean_absolute_error == pytest.approx(
        np.mean(np.abs(expected_residuals))
    )
    assert diagnostics.mean_residual == pytest.approx(
        np.mean(expected_residuals)
    )
    assert diagnostics.maximum_absolute_error == pytest.approx(
        np.max(np.abs(expected_residuals))
    )
    assert diagnostics.sample_count == 3
    assert not diagnostics.measured_rate.flags.writeable
    assert not diagnostics.model_rate.flags.writeable
    assert not diagnostics.residuals.flags.writeable


def test_dataset_identity_depends_on_ordered_measured_rates(serializable_config):
    copied = replace(
        serializable_config,
        experimental_rate=np.array(serializable_config.experimental_rate),
    )
    changed_rates = np.array(serializable_config.experimental_rate)
    changed_rates[0] *= 1.01
    changed = replace(serializable_config, experimental_rate=changed_rates)

    assert dataset_fingerprint(copied) == dataset_fingerprint(serializable_config)
    assert dataset_fingerprint(changed) != dataset_fingerprint(serializable_config)


def test_comparison_rejects_a_model_output_with_the_wrong_shape(
    serializable_config,
):
    incompatible = replace(
        serializable_config,
        experimental_args_for_rate=(
            serializable_config.experimental_args_for_rate[0][:-1],
            serializable_config.experimental_args_for_rate[1][:-1],
        ),
    )

    with pytest.raises(ValueError, match="same shape"):
        compare_fit(incompatible, [1e8, 60000., 1.5])


def test_multistart_summary_reports_fit_and_parameter_stability(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    jobs = queue.add_many(
        (serializable_config,) * 3,
        ('Baseline', 'Alternative', 'Pending'),
        group_name='Nth-order stability',
        group_kind='multi_start',
        group_seed=12,
    )
    outcomes = (
        OptimizationRunResult(
            OptimizeResult(
                x=np.array([1e8, 60000., 1.5]),
                fun=0.,
                success=True,
                message='done',
            ),
            1.,
        ),
        OptimizationRunResult(
            OptimizeResult(
                x=np.array([8e7, 55000., 1.4]),
                fun=1.,
                success=False,
                message='budget reached',
            ),
            2.,
        ),
    )
    for job, outcome in zip(jobs, outcomes):
        queue.set_status(job.identifier, JobStatus.RUNNING)
        queue.complete(job.identifier, outcome)

    summaries = summarize_multistart_groups(queue.list_jobs())

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.group_name == 'Nth-order stability'
    assert summary.seed == 12
    assert summary.total_count == 3
    assert summary.completed_count == 2
    assert summary.comparable_count == 2
    assert summary.converged_count == 1
    assert summary.best_job_name == 'Baseline'
    assert summary.best_rmse == pytest.approx(0.)
    alternative_rmse = compare_fit(
        serializable_config,
        outcomes[1].result.x,
    ).rmse
    assert summary.median_rmse == pytest.approx(alternative_rmse / 2.)
    assert summary.maximum_relative_parameter_range == pytest.approx(0.2)
