![Python](https://img.shields.io/badge/Python-3.9-blue)

# KinOpt

The aim of the KinOpt project is to use kinetics data to perform isoconversional analysis and model optimization.

## Documentation

A documentation of the KinOpt module is available at [KinOpt Documentation](https://kinopt.readthedocs.io/en/latest/index.html)

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
The first step is to obtain experimental kinetic data (e.g. from FTIR, DSC or rheological experiments). These data should be stored as text or csv files containing four columns arranged in the following order: 
1. Time (in seconds)
2. Temperature (in Kelvin)
3. Reaction speed (in s-1)
4. Extent of reaction (no unit)

#### Python
This project uses Python, so please make sure you installed it and that the version is superior or equal to 3.9.


### Installation

To install this module, simply download the project in a zip file and extract it.

Once you’ve downloaded the project, you can install the required python modules from PyPI with pip or with conda.

Open a command prompt in the KinOpt folder and execute:
``` bash
python -m pip install requirements.txt
```
or with conda:
``` bash
conda install requirements.txt
```

### Tutorials

Tutorials are available on Youtube to show you how to install and use the software:

**[Youtube Tutorials for KinOpt](https://youtube.com/playlist?list=PLxgAQK6NxsvJIZDw5gI6Xi16PfxUrXFI0&si=ICWPLX2gbCdEuDp9)**
*(Make sure you installed VSCode to follow the tutorials)*

## Usage

To start the graphical interface:
1. Open a command prompt in the ‘src’ folder
2. Run the “main.py” script using python.
``` bash   
>> python3 main.py
```


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
