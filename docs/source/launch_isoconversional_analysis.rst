Performing an isoconversional analysis
======================================

To perform an isoconversional analysis:

1. Make sure you loaded the data
2. Select an isoconversional method
3. Fill the required parameters

You'll find a description of the isoconversional methods in: :doc:`../isoconversional_methods`

If you're wondering why you should perform an isoconversional analysis here a some reasons:

Reasons to perform isoconversional analysis
-------------------------------------------

Estimation of Activation Energy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By applying isoconversional methods such as the Vyazovkin or Friedman methods, 
it is possible to estimate the activation energy of a reaction without assuming 
a specific reaction mechanism. 
This is particularly useful when the mechanism is unknown or complex.

Determination of Reaction mechanism
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Isoconversional analysis can help elucidate the reaction mechanism. 
For instance, significant changes in activation energy with conversion may indicate
transitions between different rate-determining steps or the involvement of different species 
at different stages of the reaction.

Prediction of Reaction Kinetics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Isoconversional analysis allows for the prediction of reaction kinetics parameters.
For example, if one assumes that a reaction follows a Kamal model:

.. math::
    \frac{d\alpha}{dt} = \left( A_1 e^{ \left( \frac{-E_1}{RT} \right)}  +  A_2 e^{ \left( \frac{-E_2}{RT} \right) } \alpha^m \right) (1-\alpha)^n

Then, the apparent activation energy (on the isoconversional plot) is equal to [#f1]_ :

.. math::
    E_{app}(\alpha) = \frac{\frac{A_1}{A_2}*exp(-\frac{E_1}{RT})*E_1 + exp(-\frac{E_2}{RT})*E_2*\alpha^m}{\frac{A_1}{A_2} exp(-\frac{E_1}{RT}) + exp(-\frac{E_2}{RT})*\alpha^m} 

And when the extent tends to 0, the apparent activation energy is equal to :math:`E_1`.

.. [#f1] C. Alzina, N. Sbirrazzuoli, et A. Mija, « Hybrid Nanocomposites: Advanced Nonlinear Method for Calculating Key Kinetic Parameters of Complex Cure Kinetics », J. Phys. Chem. B, vol. 114, nᵒ 39, p. 12480‑12487, oct. 2010, doi: 10.1021/jp1040629.


Additional insights
^^^^^^^^^^^^^^^^^^^^
Isoconversional analysis can also be used to assess the quality of kinetic data 
or the thermal stability when studying thermal degradation or decomposion reactions.





