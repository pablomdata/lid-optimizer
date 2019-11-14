#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
from tqdm import tqdm
from lidopt.model import evaluate, calculate_metrics
from lidopt import PARAM_GRID, METRICS, EXP, SIM, MODE
from lidopt.parsers import parse_experiment

def run(event=None, event_name=None, path='./data/output/results.csv'):
    col_names = list(PARAM_GRID.keys())
    all_combinations = list(itertools.product(*[PARAM_GRID[k] for k in PARAM_GRID.keys()]))
    df = pd.DataFrame.from_records(all_combinations, columns=col_names)

    for metric in METRICS:
        df[metric] = 0
   
    for i in tqdm(range(df.shape[0])):
        if event_name is not None:
            results = evaluate(reportfile='./data/output/reports/parameters_RE_{0}_{1}.txt'.format(event_name+1,i+1), experiment=event, params=df.loc[i, col_names])
        else:
            results = evaluate(reportfile='./data/output/reports/parameters_{}.txt'.format(str(i+1)), experiment=event, params=df.loc[i, col_names])

        for metric in METRICS:
            df.loc[i, metric] = results[metric]
    
    if event_name is not None:
        df.to_csv(path.format(event_name+1), index_label='simulation_number')
    else:
        idx = pd.Series([i+1 for i in range(len(df))])
        df.set_index(idx, inplace=True)
        df.to_csv(path, index_label='simulation_number')
    
    return df


def run_per_event():
    rain_events = pd.read_csv(EXP['rain_events'], parse_dates=True)
    total_rain_events = rain_events.shape[0]  
    event_path = "./data/output/events/event_CAL_{}_RE_{}.csv"
    df = run()
   
    for i,row in tqdm(df.iterrows(), total = df.shape[0]):
        for j in range(total_rain_events):
            # Initialize metrics object
            col_names = list(PARAM_GRID.keys())
            all_combinations = list(itertools.product(*[PARAM_GRID[k] for k in PARAM_GRID.keys()]))
            metrics_df = pd.DataFrame.from_records(all_combinations, columns=col_names)

            for metric in METRICS:
                metrics_df[metric] = 0

            start= pd.to_datetime(rain_events.loc[j,'Start'], format="%m/%d/%Y %H:%M")      
            end = pd.to_datetime(rain_events.loc[j,'End'], format='%m/%d/%Y %H:%M')    
            event = pd.read_csv('./data/output/reports/parameters_{}.txt'.format(str(i)), index_col=0, parse_dates=True)
            
            event.sort_index(ascending=True, inplace=True)
            event = event.loc[start:end]
            
            # Recover values from simulation and exp
            sim_inflow = event[SIM['inflow_mm_hr']]
            sim_outflow = event[SIM['outflow_mm_hr']]

            exp_inflow = event[EXP['inflow']]
            exp_outflow = event[EXP['outflow']]


            if event.shape[0] > 0: 
                results = calculate_metrics(sim_inflow, sim_outflow, exp_inflow, exp_outflow)
                
                # Save metrics per subset
                for metric in METRICS:
                    metrics_df.loc[i, metric] = results[metric]

                metrics_df.to_csv('./data/output/events/results_CAL_{}_RE_{}.csv'.format(i+1,j+1), index_label='simulation_number')

            # Save event
            event.to_csv(event_path.format(i+1,j+1))


def main():
    if MODE['save_rain_events']:
        print('*'*100)
        print("INFO: Running calibration AND saving individual events")
        print('*'*100)
        run_per_event()
    else:
        print('*'*100)
        print("INFO: Running calibration WITHOUT saving individual events")
        print('*'*100)
        run()        

if __name__ == "__main__":
    main()

