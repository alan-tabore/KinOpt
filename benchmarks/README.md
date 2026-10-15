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
