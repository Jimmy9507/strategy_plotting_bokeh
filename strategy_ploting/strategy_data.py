import rqportal as rp
from .calculator import *
from .round_trips import generate_round_trips


class StrategyData:
    def __init__(self, strategy_id):
        self.strategy_id = strategy_id
        self.returns = self._load_returns()
        self.factor_returns = self._load_factor_returns()
        self.positions = self._load_positions()
        self.trades = self._load_trades()
        self._returns_volatility_matched = None
        self._cumulative_returns_volatility_matched = None
        self._performance_statistic = None
        self._cumulative_returns = None
        self._cumulative_factor_returns = None
        self._rolling_beta = None
        self._rolling_sharpe = None
        self._drawhown_table = None
        self._turnover = None
        self._monthly_returns_table = None
        self._annual_returns_table = None
        self._round_trips = None

    def _load_returns(self):
        # 每日收益率
        ptf = rp.portfolio(self.strategy_id).tz_localize('utc')
        if ptf.shape[0] == 0:
            return None
        ret = ptf['daily_returns']
        ret.index = [d.normalize() for d in ret.index]
        return ret

    def _load_factor_returns(self):
        # benchmark的每日收益率
        ptf = rp.portfolio(self.strategy_id).tz_localize('utc')
        if ptf.shape[0] == 0:
            return None
        bench_ret = ptf['benchmark_daily_returns']
        bench_ret.index = [d.normalize() for d in bench_ret.index]
        return bench_ret

    def _load_positions(self):
        # 每日持仓
        pos = rp.positions(self.strategy_id).tz_localize('utc')
        if pos.shape[0] == 0:
            return None
        pos = pos.fillna(0)
        return pos

    def _load_trades(self):
        # 交易情况
        try:
            trd = rp.trades(self.strategy_id).tz_localize('utc')
        except KeyError:
            return None
        return trd

    @property
    def round_trips(self):
        if self._round_trips is not None:
            return self._round_trips
        if self.trades is None or self.positions is None:
            return None
        self._round_trips = generate_round_trips(self.trades, self.positions)
        return self._round_trips

    @property
    def monthly_returns_table(self):
        if self._monthly_returns_table is not None:
            return self._monthly_returns_table
        if self.returns is None:
            return None
        self._monthly_returns_table = aggregate_returns(self.returns)
        return self._monthly_returns_table

    @property
    def annual_returns_table(self):
        if self._annual_returns_table is not None:
            return self._annual_returns_table
        if self.returns is None:
            return None
        self._annual_returns_table = aggregate_returns(self.returns, 'yearly')
        return self._annual_returns_table

    @property
    def turnover(self):
        if self._turnover is not None:
            return self._turnover
        if self.positions is None or self.trades is None:
            return None
        self._turnover = calc_turnover(self.positions, self.trades)
        return self._turnover

    @property
    def drawdrown_table(self):
        if self._drawhown_table is not None:
            return self._drawhown_table
        if self.returns is None or self.cumulative_returns is None:
            return None
        self._drawhown_table = gen_drawdown_table(self.returns, self.cumulative_returns)
        return self._drawhown_table

    @property
    def rolling_beta(self):
        if self._rolling_beta is not None:
            return self._rolling_beta
        self._rolling_beta = [rolling_beta(self.returns, self.factor_returns, 6),
                              rolling_beta(self.returns, self.factor_returns, 12)]
        return self._rolling_beta

    @property
    def rolling_sharpe(self):
        if self._rolling_sharpe is not None:
            return self._rolling_sharpe
        self._rolling_sharpe = rolling_sharpe(self.returns)
        return self._rolling_sharpe

    @property
    def cumulative_returns(self):
        # 累计收益率
        if self._cumulative_returns is not None:
            return self._cumulative_returns
        if self.returns is None:
            return None
        self._cumulative_returns = cum_returns(self.returns)
        return self._cumulative_returns

    @property
    def cumulative_factor_returns(self):
        if self._cumulative_factor_returns is not None:
            return self._cumulative_factor_returns
        if self.factor_returns is None:
            return None
        if pd.isnull(self.factor_returns.iloc[0]):
            self.factor_returns.iloc[0] = 0.
        cum_lst = [1 + self.factor_returns[0]]
        for i in range(len(self.factor_returns) - 1):
            cum_lst.append((1 + self.factor_returns[i + 1]) * cum_lst[i])
        self._cumulative_factor_returns = pd.Series(cum_lst, index=self.factor_returns.index)
        return self._cumulative_factor_returns

    @property
    def returns_volatility_matched(self):
        if self._returns_volatility_matched is not None:
            return self._returns_volatility_matched
        if self.returns is None:
            return None
        bmark_vol = self.factor_returns.loc[self.returns.index].std()
        self._returns_volatility_matched = (self.returns / self.returns.std()) * bmark_vol
        return self._returns_volatility_matched

    @property
    def cumulative_returns_volatility_matched(self):
        if self._cumulative_returns_volatility_matched is not None:
            return self._cumulative_returns_volatility_matched
        if self.returns_volatility_matched is None:
            return None
        cum_lst = [1 + self.returns_volatility_matched[0]]
        for i in range(len(self.returns_volatility_matched) - 1):
            cum_lst.append((1 + self.returns_volatility_matched[i + 1]) * cum_lst[i])
        self._cumulative_returns_volatility_matched = pd.Series(cum_lst, index=self.returns_volatility_matched.index)
        return self._cumulative_returns_volatility_matched
