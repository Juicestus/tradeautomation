import pandas as pd
import numpy as np

from priceanalytics.plot import MultiPlot
import matplotlib.pyplot as plt, numpy as np

class Backtester(object):
    def __init__(self, df, start=50, verbose=False):
        self.df = df
        self.i = start - 1
        self.m = len(df.index)
        self.buys = {}
        self.sells = {}
        self.verb = verbose
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):      
#         self.kelly_anaylsis()
        #self.results(0.1891891891891892)
        if self.verb:
            self.results(.2)
            
            with MultiPlot(2) as m:
                m.ohlc(self.df)
                m.next()
                plt.plot(np.array(self.df['wt1']), color='#000000')


    def kelly_anaylsis(self):
        wins, losses = [], []      
        position = 0
        for i in range(len(self.df.index)):
            if i in self.buys.keys():
                x = self.buys[i]
                if position != 0: 
                    continue
                position = x
            elif i in self.sells.keys():
                x = self.sells[i]
                if position == 0: 
                    continue
                gain = (x - position) / position
                if gain > 0:
                    wins.append(gain)
                if gain < 0:
                    losses.append(gain)
                position = 0        
        f = (len(wins) - len(losses)) / len(wins)
        print(f"kelly f = {f}")
        
    def results(self, f):
        balance = 10000
        position = 0
        m_sell_t = max(self.sells.keys())
        balance_pts = []
        for i in range(len(self.df.index)):
            balance_pts.append(balance)
            if i in self.buys.keys():
                x = self.buys[i]
                if position != 0 or i >= m_sell_t:
                    continue
                bid = f * balance 
                balance -= bid
                position = bid / x
                
            elif i in self.sells.keys():
                x = self.sells[i]
                if position == 0: 
                    continue
                equity = x * position
                if self.verb:
                    print(f"eqy = {equity}")
                balance += equity
                position = 0 
               
        if self.verb: 
            print(f"result = ${balance}")
        
        return balance
        
    def __iter__(self):
        return self
    
    def __next__(self):
        self.i += 1
        if self.i > self.m:
            raise StopIteration
        self.fr = self.df[:self.i]
        return self.i, self.fr
    
    def crossover(self, k1, k2):
        return self.fr[k1][-1] > self.fr[k2][-1] \
            and self.fr[k1][-2] < self.fr[k2][-2]
    
    def buy(self):
        self.buys[self.i] = self.df.iloc[self.i]['close']
    
    def sell(self):
        self.sells[self.i] =self.df.iloc[self.i]['close']        
    