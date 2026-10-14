"""Exercise durable optimization jobs and their lifecycle."""

from concurrent.futures import ThreadPoolExecutor
import sqlite3
from threading import Barrier

import numpy as np
import pytest

from kinopt.src.optimization_queue import JobStatus, OptimizationQueue


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
    assert version == 2
    assert {'started_at', 'finished_at', 'result_json'} <= columns


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
