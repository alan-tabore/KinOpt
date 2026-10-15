![Python](https://img.shields.io/badge/Python-3.9-blue)

# KinOpt

The aim of the KinOpt project is to use kinetics data to perform isoconversional analysis and model optimization.

## Documentation

A documentation of the KinOpt module is available at [KinOpt Documentation](https://kinopt.readthedocs.io/en/latest/index.html)

For development checks and merging changes, see the [validation guide (French)](VALIDATION.md).

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Tutorials](#tutorials)
- [Usage](#usage)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Getting Started

### Prerequisites

#### Kinetic data
The first step is to obtain experimental kinetic data (e.g. from FTIR, DSC or
rheological experiments). Text or CSV files need columns for time, temperature,
reaction rate, and extent of reaction. The graphical import assistant previews
the files, maps those columns in any order, ignores unrelated columns, and
converts seconds/minutes, Kelvin/Celsius, rates per second/per minute, and
fractional/percentage extent into KinOpt's standard units.

#### Python
This project uses Python, so please make sure you installed it and that the version is superior or equal to 3.9.


### Installation

Choose the instructions for your operating system:

- **Windows:** follow the [step-by-step Windows guide](docs/source/installation_windows.rst),
  from installing Python to creating a desktop shortcut and trying the included data.
- **Linux:** use the instructions below.

#### Windows (PowerShell)

With Python 3.14 installed, open PowerShell in the extracted repository folder
(the one containing `pyproject.toml`):

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\kinopt.exe
```

Use the `.exe` paths directly; activating the environment is optional. The
Windows guide explains later launches, paths with spaces, result locations,
updates and common errors. VSCode is not required to run KinOpt.

#### Linux

Download or clone the repository. From its root directory, install
KinOpt in an isolated Python environment:

``` bash
python3 -m venv .venv
.venv/bin/python -m pip install .
```

To make `kinopt` available from any directory without activating the environment:

```bash
mkdir -p "$HOME/.local/bin"
ln -s "$PWD/.venv/bin/kinopt" "$HOME/.local/bin/kinopt"
```

`~/.local/bin` must be on your `PATH`. If your desktop does not add it, add
`export PATH="$HOME/.local/bin:$PATH"` to your shell configuration and open a new
terminal. If a `kinopt` command already exists, check its location with
`command -v kinopt` before replacing it.

After updating the repository, run `.venv/bin/python -m pip install .` again.
The dependencies needed by the application are declared in `pyproject.toml`;
the old `requirements.txt` is kept as a historical environment snapshot.

### Tutorials

Tutorials are available on Youtube to show you how to install and use the software:

**[Youtube Tutorials for KinOpt](https://youtube.com/playlist?list=PLxgAQK6NxsvJIZDw5gI6Xi16PfxUrXFI0&si=ICWPLX2gbCdEuDp9)**
*(Make sure you installed VSCode to follow the tutorials)*

## Usage

On **Linux**, after installing the command on your PATH:

```bash
kinopt
```

On **Windows**, from the project folder in PowerShell:

```powershell
.\.venv\Scripts\kinopt.exe
```

Results are saved in `KinOpt/results` inside your desktop's Documents folder
(usually `~/Documents/KinOpt/results` on Linux, or `Documents\KinOpt\results`
on Windows). The output panel shows the saved file's full path, including if
Documents is redirected by Windows. To choose a different folder:

```bash
kinopt --results-dir "$HOME/mes-resultats-kinopt"
```

```powershell
.\.venv\Scripts\kinopt.exe --results-dir "$env:USERPROFILE\KinOpt Results"
```

Relative paths are resolved from the terminal's current directory. Existing
results in the checkout's `kinopt/results` folder remain available through
**Load result file(s)**.

```bash
kinopt --help
kinopt --version
```

On Windows, use `.\.venv\Scripts\kinopt.exe --help` or `--version`.
You can also launch the module with the environment's Python:

```bash
/path/to/KinOpt/.venv/bin/python -m kinopt
```

```powershell
.\.venv\Scripts\python.exe -m kinopt
```

The historical `python main.py` launch from `kinopt/src` remains supported.
All launchers open the graphical interface; they do not start an optimization
automatically.

## License

Copyright (c) 2024, Alan Tabore.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of Alan Tabore nor the names of any contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Acknowledgments


We would like to express our gratitude to the following individuals, organizations, and projects for their contributions and support to this project:

- **[NumPy](https://numpy.org)** and **[SciPy](https://www.scipy.org)** teams for their invaluable libraries that power scientific computing in Python.
- **[Matplotlib](https://matplotlib.org)** developers for providing an extensive plotting library for Python.
- **[PyQt5](https://riverbankcomputing.com/software/pyqt/intro)** developers for their powerful cross-platform GUI toolkit.
- **[tqdm](https://github.com/tqdm/tqdm)** developers for their handy progress bar utility.
- **[Python Software Foundation](https://www.python.org/psf-landing/)** for maintaining the Python programming language and its rich standard library.

We are grateful to the open-source community for their continuous contributions, bug reports, and feedback, which help improve this project over time.
