import pandas as pd, numpy as np, math

def n_log_10_safe(x):
    if x == 0: return 0
    return math.copysign(math.log10(abs(x)), x)

def force_index(df, n): 
    return df.join(pd.Series(df['close'].diff(n) * df['volume'], name='force_index'))

def force_index_log(df, n): 
    return df.join(force_index(df, n)['force_index'].map(n_log_10_safe))
    
