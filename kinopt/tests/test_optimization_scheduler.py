"""Validate sequential execution and failure isolation for queued runs."""

from dataclasses import replace
from multiprocessing import get_context
import time

import numpy as np
from scipy import optimize
from scipy.optimize import OptimizeResult

from kinopt.src.optimization_queue import JobStatus, OptimizationQueue
from kinopt.src.optimization_runner import (
    LOG_SPACE_LEAST_SQUARES,
    OptimizationRunResult,
)
from kinopt.src.optimization_scheduler import (
    ConcurrentOptimizationScheduler,
    SequentialOptimizationScheduler,
    optimization_process_cost,
)


def _delayed_process(
    identifier,
    serialized_config,
    cancellation_event,
    result_connection,
):
    """Small spawn-safe process used to exercise orchestration only."""
    deadline = time.monotonic() + 0.2
    while time.monotonic() < deadline:
        if cancellation_event.is_set():
            result_connection.send(
                (identifier, "cancelled", "Optimization cancelled.")
            )
            result_connection.close()
            return
        time.sleep(0.005)
    result_connection.send(
        (
            identifier,
            "completed",
            OptimizationRunResult(
                result=OptimizeResult(
                    x=np.array([1.0, 2.0, 3.0]),
                    fun=0.25,
                    success=True,
                    message="done",
                    nit=2,
                    nfev=4,
                ),
                elapsed_seconds=0.2,
            ),
        )
    )
    result_connection.close()


def test_scheduler_runs_and_persists_a_real_optimization(
    tmp_path,
    serializable_config,
):
    database = tmp_path / 'queue.sqlite3'
    queue = OptimizationQueue(database)
    queued = queue.add(serializable_config, 'Short fit')

    finished = SequentialOptimizationScheduler(queue).run_next()

    assert finished.identifier == queued.identifier
    assert finished.status is JobStatus.COMPLETED
    assert finished.started_at is not None
    assert finished.finished_at is not None
    assert finished.result is not None
    assert np.isfinite(finished.result.cost)
    assert finished.result.elapsed_seconds >= 0
    assert len(finished.result.parameters) == 3

    reopened = OptimizationQueue(database).get(queued.identifier)
    assert reopened.result == finished.result


def test_scheduler_persists_log_space_least_squares_result(
    tmp_path,
    serializable_config,
):
    config = replace(
        serializable_config,
        local_method=LOG_SPACE_LEAST_SQUARES,
        local_optimizer=optimize.least_squares,
        local_options={
            'jac': '2-point',
            'max_nfev': 200,
            'bounds': ((1e5, 1e10), (1e3, 2e5), (0.1, 5.0)),
        },
        max_iterations=200,
    )
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    queued = queue.add(config, 'Scaled fit')

    finished = SequentialOptimizationScheduler(queue).run_next()

    assert finished.identifier == queued.identifier
    assert finished.status is JobStatus.COMPLETED
    assert finished.result.solver_success is True
    assert finished.result.iterations is None
    assert finished.result.evaluations is not None
    np.testing.assert_allclose(
        finished.result.parameters,
        [1e8, 60000.0, 1.5],
        rtol=1e-5,
    )


def test_failed_job_does_not_block_following_jobs(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    queued = [queue.add(serializable_config) for _ in range(3)]
    calls = []

    def fail_once_then_succeed(config, callback=None, is_cancelled=None):
        calls.append(config)
        if len(calls) == 1:
            raise RuntimeError('synthetic solver failure')
        return OptimizationRunResult(
            result=OptimizeResult(
                x=np.array([1., 2., 3.]),
                fun=0.25,
                success=False,
                message='Iteration budget reached',
                nit=10,
                nfev=25,
            ),
            elapsed_seconds=0.5,
        )

    scheduler = SequentialOptimizationScheduler(
        queue,
        runner=fail_once_then_succeed,
    )
    finished = scheduler.run_pending()

    assert [job.identifier for job in finished] == [
        job.identifier for job in queued
    ]
    assert [job.status for job in finished] == [
        JobStatus.FAILED,
        JobStatus.COMPLETED,
        JobStatus.COMPLETED,
    ]
    assert 'synthetic solver failure' in finished[0].message
    assert finished[1].result.solver_success is False
    assert finished[1].result.solver_message == 'Iteration budget reached'
    assert finished[1].result.iterations == 10
    assert finished[1].result.evaluations == 25


def test_cancellation_marks_only_claimed_job(tmp_path, serializable_config):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    first = queue.add(serializable_config)
    second = queue.add(serializable_config)
    scheduler = SequentialOptimizationScheduler(queue)

    cancelled = scheduler.run_next(
        cancellation_requested=lambda job: job.identifier == first.identifier
    )

    assert cancelled.status is JobStatus.CANCELLED
    assert queue.get(second.identifier).status is JobStatus.PENDING


def test_pausing_launches_leaves_following_job_pending(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    first = queue.add(serializable_config)
    second = queue.add(serializable_config)
    decisions = iter([True, False])

    finished = SequentialOptimizationScheduler(queue).run_pending(
        should_continue=lambda: next(decisions)
    )

    assert [job.identifier for job in finished] == [first.identifier]
    assert finished[0].status is JobStatus.COMPLETED
    assert queue.get(second.identifier).status is JobStatus.PENDING


def test_concurrent_scheduler_runs_two_isolated_jobs_together(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / "queue.sqlite3")
    queue.add(serializable_config, "First")
    queue.add(serializable_config, "Second")
    active_snapshots = []

    finished = ConcurrentOptimizationScheduler(
        queue,
        max_concurrent_jobs=2,
        process_budget=2,
        process_context=get_context("spawn"),
        process_target=_delayed_process,
    ).run_pending(active_jobs_changed=active_snapshots.append)

    assert any(len(snapshot) == 2 for snapshot in active_snapshots)
    assert [job.status for job in finished] == [
        JobStatus.COMPLETED,
        JobStatus.COMPLETED,
    ]


def test_concurrent_scheduler_cancels_only_requested_job(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / "queue.sqlite3")
    first = queue.add(serializable_config, "First")
    second = queue.add(serializable_config, "Second")

    finished = ConcurrentOptimizationScheduler(
        queue,
        max_concurrent_jobs=2,
        process_budget=2,
        process_context=get_context("spawn"),
        process_target=_delayed_process,
    ).run_pending(
        cancellation_requested=lambda job: job.identifier == first.identifier
    )

    statuses = {job.identifier: job.status for job in finished}
    assert statuses[first.identifier] is JobStatus.CANCELLED
    assert statuses[second.identifier] is JobStatus.COMPLETED


def test_process_cost_accounts_for_nested_solver_workers(serializable_config):
    configured = replace(serializable_config, global_options={"workers": 4})

    assert optimization_process_cost(configured, cpu_count=8) == 4
    assert optimization_process_cost(
        replace(configured, global_options={"workers": -1}),
        cpu_count=8,
    ) == 8
