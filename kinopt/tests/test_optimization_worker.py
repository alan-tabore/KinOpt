"""Exercise solver dispatch with tiny fits, independently of GUI form defaults."""

from copy import deepcopy

import numpy as np
import pytest
from scipy import optimize


def quadratic(parameters, *args):
    return (parameters[0] - 3.) ** 2


@pytest.fixture
def worker_factory(monkeypatch):
    monkeypatch.setenv('QT_QPA_PLATFORM', 'offscreen')
    from kinopt.src.main import OptimizationThread
    from kinopt.src.optimization_runner import OptimizationRunConfig

    def make_worker(
        global_name='', global_options=None, global_optimizer=None,
        local_optimizer=optimize.minimize,
    ):
        config = OptimizationRunConfig(
            cost_function=quadratic, initial_guess=np.array([1.]),
            global_method=global_name,
            global_optimizer=(
                global_optimizer or getattr(optimize, global_name)
                if global_name else None
            ),
            global_options=global_options,
            local_method='Nelder-Mead', local_optimizer=local_optimizer,
            local_options={'method': 'Nelder-Mead', 'options': {'maxiter': 100}},
            experimental_rate=np.array([0.]), rate_law=None,
            experimental_args_for_rate=(), rate_parameter_count=0,
            vitrification_law=None, experimental_args_for_vitrification=(),
            vitrification_parameter_count=0,
            coupling_law=None, experimental_args_for_coupling=(), tg_law=None,
            experimental_args_for_tg=(), tg_args=(), cost_function_args=(),
            experimental_args_for_cost_function=(), max_iterations=100,
        )
        return OptimizationThread(config)
    return make_worker


@pytest.mark.parametrize('solver,options', [
    ('', None),
    ('basinhopping', {'niter': 2, 'seed': 42}),
    ('differential_evolution', {'bounds': [(-5., 5.)], 'maxiter': 8, 'popsize': 5, 'seed': 42}),
    ('shgo', {'bounds': [(-5., 5.)], 'n': 16, 'iters': 1}),
])
def test_supported_solvers_recover_known_minimum(worker_factory, solver, options):
    original_options = deepcopy(options)
    worker = worker_factory(solver, options)
    completed, errors = [], []
    worker.end_of_optimization.connect(lambda result, elapsed: completed.append(result))
    worker.error_in_optimization_thread.connect(errors.append)

    worker.run()

    assert errors == []
    assert len(completed) == 1
    np.testing.assert_allclose(completed[0].x, [3.], atol=1e-4)
    assert completed[0].fun < 1e-8
    assert options == original_options


def test_basinhopping_keeps_solver_result_after_rejected_trial(worker_factory):
    expected = optimize.OptimizeResult(x=np.array([5.]), fun=4., success=True)
    completed = []

    def solver(function, initial_guess, callback, **kwargs):
        callback(np.array([5.]), 4., True)
        callback(np.array([4.]), 1., False)
        return expected

    worker = worker_factory(
        'basinhopping', {'niter': 2}, global_optimizer=solver
    )
    worker.end_of_optimization.connect(lambda result, elapsed: completed.append(result))
    worker.run()
    assert completed == [expected]
    np.testing.assert_array_equal(expected.x, [5.])
    assert expected.fun == 4.


@pytest.mark.parametrize('parameters,cost', [(np.array([np.inf]), 0.), (np.array([3.]), np.nan)])
def test_nonfinite_solver_result_is_reported_as_error(worker_factory, parameters, cost):
    worker = worker_factory(
        local_optimizer=lambda *args, **kwargs: optimize.OptimizeResult(
            x=parameters, fun=cost
        )
    )
    completed, errors = [], []
    worker.end_of_optimization.connect(lambda *args: completed.append(args))
    worker.error_in_optimization_thread.connect(errors.append)
    worker.run()
    assert completed == []
    assert len(errors) == 1
    assert 'non-finite' in str(errors[0])


def test_progress_callback_handles_timer_without_elapsed_tick(worker_factory, monkeypatch):
    from kinopt.src import main

    worker = worker_factory()
    worker.count = 0
    worker.start_time = 12.5
    monkeypatch.setattr(main.time_module, 'perf_counter', lambda: 12.5)
    updates = []
    worker.update_graph_signal.connect(lambda *values: updates.append(values))

    worker.optimization_callback(np.array([3.]))

    assert len(updates) == 1
    assert updates[0][1] >= 0
