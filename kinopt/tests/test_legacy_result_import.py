"""Validate migration of historical KinOpt text results."""

import numpy as np

from kinopt.src import kinetic_models
from kinopt.src.legacy_result_import import import_legacy_result
from kinopt.src.optimization_comparison import compare_fit
from kinopt.src.optimization_queue import OptimizationQueue


def test_complete_legacy_result_is_imported_into_comparisons(tmp_path):
    parameters = np.array([1e8, 60000.0, 1.5])
    extents = (np.array([0.1, 0.2]), np.array([0.3, 0.4]))
    temperatures = (np.array([350.0, 360.0]), np.array([370.0, 380.0]))
    rates = tuple(
        kinetic_models.rate_for_nth_order(extent, temperature, *parameters)
        for extent, temperature in zip(extents, temperatures)
    )
    rows = "\n".join(
        "\t".join(str(value) for value in row)
        for row in zip(
            np.array([0.0, 1.0]), temperatures[0], rates[0], extents[0],
            np.array([0.0, 1.0]), temperatures[1], rates[1], extents[1],
        )
    )
    path = tmp_path / "old_result.txt"
    path.write_text(
        """================ Files ================
Files used for optimization:
- first.csv
- second.csv

================ Rate ================
Rate law: rate_for_nth_order
Experimental parameters for rate computation: ['extent', 'T']
Rate parameters initial guess:
- A1: 80000000
- E1: 55000
- n: 1.4

================ Optimization ================
Local optimization method: Nelder-Mead

================ Cost Function ================
Cost function: rss_mean
Experimental parameters for cost function computation: []
Cost function parameters: ()

================ Results ================
Rate optimization results:
- A1: 100000000
- E1: 60000
- n: 1.5

Final cost function value: 0.0
Total time for optimization: 2.5
Scipy final output:
 success: True
 nfev: 30
 nit: 15

================ Data used for optimization ================
Time1\tTemperature1\tRate1\tExtent1\tTime2\tTemperature2\tRate2\tExtent2
""" + rows + "\n",
        encoding="utf-8",
    )

    imported = import_legacy_result(path)
    queue = OptimizationQueue(tmp_path / "queue.sqlite3")
    job = queue.record_completed(
        imported.config,
        imported.outcome,
        imported.name,
    )

    assert job.name.startswith("Imported legacy result")
    assert job.config.experiment_lengths == (2, 2)
    assert job.result.parameters == tuple(parameters)
    assert compare_fit(job.config, job.result.parameters).rmse == 0.0
