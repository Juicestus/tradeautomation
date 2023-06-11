import matplotlib.pyplot as plt, numpy as np

def plot_ohlc(df, ax):
    x = np.arange(0, len(df))
    for idx, (_, val) in enumerate(df.iterrows()):
        color = '#F04730' if val['open'] > val['close'] else '#2CA453'
        # high/low lines
        ax.plot([x[idx], x[idx]], 
                [val['low'], val['high']], 
                color=color)
        # open marker
        ax.plot([x[idx], x[idx]-0.1], 
                [val['open'], val['open']], 
                color=color)
        # close marker
        ax.plot([x[idx], x[idx]+0.1], 
                [val['close'], val['close']], 
                color=color)
    return ax
 
