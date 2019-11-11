import yaml
import numpy as np

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

EXP = config['experiment']
SIM = config['simulation']
PARAM_GRID = config['param_grid']
METRICS = config['metrics']
MODE = config['calibration_mode']
