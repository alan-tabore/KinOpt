# KinOpt performance benchmarks

The Kamal baseline runs the same four packaged datasets, illustrative model
parameters, Nelder-Mead solver, mean residual cost and **Quick check** budget as
the graphical example. It records speed and fit quality together so that a
faster result is not mistaken for an equivalent result when its fit is worse.

From the repository root, with KinOpt installed in its virtual environment:

```bash
.venv/bin/python -m benchmarks.kamal_baseline \
  --repeats 3 \
  --output /tmp/kinopt-kamal-baseline.json
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m benchmarks.kamal_baseline `
  --repeats 3 `
  --output "$env:TEMP\kinopt-kamal-baseline.json"
```

The concise terminal line is useful for a quick check. The JSON report also
contains the Python, NumPy and SciPy versions, platform, dataset size, initial
and final parameters, solver status, iterations, function evaluations, cost,
RMSE and timing for every repetition. Keep reports outside the repository by
default because timings depend on the machine and its current load.

Run this benchmark before and after a numerical or performance change on the
same machine. Compare the median time only when RMSE, solver status and the
resulting parameters remain scientifically acceptable.

To measure the scaled least-squares solver with the same data, starting values,
bounds and Quick check budget:

```bash
.venv/bin/python -m benchmarks.kamal_baseline \
  --solver log-space-least-squares \
  --repeats 3 \
  --output /tmp/kinopt-kamal-log-least-squares.json
```

The ``--profile quick|balanced|thorough`` option applies the corresponding GUI
profile to either solver. For example, this measures whether a Thorough search
with Nelder-Mead reaches a quality comparable to Quick log-space least squares:

```bash
.venv/bin/python -m benchmarks.kamal_baseline \
  --solver nelder-mead \
  --profile thorough \
  --repeats 3 \
  --output /tmp/kinopt-kamal-nelder-thorough.json
```

Log-space least squares uses ``--jacobian auto`` through every calculation
profile. Standalone nth-order, autocatalytic, and Kamal rate models use
KinOpt's analytic derivatives. Vitrification, coupled, and custom model
combinations fall back to SciPy's ``2-point`` numerical derivative. To measure
the Kamal finite-difference baseline explicitly on the same machine:

```bash
.venv/bin/python -m benchmarks.kamal_baseline \
  --solver log-space-least-squares \
  --jacobian 2-point \
  --repeats 3 \
  --output /tmp/kinopt-kamal-numerical-jacobian.json
```

Each run records both SciPy's ``evaluations`` value and the actual number of
calls to KinOpt's residual function in ``residual_evaluations``. This second
number includes the extra residual calls used to approximate a numerical
Jacobian and therefore makes the comparison explicit. The
``kinetic_evaluations`` field counts full kinetic calculation passes. With an
analytic Jacobian, KinOpt calculates the rate and derivatives together and
reuses them when SciPy asks for both at the same parameter vector.

## Representative two-stage fitting

For a local solver, `--exploratory-fraction` first fits evenly distributed
points from every experiment with a fraction of the evaluation budget. KinOpt
then uses those parameters as the starting point for a normal fit on every
fitting point. The reported time includes both stages and the reported RMSE is
always calculated on the complete dataset.

Compare it with a direct run on the same machine before using it for a long
campaign:

```bash
.venv/bin/python -m benchmarks.kamal_baseline \
  --solver log-space-least-squares --profile quick --repeats 3 \
  --output /tmp/kinopt-kamal-direct.json

.venv/bin/python -m benchmarks.kamal_baseline \
  --solver log-space-least-squares --profile quick --repeats 3 \
  --exploratory-fraction 0.25 \
  --output /tmp/kinopt-kamal-two-stage.json
```

The strategy is optional because its gain depends on the dataset, starting
values, and solver. Compare timing, final parameters, convergence, and RMSE;
do not select it from timing alone.

## Isoconversional integral benchmark

Vyazovkin analyses repeatedly evaluate the same time intervals and average
temperatures at different activation energies. KinOpt prepares those fixed
arrays once. The following benchmark compares the cached objective with a
version that rebuilds them for every evaluation and verifies identical values:

```bash
.venv/bin/python -m benchmarks.isoconversional_baseline \
  --repeats 5 --points 2000 --evaluations 200 \
  --output /tmp/kinopt-isoconversional.json
```
