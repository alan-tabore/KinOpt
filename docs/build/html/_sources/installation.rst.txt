Installation
============

Installation from source
-------------------------

To install this module, simply download the project in a zip file and extract it.

Once you've downloaded the project, you can install the required python modules 
from PyPI with pip or with conda.

Open a command prompt in the KinOpt folder and execute:

.. code-block:: bash

    >> python -m pip install requirements.txt

or with conda:

.. code-block:: bash

    >> conda install requirements.txt

*(Note: The requirements.txt contains the list and version of all modules used to run the KinOpt software.)*

Project structure
-----------------
The project is structured has follow:

.. code-block:: text

    ├── src
    │   ├── data_extraction.py
    │   ├── interpolation.py
    │   ├── isoconversional_methods.py
    │   ├── kinetic_models.py
    │   ├── optimization.py
    │   ├── kinopt_interface.py
    │   └── main.py
    │   
    ├── data
    ├── results
    │
    ├── tests
    ├── docs
    ├── screenshots
    └── ressources

The src folder contains all the useful python scripts.
If you want to use the package without the graphical interface you can 
directly work in this folder to easily import all :doc:`modules <modules>`.

The '*data*' folder is designed to store your raw kinetic data.

The '*results*' folder is where you'll find the results of optimization performed through the GUI.