from .plotter import *
from .strategy_data import StrategyData
from .strategy_data import rp as _rp
from datetime import datetime as dt
from six import iteritems

_rp_inited = None
_p = None
width = 800
height = 400

scenario_range = {'scenario_1': [dt(2015, 3, 3), dt(2015, 6, 3)],
                  'scenario_2': [dt(2014, 12, 1), dt(2015, 3, 1)],
                  'scenario_3': [dt(2015, 6, 1), dt(2015, 9, 1)],
                  'scenario_4': [dt(2015, 12, 15), dt(2016, 3, 15)],
                  'scenario_5': [dt(2016, 5, 5), dt(2016, 8, 5)]
                  }
scenario_keys = ['scenario_1', 'scenario_2', 'scenario_3', 'scenario_4', 'scenario_5']


class Strategy:
    def __init__(self, strategy_id, environment='internal', rp_config=None):
        global _rp_inited
        if _rp_inited != environment:
            _rp.init(config_path=rp_config, online=False if environment == 'internal' else True)
            _rp_inited = environment
        self.strategy_data = StrategyData(strategy_id)
        self._rolling_returns_plot = None
        self._rolling_returns_volatility_matched = None
        self._rolling_returns_log = None
        self._returns_plot = None
        self._rolling_beta_plot = None
        self._rolling_sharpe_plot = None
        self._top_drawdown_plot = None
        self._position_exposure_plot = None
        self._top_positions_plot = None
        self._holding_plot = None
        self._turnover_plot = None
        self._monthly_returns_plot = None
        self._scenario_plots = None
        self._dist_monthly_returns_plot = None
        self._annual_returns_plot = None
        self._round_trip_pnl_plot = None
        self._round_trip_return_plot = None
        self._prob_profit_trade_plot = None
        self._round_trip_holding_time_plot = None


    @property
    def rolling_returns_plot(self):
        # 对应 jira 图1
        if self._rolling_returns_plot is not None:
            return self._rolling_returns_plot
        if self.strategy_data.cumulative_returns is None or self.strategy_data.cumulative_factor_returns is None:
            return None
        self._rolling_returns_plot = rolling_returns_plot(
            self.strategy_data.cumulative_returns, self.strategy_data.cumulative_factor_returns)
        return self._rolling_returns_plot

    @property
    def rolling_returns_volatility_matched(self):
        if self._rolling_returns_volatility_matched is not None:
            return self._rolling_returns_volatility_matched
        if self.strategy_data.cumulative_returns is None or self.strategy_data.cumulative_factor_returns is None:
            return None
        self._rolling_returns_volatility_matched = rolling_returns_plot(
            self.strategy_data.cumulative_returns_volatility_matched,
            self.strategy_data.cumulative_factor_returns,
            mark='plot_2')
        return self._rolling_returns_volatility_matched

    @property
    def rolling_returns_log(self):
        if self._rolling_returns_log is not None:
            return self._rolling_returns_log
        if self.strategy_data.cumulative_returns is None or self.strategy_data.cumulative_factor_returns is None:
            return None
        self._rolling_returns_log = rolling_returns_plot(
            self.strategy_data.cumulative_returns,
            self.strategy_data.cumulative_factor_returns,
            y_axis_type='log',
            mark='plot_3')
        return self._rolling_returns_log

    @property
    def returns_plot(self):
        if self._returns_plot is not None:
            return self._returns_plot
        self._returns_plot = returns_plot(self.strategy_data.returns)
        return self._returns_plot

    @property
    def rolling_beta_plot(self):
        if self._rolling_beta_plot is not None:
            return self._rolling_beta_plot
        if self.strategy_data.rolling_beta[0] is None and self.strategy_data.rolling_beta[1] is None:
            return None
        self._rolling_beta_plot = rolling_beta_plot(self.strategy_data.rolling_beta[0],
                                                    self.strategy_data.rolling_beta[1])
        return self._rolling_beta_plot

    @property
    def rolling_sharpe_plot(self):
        if self._rolling_sharpe_plot is not None:
            return self._rolling_sharpe_plot
        self._rolling_sharpe_plot = rolling_sharpe_plot(self.strategy_data.rolling_sharpe)
        return self._rolling_sharpe_plot

    @property
    def top_drawdown_plot(self):
        if self._top_drawdown_plot is not None:
            return self._top_drawdown_plot
        self._top_drawdown_plot = top_drawdown_plot(self.strategy_data.cumulative_returns,
                                                    self.strategy_data.drawdrown_table)
        return self._top_drawdown_plot

    @property
    def position_exposure_plot(self):
        if self._position_exposure_plot is not None:
            return self._position_exposure_plot
        self._position_exposure_plot = position_exposure_plot(self.strategy_data.positions)
        return self._position_exposure_plot

    @property
    def top_positions_plot(self):
        if self._top_positions_plot is not None:
            return self._top_positions_plot
        if self.strategy_data.positions is None:
            return None
        self._top_positions_plot = top_positions_plot(self.strategy_data.positions)
        return self._top_positions_plot

    @property
    def holding_plot(self):
        if self._holding_plot is not None:
            return self._holding_plot
        if self.strategy_data.positions is None:
            return None
        self._holding_plot = holding_plot(self.strategy_data.positions)
        return self._holding_plot

    @property
    def turnover_plot(self):
        if self._turnover_plot is not None:
            return self._turnover_plot
        if self.strategy_data.turnover is None:
            return None
        self._turnover_plot = turnover_plot(self.strategy_data.turnover)
        return self._turnover_plot

    @property
    def monthly_returns_plot(self):
        if self._monthly_returns_plot is not None:
            return self._monthly_returns_plot
        self._monthly_returns_plot = monthly_returns_plot(self.strategy_data.monthly_returns_table)
        return self._monthly_returns_plot

    @property
    def scenario_plots(self):
        if self._scenario_plots is not None:
            return self._scenario_plots
        if self.strategy_data.cumulative_returns is None or self.strategy_data.cumulative_factor_returns is None:
            return []
        self._scenario_plots = []
        for scenario, range in iteritems(scenario_range):
            self._scenario_plots.append(scenario_plot(self.strategy_data.cumulative_returns,
                                                      self.strategy_data.cumulative_factor_returns,
                                                      range, scenario))
        return self._scenario_plots

    @property
    def dist_monthly_returns_plot(self):
        if self._dist_monthly_returns_plot is not None:
            return self._dist_monthly_returns_plot
        if self.strategy_data.monthly_returns_table is None:
            return None
        self._dist_monthly_returns_plot = distrubution_plot(self.strategy_data.monthly_returns_table.tolist(),
                                                            'plot_11', '0.00%')
        return self._dist_monthly_returns_plot

    @property
    def annual_returns_plot(self):
        if self._annual_returns_plot is not None:
            return self._annual_returns_plot
        self._annual_returns_plot = annual_returns_plot(self.strategy_data.annual_returns_table)
        return self._annual_returns_plot

    @property
    def round_trip_pnl_plot(self):
        if self._round_trip_pnl_plot is not None:
            return self._round_trip_pnl_plot
        if self.strategy_data.round_trips is None:
            return None
        self._round_trip_pnl_plot = distrubution_plot([item['pnl'] for item in self.strategy_data.round_trips],
                                                      'plot_26')
        return self._round_trip_pnl_plot

    @property
    def round_trip_return_plot(self):
        if self._round_trip_return_plot is not None:
            return self._round_trip_return_plot
        if self.strategy_data.round_trips is None:
            return None

        self._round_trip_return_plot = distrubution_plot([item['return'] for item in self.strategy_data.round_trips],
                                                         'plot_27', '0.00%')
        return self._round_trip_return_plot

    @property
    def prob_profit_trade_plot(self):
        if self._prob_profit_trade_plot is not None:
            return self._prob_profit_trade_plot
        self._prob_profit_trade_plot = prob_profit_trade_plot(self.strategy_data.round_trips, )
        return self._prob_profit_trade_plot

    @property
    def round_trip_holding_time_plot(self):
        if self._round_trip_holding_time_plot is not None:
            return self._round_trip_holding_time_plot
        if self.strategy_data.round_trips is None:
            return None
        self._round_trip_holding_time_plot = distrubution_plot(
            [item['holding_days'] for item in self.strategy_data.round_trips], 'plot_25')
        return self._round_trip_holding_time_plot
