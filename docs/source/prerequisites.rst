Prerequisites
=============

Kinetic data
-------------

The first step is to obtain experimental kinetic data 
(e.g. from FTIR, DSC or rheological experiments). 
These data should be stored as ``.txt`` or ``.csv`` files containing columns
for the following four quantities:

1. Time
2. Temperature
3. Reaction rate
4. Extent of reaction

The import assistant maps columns in any order and converts the supported
units. Extra columns are ignored. KinOpt stores the validated values in
seconds, Kelvin, :math:`s^{-1}`, and a fractional extent from 0 to 1.

.. note::
    It is highly recommended to perform an interpolation of data over extent.
    An interpolation module is available among the Kinopt modules (see :mod:`interpolation`).

Python
------
This project uses Python, so please make sure you installed it and that the version is superior or equal to 3.9.
