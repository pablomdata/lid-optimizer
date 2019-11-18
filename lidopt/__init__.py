import yaml
import numpy as np
import pandas as pd

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

EXP = config['experiment']
SIM = config['simulation']
PARAM_GRID = config['param_grid']
METRICS = config['metrics']
MODE = config['calibration_mode']

CYLINDER = config['is_cylinder']
CYLINDER_DELAY_EXP = config['cylinder_delay_exp']
CYLINDER_DELAY_SIM = config['cylinder_delay_sim']


START_DATE = config['metrics_start_date']
END_DATE = config['metrics_end_date']