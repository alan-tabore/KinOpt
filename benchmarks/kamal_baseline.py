"""Benchmark the packaged Kamal example with KinOpt's quick-check setup."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import statistics
import sys
from typing import Callable, Optional, Sequence
import warnings

import numpy as np
import scipy
from scipy import optimize

from kinopt.examples import KAMAL_EXAMPLE, included_example_files
from kinopt.src import kinetic_models, optimization
from kinopt.src.data_extraction import extract_dsc_data_multiple_files
from kinopt.src.optimization_profiles import optimization_profile
from kinopt.src.optimization_runner import (
    OptimizationRunConfig,
    OptimizationRunResult,
    run_optimization,
)
from kinopt.src.parameter_examples import model_parameter_example


BENCHMARK_NAME = "packaged-kamal-quick-check"
PARAMETER_NAMES = ("A1", "E1", "A2", "E2", "m", "n")


def _profile_value(value):
    """Convert one GUI profile value to the type expected by SciPy."""
    if value is None:
        return None
    if value == "Yes":
        return True
    if value == "No":
        return False
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return float(value)
        except (TypeError, ValueError):
            return value


def build_kamal_benchmark_config() -> OptimizationRunConfig:
    """Build the same deterministic quick setup offered by the GUI example."""
    paths = included_example_files(KAMAL_EXAMPLE)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*zero initial extent.*")
        _, temperature, rate, extent = extract_dsc_data_multiple_files(
            paths,
            delimiter=KAMAL_EXAMPLE.delimiter,
            has_header=KAMAL_EXAMPLE.has_header,
        )

    initial_guess = np.array([
        float(model_parameter_example(name).value)
        for name in PARAMETER_NAMES
    ])
    profile = optimization_profile(KAMAL_EXAMPLE.calculation_profile)
    options = {
        name: converted
        for name, value in profile.values_for(KAMAL_EXAMPLE.local_method).items()
        if (converted := _profile_value(value)) is not None
    }

    return OptimizationRunConfig(
        cost_function=optimization.rss_mean,
        initial_guess=initial_guess,
        global_method="",
        global_optimizer=None,
        global_options=None,
        local_method=KAMAL_EXAMPLE.local_method,
        local_optimizer=optimize.minimize,
        local_options={
            "method": KAMAL_EXAMPLE.local_method,
            "options": options,
        },
        experimental_rate=rate,
        rate_law=kinetic_models.rate_for_kamal,
        experimental_args_for_rate=(extent, temperature),
        rate_parameter_count=len(PARAMETER_NAMES),
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
        max_iterations=int(options["maxiter"]),
    )


def _run_record(
    config: OptimizationRunConfig,
    runner: Callable[[OptimizationRunConfig], OptimizationRunResult],
    number: int,
) -> dict:
    outcome = runner(config)
    result = outcome.result
    modeled_rate = optimization.model(
        result.x,
        config.rate_law,
        config.experimental_args_for_rate,
        config.rate_parameter_count,
        config.vitrification_law,
        config.experimental_args_for_vitrification,
        config.vitrification_parameter_count,
        config.coupling_law,
        config.experimental_args_for_coupling,
        config.tg_law,
        config.experimental_args_for_tg,
        config.tg_args,
    )
    rmse = float(np.sqrt(np.mean((modeled_rate - config.experimental_rate) ** 2)))
    return {
        "run": number,
        "elapsed_seconds": float(outcome.elapsed_seconds),
        "success": bool(result.success),
        "status": int(result.status),
        "message": str(result.message),
        "evaluations": int(result.nfev),
        "iterations": int(result.nit),
        "cost": float(result.fun),
        "rmse": rmse,
        "parameters": {
            name: float(value)
            for name, value in zip(PARAMETER_NAMES, result.x)
        },
    }


def build_benchmark_report(
    repeats: int = 3,
    runner: Callable[[OptimizationRunConfig], OptimizationRunResult] = run_optimization,
) -> dict:
    """Run the benchmark and return measurements suitable for JSON output."""
    if repeats < 1:
        raise ValueError("The repeat count must be at least 1.")

    config = build_kamal_benchmark_config()
    runs = [_run_record(config, runner, number) for number in range(1, repeats + 1)]
    elapsed = [run["elapsed_seconds"] for run in runs]
    rmse = [run["rmse"] for run in runs]

    return {
        "schema_version": 1,
        "benchmark": BENCHMARK_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "dataset": {
            "experiments": len(KAMAL_EXAMPLE.file_names),
            "points": int(config.experimental_rate.size),
            "files": list(KAMAL_EXAMPLE.file_names),
        },
        "configuration": {
            "model": KAMAL_EXAMPLE.rate_model,
            "cost_function": KAMAL_EXAMPLE.cost_function,
            "solver": KAMAL_EXAMPLE.local_method,
            "profile": KAMAL_EXAMPLE.calculation_profile,
            "initial_parameters": {
                name: float(value)
                for name, value in zip(PARAMETER_NAMES, config.initial_guess)
            },
            "maximum_iterations": config.max_iterations,
        },
        "runs": runs,
        "summary": {
            "repeats": repeats,
            "elapsed_seconds": {
                "minimum": min(elapsed),
                "median": statistics.median(elapsed),
                "maximum": max(elapsed),
            },
            "rmse": {
                "minimum": min(rmse),
                "median": statistics.median(rmse),
                "maximum": max(rmse),
            },
            "successful_runs": sum(run["success"] for run in runs),
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the packaged four-file Kamal optimization benchmark and "
            "record both speed and fit quality."
        )
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="number of complete optimizations to run (default: 3)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional path for the complete JSON report",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = build_benchmark_report(args.repeats)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    summary = report["summary"]
    timing = summary["elapsed_seconds"]
    quality = summary["rmse"]
    print(
        f"{report['benchmark']}: {summary['repeats']} run(s), "
        f"median {timing['median']:.6f} s, "
        f"median RMSE {quality['median']:.6g}, "
        f"solver success {summary['successful_runs']}/{summary['repeats']}"
    )
    if args.output is not None:
        print(f"JSON report: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
