
import sys, importlib, asyncio, data, util

from alpaca.data.timeframe import TimeFrame

def backtest(s, tf, symbols, past):
    for (symbol, df) in data.download_auto(symbols, timeframe=tf, start=util.n_days_ago(past)).items():
        l = len(df)
        for i in range(l):
            s.update(df[0:i].copy(), l)

def live(s, symbols, past=0):
    data.subscribe(symbols, s.update, past_days=past)

def main(args):
    sys.path.append('strategies')
    if len(args) <= 1:
        print("Strategy not specified")
        return

    s = importlib.import_module("strategies." + args[1])
    
    tf, symbols, past = s.register()
    
    if args[2] == 'backtest':
        backtest(s, tf, symbols, past)
        
    elif args[2] == 'live':
        live(s, symbols)

if __name__ == '__main__':
    main(sys.argv)
