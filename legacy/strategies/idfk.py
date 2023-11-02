from alpaca.data.timeframe import TimeFrame
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
from legacy.settings import SymbolType

import priceanalytics.indicators as indicators
from priceanalytics.plot import plot_ohlc

def register(settings):
    settings.timeframe = TimeFrame.Minute
    settings.symbols = ['AAPL']
    settings.symbol_type = SymbolType.Stock
    settings.past_days = 4
    return settings

def update(symbol, df, equity):

    if len(df) < 100:
        return df, 0

    df = indicators.force_index(df, 50)
    
    # if df.iloc[-1]['force_index'] < -1e6 * 1/8:
    #     return df, -1
    # if df.iloc[-1]['force_index'] > 1e6 * 1/8:
    #     return df, .2
    
    
    
    
def sell(df, equity):
    return df, -equity
def buy(df, equity):
    return df, equity


    return df, 0 

def plot(df, buys_x, sells_x):
    #fig, ax = plt.subplots(1, figsize=(12,6))
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(2, 1, 1)
    # ax = plot_ohlc(df, ax)
    plt.plot(np.array(df['close']), color='#000000')

    buys_y = [df.iloc[x]['close'] for x in buys_x]
    plt.scatter(buys_x, buys_y, color="#FF0000", marker="^")

    sells_y = [df.iloc[x]['close'] for x in sells_x]
    plt.scatter(sells_x, sells_y, color="#00FF00", marker="v")

    bx = fig.add_subplot(2, 1, 2)
    plt.plot(np.array(df['force_index']), color='#0000FF')

    plt.tight_layout()
    plt.show()


'''
    if len(df) < size - 2:
        return
    
    plt.plot(np.array(df['short']), color='#F04730')
    plt.plot(np.array(df['long']), color='#F04730')
    '''
    
