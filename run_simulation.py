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
df['volume_difference_sim'] = 0
df['volume_deviation'] = 0

###########################################################
# Main simulation code
###########################################################

for i,row in tqdm(df.iterrows(), total = df.shape[0]):
    a, b, c, d, e, f = evaluate(reportfile='./reports/parameters_{}.txt'.format(str(i)), params=df.loc[i, col_names])
    df.loc[i,'nse_inflow'] = a
    df.loc[i,'nse_outflow'] = b
    df.loc[i,'volume_inflow'] = c
    df.loc[i, 'volume_outflow'] = d
    df.loc[i, 'volume_difference_sim'] = e
    df.loc[i, 'volume_deviation'] = f
    #print("\n")
    #print("*"*100+"\n")
    #print("Writing row:", a, b, c, d)
    #print("*"*100)

df.to_csv("results.csv", index_label='simulation_number')