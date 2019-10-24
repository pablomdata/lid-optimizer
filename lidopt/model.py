# ## Running the simulation in SWMM
import numpy as np
from pyswmm import Simulation, LidGroups
from pyswmm.lidlayers import Soil
from pyswmm.lidcontrols import LidControls
from .parsers import parse_experiment, parse_report, merge_and_correct
from . import exp, sim

def evaluate(inputfile=sim['file'], reportfile='report.txt', params=None):
    
    with Simulation(inputfile=inputfile) as simulation:
        lid=LidControls(simulation)[sim['lid.name']]

        lid.soil.porosity = params['soil.porosity']
        lid.soil.field_capacity = params['soil.field_capacity']
        lid.soil.k_saturated = params['soil.k_saturated']
        lid.soil.k_slope = params['soil.k_slope']
        lid.soil.suction_head = params['soil.suction_head']
            
        lid.surface.void_fraction = params['surface.void_fraction']
        lid.storage.void_fraction = params['storage.void_fraction']
        lid.storage.clog_factor = params['storage.clog_factor']

        for step in simulation:
            pass
    

    print("\n")
    print('Simulation executed')
    try:      
        # Read report and compare with experiment
        report = parse_report('report.txt')
        experiment = parse_experiment(exp['file'])
        out = merge_and_correct(experiment=experiment, report=report)         
        out.to_csv(reportfile)
    except:
        return -1,-1,-1,-1, -1, -1
       
    #############################
    # METRICS
    #############################

    # Recover values from simulation and exp
    sim_inflow = out[sim['inflow_ml_min']]
    sim_outflow = out[sim['outflow_ml_min']]

    exp_inflow = out[exp['inflow']]
    exp_outflow = out[exp['outflow']]

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

    # Inflow vol
    volume_inflow = np.sum(sim_inflow)
    metrics['volume_inflow'] = volume_inflow
            
    #Outflow vol
    volume_outflow = np.sum(sim_outflow)
    metrics['volume_outflow'] = volume_outflow

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