# This library is actually a pretty bad, but it works for now.
# I (jus) will rewrite it in the future once there is a clear need.

from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.live import CryptoDataStream, StockDataStream
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime
import pandas as pd
import keys
import asyncio
from legacy.settings import SymbolType

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

def download_simple(tckr, past_days=2, interval=5, time_unit=TimeFrameUnit):
    t_f = TimeFrame(interval, time_unit)
    d_f = ownload_stock(symbol, n_days_ago(past_days), timeframe=t_f)
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

@asyncio.coroutine
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
        
