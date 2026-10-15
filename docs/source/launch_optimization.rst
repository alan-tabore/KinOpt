Performing the optimization of a kinetic model
==============================================

To perform the optimization of a kinetic model:

1. Make sure you loaded the data
2. Select a model
    1. You must at least select a rate model or a vitrification model
    2. If a vitrification model is selected, you must provide a tg law
    3. If both rate and vitrification model, you must provide a coupling law
3. Provide the initial guess for your model
4. Switch to the *'optimization method and parameters'* section
5. Select an optimization method
    1. You must at least select a global or local optimization method
    2. If you selected the *'basinhopping'* or *'shgo'* global optimization method, it is recommended to also select a local optimization method.
    3. You must select a cost function (:func:`rss_mean<optimization.rss_mean>` is recommended)
6. Select a calculation profile and click *Apply profile*
7. Click *Review setup…* to inspect the frozen configuration and any warning
8. Start from the review window, or click *Start optimization* to start directly

When you select a model, optimization method, or cost function, KinOpt displays
a short explanation at the top of the current page. It describes the main
assumption, a typical use, and the most important point to check. You can also
hover over an option in a selection list to preview the same guidance before
choosing it. When a mathematical expression applies, the contextual panel also
shows the equation used by KinOpt.

Empty parameter fields show a grey illustrative value and its unit when one is
available. This text is only a placeholder: KinOpt does not treat it as an
entered value. Replace it with a value appropriate for your material and data,
or use ``Autofill`` to write the example values into the fields. These examples
are starting points, not universal kinetic constants.

The calculation profiles provide understandable starting configurations for
the selected solver:

* *Quick check* uses a small budget to verify that the data, model, bounds, and
  optimization setup work together. Its result is preliminary.
* *Balanced (recommended)* uses practical budgets and tolerances for a routine
  fit.
* *Thorough search* increases the search budget and tightens tolerances. It can
  take substantially longer, so compare its result with the balanced fit.

Clicking *Apply profile* writes values into the solver, bounds, and cost fields
currently displayed. Every field remains editable. Selecting another profile
only changes its explanation; it does not replace your values until you click
*Apply profile*. A larger calculation budget does not guarantee a better or
physically meaningful model, so always inspect convergence and residuals.

For models whose fitted parameters are all strictly positive, *Log-space least
squares* is a fast local option designed for rate-fitting objectives. KinOpt
optimizes the base-10 logarithm of each parameter and converts the final result
back to the physical values shown elsewhere in the application. This prevents
a factor near ``1e13`` from sharing the same numerical scale as an exponent
near ``1``. The method requires a positive lower and upper bound for every free
parameter, and each starting value must lie inside its bounds. It runs on its
own and cannot be combined with a global method.

The method fits one residual per measured point and supports every cost
function currently offered by KinOpt, including the relative and weighted
variants. Its *max_nfev* field limits model evaluations. As with every local
method, compare the final residuals and fitted parameters rather than relying
only on the solver's success flag.

Keep the *jac* field on ``auto`` for normal use. With a standalone nth-order,
autocatalytic, or Kamal rate model, KinOpt then uses its analytic derivatives
to avoid the extra model calls needed by finite differences. This applies to
*Log-space least squares* and to the gradient-based *CG*, *BFGS*, and
*L-BFGS-B* methods. For those three scalar minimizers, KinOpt derives the cost
gradient from the rate Jacobian and the selected residual weighting. A
*basinhopping* or *SHGO* run also uses it during a selected gradient-based local
refinement. Their global search, and the derivative-free *Nelder-Mead* method,
do not use derivatives.

Vitrification, coupled, and custom model combinations automatically use a
numerical derivative. The explicit ``None``, ``2-point``, ``3-point``, and
``cs`` choices shown for the selected method remain available for comparison
and diagnosis.

The *Review setup…* window summarizes the exact configuration that would be
sent to the optimizer: input files, number of measured points, selected models,
free and fixed parameters, starting values, bounds, methods, cost function, and
calculation budget. It also highlights structural points such as an initial
value outside its bounds, an unconstrained method, or a selected local method
that the current global strategy will not execute. Returning to the form leaves
the configuration editable. The displayed profile is the last one applied;
individual fields may have been edited since then. Starting from this window
uses the reviewed frozen snapshot even if a form value changes afterwards.


⚠ The start of optimization can take a few seconds up to a few minutes to start, please be patient.

At the end of optimization, a result file is saved in ``KinOpt/results`` inside
your desktop's Documents folder, or in the directory selected with
``kinopt --results-dir DIRECTORY``. Its full path appears in the output panel.
A run that finishes with a finite result is also added automatically to **Batch
optimizations...**, where it can be compared with another direct or batch
result.

.. note::
    * The GUI will frequently be updated with the current state of optimization.
    * An estimated remaining time is given. This estimated remaining time is not representative until at least ten optimization iterations have been performed.

* You'll find a description of the kinetic models in :doc:`../kinetic_models`
* You'll find a description of the optimization methods on `Scipy documentation <https://docs.scipy.org/doc/scipy/reference/optimize.html>`_
* You'll find a description of cost function in :doc:`../optimization`
