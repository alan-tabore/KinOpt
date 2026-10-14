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
6. Start the optimization by clicking the 'Start optimization' button

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


⚠ The start of optimization can take a few seconds up to a few minutes to start, please be patient.

At the end of optimization, a result file is saved in ``KinOpt/results`` inside
your desktop's Documents folder, or in the directory selected with
``kinopt --results-dir DIRECTORY``. Its full path appears in the output panel.

.. note::
    * The GUI will frequently be updated with the current state of optimization.
    * An estimated remaining time is given. This estimated remaining time is not representative until at least ten optimization iterations have been performed.

* You'll find a description of the kinetic models in :doc:`../kinetic_models`
* You'll find a description of the optimization methods on `Scipy documentation <https://docs.scipy.org/doc/scipy/reference/optimize.html>`_
* You'll find a description of cost function in :doc:`../optimization`
