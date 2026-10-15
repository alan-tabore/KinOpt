"""Exercise durable optimization jobs and their lifecycle."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import sqlite3
from threading import Barrier

import numpy as np
import pytest
from scipy.optimize import OptimizeResult

from kinopt.src.optimization_queue import JobStatus, OptimizationQueue
from kinopt.src.optimization_runner import (
    OptimizationProgress,
    OptimizationRunResult,
)


def test_queue_preserves_order_names_and_configurations(
    tmp_path,
    serializable_config,
):
    database = tmp_path / 'state' / 'queue.sqlite3'
    queue = OptimizationQueue(database)

    first = queue.add(serializable_config, name='Nth-order trial')
    second = queue.add(serializable_config)

    assert first.position == 1
    assert first.name == 'Nth-order trial'
    assert second.position == 2
    assert second.name == 'Optimization 002'
    assert first.status is JobStatus.PENDING

    reopened_jobs = OptimizationQueue(database).list_jobs()
    assert [job.identifier for job in reopened_jobs] == [
        first.identifier,
        second.identifier,
    ]
    np.testing.assert_array_equal(
        reopened_jobs[0].config.initial_guess,
        serializable_config.initial_guess,
    )


def test_queue_adds_a_named_configuration_group_atomically(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    queue.add(serializable_config, 'Existing')
    configs = (
        serializable_config,
        replace(
            serializable_config,
            initial_guess=np.array([7e7, 50_000.0, 1.1]),
        ),
    )

    added = queue.add_many(configs, ('Start 1', 'Start 2'))

    assert [job.name for job in added] == ['Start 1', 'Start 2']
    assert [job.position for job in added] == [2, 3]
    np.testing.assert_array_equal(
        queue.get(added[1].identifier).config.initial_guess,
        [7e7, 50_000.0, 1.1],
    )


def test_queue_persists_multi_start_group_metadata(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')

    added = queue.add_many(
        (serializable_config, serializable_config),
        ('Start 1', 'Start 2'),
        group_name='Kamal starts',
        group_kind='multi_start',
        group_seed=42,
    )

    assert added[0].group_identifier
    assert added[1].group_identifier == added[0].group_identifier
    assert all(job.group_name == 'Kamal starts' for job in added)
    assert all(job.group_kind == 'multi_start' for job in added)
    assert all(job.group_seed == 42 for job in added)


def test_queue_rejects_an_invalid_group_without_partial_jobs(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    invalid = replace(serializable_config, cost_function=lambda *args: 0.0)

    with pytest.raises(ValueError, match='cost function'):
        queue.add_many(
            (serializable_config, invalid, serializable_config),
            ('First', 'Invalid', 'Third'),
        )

    assert queue.list_jobs() == []


def test_queue_validates_group_size_and_assigns_default_names(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')

    with pytest.raises(ValueError, match='At least one'):
        queue.add_many(())
    with pytest.raises(ValueError, match='one name for each'):
        queue.add_many((serializable_config,), ('First', 'Extra'))

    jobs = queue.add_many((serializable_config, serializable_config))

    assert [job.name for job in jobs] == [
        'Optimization 001',
        'Optimization 002',
    ]


def test_completed_external_run_is_recorded_atomically(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    outcome = OptimizationRunResult(
        result=OptimizeResult(
            x=np.array([1e8, 60000., 1.5]),
            fun=0.125,
            success=True,
            message='Converged',
            nit=12,
            nfev=34,
        ),
        elapsed_seconds=2.5,
    )

    recorded = queue.record_completed(
        serializable_config,
        outcome,
        name='Direct optimization',
    )

    assert recorded.name == 'Direct optimization'
    assert recorded.status is JobStatus.COMPLETED
    assert recorded.started_at is not None
    assert recorded.finished_at is not None
    assert recorded.message == 'Converged'
    assert recorded.result.parameters == (1e8, 60000., 1.5)
    assert recorded.result.cost == pytest.approx(0.125)
    assert recorded.result.elapsed_seconds == pytest.approx(2.5)

    reopened = OptimizationQueue(queue.database_path).get(recorded.identifier)
    assert reopened.result == recorded.result


def test_invalid_external_result_does_not_leave_a_partial_job(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    invalid_outcome = OptimizationRunResult(
        result=OptimizeResult(x=np.array([np.nan]), fun=np.nan),
        elapsed_seconds=1.,
    )

    with pytest.raises(ValueError):
        queue.record_completed(serializable_config, invalid_outcome)

    assert queue.list_jobs() == []


def test_running_job_is_recovered_as_interrupted(tmp_path, serializable_config):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    job = queue.add(serializable_config)
    running = queue.set_status(job.identifier, JobStatus.RUNNING)
    assert running.status is JobStatus.RUNNING

    reopened_queue = OptimizationQueue(queue.database_path)
    assert reopened_queue.recover_interrupted_jobs() == 1
    interrupted = reopened_queue.get(job.identifier)
    assert interrupted.status is JobStatus.INTERRUPTED
    assert 'stopped' in interrupted.message

    pending = reopened_queue.set_status(job.identifier, JobStatus.PENDING)
    assert pending.status is JobStatus.PENDING
    assert pending.message is None


def test_invalid_status_transition_does_not_change_job(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    job = queue.add(serializable_config)

    with pytest.raises(ValueError, match='pending to failed'):
        queue.set_status(job.identifier, JobStatus.FAILED)

    assert queue.get(job.identifier).status is JobStatus.PENDING


def test_unknown_database_schema_is_rejected(tmp_path):
    database = tmp_path / 'queue.sqlite3'
    with sqlite3.connect(database) as connection:
        connection.execute('PRAGMA user_version = 99')

    with pytest.raises(ValueError, match='Unsupported.*schema'):
        OptimizationQueue(database)


def test_version_one_database_is_migrated(tmp_path):
    database = tmp_path / 'queue.sqlite3'
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE optimization_jobs (
                identifier TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                config_json TEXT NOT NULL,
                status TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                message TEXT
            )
            """
        )
        connection.execute('PRAGMA user_version = 1')

    OptimizationQueue(database)

    with sqlite3.connect(database) as connection:
        version = connection.execute('PRAGMA user_version').fetchone()[0]
        columns = {
            row[1]
            for row in connection.execute(
                'PRAGMA table_info(optimization_jobs)'
            ).fetchall()
        }
    assert version == 4
    assert {
        'started_at',
        'finished_at',
        'result_json',
        'group_identifier',
        'group_name',
        'group_kind',
        'group_seed',
        'progress_json',
    } <= columns


