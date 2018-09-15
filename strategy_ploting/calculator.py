import pandas as pd
import numpy as np
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from .utils import APPROX_BDAYS_PER_MONTH, APPROX_BDAYS_PER_YEAR, APPROX_DAYS_PER_MON, APPROX_DAYS_PER_YR
from .utils import DAILY, WEEKLY, MONTHLY, YEARLY, ANNUALIZATION_FACTORS, YIELD_CURVE_TENORS
import rqdata

rqdata.init()


def rolling_beta(returns, factor_returns, rolling_windows_months=6):
    out = pd.Series(index=returns.index)
    for date_index in returns.index:
        end_date = date_index.to_pydatetime() + timedelta(days=1)
        start_day = date_index.to_pydatetime() - relativedelta(months=rolling_windows_months) + timedelta(days=1)
        if pd.to_datetime(start_day) < returns.index[0]:
            continue
        section_returns = returns[pd.to_datetime(start_day):pd.to_datetime(end_date)]
        section_factor_returns = factor_returns[pd.to_datetime(start_day):pd.to_datetime(end_date)]
        beta = beta_calculate(section_returns, section_factor_returns)
        out.loc[date_index] = beta
    return out.dropna()


def beta_calculate(returns, factor_returns):
    ret_index = returns.index
    bench_ret = factor_returns.loc[ret_index]
    beta = np.cov(bench_ret, returns, bias=True)[0][1] / np.var(bench_ret)
    return beta


def annual_factor(period):
    try:
        return ANNUALIZATION_FACTORS[period]
    except KeyError:
        raise ValueError("period cannot be {}, possible values: {}".format(
            period, ", ".join(ANNUALIZATION_FACTORS.keys())))


def rolling_sharpe(returns):
    yield_curve = rqdata.get_yield_curve(returns.index[0], returns.index[-1])
    out = pd.Series(index=returns.index)
    for date_index in returns.index:
        end_date = date_index.to_pydatetime() + timedelta(days=1)
        start_day = date_index.to_pydatetime() - relativedelta(months=12) + timedelta(days=1)
        if pd.to_datetime(start_day) < returns.index[0]:
            continue
        section_returns = returns[pd.to_datetime(start_day):pd.to_datetime(end_date)]
        if yield_curve[pd.to_datetime(start_day): pd.to_datetime(start_day)].shape[0] > 0:
            risk_free = get_risk_free_rate(pd.to_datetime(start_day), date_index,
                                           yield_curve[pd.to_datetime(start_day): pd.to_datetime(start_day)])
        sharpe = sharpe_calculate(section_returns, risk_free)
        out.loc[date_index] = sharpe
    return out.dropna()


def sharpe_calculate(returns, risk_free):
    days = (returns.index[-1] - returns.index[0]).days
    cumulative_return = (1 + returns).prod() - 1
    annualized_return = (cumulative_return + 1) ** (APPROX_DAYS_PER_YR / days) - 1
    volatility = returns.std() * (days ** 0.5)
    sharpe = (annualized_return - risk_free) / volatility
    return sharpe


def get_risk_free_rate(start_date, end_date, yield_curve):
    duration = (end_date - start_date).days
    tenor = 'S0'
    for days, t in YIELD_CURVE_TENORS:
        if duration > days:
            tenor = t
        else:
            break
    rate = yield_curve[tenor[1:] + tenor[0]][0]
    if np.isnan(rate):
        return 0
    return rate


def get_max_drawdown_underwater(underwater):
    valley = np.argmin(underwater)
    peak = underwater[:valley][underwater[:valley] == 0].index[-1]
    try:
        recovery = underwater[valley:][underwater[valley:] == 0].index[0]
    except IndexError:
        recovery = np.nan
    return peak, valley, recovery


def get_top_drawdowns(returns, cumulative_return, top):
    returns = returns.copy()
    df_cum = cumulative_return
    running_max = np.maximum.accumulate(df_cum)
    underwater = df_cum / running_max - 1
    drawdowns = []
    for t in range(top):
        peak, valley, recovery = get_max_drawdown_underwater(underwater)
        if not pd.isnull(recovery):
            underwater.drop(underwater[peak: recovery].index[1:-1], inplace=True)
        else:
            underwater = underwater.loc[:peak]
        drawdowns.append((peak, valley, recovery))
        if (len(returns) == 0) or (len(underwater) == 0):
            break
    return drawdowns


