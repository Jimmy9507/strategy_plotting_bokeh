from .strategy import Strategy
from bokeh.plotting import show

if __name__=='__main__':

    s = Strategy(5233)
    p = s.rolling_beta_plot()
    show(p)
