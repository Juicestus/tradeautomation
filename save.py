# Save from: Stochastic Analytics .ipynb

import priceanalytics.data as data
from alpaca.data.timeframe import TimeFrameUnit

df = data.alpaca_download_single(
    'QQQ',     
    past_days=10000, 
    interval=1,
    time_unit=TimeFrameUnit.Day
)

daily = df['close'].to_numpy()

# ----------------------------------------------------

import pandas as pd
import numpy as np
import priceanalytics.plot as plot
import matplotlib.pyplot as plt

print(len(daily))
split = -200 -200
sample = daily[:split]
test = daily[split:]

print(len(sample), len(test))

with plot.MultiPlot(1, size=(8, 4)) as m:
    
    plt.plot(daily)
    plt.plot(sample)

# ----------------------------------------------------

returns = np.diff(sample) / sample[0]
log_returns = np.diff(np.log(sample))

print("datalen = ",  len(sample))
    
with plot.MultiPlot(2, size=(8, 4)) as m:
    plt.plot(returns)
    m.next()
    plt.plot(log_returns)
    
# ----------------------------------------------------

import scipy

# critical value multiplier
cvm = 252//4

mu = returns.mean() * cvm
print("mu = ", mu)
sigma = returns.std() * (cvm**0.5)
print("sigma = ", sigma)

from scipy.stats import t as students_t

dof, loc, scale = students_t.fit(log_returns)
mu, var, skew, kurt = students_t.stats(dof, moments='mvsk') 
print(mu, var, skew, kurt)

# random = students_t.rvs(dof, loc=loc, scale=scale, size=len(log_returns))
nse = len(test) # number of samples to extrapolate

def remove_outliers(l, B):
    minmax = lambda x: max(min(x, B), -B)  # remove outliers 
    return np.array([minmax(x) for x in l])
    
with plot.MultiPlot(2, size=(8, 4)) as m:
    plt.hist(remove_outliers(log_returns, .5), bins='auto', density=True)
    plt.axvline(x=mu/nse, color='red', linestyle='--')
    m.next()
    random = students_t.rvs(dof, loc=loc, scale=scale, size=len(log_returns))
    plt.hist(remove_outliers(random, .5), bins='auto', density=True)

S0 = sample[-1]
T = 1
dt = 1/cvm
inter = int(T/dt)

np.random.seed(20)
sims = 300
paths = np.zeros((inter+1, sims))
paths[0] = S0

for t in range(1, inter+1):
    # different random strategies
    # z_score = np.random.standard_normal(sims)
    z_score = scipy.stats.laplace.rvs(size=sims)
    #z_score = students_t.rvs(dof, loc=loc, scale=scale, size=sims)

    paths[t] = paths[t-1] * np.exp((mu-0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z_score)
    
def calc(paths, S0, mu, sigma, T):
    pts = paths[-1]
    scale = S0 * np.exp(mu * T)
    probabilities = scipy.stats.lognorm.pdf(pts, s=sigma * np.sqrt(T), scale=scale)
    return probabilities

probabilities = calc(paths, S0, mu, sigma, T)
normalized = probabilities / probabilities.max()
indices = np.argsort(normalized)
paths = paths[:, indices]
new_probabilities = normalized[indices]
d = (paths[-1] - S0).mean() / S0

# ----------------------------------------------------

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable

consolidated_path = np.sum(((paths * new_probabilities) / 100), axis=1) + sample[-1]
consolidated_path -= consolidated_path[0]
consolidated_path += sample[-1]

lsc = LinearSegmentedColormap.from_list("RedToGreen", ["red", "green"])
fig, axis = plt.subplots(figsize=(10, 6))

for i in range(sims):
    prob = new_probabilities[i]
    # if prob > .3 and prob < .31:

sm = ScalarMappable(cmap=lsc)
prob_bar = plt.colorbar(sm, ax=axis)
prob_bar.set_label('Probability')

axis.plot(consolidated_path, lw=2, color='blue', label='Prediction')
axis.plot(test[:len(consolidated_path)], lw=2, color='black', label='Real')
# axis.plot(test, lw=2, color='red', label='Real')

axis.set_title('Brownian Motion Paths')
axis.set_xlabel('T')
axis.set_ylabel('Price')

plt.legend()
plt.show()

# ----------------------------------------------------

def price_level_calc(d, n, lvls):
    lvls = sorted(lvls, reverse=True) + [0]
    output = [] 

    path_by_sim = [[] for _ in range(sims)]
    for t in range(1, inter+1):
        for snum in range(sims):
            path_by_sim[snum].append(paths[t][snum])
    
    ub = int(S0 * (1 + d))
    # lb = S0 * (1 - d) 
    lb = int(S0)
    dp = (ub - lb) // n
    for S_level in range(lb, ub, dp):
        n = 0
        for i, sim_path in enumerate(path_by_sim):
            # if sum([s > S_level for s in sim_path]) > .5 * len(sim_path):
            if sum([s > S_level for s in sim_path]) > .5 * len(sim_path): 
            # if any([s > S_level for s in sim_path]): # > 0% 
                n += 1
        if n/sims < lvls[0]:
            lvls = lvls[1:]
            output.append(S_level)
        # print(f'${S_level} --> {n/sims * 100:.2f}%')
    return output

lvls = price_level_calc(.25, 30, [.68, .34, .05])
for lvl in lvls:
    plt.axhline(y=lvl, color='g', linestyle='-')