def gen_drawdown_table(returns, cumulative_returns, top=5):
    def time_localize(time):
        if pd.isnull(time):
            return returns.index[-1]
        return pd.to_datetime(time).tz_localize('utc')

    df_cum = cumulative_returns
    drawdown_periods = get_top_drawdowns(returns, cumulative_returns, top=top)
    df_drawdowns = pd.DataFrame(index=list(range(top)),
                                columns=['net drawdown in %',
                                         'peak date',
                                         'valley date',
                                         'recovery date',
                                         'duration'])
    for i, (peak, valley, recovery) in enumerate(drawdown_periods):
        if pd.isnull(recovery):
            df_drawdowns.loc[i, 'duration'] = np.nan
        else:
            df_drawdowns.loc[i, 'duration'] = len(pd.date_range(peak, recovery, freq='B'))
        df_drawdowns.loc[i, 'peak date'] = (peak.to_pydatetime().strftime('%Y-%m-%d'))
        df_drawdowns.loc[i, 'valley date'] = (valley.to_pydatetime().strftime('%Y-%m-%d'))
        if isinstance(recovery, float):
            df_drawdowns.loc[i, 'recovery date'] = recovery
        else:
            df_drawdowns.loc[i, 'recovery date'] = (recovery.to_pydatetime().strftime('%Y-%m-%d'))
        df_drawdowns.loc[i, 'net drawdown in %'] = (
                                                       (df_cum.loc[peak] - df_cum.loc[valley]) / df_cum.loc[peak]) * 100
    df_drawdowns['peak date'] = [time_localize(item) for item in df_drawdowns['peak date']]
    df_drawdowns['valley date'] = [time_localize(item) for item in df_drawdowns['valley date']]
    df_drawdowns['recovery date'] = [time_localize(item) for item in df_drawdowns['recovery date']]
    return df_drawdowns


def get_txn_vol(transactions):
    transactions.index = transactions.index.normalize()
    amounts = transactions.quantity.abs()
    prices = transactions.price
    values = amounts * prices
    daily_amounts = amounts.groupby(amounts.index).sum()
    daily_values = values.groupby(values.index).sum()
    daily_amounts.name = "txn_shares"
    daily_values.name = "txn_volume"
    return pd.concat([daily_values, daily_amounts], axis=1)


def calc_turnover(positions, transactions, average=True):
    txn_vol = get_txn_vol(transactions)
    traded_value = txn_vol.txn_volume
    portfolio_value = positions.sum(axis=1)
    turnover = traded_value / 2.0
    portfolio_value = portfolio_value.resample('D').mean()
    turnover_rate = turnover.div(portfolio_value, axis='index')
    turnover_rate = turnover_rate.fillna(0)
    return turnover_rate


def cum_returns(returns):
    if pd.isnull(returns.iloc[0]):
        returns.iloc[0] = 0.
    df_cum_lst = [1 + returns[0]]
    for i in range(len(returns) - 1):
        df_cum_lst.append((1 + returns[i + 1]) * df_cum_lst[i])

    df_cum = pd.Series(df_cum_lst, index=returns.index)
    return df_cum


def aggregate_returns(df_daily_rets, convert_to='monthly'):
    def cumulate_returns(x):
        return (cum_returns(x)[-1] - cum_returns(x)[0]) / cum_returns(x)[0]

    if convert_to == WEEKLY:
        return df_daily_rets.groupby(
            [lambda x: x.year,
             lambda x: x.isocalendar()[1]]).apply(cumulate_returns)
    elif convert_to == MONTHLY:
        return df_daily_rets.groupby(
            [lambda x: x.year, lambda x: x.month]).apply(cumulate_returns)
    elif convert_to == YEARLY:
        return df_daily_rets.groupby(
            [lambda x: x.year]).apply(cumulate_returns)
    else:
        ValueError(
            'convert_to must be {}, {} or {}'.format(WEEKLY, MONTHLY, YEARLY)
        )


def cal_volatility(returns):
    if len(returns) <= 1:
        return 0.
    volatility = len(returns) ** 0.5 * np.std(returns, ddof=1)
    return volatility
