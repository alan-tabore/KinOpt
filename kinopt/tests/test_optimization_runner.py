"""Tests for the optimization engine without importing the Qt interface."""

from dataclasses import replace

import numpy as np
import pytest
from scipy import optimize

from kinopt.src import kinetic_models, optimization
from kinopt.src.optimization_runner import (
    LOG_SPACE_LEAST_SQUARES,
    OptimizationCancelled,
    OptimizationRunConfig,
    run_optimization,
)


def quadratic(parameters, *args):
    return (parameters[0] - 3.) ** 2


def make_config(initial_guess=None, local_options=None):
    return OptimizationRunConfig(
        cost_function=quadratic,
        initial_guess=np.array([1.]) if initial_guess is None else initial_guess,
        global_method='',
        global_optimizer=None,
        global_options=None,
        local_method='Nelder-Mead',
        local_optimizer=optimize.minimize,
        local_options=(
            {'method': 'Nelder-Mead', 'options': {'maxiter': 100}}
            if local_options is None else local_options
        ),
        experimental_rate=np.array([0.]),
        rate_law=None,
        experimental_args_for_rate=(),
        rate_parameter_count=0,
        vitrification_law=None,
        experimental_args_for_vitrification=(),
        vitrification_parameter_count=0,
        coupling_law=None,
        experimental_args_for_coupling=(),
        tg_law=None,
        experimental_args_for_tg=(),
        tg_args=None,
        cost_function_args=(),
        experimental_args_for_cost_function=(),
        max_iterations=100,
    )


def test_config_copies_and_freezes_mutable_inputs():
    initial_guess = np.array([1.])
    local_options = {'method': 'Nelder-Mead', 'options': {'maxiter': 100}}

    config = make_config(initial_guess, local_options)
    initial_guess[0] = 9.
    local_options['options']['maxiter'] = 1

    np.testing.assert_array_equal(config.initial_guess, [1.])
    assert config.local_options['options']['maxiter'] == 100
    with pytest.raises(ValueError):
        config.initial_guess[0] = 2.
    with pytest.raises(TypeError):
        config.local_options['method'] = 'BFGS'


def test_runner_fits_without_qt_and_keeps_config_unchanged():
    config = make_config()

    outcome = run_optimization(config)

    np.testing.assert_allclose(outcome.result.x, [3.], atol=1e-4)
    assert outcome.result.fun < 1e-8
    assert outcome.elapsed_seconds >= 0
    assert 'args' not in config.local_options
    assert 'callback' not in config.local_options


def test_runner_honours_cancellation_before_start():
    config = make_config()

    with pytest.raises(OptimizationCancelled):
        run_optimization(config, is_cancelled=lambda: True)


def test_runner_honours_cancellation_during_solver_callback():
    cancellation_checks = iter([False, True])

    def solver(function, initial_guess, callback, **kwargs):
        callback(initial_guess)
        raise AssertionError('Cancellation did not stop the solver callback')

    config = replace(make_config(), local_optimizer=solver)

    with pytest.raises(OptimizationCancelled):
        run_optimization(
            config,
            is_cancelled=lambda: next(cancellation_checks),
        )


def test_log_space_least_squares_returns_physical_parameters(
    serializable_config,
):
    config = replace(
        serializable_config,
        local_method=LOG_SPACE_LEAST_SQUARES,
        local_optimizer=optimize.least_squares,
        local_options={
            'jac': '2-point',
            'max_nfev': 200,
            'ftol': 1e-10,
            'xtol': 1e-10,
            'gtol': 1e-10,
            'bounds': ((1e5, 1e10), (1e3, 2e5), (0.1, 5.0)),
        },
        max_iterations=200,
    )
    callbacks = []

    outcome = run_optimization(config, callback=lambda values: callbacks.append(values))

    assert outcome.result.success
    assert outcome.result.fun < 1e-15
    np.testing.assert_allclose(
        outcome.result.x,
        [1e8, 60000.0, 1.5],
        rtol=1e-5,
    )
    assert outcome.result.residuals.shape == config.experimental_rate.shape
    assert callbacks
    assert np.all(callbacks[0] > 0)


