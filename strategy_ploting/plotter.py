from .config import *
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import *
from bokeh.models.tools import *
from .calculator import *
from scipy.stats import beta
from bokeh.charts import HeatMap, defaults
from bokeh import palettes

_conf = None
_color_conf = None


def get_conf():
    global _conf
    if _conf is not None:
        return _conf
    _conf = PlotingConfig()
    return _conf


def get_color_conf():
    global _color_conf
    if _color_conf is not None:
        return _color_conf
    _color_conf = ColorConfig()
    return _color_conf


def set_axises(p, yaxis_label=None, yaxis_formatter=None,xaxis_formatter=None, yaxis_label_text_fond_style='normal', xaxis_label=None):
    p.yaxis.axis_label = yaxis_label
    p.xaxis.axis_label = xaxis_label
    p.yaxis.axis_label_text_font_style = yaxis_label_text_fond_style
    p.xaxis.axis_line_alpha = p.yaxis.axis_line_alpha = 0
    p.xaxis.minor_tick_line_alpha = p.yaxis.minor_tick_line_alpha = 0
    p.xaxis.major_tick_line_alpha = p.yaxis.major_tick_line_alpha = 0.1
    if yaxis_formatter is not None:
        p.yaxis.formatter = yaxis_formatter
    if xaxis_formatter is not None:
        p.xaxis.formatter=xaxis_formatter
    p.add_tools(CrosshairTool())
    return p


def rolling_returns_plot(cum_returns, cum_factor_returns, y_axis_type='linear', mark='plot_1'):
    p = figure(title=get_conf().get('%s.title' % mark),
               width=get_conf().get('%s.width' % mark),
               height=get_conf().get('%s.height' % mark),
               x_axis_type='datetime',
               y_axis_type=y_axis_type)

    source = ColumnDataSource(data=dict(returns_index=cum_returns.index,
                                        returns=cum_returns,
                                        factor_returns_index=cum_factor_returns.index,
                                        factor_returns=cum_factor_returns,
                                        dates=cum_returns.index.strftime('%Y-%m-%d'),
                                        returns_str=round(cum_returns * 100, 2).map(str) + '%',
                                        factor_returns_str=round(cum_factor_returns * 100, 2).map(str) + '%'))

    cum_renders = p.line('returns_index', 'returns',
                         color=get_color_conf().get('%s.color' % mark),
                         line_width=2,
                         line_join='round', source=source)

    cum_factor_renders = p.line('factor_returns_index', 'factor_returns',
           color=get_color_conf().get('%s.color_factor' % mark),
           line_width=2,
           line_join='round', source=source)

    span = Span(location=1, dimension='width', line_width=2, line_alpha=0.1)
    legend = Legend(items=[LegendItem(label=get_conf().get('%s.legend' % mark)[0], renderers=[cum_renders]),
                           LegendItem(label=get_conf().get('%s.legend' % mark)[1], renderers=[cum_factor_renders])],
                    label_text_font_size={'value': '8pt'}, margin=3, padding=3, background_fill_alpha=0.4)
    p.add_layout(legend)
    p.add_layout(span)

    p.add_tools(HoverTool(tooltips=[("日期", "@dates"),
                                    (get_conf().get('%s.legend' % mark)[0], "@returns_str"),
                                    (get_conf().get('%s.legend' % mark)[1], "@factor_returns_str")],
                          mode='vline', show_arrow=False, renderers=[cum_renders], line_policy='nearest'))

    return set_axises(p, yaxis_formatter=NumeralTickFormatter(format='0 %'),
                      xaxis_formatter=DatetimeTickFormatter(months='%Y-%m'))


def scenario_plot(cumulative_returns, cumulative_factor_returns, range, mark):
    cum_ret = cumulative_returns[(cumulative_returns.index >= range[0]) & (range[1] >= cumulative_returns.index)]
    cum_fac_ret = cumulative_factor_returns[(cumulative_factor_returns.index >= range[0]) &
                                            (range[1] >= cumulative_factor_returns.index)]
    if cum_ret.shape[0] == 0 or cum_fac_ret.shape[0] == 0:
        return None
    cum_ret = cum_ret / (cum_ret[0])
    cum_fac_ret = cum_fac_ret / (cum_fac_ret[0])
    return rolling_returns_plot(cum_ret, cum_fac_ret, mark=mark)


