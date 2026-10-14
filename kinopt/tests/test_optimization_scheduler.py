"""Validate sequential execution and failure isolation for queued runs."""

import numpy as np
from scipy.optimize import OptimizeResult

from kinopt.src.optimization_queue import JobStatus, OptimizationQueue
from kinopt.src.optimization_runner import OptimizationRunResult
from kinopt.src.optimization_scheduler import SequentialOptimizationScheduler


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
