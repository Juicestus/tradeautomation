
import sys, importlib, asyncio, data, util
import matplotlib.pyplot as plt
import numpy as np

from alpaca.data.timeframe import TimeFrame

from settings import *

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

def backtest(s, settings):        
    for (symbol, df) in data.download(settings).items():
        l = len(df)
        initial = 1
        last_buy_price = -1
        cash = 1
        equity = 0
        print(len(df)) 
        for i in range(l):
            dirty, order = s.update(symbol, df[0:i].copy())
            
            if order > 0 and last_buy_price == -1:
                cash -= order
                equity += order
                last_buy_price = df['close'].iloc[i]
            elif order < 0 and last_buy_price != -1:
                gain = df['close'].iloc[i] / last_buy_price
                cash += equity * gain
                equity = 0 
                last_buy_price = -1
            else:
                pass
            
        print("Equity: " + str(equity))
        print("Cash: " + str(round(cash, 8)))
        print("Gain: " + str(round((cash + equity - initial) / initial * 100, 2)) + "%")
            

def live(s, symbols, past=0):
    data.subscribe(symbols, s.update, past_days=past)
   

def main(args):
    sys.path.append('strategies')
    if len(args) <= 1:
        print("Strategy not specified")
        return

    s = importlib.import_module("strategies." + args[1])
    
    settings = s.register(Settings())
    
    if args[2] == 'backtest':
        backtest(s, settings)
        
    elif args[2] == 'live':
        live(s, settings)

if __name__ == '__main__':
    main(sys.argv)
