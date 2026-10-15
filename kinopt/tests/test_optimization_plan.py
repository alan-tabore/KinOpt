"""Validate generated model, method, and profile comparison plans."""

import numpy as np
import pytest
from scipy import optimize

from kinopt.src import kinetic_models
from kinopt.src.optimization_plan import generate_comparison_plan
from kinopt.src.optimization_profiles import (
    BALANCED_PROFILE_NAME,
    QUICK_PROFILE_NAME,
)
from kinopt.src.optimization_runner import (
    LOG_SPACE_LEAST_SQUARES,
    run_optimization,
)


def test_plan_builds_the_selected_cross_product(serializable_config):
    entries = generate_comparison_plan(
        serializable_config,
        ('rate_for_nth_order', 'rate_for_kamal'),
        (LOG_SPACE_LEAST_SQUARES, 'L-BFGS-B'),
        (QUICK_PROFILE_NAME, BALANCED_PROFILE_NAME),
        'Kinetic comparison',
    )

    assert len(entries) == 8
    assert entries[0].name == (
        'Kinetic comparison - Nth-order model - Log-space least squares - '
        'Quick check'
    )
    combinations = {
        (entry.rate_model, entry.local_method, entry.profile_name)
        for entry in entries
    }
    assert len(combinations) == 8

    nth_order = entries[0].config
    np.testing.assert_array_equal(
        nth_order.initial_guess,
        serializable_config.initial_guess,
    )
    assert nth_order.local_optimizer is optimize.least_squares
    assert nth_order.local_options['bounds'] == (
        (1., 1e20),
        (1000., 350000.),
        (0.1, 20.),
    )

    kamal = next(
        entry.config
        for entry in entries
        if entry.rate_model == 'rate_for_kamal'
        and entry.local_method == 'L-BFGS-B'
        and entry.profile_name == QUICK_PROFILE_NAME
    )
    assert kamal.rate_law is kinetic_models.rate_for_kamal
    assert kamal.rate_parameter_count == 6
    np.testing.assert_array_equal(
        kamal.initial_guess,
        [1e8, 50000., 1e8, 50000., 2., 2.],
    )
    assert kamal.local_optimizer is optimize.minimize
    assert kamal.local_options['method'] == 'L-BFGS-B'
    assert kamal.local_options['jac'] == 'auto'
    assert len(kamal.local_options['bounds']) == 6


def test_generated_log_space_model_comparison_runs(serializable_config):
    entries = generate_comparison_plan(
        serializable_config,
        (
            'rate_for_nth_order',
            'rate_for_autocatalytic',
            'rate_for_kamal',
        ),
        (LOG_SPACE_LEAST_SQUARES,),
        (QUICK_PROFILE_NAME,),
        'Executable plan',
    )

    outcomes = [run_optimization(entry.config) for entry in entries]

    assert len(outcomes) == 3
    assert all(np.all(np.isfinite(outcome.result.x)) for outcome in outcomes)
    assert all(np.isfinite(outcome.result.fun) for outcome in outcomes)


@pytest.mark.parametrize(
    'models,methods,profiles,message',
    [
        ((), (LOG_SPACE_LEAST_SQUARES,), (QUICK_PROFILE_NAME,), 'rate model'),
        (('rate_for_nth_order',), (), (QUICK_PROFILE_NAME,), 'method'),
        (('rate_for_nth_order',), (LOG_SPACE_LEAST_SQUARES,), (), 'profile'),
    ],
)
def test_plan_requires_each_selection(
    serializable_config,
    models,
    methods,
    profiles,
    message,
):
    with pytest.raises(ValueError, match=message):
        generate_comparison_plan(
            serializable_config,
            models,
            methods,
            profiles,
            'Invalid plan',
        )
