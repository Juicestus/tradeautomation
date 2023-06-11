
import sys, importlib, asyncio, data, util
import matplotlib.pyplot as plt
import numpy as np

from alpaca.data.timeframe import TimeFrame

from settings import *
  
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
        dirty = None
        buys = []
        sells = []
        for i in range(l):
            dirty, order = s.update(symbol, df[0:i].copy())
            
            if order > 0 and last_buy_price == -1:
                cash -= order
                equity += order
                last_buy_price = df['close'].iloc[i]
                buys.append(i)
            elif order < 0 and last_buy_price != -1:
                gain = df['close'].iloc[i] / last_buy_price
                cash += equity * gain
                equity = 0 
                last_buy_price = -1
                sells.append(i)
            else:
                pass
            
        print("Equity: " + str(equity))
        print("Cash: " + str(round(cash, 8)))
        print("Gain: " + str(round((cash + equity - initial) / initial * 100, 2)) + "%")

        s.plot(dirty, buys, sells)

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
