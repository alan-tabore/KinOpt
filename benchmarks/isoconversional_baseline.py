"""Measure cached versus repeatedly prepared Vyazovkin objectives."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import statistics
import time
from typing import Optional, Sequence

import numpy as np
import scipy

from kinopt.src import isoconversional_methods as icm


BENCHMARK_NAME = "vyazovkin-prepared-integrals"


def _dataset(points):
    durations = (900.0, 720.0, 600.0, 480.0)
    heating_rates = (0.08, 0.10, 0.12, 0.15)
    times = tuple(np.linspace(0.0, duration, points) for duration in durations)
    temperatures = tuple(
        300.0 + rate * values
        for rate, values in zip(heating_rates, times)
    )
    return times, temperatures


def build_benchmark_report(repeats=5, points=2000, evaluations=200):
    """Benchmark equal objective values with and without cached intervals."""
    if repeats < 1 or points < 2 or evaluations < 1:
        raise ValueError("Repeats and evaluations must be positive; points need two.")
    times, temperatures = _dataset(points)
    energies = np.linspace(40_000.0, 120_000.0, evaluations)
    prepared = tuple(
        icm.prepare_integral_J(time_values, temperature_values)
        for time_values, temperature_values in zip(times, temperatures)
    )

    uncached_durations = []
    cached_durations = []
    uncached_values = cached_values = None
    for _ in range(repeats):
        started = time.perf_counter()
        uncached_values = np.asarray(
            [
                icm.compute_function_to_minimize(
                    energy,
                    times,
                    temperatures,
                )
                for energy in energies
            ]
        )
        uncached_durations.append(time.perf_counter() - started)

        started = time.perf_counter()
        cached_values = np.asarray(
            [
                icm.compute_prepared_function_to_minimize(energy, prepared)
                for energy in energies
            ]
        )
        cached_durations.append(time.perf_counter() - started)

    np.testing.assert_allclose(cached_values, uncached_values, rtol=1e-13)
    uncached_median = statistics.median(uncached_durations)
    cached_median = statistics.median(cached_durations)
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
        "configuration": {
            "experiments": len(times),
            "points_per_experiment": points,
            "objective_evaluations": evaluations,
            "repeats": repeats,
        },
        "uncached_seconds": uncached_durations,
        "cached_seconds": cached_durations,
        "summary": {
            "uncached_median_seconds": uncached_median,
            "cached_median_seconds": cached_median,
            "speedup": uncached_median / cached_median,
            "maximum_absolute_difference": float(
                np.max(np.abs(cached_values - uncached_values))
            ),
        },
    }


def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--points", type=int, default=2000)
    parser.add_argument("--evaluations", type=int, default=200)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = build_benchmark_report(args.repeats, args.points, args.evaluations)
    if args.output is not None:
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    summary = report["summary"]
    print(
        f"{BENCHMARK_NAME}: {summary['speedup']:.2f}x, "
        f"{summary['uncached_median_seconds']:.6f} s -> "
        f"{summary['cached_median_seconds']:.6f} s, "
        f"max |difference| "
        f"{summary['maximum_absolute_difference']:.3g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
