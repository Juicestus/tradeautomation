# package to handle current marketdata and historical datasets

from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.live import CryptoDataStream, StockDataStream
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

import datetime as dt
import pandas as pd
import priceanalytics.keys as keys
from priceanalytics.backtest import perc_ret

alpaca_client = StockHistoricalDataClient(api_key=keys.API_KEY, secret_key=keys.SECRET_KEY)

def n_days_ago(n):
    return dt.datetime.now() - dt.timedelta(days=n)

def alpaca_download_single(symbol, past_days=2, interval=1, time_unit=TimeFrameUnit.Minute):
    tf = TimeFrame(interval, time_unit)
    start = n_days_ago(past_days)
    return alpaca_client.get_stock_bars(
            StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=tf,
                start=start
            )).df

class Slice:
    def __init__(self, start, wd):
        self.start = start
        self.end = start
        self.wd = wd
    def valid(self):
        return self.wd < 5

def split_alpaca_on_day(df):
    slices = {}
    current_slice = None
    for i, (index, row) in enumerate(df.iterrows()):
        ts = index[1].to_pydatetime()
        # utc market open = 14:30
        if ts.time().hour == 14 and ts.time().minute == 30:
            current_slice = Slice(i, ts.weekday())
        # utc market close = 21:00
        if ts.time().hour == 21 and ts.time().minute == 0:
            if current_slice is None:
                continue
            current_slice.end = i
            day_id = ts.date().month * 100 + ts.date().day
            slices[day_id] = current_slice
            current_slice = None
    dfs = []
    for i, sl in slices.items():
        if not sl.valid(): continue
        dfs.append(df[sl.start:sl.end])
    return dfs

def normalize(ser, init=1):
    ser = ser.to_numpy()
    N = len(ser)
    norm, _ = np.zeroes((2, N))
    norm[0] = init
    for i in range(1, N):
        norm[i] = (ser[i] / ser[i-1]) * norm[i-1]
    return norm

def normalize_series(dfs, key):
    ds = [1]
    for df in dfs:
        ds += (normalize(df[key], init=ds[-1]))
    return pd.Series(ds)


