import pandas as pd
import numpy as np

from priceanalytics.plot import MultiPlot
import matplotlib.pyplot as plt, numpy as np

class Backtester(object):
    def __init__(self, df, start=1, verbose=False):
        self.df = df
        self.i = start - 1
        self.m = len(df.index)
        self.buys = {}
        self.sells = {}
        self.verb = verbose
        self.i_price = None
        self.in_position = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
#         self.kelly_anaylsis()
        #self.results(0.1891891891891892)
        if self.verb:
            self.results(.2)

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
        if len(self.buys.keys()) <= 0 or len(self.sells.keys()) <= 0:
            return 0

        start = 1
        balance = start
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

        return (balance / start) - 1

    def __iter__(self):
        return self

    def __next__(self):
        self.i += 1
        if self.i >= self.m:
            self.i_price = None
            raise StopIteration
        self.fr = self.df[:self.i]
        self.i_price = self.price_at(self.i)
        return self.i, self.fr

    def buy(self, bypass=False):
        if not self.in_position or bypass:
            self.buys[self.i] = self.price_at(self.i)
            self.in_position = True
            return True
        return False

    def sell(self, bypass=False):
        if self.in_position or bypass:
            self.sells[self.i] = self.price_at(self.i)
            self.in_position = False
            return True
        return False

    # Returns price at i (deprecated)
    def at(self, i):
        return self.df['close'][i]

    # Returns price at i
    def price_at(self, i):
        return self.at(i)

    # Returns current price
    def price(self):
        if self.i_price is None:
            raise Exception("Cannot access this function from outside iteration")
        return self.i_price

# Percent from a proportion
def perc_ret(incr):
    return round(incr * 100, 2)

def avg(l):
    return sum(l)/len(l)

def med(l):
    return sorted(l)[len(l)//2]

# this is kindof bullshit
def mode(l, p=2):
    y = {}
    for r in l:
        a = round(r, p)
        if a not in y.keys():
            y[a] = 0
        y[a] += 1
    m = max(y.values())
    for g, l in y.items():
        if l == m:
            return g
    return None

def print_test_results(rets):
    print('Model Results\n')
    print(f'maximum: {perc_ret(max(rets)):7.2f}%')
    print(f'median: {perc_ret(med(rets)):8.2f}%')
    print(f'minimum: {perc_ret(min(rets)):7.2f}%')
    print(f'mean: {perc_ret(avg(rets)):10.2f}%')
    print(f'mode: {perc_ret(mode(rets, p=3)):10.2f}%')

    print(f'\noperated:  {len(rets):3d} days')
    t = 1
    for ret in rets:
        t *= 1 + ret
    print(f'returned:   {perc_ret(t-1):.2f}%')
