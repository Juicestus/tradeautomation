from alpaca.data.timeframe import TimeFrame
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

def register():
    return TimeFrame.Minute, ['ETH/USDT'], 2

def plot_ohlc(df):
    x = np.arange(0, len(df))
    fig, ax = plt.subplots(1, figsize=(12,6))
    for idx, (_, val) in enumerate(df.iterrows()):
        color= '#F04730' if val['open'] > val['close'] else '#2CA453'
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
   
def run_plot(stop=False):
    plt.show(block=stop)
    if stop: return
    plt.pause(.01)
    plt.close()
    

def update(df, size):

    if len(df) < 100:
        return
    
    df['sma_30'] = df['close'].rolling(30).mean()
    df['sma_100'] = df['close'].rolling(100).mean()
    
    if len(df) < size - 2:
        return
    
    plot_ohlc(df)
    
    plt.plot(np.array(df['sma_30']), color='#F04730')
    plt.plot(np.array(df['sma_100']), color='#F04730')
    
    run_plot(stop=True)
    
