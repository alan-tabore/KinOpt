Kinetic models module
=====================

KinOpt keeps the display name, equation, practical guidance, parameter role,
unit, illustrative starting value, and illustrative bounds for every selectable
kinetic law in one catalogue. The model panel uses this catalogue for its
contextual explanation and parameter tooltips, and the comparison-plan
assistant uses the same values when preparing another rate model.

The supplied values are broad examples intended to make a first calculation
possible. They are not universal material constants. Check their units and
replace them with values and bounds justified by the material and experiments.

Available rate models
---------------------

* **Nth-order model** fits ``A1`` (s⁻¹), ``E1`` (J/mol), and ``n``. It provides
  a simple baseline without autocatalytic acceleration.
* **Autocatalytic model** fits ``A`` (s⁻¹), ``Ea`` (J/mol), ``m``, and ``n``.
  For ``m > 0``, a simulation starting exactly at zero conversion has zero
  predicted rate.
* **Kamal model** fits ``A1``, ``E1``, ``A2``, ``E2``, ``m``, and ``n``. Its
  extra flexibility requires informative experiments and careful stability
  checks.

The optional WLF vitrification laws fit ``Ad`` (s⁻¹), ``C1``, and ``C2`` (K).
They require the DiBenedetto Tg law, whose ``Tg_0`` and ``Tg_inf`` inputs are in
kelvin and whose ``coeff`` input is dimensionless.

.. automodule:: kinetic_models
   :members:
   :undoc-members:
