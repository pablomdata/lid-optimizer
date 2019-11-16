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

def assign_events(df, t, C):
# function assigns number of events (ev_num) to datasets (df)
# df = dataset
# t = minimum time span between two events (condition of time span among the events) IN SECONDS
# C = the column with rainfall data
    df = df[df[C] != 0].reset_index()
    df['event_num'] = 0

    for i in range(1, df.shape[0]):
        td = df.loc[i, 'DateTime'] - df.loc[i-1, 'DateTime']
        if td.seconds > t:
            df.loc[i, 'event_num'] = df.loc[i-1, 'event_num'] + 1
        else:
            df.loc[i, 'event_num'] = df.loc[i-1, 'event_num']
        return df

def merge_and_correct(report, experiment):

    if CYLINDER:
        # Merging to account for cylinder experiment
        exp_cols = [EXP['inflow'], EXP['outflow']]

        rain = assign_events(experiment, 3600, EXP['inflow'])
        rain = rain[['DateTime', 'event_num']+exp_cols]
        rain.drop_duplicates(inplace=True)

        # Same shift for simulation
        sim = assign_events(report, 120, SIM['inflow_mm_hr'])
        
        sim_cols = [SIM['inflow_mm_hr'], SIM['outflow_mm_hr']]
        sim = sim[['DateTime', 'event_num']+sim_cols]
        sim.drop_duplicates(inplace=True)
       
        out = pd.merge(sim, rain, on=['DateTime','event_num'], how='right')
        cols = ['DateTime']+sim_cols+exp_cols
        out = out[cols]
        out.drop_duplicates(keep='first', inplace=True)
        out.dropna(inplace=True, axis=0)
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