import numpy as np
import pandas as pd
from . import exp, sim

def parse_experiment(experiment_file=exp['file'], names=exp['headers']):
    exp = pd.read_csv(experiment_file
                         , sep='\t'
                         , header=None
                         , index_col=0
                         , parse_dates=True
                         , names=names)
    
    
    exp.sort_index(ascending=True, inplace=True)
    return exp


def parse_report(report_file='report.txt', names=sim['headers']):
    report = pd.read_csv(report_file
                        , skiprows=9
                        , header=None
                        , parse_dates=True
                        , index_col=0
                        , sep='\t'
                        , names=names)
        
    report.sort_index(ascending=True, inplace=True)
    report[sim['inflow_ml_min']] = report[sim['inflow_mm_hr']].apply(lambda val: convert_units(val))
    report[sim['outflow_ml_min']] = report[sim['outflow_mm_hr']].apply(lambda val: convert_units(val))
    return report


def merge_and_correct(report, experiment):
    out = pd.merge_asof(report
                        , experiment
                        , left_index=True
                        , right_index=True
                        , direction='forward'
                        , tolerance=pd.Timedelta('1min'))

    # Correct NAs
    out.fillna(method='pad', inplace=True)

    # Apply correction factor
    correction_factor = (1+out[exp['inflow']])/(1+out[sim['inflow_ml_min']])

    out[exp['inflow']] = out[exp['inflow']]*correction_factor
    out[exp['outflow']] = out[exp['outflow']]*correction_factor

    out[sim['inflow_ml_min']] = out[sim['inflow_ml_min']]*correction_factor
    out[sim['outflow_ml_min']] = out[sim['outflow_ml_min']]*correction_factor

    return out[[sim['inflow_ml_min'], sim['outflow_ml_min'], exp['inflow'], exp['outflow']]]


def convert_units(flow):
    '''
    Input: flow vector in mm/hr
    Output: flow vector in ml/min
    '''
    diameter = exp['diameter']
    area = diameter**2*np.pi/4
    return flow*area/(60*10)    