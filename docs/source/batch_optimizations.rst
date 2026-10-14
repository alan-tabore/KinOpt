Running several optimizations
=============================

KinOpt can save several model and optimizer configurations and run them in a
persistent queue. This is useful for comparing models, initial guesses, bounds,
or optimization methods on the same experimental data.

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

Running and monitoring jobs
---------------------------

Click **Start pending jobs** to process the queue. The first version runs one
optimization at a time so that several expensive calculations do not compete
for the same processor and memory. Closing and reopening KinOpt preserves the
queue and completed result summaries.

The table displays the selected model and strategy, queue state, solver
convergence, cost, duration, fitted parameters, and the solver's final message.
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

The regular **Start optimization** button and the batch runner cannot calculate
at the same time in one KinOpt window. Detailed text result files are currently
created by the regular single-run workflow; batch results are retained in the
batch table and its persistent local database.