def returns_plot(returns):
    if returns is None:
        return None
    p = figure(title=get_conf().get('plot_4.title'),
               width=get_conf().get('plot_4.width'),
               height=get_conf().get('plot_4.height'),
               x_axis_type='datetime')

    source = ColumnDataSource(data=dict(returns_index=returns.index,
                                        returns=returns,
                                        dates=returns.index.strftime('%Y-%m-%d'),
                                        returns_str=round((returns * 100), 2).map(str) + '%'))

    p.line('returns_index', 'returns',
           color=get_color_conf().get('plot_4.color'),
           line_join='round', source=source)

    span = Span(location=0.0, dimension='width', line_width=2, line_alpha=0.1)
    p.add_layout(span)

    p.add_tools(HoverTool(tooltips=[('日期', '@dates'), (get_conf().get('plot_4.legend')[0], "@returns_str")],
                          mode='vline', show_arrow=False, line_policy='nearest'))
    return set_axises(p, yaxis_formatter=NumeralTickFormatter(format='0.00 %'),
                      xaxis_formatter=DatetimeTickFormatter(months='%Y-%m'))


def rolling_beta_plot(rolling_beta_6, rolling_beta_12):
    p = figure(title=get_conf().get('plot_5.title'),
               width=get_conf().get('plot_5.width'),
               height=get_conf().get('plot_5.height'),
               x_axis_type='datetime')

    source = ColumnDataSource(data=dict(beta6_x=rolling_beta_6.index,
                                        beta6_y=rolling_beta_6,
                                        beta12_x=rolling_beta_12.index,
                                        beta12_y=rolling_beta_12,
                                        month6_dates=rolling_beta_6.index.strftime('%Y-%m-%d'),
                                        month12_dates=rolling_beta_12.index.strftime('%Y-%m-%d'),
                                        month6_beta=round(rolling_beta_6, 2),
                                        month12_beta=round(rolling_beta_12, 2)))

    if rolling_beta_6 is None:
        return None
    render_beta_6 = p.line('beta6_x', 'beta6_y',
                           color=get_color_conf().get('plot_5.color_6'),
                           legend=get_conf().get('plot_5.legend')[0],
                           line_join='round',
                           line_width=2, source=source)

    if rolling_beta_12 is not None:
        p.line('beta12_x', 'beta12_y',
               color=get_color_conf().get('plot_5.color_12'),
               legend=get_conf().get('plot_5.legend')[1],
               line_join='round',
               line_width=2, source=source)

    span = Span(location=1.0, dimension='width', line_width=2, line_dash='dashed', line_alpha=0.5)
    p.add_layout(span)
    p.add_tools(HoverTool(tooltips=[
        ('日期（6个月）', '@month6_dates'),
        ('日期（12个月）', '@month12_dates'),
        (get_conf().get('plot_5.legend')[0] + '累计beta', '@month6_beta'),
        (get_conf().get('plot_5.legend')[1] + '累计beta', '@month12_beta')],
        mode='vline', show_arrow=False, renderers=[render_beta_6], line_policy='nearest'
    ))

    return set_axises(p)


