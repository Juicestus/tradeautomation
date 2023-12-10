# based off and_test.ipybn notebook but is multithreaded

from priceanalytics.data import download_df_map, cache_df_map, load_cached_df_map
from priceanalytics.plot import MultiPlot
from priceanalytics import indicators as I
from priceanalytics.backtest import Backtester

from datetime import datetime, date, time

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from priceanalytics.backtest import perc_ret

def test_and_strat(total, _len, sig_len):
    tpr = 1
    for n, df in enumerate(total):



        df = I.add_square_bounds_osc(df, _len=_len, sig_len=sig_len)
        df = df.iloc[_len:]

        # with MultiPlot(2, size=(40,20)) as m:
        #     m.ohlc(df)
        #     m.next()
        #     plt.plot(np.array(df['sbosc_bull']), color='#00ff00')
        #     plt.plot(np.array(df['sbosc_bear']), color='#ff0000')
        #     plt.plot(np.array(df['sbosc_signal']), color='#000000')

        #print('\nSAMPLE #', n + 1)

        with Backtester(df, verbose=False) as b:
            for i, fr in b:
                if b.crossover("sbosc_bull", "sbosc_bear"):
                    if not b.in_position: #should probably do this check automatically
                        b.buy()
    #                 print("buy @ $", b.at(i))

                elif b.crossover("sbosc_signal", "sbosc_bull"):
                    if b.in_position: #should also probably do this check automatically
                        b.sell()
    #                 print("sell @ $", b.at(i))
    #             b.sell()

                if b.in_position:
                    if i >= len(df) - 1:
                        b.sell()

            incr = b.results(1)
            tpr *= (1 + incr)
            #print(f"returned {perc_ret(incr)}%")


    #print(f'\ntotal returned {perc_ret(tpr - 1)}%')
    return tpr - 1
    #         with MultiPlot(2, size=(40,20)) as m:
    #             m.ohlc(df)
    #             m.next()
    #             plt.plot(np.array(df['sbosc_bull']), color='#00ff00')
    #             plt.plot(np.array(df['sbosc_bear']), color='#ff0000')
    #             plt.plot(np.array(df['sbosc_signal']), color='#000000')

def target(_len_range, sig_len_range, q, dataset):
    for _len in _len_range:
        for sig_len_m in sig_len_range:
            sig_len = (sig_len_m / 10) * _len
            tpr = test_and_strat(dataset, _len, sig_len)
            q.put((_len, sig_len, tpr))

if __name__ == '__main__':

    #old_tdfs = load_cached_df_map(_dir="cache") # was @ interval = 5
    #old_dataset = old_tdfs['AAPL'] + old_tdfs['MSFT']

    tickers = ['AAPL', 'MSFT', 'AMZN', 'NVDA']
    new_tdfs = download_df_map(tickers, interval=1)
    new_dataset = []
    for ticker, dfs in new_tdfs.items():
        new_dataset += dfs

    #dataset = old_dataset + new_dataset
    dataset = new_dataset

    datapts = sum([len(df) for df in dataset])
    print("Loaded", len(dataset), "datasets containing", datapts, "datapoints")

    # bulk test

    import multiprocessing as mp

    results = {}

    def dif_range(s, e):
        return range(s, e), s - e

    def n_ranges(a, n):
        k, m = divmod(len(a), n)
        return list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    test = 1
    _len_range, ld = dif_range(5, 100)

    procs = round(mp.cpu_count() * 3/4)

    _len_sets = n_ranges(_len_range, procs)
    print('Will start', procs, 'processes using _len_ranges: ', _len_sets)

    sig_len_range, lr = dif_range(10, 100)
    total = ld * lr

    q = mp.Queue()

    ps = []
    for _len_range in _len_sets:
        p = mp.Process(target=target, args=(_len_range, sig_len_range, q, dataset))
        p.start()
        ps.append(p)

    print('Started', len(ps), 'processes')

    import json

    with open('sbosc_results.json', 'w') as f:

        def save():
            f.write(json.dumps(results))

        while True:
            if not q.empty():
                _len, sig_len, tpr = q.get()
                print(f"test={test}/{total} _len={_len} sig_len={sig_len} returns={perc_ret(tpr)}%")
                if _len not in results:
                    results[_len] = {}
                results[_len][sig_len] = tpr
                test += 1
                if test % 10 == 0:
                    save() #save all results on every 10th test
