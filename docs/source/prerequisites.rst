Prerequisites
=============

Kinetic data
-------------

The first step is to obtain experimental kinetic data 
(e.g. from FTIR, DSC or rheological experiments). 
These data should be stored as ``.txt`` or ``.csv`` files containing four columns arranged in the following order: 

1. Time (in :math:`s`)
2. Temperature (in :math:`K`)
3. Reaction rate (in :math:`s^{-1}`)
4. Extent of reaction (no unit)

.. note::
    It is highly recommended to perform an interpolation of data over extent.
    An interpolation module is available among the Kinopt modules (see :mod:`interpolation`).

Python
------
This project uses Python, so please make sure you installed it and that the version is superior or equal to 3.9.