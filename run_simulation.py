#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
from tqdm import tqdm
from lidopt.model import evaluate
from lidopt import PARAM_GRID, METRICS, EXP, MODE
from lidopt.parsers import parse_experiment

def run(event=None, event_name=None, path='./data/output/results.csv'):
    col_names = list(PARAM_GRID.keys())
    all_combinations = list(itertools.product(*[PARAM_GRID[k] for k in PARAM_GRID.keys()]))
    df = pd.DataFrame.from_records(all_combinations, columns=col_names)

    for metric in METRICS:
        df[metric] = 0
   
    for i,row in tqdm(df.iterrows(), total = df.shape[0]):
        if event_name is not None:
            results = evaluate(reportfile='./data/output/reports/parameters_RE_{0}_{1}.txt'.format(event_name+1,i+1), experiment=event, params=df.loc[i, col_names])
        else:
            results = evaluate(reportfile='./data/output/reports/parameters_{}.txt'.format(str(i+1)), experiment=event, params=df.loc[i, col_names])
        for metric in METRICS:
            df.loc[i, metric] = results[metric]
    
    if event_name is not None:
        df.to_csv(path.format(event_name+1), index_label='simulation_number')
    else:
        df.to_csv(path, index_label='simulation_number')
    
    return df


def run_per_event():
    rain_events = pd.read_csv(EXP['rain_events'], parse_dates=True)
    total_rain_events = rain_events.shape[0]
    experiment = parse_experiment(EXP['file'])   
    event_path = "./data/output/events/results_CAL_{}_RE_{}.csv"
    df = run()

    for i,row in tqdm(df.iterrows(), total = df.shape[0]):
        for j in range(total_rain_events):
            start= pd.to_datetime(rain_events.loc[j,'Start'], format='%m/%d/%Y %H:%M')      
            end = pd.to_datetime(rain_events.loc[j,'End'], format='%m/%d/%Y %H:%M')    
            event = pd.read_csv('./data/output/reports/parameters_{}.txt'.format(str(i+1)), index_col=0, parse_dates=True)
            event = event.loc[start:end]
            event.to_csv(event_path.format(i+1,j+1))


def main():
    if MODE['save_rain_events']:
        print('*'*100)
        print("INFO: Running calibration WITHOUT saving individual events")
        print('*'*100)
        run_per_event()
    else:
        print('*'*100)
        print("INFO: Running calibration AND saving individual events")
        print('*'*100)
        run()        

if __name__ == "__main__":
    main()

