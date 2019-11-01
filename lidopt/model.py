# ## Running the simulation in SWMM
import numpy as np
from pyswmm import Simulation, LidGroups
from pyswmm.lidlayers import Soil
from pyswmm.lidcontrols import LidControls
from .parsers import parse_experiment, parse_report, merge_and_correct
from . import EXP, SIM, METRICS

def evaluate(inputfile=SIM['file'], experiment=None, reportfile='report.txt', params=None):
    
    with Simulation(inputfile=inputfile) as simulation:
        lid=LidControls(simulation)[SIM['lid.name']]

        for p in params.keys():
            setattr(lid, p, params[p])

        for step in simulation:
            pass
    

    print("\n")
    print('Simulation executed')

    metrics = {}

    try:      
        # Read report and compare with experiment
        report = parse_report('report.txt')
        if experiment is None:
            experiment = parse_experiment(EXP['file'])
        out = merge_and_correct(experiment=experiment, report=report)      
        out.to_csv(reportfile)
    except:
        for metric in METRICS:
            metrics[metric] = -1
        return metrics
                  
    # Recover values from simulation and exp
    sim_inflow = out[SIM['inflow_mm_hr']]
    sim_outflow = out[SIM['outflow_mm_hr']]

    exp_inflow = out[EXP['inflow']]
    exp_outflow = out[EXP['outflow']]

    metrics = calculate_metrics(sim_inflow, sim_outflow, exp_inflow, exp_outflow)
    return metrics


#############################
# METRICS
#############################
def calculate_metrics(sim_inflow, sim_outflow, exp_inflow, exp_outflow):

    metrics = {}
    ####################################################
     # Inflow NSE
    residuals = np.sum((sim_inflow-exp_inflow)**2)
    ss = np.sum((exp_inflow-exp_inflow.mean())**2)
    nse_inflow = (1-residuals/ss)
    metrics['nse_inflow'] = nse_inflow

    # Outflow NSE
    residuals = np.sum((sim_outflow-exp_outflow)**2)
    ss = np.sum((exp_outflow-exp_outflow.mean())**2)
    nse_outflow = (1-residuals/ss)
    metrics['nse_outflow'] = nse_outflow

    # Inflow vol sim
    volume_inflow_sim = np.sum(sim_inflow)
    metrics['volume_inflow_sim'] = volume_inflow_sim
            
    #Outflow vol sim
    volume_outflow_sim = np.sum(sim_outflow)
    metrics['volume_outflow_sim'] = volume_outflow_sim

    # Inflow vol exp
    volume_inflow_exp = np.sum(exp_inflow)
    metrics['volume_inflow_exp'] = volume_inflow_exp
            
    #Outflow vol sim
    volume_outflow_exp = np.sum(exp_outflow)
    metrics['volume_outflow_exp'] = volume_outflow_exp

    # Percent bias
    metrics['pbias'] = 100*(exp_outflow-sim_outflow).sum()/exp_outflow.sum()

    # Peak flow
    metrics['peak_flow'] = np.abs(exp_outflow.max()-sim_outflow.max())

    # Time peak
    metrics['time_peak'] = np.argmax(exp_outflow.values)-np.argmax(sim_outflow.values)

    # Systematic deviation
    metrics['sd'] = (exp_outflow-sim_outflow).mean()

    # Absolut deviation
    metrics['ad'] = (exp_outflow-sim_outflow).abs().mean()

    # Quadratic deviation
    metrics['qd'] = np.sqrt(np.sum((exp_outflow.values-sim_outflow.values)**2)/len(exp_outflow))
    return metrics