def rolling_sharpe_plot(rolling_sharpe):
    p = figure(title=get_conf().get('plot_6.title'),
               width=get_conf().get('plot_6.width'),
               height=get_conf().get('plot_6.height'),
               x_axis_type='datetime')

    source = ColumnDataSource(data=dict(x=rolling_sharpe.index,
                                        y=rolling_sharpe,
                                        dates=rolling_sharpe.index.strftime('%Y-%m-%d'),
                                        cum_sharpe=round(rolling_sharpe, 2)))
    p.line('x', 'y',
           color=get_color_conf().get('plot_6.color'),
           legend=get_conf().get('plot_6.legend')[0],
           line_join='round',
           line_width=2, source=source)

    p.line([rolling_sharpe.index[0], rolling_sharpe.index[0]],
           [rolling_sharpe[0], [rolling_sharpe[0]]],
           color=get_color_conf().get('plot_6.color_average'),
           legend=get_conf().get('plot_6.legend')[1],
           line_dash='4 4',
           line_width=2)  # 这条线不会显示出来的，我为了给虚线加一个legend也是很拼。

    span = Span(location=rolling_sharpe.mean(), dimension='width', line_width=2, line_dash='dashed',
                line_color=get_color_conf().get('plot_6.color_average'))
    p.add_layout(span)

    p.add_tools(HoverTool(tooltips=[('日期', '@dates'), (get_conf().get('plot_6.legend')[0], '@cum_sharpe')],
                          mode='vline', line_policy='nearest'))
    return set_axises(p)


def top_drawdown_plot(cumulative_returns, drawdown_table):
    if cumulative_returns is None or drawdown_table is None:
        return None

    def datetime2int(date):
        return date.year * 10000 + date.month * 100 + date.day

    drowndown_list = [{'peak': peak, 'recovery': recovery}
                      for i, (peak, recovery) in drawdown_table[['peak date', 'recovery date']].iterrows()]

    def drawdown_interval(date):
        for i, value in enumerate(drowndown_list):
            peak = value['peak']
            recovery = value['recovery']
            if pd.isnull(recovery):
                recovery = cumulative_returns.index[-1]
            if datetime2int(peak) <= datetime2int(date) <= datetime2int(recovery):
                net_drawdown = drawdown_table['net drawdown in %'][i]
                return '%s - %s' % (peak.strftime('%Y-%m-%d'), recovery.strftime('%Y-%m-%d')), \
                       '%.2f%%' % net_drawdown
        return '不在五大回撤中', '不适用'

    cumulative_returns = cumulative_returns - 1
    p = figure(title=get_conf().get('plot_8.title'),
               width=get_conf().get('plot_8.width'),
               height=get_conf().get('plot_8.height'),
               x_axis_type='datetime')

    source = ColumnDataSource(data=(dict(x=cumulative_returns.index,
                                         y=cumulative_returns,
                                         dates=cumulative_returns.index.strftime('%Y-%m-%d'),
                                         returns=round(cumulative_returns * 100, 2).map(str) + '%',
                                         interval=[drawdown_interval(item)[0] for item in cumulative_returns.index],
                                         net_drawdown=[drawdown_interval(item)[1] for item in
                                                       cumulative_returns.index])))
    renders = p.line('x', 'y',
                     color=get_color_conf().get('plot_8.color'),
                     line_join='round',
                     line_width=2, source=source)

    colors = get_color_conf().get('plot_8.color_box')

    legend = Legend(items=[LegendItem(label=get_conf().get('plot_8.legend')[0], renderers=[renders])],
                    label_text_font_size={'value': '8pt'}, margin=3, padding=3, background_fill_alpha=0.4)
    p.add_layout(legend)
    for i, (peak, recovery) in drawdown_table[['peak date', 'recovery date']].iterrows():
        if pd.isnull(recovery):
            recovery = cumulative_returns.index[-1]
        box = BoxAnnotation(left=peak.to_pydatetime().timestamp() * 1000,
                            right=recovery.to_pydatetime().timestamp() * 1000,
                            fill_color=colors[i])
        p.add_layout(box)

    p.add_tools(HoverTool(tooltips=[('日期', '@dates'),
                                    (get_conf().get('plot_8.legend')[0], '@returns'),
                                    ('回撤区间', '@interval'),
                                    ('回撤幅度', '@net_drawdown')], mode='vline', show_arrow=False, line_policy='nearest'))
    return set_axises(p, yaxis_formatter=NumeralTickFormatter(format='0.00 %'),
                      xaxis_formatter=DatetimeTickFormatter(months='%Y-%m'))


