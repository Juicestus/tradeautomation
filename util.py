from datetime import datetime, timedelta

def n_days_ago(n):
    return datetime.now() - timedelta(days=n)

def is_crypto(symbol):
    return '/' in symbol

def all_crypto(symbols):
    return all(map(is_crypto, symbols))

def all_stock(symbols):
    return not any(map(is_crypto, symbols))