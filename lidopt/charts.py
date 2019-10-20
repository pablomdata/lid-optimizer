import matplotlib.pyplot as plt

def single_plot(df, sim_col, exp_col):
    fig, ax = plt.subplots(figsize=(7,7))
    df[[sim_col,exp_col]].plot(ax=ax)
    ax.legend(loc='best')
    ax.set(title='Experiment vs Simulation - Inflow')
    ax.legend(['Simulation', 'Experiment'])
    return fig

def two_plots(df, sim_col, exp_col):
    fig, (ax0,ax1) = plt.subplots(figsize=(14,7), nrows=1, ncols=2, sharey=True)
    df[sim_col].plot(ax=ax0, color='blue')
    ax0.set(title='Simulated flow')
    df[exp_col].plot(ax=ax1, color='orange')
    ax1.set(title='Experimental flow');    