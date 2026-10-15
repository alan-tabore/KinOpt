"""Keep the isoconversional benchmark executable and quality checked."""

from benchmarks.isoconversional_baseline import build_benchmark_report


def test_isoconversional_benchmark_preserves_objective_values():
    report = build_benchmark_report(repeats=1, points=50, evaluations=5)

    assert report["configuration"]["experiments"] == 4
    assert report["summary"]["maximum_absolute_difference"] < 1e-10
    assert report["summary"]["speedup"] > 0
