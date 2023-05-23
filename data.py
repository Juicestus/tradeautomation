from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

client = CryptoHistoricalDataClient();

def download_data(symbols, start=datetime.now(), timeframe=TimeFrame.Day):
    req_params = CryptoBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Day,
            start=start
            )
    return client.get_crypto_bars(req_params)

d = download_data(['BTC/USDT'], start=datetime(2023, 5, 10, 5, 0))
print(d)