def position_exposure_plot(positions):
    # 持仓占比
    if positions is None:
        return None
    positions = positions.divide(positions.sum(axis='columns'), axis='rows')
    pos_wo_cash = positions.drop('cash', axis=1)
    longs = pos_wo_cash[pos_wo_cash > 0].sum(axis=1).fillna(0)
    shorts = pos_wo_cash[pos_wo_cash < 0].sum(axis=1).fillna(0)
    cash = positions.cash
    net_liquidation = longs - shorts + cash
    df_pos = pd.DataFrame({'long': longs.divide(net_liquidation, axis='index'),
                           'short': shorts.divide(net_liquidation, axis='index')})
    df_pos['net'] = df_pos['long'] + df_pos['short']

    source = ColumnDataSource(data=dict(index=df_pos.index,
                                        long=df_pos['long'],
                                        short=df_pos['short'],
                                        net=df_pos['net'],
                                        long_str=round(df_pos['long'], 3).map(str),
                                        short_str=round(df_pos['short'], 3).map(str),
                                        net_str=round(df_pos['net'], 3).map(str),
                                        dates=df_pos.index.strftime('%Y-%m-%d')))

    p = figure(title=get_conf().get('plot_17.title'),
               width=get_conf().get('plot_17.width'),
               height=get_conf().get('plot_17.height'),
               x_axis_type='datetime')

    long_line = p.line('index', 'long',
                       color=get_color_conf().get('plot_17.color_long'),
                       line_join='round',
                       line_width=2,
                       source=source)
    short_line = p.line('index', 'short',
                        color=get_color_conf().get('plot_17.color_short'),
                        line_join='round',
                        line_width=2,
                        source=source)
    net_line = p.line('index', 'net',
                      color=get_color_conf().get('plot_17.color_net'),
                      line_join='round',
                      line_width=2,
                      line_dash='3 4',
                      source=source)
    legend = Legend(items=[LegendItem(label=get_conf().get('plot_17.legend')[1], renderers=[short_line]),
                           LegendItem(label=get_conf().get('plot_17.legend')[2], renderers=[net_line]),
                           LegendItem(label=get_conf().get('plot_17.legend')[0], renderers=[long_line])],
                    label_text_font_size={'value': '8pt'}, margin=3, padding=3, background_fill_alpha=0.4)
    p.add_layout(legend)
    p.add_tools(HoverTool(tooltips=[('日期', '@dates'),
                                    (get_conf().get('plot_17.legend')[0], '@long_str'),
                                    (get_conf().get('plot_17.legend')[1], '@short_str'),
                                    (get_conf().get('plot_17.legend')[2], '@net_str')],
                          mode='vline',
                          show_arrow=False,
                          renderers=[long_line],
                          line_policy='nearest'))
    return set_axises(p,xaxis_formatter=DatetimeTickFormatter(months='%Y-%m'))


def top_positions_plot(positions, top=10):
    # 前十大重仓股持仓占比
    legend_location = (0, 0)
    positions = positions.divide(positions.sum(axis='columns'), axis='rows')
    positions = positions.drop('cash', axis='columns')
    df_top_abs = positions.abs().max().nlargest(top)
    source_data = {item.replace('.', '_'): positions[item] for item in df_top_abs.index}
    source_data.update({item.replace('.', '_') + '_str': (round(positions[item] * 100, 3).map(str) + '%')
                        for item in df_top_abs.index})
    source_data['index'] = positions.index
    source_data['dates'] = positions.index.strftime('%Y-%m-%d')
    source_data['max'] = pd.Series(max(positions.max()) / 2, index=positions.index)
    source = ColumnDataSource(data=source_data)
    p = figure(title=get_conf().get('plot_18.title'),
               width=get_conf().get('plot_18.width'),
               height=get_conf().get('plot_18.height'),
               x_axis_type='datetime')
    colors = get_color_conf().get('plot_18')
    items = []
    for i in range(len(df_top_abs.index)):
        instrument = df_top_abs.index[i]
        line = p.line('index', instrument.replace('.', '_'), color=colors[i], line_join='round', line_width=2,
                      source=source)
        items.append((instrument, [line]))
    if len(items) <= 5:
        legend1 = Legend(items=items, label_text_font_size={'value': '8pt'}, padding=5,
                         location=legend_location, orientation='horizontal', border_line_alpha=0)
        p.add_layout(legend1)
    else:
        legend1 = Legend(items=[items[i] for i in range(0, 5)], location=legend_location, padding=5,
                         orientation='horizontal', border_line_alpha=0, label_text_font_size={'value': '8pt'},
                         label_text_align='left')
        legend2 = Legend(items=[items[i] for i in range(5, len(items))], location=legend_location, padding=5,
                         orientation='horizontal', border_line_alpha=0, label_text_font_size={'value': '8pt'},
                         label_text_align='left')
        p.add_layout(legend1, 'below')
        p.add_layout(legend2, 'below')
    refer_line = p.line('index', 'max', source=source, line_alpha=0)
    tooltips = [(item, '@%s_str' % item.replace('.', '_')) for item in df_top_abs.index]
    p.add_tools(HoverTool(tooltips=[('日期', '@dates')] + tooltips,
                          mode='vline',
                          show_arrow=False,
                          renderers=[refer_line],
                          line_policy='nearest',
                          ),
                )
    return set_axises(p,xaxis_formatter=DatetimeTickFormatter(months='%Y-%m'))


