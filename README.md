# Astrometrica2ADES
Code to convert Astrometrica output files into the new MPC ADES format for astrometry data interchange ([link to MPC ADES page](https://minorplanetcenter.net/iau/info/ADES.html))

## Installation instructions

### Linux/Unix

If you want to look at and (potentially) modify the code, the method below will give you a local checkout and install it (you likely want to make an activate a `virtualenv` first):
1. `git clone https://github.com/LCOGT/Astrometrica2ADES`
2. `cd Astrometrica2ADES`
3. `pip install -r requirements.txt`
4. `python setup.py install`

To install it in one step, you can just do: `pip install git+https://github.com/LCOGT/Astrometrica2ADES`

### Windows

This will setup a Virtual Environment, activate it and then install the code. You will need to `activate` the Virtualenv again if you restart the computer or quit the Git Bash shell.

0. Get and install Python3 if you don't have it already (https://www.python.org/downloads/)
1. Launch Git Bash (https://git-scm.com/downloads)
2. `virtualenv ~/ades_venv`
3. `source ~/adev/Scripts/activate`
4. `pip install git+https://github.com/LCOGT/Astrometrica2ADES`

## Usage

The basic usage is `astrometrica2ades ~/path/to/MPCReport.txt`. This will create an output file in MPC ADES Pipe Separated Value (PSV) format in `~/path/to/MPCReport.psv`. If you want to put the PSV output in a different file, you can add it after the path to MPCReport.txt e.g. `astrometrica2ades ~/path/to/MPCReport.txt ~/different/path/to/My_Output.psv`
