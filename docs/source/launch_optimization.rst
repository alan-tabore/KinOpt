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


⚠ The start of optimization can take a few seconds up to a few minutes to start, please be patient.

At the end of optimization, a result file is saved under 'KinOpt/results/'.

.. note::
    * The GUI will frequently be updated with the current state of optimization.
    * An estimated remaining time is given. This estimated remaining time is not representative until at least ten optimization iterations have been performed.

* You'll find a description of the kinetic modelds in :doc:`../kinetic_models` 
* You'll find a description of the optimization methods on `Scipy documentation <https://docs.scipy.org/doc/scipy/reference/optimize.html>`_
* You'll find a description of cost function in :doc:`../optimization`