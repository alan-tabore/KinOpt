Installation
============

Windows
-------

Follow :doc:`installation_windows` for the complete PowerShell walkthrough:
Python installation, downloading KinOpt, setup, desktop shortcut, sample data,
results and troubleshooting.

.. toctree::
    :maxdepth: 1

    installation_windows

Linux: installation from source
-------------------------------

Download or clone KinOpt, then open a terminal at the repository root.
On Linux, install the application in an isolated environment:

.. code-block:: bash

    python3 -m venv .venv
    .venv/bin/python -m pip install .

To make the command available from any directory:

.. code-block:: bash

    mkdir -p "$HOME/.local/bin"
    ln -s "$PWD/.venv/bin/kinopt" "$HOME/.local/bin/kinopt"

The ``~/.local/bin`` directory must be on your ``PATH``. If necessary, add
``export PATH="$HOME/.local/bin:$PATH"`` to your shell configuration and open a
new terminal. Check ``command -v kinopt`` before replacing an existing command.

After updating the repository, reinstall with ``.venv/bin/python -m pip install .``.
Application dependencies are declared in ``pyproject.toml``. The old
``requirements.txt`` is retained as a historical environment snapshot.

Project structure
-----------------
The main package is structured as follows:

.. code-block:: text

    KinOpt/
    ├── pyproject.toml
    ├── kinopt/
    │   ├── cli.py
    │   ├── __main__.py
    │   ├── src/
    │   │   ├── data_extraction.py
    │   │   ├── interpolation.py
    │   │   ├── isoconversional_methods.py
    │   │   ├── kinetic_models.py
    │   │   ├── optimization.py
    │   │   ├── kinopt_interface.py
    │   │   └── main.py
    │   ├── data/
    │   ├── tests/
    │   └── ressources/
    └── docs/

The ``kinopt/src`` folder contains the scientific modules and graphical interface.
Installed modules can also be imported in Python, for example
``from kinopt.src import kinetic_models``. See :doc:`modules <modules>`.

The '*data*' folder is designed to store your raw kinetic data.

New results are saved in ``KinOpt/results`` inside your desktop's Documents
folder, or in the folder passed with ``kinopt --results-dir DIRECTORY``.
Existing files in the repository's old results folder can still be opened.
