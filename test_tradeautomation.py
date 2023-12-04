from priceanalytics import indicators as I
import numpy as np

def loadarr(fn):
    with open('tradeautomation/' + fn, 'r') as f:
        return np.array([float(l) for l in f])
_open = loadarr("_open.dat")
_close = loadarr("_close.dat")

bull, bear, sig = I.__square_bounds_osc(_close, _open, 14, 28)
print(len(_open), len(_close), len(bull), len(bear), len(sig))
for i, _ in enumerate(bull):
    print(f'open={_open[i]:.4f}  close={_close[i]:.4f}  bull={bull[i]:.4f}  bear={bear[i]:.4f}  sig={sig[i]:.4f}')
