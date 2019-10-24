# lid-optimizer
Calibration of Low Impact Development units.

## Setup

Below are the instructions for Windows 10.

- Download and install [Anaconda](https://www.anaconda.com/distribution/#download-section).
- Download and install [Git](https://git-scm.com/downloads).
- Download and install [EPA SWMM 5](https://www.epa.gov/water-research/storm-water-management-model-swmm).

## Clone the repository

To get the most up-to-date version, clone the repository:

`git clone https://github.com/jpmaldonado/lid-optimizer`

or `pull`:

`git pull https://github.com/jpmaldonado/lid-optimizer`.

## How to use the tool
You need to open an Anaconda Prompt (Windows Menu | Anaconda Prompt) and type

`conda env create -f environment.yaml`

Finally

`conda activate lid`

### Run the simulation

Once the virtual environment is activated and the parameters are correctly set in the `config.yaml` file,
you can run all the simulations by typing

`python run_simulation.py`

in the console.

### Deep-dive in selected experiments