def test_version_two_database_is_migrated(tmp_path):
    database = tmp_path / 'queue.sqlite3'
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE optimization_jobs (
                identifier TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                config_json TEXT NOT NULL,
                status TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                message TEXT,
                started_at TEXT,
                finished_at TEXT,
                result_json TEXT
            )
            """
        )
        connection.execute('PRAGMA user_version = 2')

    OptimizationQueue(database)

    with sqlite3.connect(database) as connection:
        version = connection.execute('PRAGMA user_version').fetchone()[0]
        columns = {
            row[1]
            for row in connection.execute(
                'PRAGMA table_info(optimization_jobs)'
            ).fetchall()
        }
    assert version == 4
    assert {
        'group_identifier',
        'group_name',
        'group_kind',
        'group_seed',
        'progress_json',
    } <= columns


def test_running_progress_is_persisted_and_cleared_on_retry(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / "queue.sqlite3")
    job = queue.add(serializable_config)
    queue.set_status(job.identifier, JobStatus.RUNNING)

    updated = queue.update_progress(
        job.identifier,
        OptimizationProgress(
            evaluations=12,
            best_cost=0.25,
            elapsed_seconds=3.5,
            estimated_remaining_seconds=5.0,
            best_parameters=(1.0, 2.0, 3.0),
        ),
    )

    assert updated.progress_history[-1].evaluations == 12
    assert updated.progress_history[-1].best_cost == pytest.approx(0.25)
    reopened = OptimizationQueue(queue.database_path).get(job.identifier)
    assert reopened.progress_history == updated.progress_history

    queue.set_status(job.identifier, JobStatus.INTERRUPTED)
    retried = queue.set_status(job.identifier, JobStatus.PENDING)
    assert retried.progress_history == ()


def test_pending_job_can_only_be_claimed_once(tmp_path, serializable_config):
    database = tmp_path / 'queue.sqlite3'
    queued = OptimizationQueue(database).add(serializable_config)
    queues = (OptimizationQueue(database), OptimizationQueue(database))
    ready = Barrier(2)

    def claim(queue):
        ready.wait()
        return queue.claim_next_pending()

    with ThreadPoolExecutor(max_workers=2) as executor:
        claimed = list(executor.map(claim, queues))

    claimed_jobs = [job for job in claimed if job is not None]
    assert [job.identifier for job in claimed_jobs] == [queued.identifier]
    assert claimed_jobs[0].status is JobStatus.RUNNING


def test_job_can_be_duplicated_as_a_new_pending_run(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    source = queue.add(serializable_config, 'Baseline')

    duplicate = queue.duplicate(source.identifier)

    assert duplicate.identifier != source.identifier
    assert duplicate.name == 'Baseline copy'
    assert duplicate.status is JobStatus.PENDING
    assert duplicate.position == 2
    np.testing.assert_array_equal(
        duplicate.config.initial_guess,
        source.config.initial_guess,
    )


def test_pending_jobs_can_be_reordered_without_moving_finished_states(
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    first = queue.add(serializable_config, 'First')
    second = queue.add(serializable_config, 'Second')
    third = queue.add(serializable_config, 'Third')

    queue.move_pending(third.identifier, -1)
    assert [job.identifier for job in queue.list_jobs()] == [
        first.identifier,
        third.identifier,
        second.identifier,
    ]
    assert [job.position for job in queue.list_jobs()] == [1, 2, 3]

    queue.set_status(second.identifier, JobStatus.CANCELLED)
    with pytest.raises(ValueError, match='Only pending'):
        queue.move_pending(second.identifier, -1)


def test_only_inactive_jobs_can_be_deleted(tmp_path, serializable_config):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    first = queue.add(serializable_config, 'First')
    second = queue.add(serializable_config, 'Second')
    running = queue.set_status(first.identifier, JobStatus.RUNNING)

    with pytest.raises(ValueError, match='running job'):
        queue.delete(running.identifier)

    queue.delete(second.identifier)
    jobs = queue.list_jobs()
    assert [job.identifier for job in jobs] == [first.identifier]
    assert jobs[0].position == 1
