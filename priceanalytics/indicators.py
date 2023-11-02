import pandas as pd
import numpy as np
from scipy import fftpack

'''
def n_log_10_safe(x):
    if x == 0: return 0
    return math.copysign(math.log10(abs(x)), x)

def force_index(df, n): 
    return df.join(pd.Series(df['close'].diff(n) * df['volume'], name='force_index'))

def force_index_log(df, n): 
    return df.join(force_index(df, n)['force_index'].map(n_log_10_safe))

'''

def add_ha_candles(dataframe):
    """
    Returns Heikin Ashi candles
    """

    df = dataframe.copy()

    df['ha_close'] = (df.open + df.high + df.low + df.close) / 4

    df.reset_index(inplace=True)

    ha_open = [(df.open[0] + df.close[0]) / 2]

    [ha_open.append((ha_open[i] + df.ha_close.values[i]) / 2) for i in range(0, len(df) - 1)]
    df['ha_open'] = ha_open

    df.set_index(dataframe.index, inplace=True)

    df['ha_high'] = df[['ha_open', 'ha_close', 'high']].max(axis=1)
    df['ha_low'] = df[['ha_open', 'ha_close', 'low']].min(axis=1)

    return df

def add_wave_trend(df, n1=10, n2=21):
    """
    Computes the Wave Trend oscillator.
    """
    df_ha = add_ha_candles(df)
    ap = (df_ha['ha_high'] + df_ha['ha_low'] + df_ha['ha_close']) / 3
    esa = ap.ewm(span=n1, min_periods=n1).mean().dropna()  # ema(ap, n1)
    d = abs(ap - esa).ewm(span=n1, min_periods=n1).mean().dropna()
       # ema(abs(ap - esa), n1)
    ci = (ap.iloc[-len(ap):] - esa) / (0.015 * d)
    tci = ci.ewm(span=n2, min_periods=n2).mean().dropna()  # ema(ci, n2)
    wt1 = tci
    wt2 = wt1.rolling(4, min_periods=4).mean().dropna()  # sma(wt1,4)
    diff = wt1.iloc[-len(wt2):] - wt2
    diff = pd.DataFrame(diff, index=df.index, columns=['diff'])

    df_ha['wt1'] = wt1
    df_ha['wt2'] = wt2
    df_ha['wtd'] = diff

    return df_ha

def add_dfdt(df, col_x, col_y):
    """
    Computes the derivative of df[col_x] into df[col_y]
    """
    df[col_y] = pd.Series(np.gradient(df[col_x]), df.index, name=col_y)
    return df

def add_fft(df, col_x, col_y): #the following is removed because interp doesnt work right, sample=1):
    """
    Computes the Fourier transform of df[col_x] into df[col_y]
    """
    cx = df[col_x].fillna(0)
    s_len = int(len(cx) / 1) #sample)
    fft = fftpack.fft(np.array(cx), s_len)
    x = np.arange(0,1, 1 / s_len)
    freqs = np.fft.fftfreq(s_len, 1 / s_len)
    y = 0
    
    for i in range(s_len):
        x_i = freqs[i] * 2 * np.pi * x
        y += 1 / s_len * (fft[i].real * np.cos(x_i) - fft[i].imag * np.sin(x_i))
    
    # d_len = len(df[col_x])
    # if s_len != d_len:
        # This is broken and does not work as expected.
        # y = np.interp(np.linspace(0, len(y) - 1, num=d_len), np.arange(len(y)), y)
    df[col_y] = pd.Series(y, df.index, name=col_y)
    
    return df

def calc_rsi(over, fn_roll, length):
    """
    Computes the RSI of over using fn_roll 
    """ 
    delta = over.diff()
    delta = delta[1:] 

    up, down = delta.clip(lower=0), delta.clip(upper=0).abs()
    roll_up, roll_down = fn_roll(up), fn_roll(down)
    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs))

    rsi[:] = np.select([roll_down == 0, roll_up == 0, True], [100, 0, rsi])
    valid_rsi = rsi[length - 1:]
    assert ((0 <= valid_rsi) & (valid_rsi <= 100)).all()

    return rsi

def rsi_sma(df, x_col, y_col, l):
    df[y_col] = calc_rsi(df[x_col], lambda s: s.ewm(span=l).mean(), l)
    return df

def rsi_ema(df, x_col, y_col, l):
    df[y_col] = calc_rsi(df[x_col], lambda s: s.ewm(span=l).mean(), l)
    return df

def rsi_rma(df, x_col, y_col, l):
    df[y_col] = calc_rsi(df[x_col], lambda s: s.ewm(alpha = 1 / l).mean(), l) 
    return df