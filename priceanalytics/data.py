# This library is actually a pretty bad, but it works for now.
# I (jus) will rewrite it in the future once there is a clear need.

from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.live import CryptoDataStream, StockDataStream
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta
import pandas as pd
import priceanalytics.keys as keys
from priceanalytics.backtest import perc_ret
import asyncio
from legacy.settings import SymbolType
import os

crypto_client = CryptoHistoricalDataClient()
stock_client = StockHistoricalDataClient(api_key=keys.API_KEY, secret_key=keys.SECRET_KEY)
crypto_stream = CryptoDataStream(api_key=keys.API_KEY, secret_key=keys.SECRET_KEY)
stock_stream = StockDataStream(api_key=keys.API_KEY, secret_key=keys.SECRET_KEY)

def n_days_ago(n):
    return datetime.now() - timedelta(days=n)

def is_crypto(symbol):
    return '/' in symbol

def all_crypto(symbols):
    return all(map(is_crypto, symbols))

def all_stock(symbols):
    return not any(map(is_crypto, symbols))

def download_crypto(symbol, start, timeframe):
    return crypto_client.get_crypto_bars(
            CryptoBarsRequest(
                    symbol_or_symbols=[symbol],
                    timeframe=timeframe,
                    start=start
            )).df

def download_stock(symbol, start, timeframe):
    return stock_client.get_stock_bars(
            StockBarsRequest(
                    symbol_or_symbols=[symbol],
                    timeframe=timeframe,
                    start=start
            )).df


def download_auto(symbols, start=datetime.now(), timeframe=TimeFrame.Minute):
    data = dict()
    for symbol in symbols:
        data[symbol] = download_crypto(symbol, start, timeframe) if is_crypto(symbol) \
                else download_stock(symbol, start, timeframe)
    return data

def download_simple(tckr, past_days=2, interval=5, time_unit=TimeFrameUnit.Minute):
    t_f = TimeFrame(interval, time_unit)
    d_f = download_stock(tckr, n_days_ago(past_days), timeframe=t_f)
    return d_f

# def download(settings):
#     start = n_days_ago(settings.past_days)
#     data = dict()
#     for symbol in settings.symbols:
#         data[symbol] = download_crypto(symbol, start, settings.timeframe) if settings.is_crypto() \
#                 else download_stock(symbol, start, settings.timeframe)
#     return data

handlers = dict()
live_data_map = dict()

# @asyncio.coroutine
async def handler(bar):
    df = pd.DataFrame({k: [v] for k, v in bar})
    if bar.symbol not in live_data_map:
        live_data_map[bar.symbol] = df
    else:
        live_data_map[bar.symbol] = pd.concat(live_data_map[bar.symbol], df)
    handlers[bar.symbol](live_data_map[bar.symbol])

# Deprecated
def subscribe_dep(symbols, callback, past_days=0):

    for symbol in symbols:
        handlers[symbol] = callback

        if is_crypto(symbol):
            crypto_stream.subscribe_bars(handler, symbol)
            if past_days > 0 or past_days is None:
                live_data_map[symbol] = download_crypto(symbol, n_days_ago(past_days), TimeFrame.Minute)
        else:
            stock_stream.subscribe_bars(handler, symbol)

    if (all_crypto(symbols)):
        crypto_stream.run()
    elif (all_stock(symbols)):
        stock_stream.run()
    else:
        raise Exception("Live cant have mixed crypto and stock symbols")

def subscribe(callback, settings):
    for symbol in settings.symbols:
        handlers[symbol] = callback

        if is_crypto(symbol):
            crypto_stream.subscribe_bars(handler, symbol)

            # Ignore this for now
            #if past_days > 0 or past_days is None:
            #     live_data_map[symbol] = download_crypto(symbol, n_days_ago(past_days), TimeFrame.Minute)
        else:
            stock_stream.subscribe_bars(handler, symbol)

    if settings.is_crypto():
        crypto_stream.run()
    else:
        stock_stream.run()

class Slicer:
    def __init__(self, weekday, start):
        self.weekday = weekday
        self.start = start
        self.end = start
    def valid(self):
        l = self.len()
        return self.weekday < 5 and 170 < l and l < 200
    def __str__(self):
        return f"{self.start} - {self.end} = {self.len()} ({self.weekday})"
    def __len__(self):
        return self.len()
    def len(self):
        return self.end - self.start

def download_df_map(tickers, past_days=50, interval=5):
    tdfs = {}
    for ticker in tickers:
        df = download_simple(ticker, past_days=past_days, interval=interval)

        print(f"raw {ticker}: {len(df.index)} datapoints from {df.index[0][-1].date()} to {df.index[-1][-1].date()}")
        last_day = 0
        info = {} # { day: Slicer }
        for i, (index, row) in enumerate(df.iterrows()):
            ts = index[1].to_pydatetime()
            day = ts.date().month * 100 + ts.date().day
            if day != last_day:
                if last_day > 0:
                    info[last_day].end = i - 1
                info[day] = Slicer(ts.weekday(), i)
            last_day = day

        tdfs[ticker] = []
        for i, slice in info.items():
            if not slice.valid(): continue
            tdfs[ticker].append(df[slice.start:slice.end])
    return tdfs


def cache_df_map(tdfs, _dir="cache"):
    os.mkdir(_dir)
    for ticker, dfs in tdfs.items():
        tdir = _dir + '/' + ticker
        os.mkdir(tdir)
        for i, df in enumerate(dfs):
            fn = tdir + '/' + str(i) + '.json'
            s = df.to_json()
            with open(fn, 'w') as f:
                f.write(s)

def load_cached_df_map(_dir="cache"):
    tdfs = {}
    for tup in os.walk(_dir):
        pre = tup[0]
        ticker = pre.replace(_dir + '/', '')
        if len(tup[-1]) <= 0: continue
        tdfs[ticker] = [None for _ in tup[-1]]
        for f in tup[-1]:
            path = pre + '/' + f
            i = int(f.replace('.json', ''))
            tdfs[ticker][i] = pd.read_json(path)
    return tdfs

def combine_dataset(_map):
    combined = []
    for ticker, dfs in _map.items():
        combined += dfs
    return combined

def calc_returns_homogenous(dataset, verbose=True):
    s = dataset[0].iloc[0]['close']
    e = dataset[-1].iloc[-1]['close']
    r = (e - s)/s
    if verbose:
        print(f'homogenous dataset yields: {perc_ret(r):5.2f}% returns')
    return r
