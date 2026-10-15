"""Validate the reproducible Kamal performance benchmark."""

import json
from types import SimpleNamespace

import numpy as np

from benchmarks.kamal_baseline import (
    BENCHMARK_NAME,
    PARAMETER_NAMES,
    build_benchmark_report,
    build_kamal_benchmark_config,
)
from kinopt.src.optimization import rss_mean
from kinopt.src.optimization_runner import OptimizationRunResult


def test_benchmark_uses_the_complete_guided_example_setup():
    config = build_kamal_benchmark_config()

    assert config.cost_function is rss_mean
    assert config.local_method == "Nelder-Mead"
    assert config.local_options["options"]["maxiter"] == 200
    assert config.max_iterations == 200
    assert config.rate_parameter_count == len(PARAMETER_NAMES)
    assert config.experimental_rate.size > 10_000
    np.testing.assert_array_equal(
        config.initial_guess,
        [1e8, 50_000, 1e8, 50_000, 2, 2],
    )


def test_report_keeps_speed_and_fit_quality_for_each_run():
    elapsed = iter((1.5, 1.0, 2.0))

    def fake_runner(config):
        parameters = np.asarray(config.initial_guess)
        cost = config.cost_function(
            parameters,
            config.experimental_rate,
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
        result = SimpleNamespace(
            x=parameters,
            fun=cost,
            success=False,
            status=2,
            message="budget reached",
            nfev=20,
            nit=10,
        )
        return OptimizationRunResult(result=result, elapsed_seconds=next(elapsed))

    report = build_benchmark_report(repeats=3, runner=fake_runner)

    assert report["benchmark"] == BENCHMARK_NAME
    assert report["dataset"]["experiments"] == 4
    assert report["summary"]["elapsed_seconds"] == {
        "minimum": 1.0,
        "median": 1.5,
        "maximum": 2.0,
    }
    assert report["summary"]["successful_runs"] == 0
    assert report["runs"][0]["evaluations"] == 20
    assert report["runs"][0]["message"] == "budget reached"
    assert report["runs"][0]["rmse"] > 0
    json.dumps(report, allow_nan=False)


def test_report_rejects_an_empty_measurement_set():
    try:
        build_benchmark_report(repeats=0)
    except ValueError as error:
        assert str(error) == "The repeat count must be at least 1."
    else:
        raise AssertionError("A benchmark without runs should be rejected")