def holding_plot(positions):
    # 每日持有股票数
    positions = positions.copy().drop('cash', axis='columns')
    df_holdings = positions.apply(lambda x: np.sum(x != 0), axis='columns')
    df_holdings_means = df_holdings.groupby(lambda x: x.year * 100 + x.month).mean()
    df_holdings_by_month = pd.Series([df_holdings_means[i.year * 100 + i.month] for i in df_holdings.index],
                                     index=df_holdings.index)
    source = ColumnDataSource(data=dict(holdings_x=df_holdings.index, holdings_y=df_holdings,
                                        holdings_month_x=df_holdings_by_month.index,
                                        holdings_month_y=df_holdings_by_month,
                                        holdings_dates=df_holdings.index.strftime('%Y-%m-%d')))

    p = figure(title=get_conf().get('plot_20.title'),
               width=get_conf().get('plot_20.width'),
               height=get_conf().get('plot_20.height'),
               x_axis_type='datetime')
    holdings_line = p.line('holdings_x', 'holdings_y',
                           color=get_color_conf().get('plot_20.daily'),
                           line_width=2,
                           line_join='round', source=source)
    months_line = p.line('holdings_month_x', 'holdings_month_y',
                         color=get_color_conf().get('plot_20.by_month'),
                         line_width=2,
                         line_join='round', source=source)
    average_line = p.line([df_holdings.index[0], df_holdings.index[0]],
                          [df_holdings[0], [df_holdings[0]]],
                          color=get_color_conf().get('plot_20.average'),
                          line_dash='4 4',
                          line_width=2)  # 这条线不会显示出来的，我为了给虚线加一个legend也是很拼。
    span = Span(location=df_holdings.values.mean(), dimension='width', line_width=2, line_dash='dashed',
                line_color=get_color_conf().get('plot_20.average'))
    p.add_layout(span)
    legend = Legend(items=[LegendItem(label=get_conf().get('plot_20.legend')[0], renderers=[holdings_line]),
                           LegendItem(label=get_conf().get('plot_20.legend')[1], renderers=[months_line]),
                           LegendItem(label=get_conf().get('plot_20.legend')[2], renderers=[average_line])],
                    label_text_font_size={'value': '8pt'}, margin=3, padding=3, background_fill_alpha=0.4)
    p.add_layout(legend)
    p.add_tools(HoverTool(tooltips=[
        ('日期', '@holdings_dates'),
        (get_conf().get('plot_20.legend')[0], '@holdings_y'),
        (get_conf().get('plot_20.legend')[1], '@holdings_month_y')],
        mode='vline', show_arrow=False, renderers=[holdings_line], line_policy='nearest'))
    return set_axises(p,xaxis_formatter=DatetimeTickFormatter(months='%Y-%m'))


