"""Portable JSON and CSV exports for optimization comparisons."""

import csv
from dataclasses import asdict
from datetime import datetime, timezone
import json
from importlib import metadata
from pathlib import Path
import platform

import numpy as np
import scipy

from kinopt.src.optimization_comparison import (
    compare_fit,
    summarize_multistart_groups,
)
from kinopt.src.optimization_serialization import config_to_dict


EXPORT_SCHEMA_VERSION = 1


def _kinopt_version():
    try:
        return metadata.version("kinopt")
    except metadata.PackageNotFoundError:
        return "development"


def _function_name(function):
    return "" if function is None else function.__name__


def _model_description(config):
    names = (
        _function_name(config.rate_law),
        _function_name(config.vitrification_law),
    )
    return " + ".join(name for name in names if name)


def _strategy_description(config):
    names = (config.global_method, config.local_method)
    return " -> ".join(name for name in names if name)


def _comparison_dict(job):
    if job.result is None:
        return None, ""
    try:
        comparison = compare_fit(job.config, job.result.parameters)
    except (TypeError, ValueError, FloatingPointError) as error:
        return None, str(error)
    return {
        "rmse": comparison.rmse,
        "overall_rmse": comparison.overall_rmse,
        "validation_rmse": comparison.validation_rmse,
        "sample_count": comparison.sample_count,
        "dataset_fingerprint": comparison.dataset_fingerprint,
        "experiments": [
            asdict(experiment) for experiment in comparison.experiment_fits
        ],
    }, ""


def _result_dict(result):
    if result is None:
        return None
    return {
        "parameters": list(result.parameters),
        "cost": result.cost,
        "elapsed_seconds": result.elapsed_seconds,
        "solver_success": result.solver_success,
        "solver_message": result.solver_message,
        "iterations": result.iterations,
        "evaluations": result.evaluations,
    }


def build_batch_export(jobs):
    """Return a versioned, JSON-compatible optimization comparison export."""
    jobs = tuple(jobs)
    exported_jobs = []
    for job in jobs:
        comparison, comparison_error = _comparison_dict(job)
        exported_jobs.append({
            "identifier": job.identifier,
            "name": job.name,
            "position": job.position,
            "status": job.status.value,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "message": job.message,
            "group": (
                None
                if job.group_identifier is None
                else {
                    "identifier": job.group_identifier,
                    "name": job.group_name,
                    "kind": job.group_kind,
                    "seed": job.group_seed,
                }
            ),
            "model": _model_description(job.config),
            "strategy": _strategy_description(job.config),
            "configuration": config_to_dict(job.config),
            "result": _result_dict(job.result),
            "progress_history": [
                asdict(point) for point in job.progress_history
            ],
            "comparison": comparison,
            "comparison_error": comparison_error,
        })

    payload = {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(
            timespec="microseconds"
        ),
        "kinopt_version": _kinopt_version(),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "jobs": exported_jobs,
        "multi_start_groups": [
            asdict(summary) for summary in summarize_multistart_groups(jobs)
        ],
    }
    json.dumps(payload, allow_nan=False)
    return payload


def write_batch_json(path, jobs):
    """Write a complete versioned comparison export as readable JSON."""
    target = Path(path)
    payload = build_batch_export(jobs)
    target.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def _csv_rows(jobs):
    jobs = tuple(jobs)
    summary_by_group = {
        summary.group_identifier: summary
        for summary in summarize_multistart_groups(jobs)
    }
    maximum_parameter_count = max(
        (
            max(
                len(job.config.initial_guess),
                0 if job.result is None else len(job.result.parameters),
            )
            for job in jobs
        ),
        default=0,
    )
    rows = []
    for job in jobs:
        comparison, comparison_error = _comparison_dict(job)
        result = job.result
        summary = summary_by_group.get(job.group_identifier)
        progress = job.progress_history[-1] if job.progress_history else None
        row = {
            "identifier": job.identifier,
            "name": job.name,
            "position": job.position,
            "status": job.status.value,
            "group_identifier": job.group_identifier or "",
            "group_name": job.group_name or "",
            "group_kind": job.group_kind or "",
            "group_seed": "" if job.group_seed is None else job.group_seed,
            "model": _model_description(job.config),
            "strategy": _strategy_description(job.config),
            "rmse": "" if comparison is None else comparison["rmse"],
            "validation_rmse": (
                ""
                if comparison is None
                else comparison["validation_rmse"]
                if comparison["validation_rmse"] is not None
                else ""
            ),
            "overall_rmse": (
                "" if comparison is None else comparison["overall_rmse"]
            ),
            "comparison_error": comparison_error,
            "solver_cost": "" if result is None else result.cost,
            "solver_success": "" if result is None else result.solver_success,
            "solver_message": "" if result is None else result.solver_message,
            "elapsed_seconds": "" if result is None else result.elapsed_seconds,
            "iterations": "" if result is None else result.iterations,
            "evaluations": "" if result is None else result.evaluations,
            "last_progress_evaluations": (
                "" if progress is None else progress.evaluations
            ),
            "last_progress_best_cost": (
                "" if progress is None else progress.best_cost
            ),
            "group_completed": "" if summary is None else summary.completed_count,
            "group_total": "" if summary is None else summary.total_count,
            "group_converged": "" if summary is None else summary.converged_count,
            "group_best_rmse": "" if summary is None else summary.best_rmse,
            "group_median_rmse": "" if summary is None else summary.median_rmse,
            "group_maximum_relative_parameter_range": (
                ""
                if summary is None
                else summary.maximum_relative_parameter_range
            ),
        }
        for index in range(maximum_parameter_count):
            row[f"start_parameter_{index + 1}"] = (
                job.config.initial_guess[index]
                if index < len(job.config.initial_guess)
                else ""
            )
            row[f"result_parameter_{index + 1}"] = (
                result.parameters[index]
                if result is not None and index < len(result.parameters)
                else ""
            )
        rows.append(row)
    return rows


def write_batch_csv(path, jobs):
    """Write a flat comparison table suitable for spreadsheets."""
    target = Path(path)
    rows = _csv_rows(jobs)
    if not rows:
        raise ValueError("At least one optimization job is required for export.")
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return target
