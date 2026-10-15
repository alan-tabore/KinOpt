"""Validate solver-independent fit comparisons."""

from dataclasses import replace

import numpy as np
import pytest

from kinopt.src import optimization
from kinopt.src.optimization_comparison import (
    compare_fit,
    dataset_fingerprint,
    diagnose_fit,
)


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