def turnover_plot(turnover):
    # 每日换手率

    turnover_means = turnover.groupby(lambda x: x.year * 100 + x.month).mean()
    turnover_by_month = pd.Series([turnover_means[i.year * 100 + i.month] for i in turnover.index],
                                  index=turnover.index)
    source = ColumnDataSource(data=dict(turnover_index=turnover.index,
                                        turnover=turnover,
                                        turnover_by_month=turnover_by_month,
                                        turnover_str=round(turnover, 4).map(str),
                                        turnover_by_month_str=round(turnover_by_month, 4).map(str),
                                        dates=turnover.index.strftime('%Y-%m-%d')))

    p = figure(title=get_conf().get('plot_21.title'),
               width=get_conf().get('plot_21.width'),
               height=get_conf().get('plot_21.height'),
               x_axis_type='datetime')
    turnover_line = p.line('turnover_index', 'turnover',
                           color=get_color_conf().get('plot_21.daily'),
                           line_width=2,
                           line_join='round',
                           source=source)
    turnover_month_line = p.line('turnover_index', 'turnover_by_month',
                                 color=get_color_conf().get('plot_21.by_month'),
                                 line_width=2,
                                 line_join='round',
                                 source=source)
    average_line = p.line([turnover.index[0], turnover.index[0]],
                          [turnover[0], [turnover[0]]],
                          color=get_color_conf().get('plot_21.average'),
                          line_dash='4 4',
                          line_width=2)  # 这条线不会显示出来的，我为了给虚线加一个legend也是很拼。
    span = Span(location=turnover.values.mean(), dimension='width', line_width=2, line_dash='dashed',
                line_color=get_color_conf().get('plot_21.average'))
    p.add_layout(span)
    legend = Legend(items=[LegendItem(label=get_conf().get('plot_21.legend')[0], renderers=[turnover_line]),
                           LegendItem(label=get_conf().get('plot_21.legend')[1], renderers=[turnover_month_line]),
                           LegendItem(label=get_conf().get('plot_21.legend')[2], renderers=[average_line])],
                    label_text_font_size={'value': '8pt'}, margin=3, padding=3, background_fill_alpha=0.4)
    p.add_layout(legend)

    p.add_tools(HoverTool(tooltips=[('日期', '@dates'),
                                    (get_conf().get('plot_21.legend')[0], '@turnover_str'),
                                    (get_conf().get('plot_21.legend')[1], '@turnover_by_month_str')],
                          mode='vline',
                          show_arrow=False,
                          renderers=[turnover_line], line_policy='nearest'))
    return set_axises(p,xaxis_formatter=DatetimeTickFormatter(months='%Y-%m'))


def handle_data(data):
    years, months, values, label_colors, positions = [], [], [], [], []
    pos_nums = [i for i in data if i >= 0]
    neg_nums = [i for i in data if i <= 0]
    pos_max_num = max(pos_nums) if len(pos_nums) != 0 else 0
    neg_min_num = min(neg_nums) if len(neg_nums) != 0 else 0

    pos_num_distance = (pos_max_num - 0) / 5.
    neg_num_distance = (0 - neg_min_num) / 5.

    for month in range(1, 13):
        for year in data.index.levels[0]:
            position = {}
            try:
                value = data[year][month]
                if value > 0:
                    position['type'] = 'pos'
                    position['color_idx'] = int((value - 0) / pos_num_distance)
                elif value < 0:
                    position['type'] = 'neg'
                    position['color_idx'] = int((0 - value) / neg_num_distance)
                else:  # value=0
                    position['type'] = 'zero'
                    position['color_idx'] = 0
                years.append(str(year))
                months.append('%d月' % month)
                values.append('%.2f%%' % (100 * value))
                positions.append(position)
                if position['color_idx'] in [3,4,5,6]:
                    label_colors.append('white')
                else:
                    label_colors.append('black')
            except KeyError:
                pass
    return {'years': years,
            'months': months,
            'values': values,
            'positions': positions,
            'label_colors': label_colors
            }


