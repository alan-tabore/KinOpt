"""Validate portable optimization comparison exports."""

import csv
import json

import numpy as np
from scipy.optimize import OptimizeResult

from kinopt.src.optimization_export import write_batch_csv, write_batch_json
from kinopt.src.optimization_queue import JobStatus, OptimizationQueue
from kinopt.src.optimization_runner import OptimizationRunResult


def completed_multistart_jobs(tmp_path, serializable_config):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    jobs = queue.add_many(
        (serializable_config, serializable_config),
        ('Start 1', 'Start 2'),
        group_name='Exported starts',
        group_kind='multi_start',
        group_seed=42,
    )
    parameters = (
        np.array([1e8, 60000., 1.5]),
        np.array([8e7, 55000., 1.4]),
    )
    for index, (job, values) in enumerate(zip(jobs, parameters), start=1):
        queue.set_status(job.identifier, JobStatus.RUNNING)
        queue.complete(
            job.identifier,
            OptimizationRunResult(
                OptimizeResult(
                    x=values,
                    fun=float(index),
                    success=index == 1,
                    message='done',
                    nit=10 * index,
                    nfev=20 * index,
                ),
                elapsed_seconds=float(index),
            ),
        )
    return queue.list_jobs()


def test_json_export_preserves_configs_results_and_group_summary(
    tmp_path,
    serializable_config,
):
    jobs = completed_multistart_jobs(tmp_path, serializable_config)
    destination = tmp_path / 'comparison.json'

    write_batch_json(destination, jobs)

    payload = json.loads(destination.read_text(encoding='utf-8'))
    assert payload['schema_version'] == 1
    assert len(payload['jobs']) == 2
    assert payload['jobs'][0]['group']['seed'] == 42
    assert payload['jobs'][0]['configuration']['initial_guess'] == [
        8e7,
        55000.,
        1.4,
    ]
    assert payload['jobs'][0]['result']['parameters'] == [
        1e8,
        60000.,
        1.5,
    ]
    assert payload['jobs'][0]['comparison']['rmse'] == 0.
    summary = payload['multi_start_groups'][0]
    assert summary['completed_count'] == 2
    assert summary['converged_count'] == 1
    assert summary['best_job_name'] == 'Start 1'


def test_csv_export_flattens_parameters_and_summary(
    tmp_path,
    serializable_config,
):
    jobs = completed_multistart_jobs(tmp_path, serializable_config)
    destination = tmp_path / 'comparison.csv'

    write_batch_csv(destination, jobs)

    with destination.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2
    assert rows[0]['name'] == 'Start 1'
    assert rows[0]['group_name'] == 'Exported starts'
    assert rows[0]['group_seed'] == '42'
    assert float(rows[0]['start_parameter_1']) == 8e7
    assert float(rows[0]['result_parameter_1']) == 1e8
    assert rows[0]['group_completed'] == '2'
    assert rows[0]['group_total'] == '2'
