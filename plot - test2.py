from strategy_ploting.strategy import Strategy
from bokeh.plotting import show
from bokeh.layouts import column
from bokeh.io import output_file


output_file('out_put_file.html')
s = Strategy(5491)

plot_1 = s.rolling_returns_plot
plot_2 = s.rolling_returns_volatility_matched
plot_3 = s.rolling_returns_log
plot_4 = s.returns_plot
plot_5 =s.rolling_beta_plot
plot_6 = s.rolling_sharpe_plot
plot_8 = s.top_drawdown_plot
plot_9 = s.monthly_returns_plot
plot_10 = s.annual_returns_plot
plot_11 = s.dist_monthly_returns_plot
plot_17 = s.position_exposure_plot
plot_18 = s.top_positions_plot
plot_20 = s.holding_plot
plot_21 = s.turnover_plot
plot_25 = s.round_trip_holding_time_plot
plot_26 = s.round_trip_pnl_plot
plot_27 = s.round_trip_return_plot
plot_22= s.prob_profit_trade_plot

plots_scenario = s.scenario_plots

plots = [plot_1, plot_2, plot_3, plot_4,plot_5,plot_6, plot_8, plot_9, plot_10, plot_11,
         plot_17, plot_18, plot_20, plot_21,plot_22, plot_25, plot_26, plot_27]

for p in plots_scenario:
    plots.append(p)

show(column([p for p in plots if p is not None]))