def monthly_returns_plot(monthly_returns_table):
    # 热力图
    if monthly_returns_table is None:
        return None
    data = handle_data(monthly_returns_table)
    if data is None:
        return None
    p = figure(title=get_conf().get('plot_9.title'),
               width=get_conf().get('plot_9.width'),
               height=get_conf().get('plot_9.height'),
               y_range=sorted(list(set(data['years']))),
               x_range=sorted(list(set(data['months'])), key=lambda x: int(x[:-1])),
               )
    p.rect(data['months'], data['years'],
           width=1, height=1,
           color=[get_color_conf().get('plot_9').get(i.get('type'))[i.get('color_idx')] for i in data['positions']])
    labels = LabelSet(x='months', y='years',
                      source=ColumnDataSource(data),
                      text='values',
                      text_color='label_colors',
                      x_offset=-15,
                      y_offset=-6,
                      text_font_size='6pt')
    p.add_layout(labels)
    p.ygrid.grid_line_alpha = 0
    p.xgrid.grid_line_alpha = 0
    p.xaxis.major_tick_line_alpha = p.yaxis.major_tick_line_alpha = 0.1
    p.xaxis.axis_line_alpha = p.yaxis.axis_line_alpha = 0
    return p


def annual_returns_plot(annual_returns_table):
    # 年度收益率
    if annual_returns_table is None:
        return None
    returns = pd.DataFrame(annual_returns_table)
    values = returns.daily_returns

    p = figure(width=get_conf().get('plot_10.width'),
               height=get_conf().get('plot_10.height'),
               y_range=[str(e) for e in list(returns.index)],
               title=get_conf().get('plot_10.title'), )

    x = [v / 2 for i, v in enumerate(values)]
    y = [i + 1 for i, v in enumerate(values)]
    width = [round(abs(v), 4) for i, v in enumerate(values)]
    x_str = [str(round(v * 100, 2)) + '%' for i, v in enumerate(values)]
    source = ColumnDataSource(data=dict(
        width=width, x=x, y=y, x_str=x_str
    ))
    p.rect(x='x',
           y='y',
           width='width',
           height=0.4,
           color=get_color_conf().get('plot_10').get('color'),
           width_units='data',
           height_units='data', source=source)
    average_line = p.line([0, 0], [0, 100],
                          line_dash='dashed',
                          color=get_color_conf().get('plot_10').get('color_mean'))
    mean_span = Span(location=np.mean(values),
                     dimension='height',
                     line_width=2,
                     line_dash='dashed',
                     line_color=get_color_conf().get('plot_10.color_mean'))
    ref_span = Span(location=0,
                    dimension='height',
                    line_width=2,
                    line_dash='solid',
                    line_alpha=0.5)
    p.xaxis.formatter = NumeralTickFormatter(format='0.00%')
    legend = Legend(items=[LegendItem(label=get_conf().get('plot_10.legend'), renderers=[average_line])],
                    label_text_font_size={'value': '8pt'}, margin=3, padding=3, background_fill_alpha=0.4)
    p.add_layout(legend)
    p.add_layout(ref_span)
    p.add_layout(mean_span)
    p.add_tools(HoverTool(tooltips=[
        (get_conf().get('plot_10.annotation'), "@x_str")
    ], show_arrow=False))
    return set_axises(p, xaxis_label=get_conf().get('plot_10').get('xaxis_label'))


