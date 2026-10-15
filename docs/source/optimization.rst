Optimization module
===================

.. automodule:: optimization
   :members:
   :undoc-members:
   :show-inheritance:

Scientific result checks
------------------------

Use the batch window to reserve a complete experiment for predictive
validation. KinOpt distinguishes solver convergence, fit error, validation
error, per-experiment residuals, stability across starting points, and fitted
values close to configured bounds. None of these checks alone establishes that
a kinetic law or its parameters are physically valid; they make the separate
questions visible for review.
