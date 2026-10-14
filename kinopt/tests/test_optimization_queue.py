"""Exercise durable optimization jobs and their lifecycle."""

import sqlite3

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

    with pytest.raises(ValueError, match='pending to completed'):
        queue.set_status(job.identifier, JobStatus.COMPLETED)

    assert queue.get(job.identifier).status is JobStatus.PENDING


def test_unknown_database_schema_is_rejected(tmp_path):
    database = tmp_path / 'queue.sqlite3'
    with sqlite3.connect(database) as connection:
        connection.execute('PRAGMA user_version = 99')

    with pytest.raises(ValueError, match='Unsupported.*schema'):
        OptimizationQueue(database)