def distrubution_plot(value_list, mark, xaxis_format=None, bar_count=20):
    if len(value_list) == 1:
        interval = abs(value_list[0]) / 10.
        counts_dict = {value_list[0]: 1}
        plot_labels = [value_list[0]]
    else:
        interval = ((max(value_list) - min(value_list)) / float(bar_count))
        labels = [min(value_list) + (i) * interval for i in range(bar_count)]
        labels.append(max(value_list))
        counts_dict = {value: 0 for value in labels}

        for i in value_list:
            is_match = False
            for index, value in enumerate(labels):
                if value > i >= labels[index - 1]:
                    counts_dict[value] += 1
                    is_match = True
            if not is_match:
                counts_dict[max(value_list)] += 1
        plot_labels = [item for item in labels if counts_dict[item] != 0]

    if mark == 'plot_11' or mark == 'plot_27':
        data_range = ['%.2f%% - %.2f%%' % (item * 100, (item + interval) * 100) for item in plot_labels]
    else:
        data_range = ['%.2f - %.2f' % (item, (item + interval)) for item in plot_labels]

    source = ColumnDataSource(
        data=dict(
            top=[str(counts_dict[value]) for value in plot_labels],
            bottom=[0 * value for value in plot_labels],
            left=[value - interval / 3 for value in plot_labels],
            right=[value + interval / 3 for value in plot_labels],
            range=data_range
        )
    )
    p = figure(title=get_conf().get('%s.title' % mark),
               width=get_conf().get('%s.width' % mark),
               height=get_conf().get('%s.height' % mark),
               y_range=DataRange1d(start=0, end=max(list(counts_dict.values())))
               )
    p.yaxis[0].ticker = AdaptiveTicker(min_interval=1)

    p.quad(top='top',
           bottom='bottom',
           left='left',
           right='right',
           color=get_color_conf().get('%s.color' % mark), source=source)
    if xaxis_format is not None:
        p.xaxis.formatter = NumeralTickFormatter(format=xaxis_format)
    span = Span(location=np.mean(value_list),
                dimension='height',
                line_width=2,
                line_dash='dashed',
                line_color=get_color_conf().get('%s.color_mean' % mark))
    p.add_layout(span)

    average_line = p.line([0, 0], [0, 0],
                          line_dash='dashed',
                          color=get_color_conf().get('%s.color_mean' % mark))
    legend = Legend(items=[LegendItem(label=get_conf().get('%s.legend' % mark), renderers=[average_line])],
                    label_text_font_size={'value': '8pt'}, margin=3, padding=3, background_fill_alpha=0.4)
    p.add_layout(legend)
    p.add_tools(HoverTool(tooltips=[(get_conf().get('%s.annotation' % mark), "@top"),
                                    ('%s范围' % get_conf().get('%s.xaxis_label' % mark), '@range')],
                          show_arrow=False, ))
    return set_axises(p, yaxis_label=get_conf().get('%s.yaxis_label' % mark),
                      xaxis_label=get_conf().get('%s.xaxis_label' % mark))


def prob_profit_trade_plot(round_trips):
    round_trips_npl = pd.Series([item['pnl'] for item in round_trips])
    x = np.linspace(0, 1., 500)
    round_trips_profitable = round_trips_npl > 0
    a = round_trips_profitable.sum()
    b = (~round_trips_profitable).sum()
    y = beta.pdf(x, a, b)
    lower_perc = beta.ppf(.025, a, b)
    upper_perc = beta.ppf(.975, a, b)
    lower_span = Span(location=lower_perc, dimension='height', line_dash='solid')
    upper_span = Span(location=upper_perc, dimension='height', line_dash='solid')
    source = ColumnDataSource(data=dict(x=x, y=y))
    lower_plot = beta.ppf(.001, a, b)
    upper_plot = beta.ppf(.999, a, b)
    p = figure(title=get_conf().get('plot_24.title'),
               width=get_conf().get('plot_24.width'),
               height=get_conf().get('plot_24.height'),
               x_range=[0.000, 1.000])
    if a == 0 or b == 0:
        print('can not make this plot because some coefficients are zero')
        return p

    p.x_range = Range1d(start=lower_plot, end=upper_plot)
    p.line('x', 'y', line_color=get_color_conf().get('plot_24.color'), legend=get_conf().get('plot_24.legend')[0],
           line_width=2, source=source)
    p.add_layout(lower_span)
    p.add_layout(upper_span)
    p.add_tools(HoverTool(tooltips=[(get_conf().get('plot_24.legend')[0], '@x'),
                                    (get_conf().get('plot_24.legend')[1], '@y')],
                          mode='vline',
                          show_arrow=False, line_policy='nearest'))
    return set_axises(p, yaxis_label=get_conf().get('plot_24.yaxis_label'),
                      xaxis_label=get_conf().get('plot_24.xaxis_label'))