@pytest.mark.parametrize(
    'initial_guess,bounds,message',
    [
        (np.array([0.0]), ((0.1, 10.0),), 'starting values'),
        (np.array([1.0]), ((0.0, 10.0),), 'bounds'),
        (np.array([1.0]), ((2.0, 10.0),), 'inside'),
        (np.array([1.0]), ((0.1, 10.0), (0.1, 10.0)), 'one lower'),
    ],
)
def test_log_space_least_squares_rejects_invalid_positive_domain(
    initial_guess,
    bounds,
    message,
):
    config = replace(
        make_config(initial_guess=initial_guess),
        local_method=LOG_SPACE_LEAST_SQUARES,
        local_optimizer=optimize.least_squares,
        local_options={'bounds': bounds, 'max_nfev': 10},
        max_iterations=10,
    )

    with pytest.raises(ValueError, match=message):
        run_optimization(config)


def test_log_space_least_squares_cannot_be_nested_in_a_global_method(
    serializable_config,
):
    with pytest.raises(ValueError, match='without a global optimizer'):
        replace(
            serializable_config,
            global_method='basinhopping',
            global_optimizer=optimize.basinhopping,
            global_options={'niter': 2},
            local_method=LOG_SPACE_LEAST_SQUARES,
            local_optimizer=optimize.least_squares,
        )


def make_kamal_least_squares_config(jacobian):
    extent = np.linspace(0.03, 0.95, 80)
    temperature = 330 + 140 * extent + 10 * np.sin(extent * 9)
    known_parameters = np.array([1e8, 60_000.0, 1e10, 80_000.0, 0.8, 1.2])
    experimental_rate = kinetic_models.rate_for_kamal(
        extent,
        temperature,
        *known_parameters,
    )
    return OptimizationRunConfig(
        cost_function=optimization.rss_mean,
        initial_guess=np.array([8e7, 57_000.0, 7e9, 76_000.0, 0.7, 1.1]),
        global_method='',
        global_optimizer=None,
        global_options=None,
        local_method=LOG_SPACE_LEAST_SQUARES,
        local_optimizer=optimize.least_squares,
        local_options={
            'jac': jacobian,
            'max_nfev': 200,
            'ftol': 1e-11,
            'xtol': 1e-11,
            'gtol': 1e-11,
            'bounds': (
                (1e6, 1e10),
                (30_000.0, 100_000.0),
                (1e8, 1e12),
                (40_000.0, 120_000.0),
                (0.1, 3.0),
                (0.1, 3.0),
            ),
        },
        experimental_rate=experimental_rate,
        rate_law=kinetic_models.rate_for_kamal,
        experimental_args_for_rate=(extent, temperature),
        rate_parameter_count=6,
        vitrification_law=None,
        experimental_args_for_vitrification=(),
        vitrification_parameter_count=0,
        coupling_law=None,
        experimental_args_for_coupling=(),
        tg_law=None,
        experimental_args_for_tg=(),
        tg_args=None,
        cost_function_args=(),
        experimental_args_for_cost_function=(),
        max_iterations=200,
    )


def test_auto_jacobian_reduces_kamal_residual_evaluations():
    analytic = run_optimization(make_kamal_least_squares_config('auto')).result
    numerical = run_optimization(make_kamal_least_squares_config('2-point')).result

    assert analytic.success
    assert numerical.success
    assert analytic.jacobian_source == 'analytic-kamal'
    assert numerical.jacobian_source == '2-point'
    assert analytic.analytic_jacobian_evaluations > 0
    assert analytic.residual_evaluations < numerical.residual_evaluations
    np.testing.assert_allclose(analytic.x, numerical.x, rtol=1e-6)


def test_auto_jacobian_falls_back_for_other_models(serializable_config):
    config = replace(
        serializable_config,
        local_method=LOG_SPACE_LEAST_SQUARES,
        local_optimizer=optimize.least_squares,
        local_options={
            'jac': 'auto',
            'max_nfev': 200,
            'bounds': ((1e5, 1e10), (1e3, 2e5), (0.1, 5.0)),
        },
        max_iterations=200,
    )

    result = run_optimization(config).result

    assert result.success
    assert result.jacobian_source == '2-point'
    assert result.analytic_jacobian_evaluations == 0
