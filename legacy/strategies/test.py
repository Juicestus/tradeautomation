from alpaca.data.timeframe import TimeFrame
import pandas as pd
import numpy as np
import time
from legacy.settings import SymbolType

def register(settings):
    settings.timeframe = TimeFrame.Minute
    settings.symbols = ['AAPL']
    settings.symbol_type = SymbolType.Stock
    settings.past_days = 10
    return settings

def update(symbol, df):

    if len(df) < 100:
        return df, 0
    
    df['short'] = df['close'].rolling(10).mean()
    df['long'] = df['close'].rolling(50).mean()

    # print("----")

    # print(str(df['short'].iloc[-2]) + " vs " + str(df['long'].iloc[-2]))

    if df['short'].iloc[-1] > df['long'].iloc[-1] and df['short'].iloc[-2] < df['long'].iloc[-2]:
        return df, -.2
    elif df['short'].iloc[-1] < df['long'].iloc[-1] and df['short'].iloc[-2] > df['long'].iloc[-2]:
        return df, .2
    
    return df, 0 

'''
    if len(df) < size - 2:
        return
    
    plt.plot(np.array(df['short']), color='#F04730')
    plt.plot(np.array(df['long']), color='#F04730')
    '''
    
