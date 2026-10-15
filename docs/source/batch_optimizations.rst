Running several optimizations
=============================

KinOpt can save several model and optimizer configurations and run them in a
persistent queue. This is useful for comparing models, initial guesses, bounds,
or optimization methods on the same experimental data.

An optimization started with the regular **Start optimization** button is added
to this table automatically when it finishes with a finite result. It receives
a dated ``Direct optimization`` name and can be compared with completed batch
jobs or another direct run. Cancelled runs and runs stopped by an error are not
added.

Preparing the queue
-------------------

1. Load and extract the experimental data.
2. Select the model, its initial parameters, and the optimization settings.
3. Click **Batch optimizations...** below **Start optimization**.
4. Enter an optional descriptive name such as ``Kamal - wide bounds``.
5. Click **Add current setup**.
6. Change the model or settings in the main window and add the next setup.

Each queued job is an independent snapshot. Later changes in the main window do
not alter jobs that have already been added.

Generating several starting points
-----------------------------------

Local optimizers can reach different solutions from different initial
parameter values. To prepare a reproducible multi-start comparison:

1. Select a local method with a finite lower and upper bound for every fitted
   parameter. *Log-space least squares* and bounded *L-BFGS-B* are suitable
   choices.
2. Enter an optional group name in **New job name**.
3. Choose the total number of runs and an integer seed.
4. Click **Add multi-start jobs**.

The first job keeps the initial values currently entered in the main window.
KinOpt distributes the other starts across the parameter bounds. Strictly
positive ranges are sampled logarithmically so that several orders of
magnitude are represented; ranges containing zero or negative values are
sampled linearly. The generated jobs show their initial values in the
**Parameters** column with a ``Start:`` prefix. Their names record the seed,
and the complete starting vector is stored in each immutable job configuration.

Using the same configuration, bounds, run count, and seed reproduces the same
starting points. Differential evolution and SHGO already explore their bounded
domain without using KinOpt's initial parameter values, so the multi-start
control refuses those strategies instead of creating duplicate calculations.

Running and monitoring jobs
---------------------------

Click **Start pending jobs** to process the queue. The first version runs one
optimization at a time so that several expensive calculations do not compete
for the same processor and memory. Closing and reopening KinOpt preserves the
queue and completed result summaries.

The table displays the selected model and strategy, queue state, solver
convergence, cost, duration, starting or fitted parameters, and the solver's
final message.
The queue state and solver result are separate: **Completed / Not converged**
means the calculation finished and produced a finite result, but the solver
stopped without reporting convergence, for example after using its iteration
budget.

Queue controls
--------------

* **Pause after current job** lets the active optimization finish and leaves the
  following jobs pending.
* **Cancel selected/current job** cancels a selected pending job or requests a
  cooperative stop of the active job.
* **Retry selected job** returns a failed, cancelled, or interrupted job to the
  pending queue.
* **Recover stopped jobs** marks jobs left running by an application or system
  interruption so that they can be selected and retried.
* **Duplicate selected** creates a new pending copy of any job's original
  configuration. The stored result is not copied.
* **Move pending job up/down** changes which pending configuration will run
  next. Jobs that have already started cannot be reordered.
* **Delete selected** removes an inactive job after confirmation. Deleting a
  completed job also deletes its stored result from the batch table.
* **Inspect result** opens measured and fitted rate curves for the selected
  completed job, together with its residuals, RMSE, mean absolute error, mean
  residual, largest residual, convergence status, and solver message.
* **Compare completed jobs** opens a table ranked by an unweighted RMSE
  recalculated from the model predictions and measured rates. This common score
  remains comparable when jobs use different solver cost functions. Lower is
  better. Jobs are grouped separately when their measured rate series differ.

Comparing completed results
---------------------------

Complete at least two jobs, then click **Compare completed jobs**. The
comparison table reports the common RMSE beside the solver cost, parameter
count, evaluation count, and duration. A solver cost is useful for understanding
the calculation that was requested, while the RMSE is the column to use for a
direct fit comparison on the same measurements.

The **Multi-start groups** tab summarizes each generated group. It reports the
number of completed and converged runs, the best and median RMSE, the best job,
and the largest relative range observed across the fitted parameters. A small
range means that the completed runs returned similar parameter values. There is
no universal acceptable percentage: interpret it together with convergence,
the residual plots, parameter units, and the physical meaning of the model.

Use **Export JSON...** to preserve the complete queued configurations, measured
data, starting values, results, comparison metrics, group summaries, seeds, and
software versions in a structured file. **Export CSV...** creates a flat table
for a spreadsheet, including one column per starting and fitted parameter plus
the main group indicators.

The RMSE has the same unit as the experimental reaction rate. It measures fit
error on the data used by the optimization; it does not by itself show whether
the fitted parameters are physically meaningful or whether the model predicts
an experiment that was not included in the fit.

Use **Inspect result** to look beyond the ranking. A residual is the model rate
minus the measured rate, so a positive value means overprediction. Residuals
should generally fluctuate around zero. Long sequences on the same side or a
few much larger errors deserve closer examination; they can come from model
limitations, experimental issues, or a particular region of the data. Solver
convergence and a visually convincing fit are separate checks, and neither one
alone proves that fitted parameters are physically meaningful.

The regular **Start optimization** button and the batch runner cannot calculate
at the same time in one KinOpt window. Detailed text result files are created by
the regular single-run workflow. Its completed result summary is also retained
in the batch table and its persistent local database; batch runs only use the
table and database.
