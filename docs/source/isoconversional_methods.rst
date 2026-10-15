Isoconversional methods module
===============================

.. automodule:: isoconversional_methods
   :members:
   :undoc-members:

Performance
-----------

Vyazovkin methods prepare the fixed time differences and average-temperature
terms once for each conversion interval, then reuse them while the optimizer
tests activation energies. This changes neither the integral nor the objective
definition. Run ``python -m benchmarks.isoconversional_baseline`` from the
repository root to measure the gain and verify numerical equivalence on the
current environment.
