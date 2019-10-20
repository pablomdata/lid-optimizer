# ## Running the simulation in SWMM
import numpy as np
from pyswmm import Simulation, LidGroups
from pyswmm.lidlayers import Soil
from pyswmm.lidcontrols import LidControls
from .parsers import parse_experiment, parse_report, merge_and_correct
import yaml

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

exp = config['experiment']
sim = config['simulation']


def evaluate(inputfile=sim['file'], reportfile='report.txt', params=None):
    
    with Simulation(inputfile=inputfile) as sim:
        lid=LidControls(sim)["valec_01"]

        lid.soil.porosity = params['soil.porosity']
        lid.soil.field_capacity = params['soil.field_capacity']
        lid.soil.k_saturated = params['soil.k_saturated']
        lid.soil.k_slope = params['soil.k_slope']
        lid.soil.suction_head = params['soil.suction_head']
            
        lid.surface.void_fraction = params['surface.void_fraction']
        lid.storage.void_fraction = params['storage.void_fraction']
        lid.storage.clog_factor = params['storage.clog_factor']

        for step in sim:
            pass
    

    print("\n")
    print('Simulation executed')
    try:      
        # Read report and compare with experiment
        report = parse_report('report.txt')
        report.to_csv(reportfile)        
        experiment = parse_experiment(exp['file'])
        out = merge_and_correct(experiment=experiment, report=report)         
    except:
        return -1,-1,-1,-1, -1, -1
       
    #############################
    # METRICS
    #############################
        
    # Inflow NSE
    residuals = np.sum((out[sim['inflow_ml_min']]-out[exp['inflow']])**2)
    ss = np.sum((out[exp['inflow']]-out[exp['inflow']].mean())**2)
    nse_inflow = (1-residuals/ss)
        
    # Outflow NSE
    residuals = np.sum((out[sim['outflow_ml_min']]-out[exp['outflow']])**2)
    ss = np.sum((out[exp['outflow']]-out[exp['outflow']].mean())**2)
    nse_outflow = (1-residuals/ss)
        
    # Inflow vol
    volume_inflow = np.sum(out[sim['inflow_ml_min']])
        
    #Outflow vol
    volume_outflow = np.sum(out[sim['outflow_ml_min']])

    # Difference between volumen inflow and outflow in the simulation
    volume_difference_sim = (sim['inflow_ml_min']-sim['outflow_ml_min'])/sim['inflow_ml_min']

    # Deviation between simulated and observed
    volume_deviation = (exp['outflow']-sim['outflow_ml_min'])/exp['outflow']
     
    return nse_inflow, nse_outflow, volume_inflow, volume_outflow, volume_difference_sim, volume_deviation