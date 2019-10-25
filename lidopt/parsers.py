import numpy as np
import pandas as pd
from . import EXP, SIM

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
    out = pd.merge_asof(report
                        , experiment
                        , left_index=True
                        , right_index=True
                        , direction=EXP['direction']
                        , tolerance=pd.Timedelta(EXP['lag']))

    # Correct NAs
    out.fillna(method='pad', inplace=True)

    # Apply correction factor
    correction_factor = (1+out[EXP['inflow']])/(1+out[SIM['inflow_mm_hr']])

    out[EXP['inflow']] = out[EXP['inflow']]*correction_factor
    out[EXP['outflow']] = out[EXP['outflow']]*correction_factor

    out[SIM['inflow_mm_hr']] = out[SIM['inflow_mm_hr']]*correction_factor
    out[SIM['outflow_mm_hr']] = out[SIM['outflow_mm_hr']]*correction_factor

    return out[[SIM['inflow_mm_hr'], SIM['outflow_mm_hr'], EXP['inflow'], EXP['outflow']]]


def convert_units(flow):
    '''
    Input: flow vector in mm/hr
    Output: flow vector in ml/min
    '''
    diameter = EXP['diameter']
    area = diameter**2*np.pi/4
    return flow*area/(60*10)    