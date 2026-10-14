"""Tests for the optimization engine without importing the Qt interface."""

from dataclasses import replace

import numpy as np
import pytest
from scipy import optimize

from kinopt.src.optimization_runner import (
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
