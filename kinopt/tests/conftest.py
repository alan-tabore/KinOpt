"""Shared test data for optimization configuration and queue tests."""

import numpy as np
import pytest
from scipy import optimize

from kinopt.src import kinetic_models
from kinopt.src import optimization
from kinopt.src.optimization_runner import OptimizationRunConfig


@pytest.fixture
def serializable_config():
    extent = np.array([0.1, 0.3, 0.6])
    temperature = np.array([350., 400., 450.])
    known_parameters = np.array([1e8, 60000., 1.5])
    experimental_rate = kinetic_models.rate_for_nth_order(
        extent,
        temperature,
        *known_parameters,
    )
    return OptimizationRunConfig(
        cost_function=optimization.rss_mean,
        initial_guess=np.array([8e7, 55000., 1.4]),
        global_method='',
        global_optimizer=None,
        global_options=None,
        local_method='Nelder-Mead',
        local_optimizer=optimize.minimize,
        local_options={
            'method': 'Nelder-Mead',
            'options': {'maxiter': 10, 'disp': False},
        },
        experimental_rate=experimental_rate,
        rate_law=kinetic_models.rate_for_nth_order,
        experimental_args_for_rate=(extent, temperature),
        rate_parameter_count=3,
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
        max_iterations=10,
    )
