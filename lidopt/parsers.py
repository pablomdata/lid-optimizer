import numpy as np
import pandas as pd
from . import EXP, SIM, START_DATE, CYLINDER, DELAY

def parse_experiment(experiment_file=EXP['file']):
    exp = pd.read_csv(experiment_file
                         , sep='\t'
                         , parse_dates=True
                         )
    
    exp['DateTime'] = exp['Date']+' '+exp['Time']
    exp.index = pd.to_datetime(exp['DateTime'], format='%m/%d/%Y %H:%M')
    exp.sort_index(ascending=True, inplace=True)
    return exp.loc[:,[EXP['inflow'], EXP['outflow']]] 


def parse_report(report_file='report.txt', names=SIM['headers']):
    report = pd.read_csv(report_file
                        , skiprows=9
                        , header=None
                        , parse_dates=True
                        , index_col=0
                        , sep='\t'
                        , names=names)
        
    report.sort_index(ascending=True, inplace=True)
    return report


def merge_and_correct(report, experiment):

    if CYLINDER:
        # Merging to account for cylinder experiment

        # 1. Keep only when it rains
        rain = experiment[experiment[EXP['inflow']] != 0].reset_index()
        rain['event_num'] = 1
        for i in range(1,rain.shape[0]):
            td = rain.loc[i,'DateTime']-rain.loc[i-1,'DateTime']
            if td.seconds > 3600:
                rain.loc[i, 'event_num'] = rain.loc[i-1, 'event_num'] + 1
            else:
                rain.loc[i, 'event_num'] = rain.loc[i-1, 'event_num']

        # Same shift for simulation
        sim = report[report[SIM['inflow_mm_hr']] != 0].reset_index()
        sim['event_num'] = 1
        for i in range(1,sim.shape[0]):
            
            td = sim.loc[i,'DateTime']-sim.loc[i-1,'DateTime']
            if td.seconds > DELAY:
                sim.loc[i, 'event_num'] = sim.loc[i-1, 'event_num'] + 1
            else:
                sim.loc[i, 'event_num'] = sim.loc[i-1, 'event_num']
        
        sim.drop(columns='DateTime', inplace=True)
        out = pd.merge(sim, rain, left_on='event_num', right_on='event_num')

        out.fillna(0, inplace=True)
        out.set_index('DateTime', inplace=True) 

    else:
        # Merge by dates
        out = pd.merge_asof(report
                            , experiment
                            , left_index=True
                            , right_index=True
                            , direction=EXP['direction']
                            , tolerance=pd.Timedelta(EXP['lag']))

        # Correct NAs
        out.fillna(method='pad', inplace=True)

    # Apply correction factor
    correction_factor = 1

    out[EXP['inflow']] = out[EXP['inflow']]*correction_factor
    out[EXP['outflow']] = out[EXP['outflow']]*correction_factor

    out[SIM['inflow_mm_hr']] = out[SIM['inflow_mm_hr']]*correction_factor
    out[SIM['outflow_mm_hr']] = out[SIM['outflow_mm_hr']]*correction_factor
    
    out = out[START_DATE:]
    return out[[SIM['inflow_mm_hr'], SIM['outflow_mm_hr'], EXP['inflow'], EXP['outflow']]]


def convert_units(flow):
    '''
    Input: flow vector in mm/hr
    Output: flow vector in ml/min
    '''
    diameter = EXP['diameter']
    area = diameter**2*np.pi/4
    return flow    