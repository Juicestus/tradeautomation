import matplotlib.pyplot as plt, numpy as np

def plot_ohlc(df, ax):
    x = np.arange(0, len(df))
    for idx, (_, val) in enumerate(df.iterrows()):
        color = '#F04730' if val['open'] > val['close'] else '#2CA453'
        # high/low lines
        ax.plot([x[idx], x[idx]],
                [val['low'], val['high']],
                color=color)
        # open marker
        ax.plot([x[idx], x[idx]-0.1],
                [val['open'], val['open']],
                color=color)
        # close marker
        ax.plot([x[idx], x[idx]+0.1],
                [val['close'], val['close']],
                color=color)
    return ax

class MultiPlot(object):
    def __init__(self, n_plots, size=(4, 6)):
        self.fig = plt.figure(figsize=size)
        self.n_plots = n_plots
        self.curr_plot = 0
        self.ax = None

    def __enter__(self):
        self.next()
        return self

    def __exit__(self, *args):
        plt.show()

    def next(self):
        self.curr_plot += 1
        if self.curr_plot > self.n_plots:
            raise IndexError()
        self.ax = self.fig.add_subplot(self.n_plots, 1, self.curr_plot)

    def ohlc(self, df):
        plot_ohlc(df, self.ax)


'''
     buys_y = [df.iloc[x]['close'] for x in buys_x]
    plt.scatter(buys_x, buys_y, color="#FF0000", marker="^")

    sells_y = [df.iloc[x]['close'] for x in sells_x]
    plt.scatter(sells_x, sells_y, color="#00FF00", marker="v")
'''

