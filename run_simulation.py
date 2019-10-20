#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
from tqdm import tqdm
from lidopt.model import evaluate
import yaml

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

param_grid = config['param_grid']

col_names = list(param_grid.keys())
all_combinations = list(itertools.product(*[param_grid[k] for k in param_grid.keys()]))
df = pd.DataFrame.from_records(all_combinations, columns=col_names)

df['nse_inflow'] = 0
df['nse_outflow'] = 0
df['volume_inflow'] = 0
df['volume_outflow']= 0
df['peak_flow'] = 0
df['time_peak'] = 0
df['pbias'] = 0
df['sd'] = 0
df['ad'] = 0
df['qd'] = 0

###########################################################
# Main simulation code
###########################################################

for i,row in tqdm(df.iterrows(), total = df.shape[0]):
    metrics = evaluate(reportfile='./data/output/reports/parameters_{}.txt'.format(str(i)), params=df.loc[i, col_names])
    df.loc[i,'nse_inflow'] = metrics['nse_inflow']
    df.loc[i,'nse_outflow'] = metrics['nse_outflow']
    df.loc[i,'volume_inflow'] = metrics['volume_inflow']
    df.loc[i, 'volume_outflow'] = metrics['volume_outflow']
    df.loc[i, 'peak_flow'] = metrics['peak_flow']
    df.loc[i, 'time_peak'] = metrics['time_peak']
    df.loc[i, 'pbias'] = metrics['pbias']
    df.loc[i, 'sd'] = metrics['sd']
    df.loc[i, 'ad'] = metrics['ad']
    df.loc[i, 'qd'] = metrics['qd']
   
df.to_csv("./data/output/results.csv", index_label='simulation_number')