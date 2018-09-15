from collections import deque
import numpy as np
import pandas as pd
from datetime import date


def timestamp2int(timestamp):
    datetime = timestamp.to_pydatetime()
    return datetime.year * 10000 + datetime.month * 100 + datetime.day


def holding_days_calculate(open_date, close_date):
    close = date(int(close_date / 10000), int((close_date % 10000)/100), int(close_date % 100))
    open = date(int(open_date / 10000), int((open_date % 10000)/100), int(open_date % 100))
    return (close - open).days


def aggregate_trades(trades):
    if np.sum(trades['quantity']) == 0:
        return None
    return {
        'order_book_id': trades['order_book_id'][0],
        'date': trades['date'][0],
        'quantity': np.sum(trades['quantity']),
        'price': np.dot(trades['price'], trades['quantity']) / np.sum(trades['quantity']),
        'transaction_cost': np.sum(trades['transaction_cost'])
    }


def generate_round_trip(open_trade, close_trade, total_position):
    pnl = 0 - (np.dot(open_trade['price'],
                                  open_trade['quantity'])+np.dot(close_trade['price'], close_trade['quantity']))
    return {
        'order_book_id': open_trade['order_book_id'],
        'open_date': open_trade['date'],
        'close_date': close_trade['date'],
        'pnl': pnl,
        'transaction_cost': open_trade['transaction_cost'] + close_trade['transaction_cost'],
        'return': pnl / total_position,
        'holding_days': holding_days_calculate(open_trade['date'], close_trade['date'])
    }


def handle_one_instrument(trades, positions):
    trade_deque = deque()
    round_trips = []
    for date in sorted(list(set(trades['date']))):
        total_position = positions[positions['date'] == date].iloc[0].drop('date').sum()
        new_trade = aggregate_trades(trades[trades['date'] == date])
        if new_trade is None:
            continue
        if len(trade_deque) == 0:
            trade_deque.append(new_trade)
        else:
            for i in range(len(trade_deque)):
                if new_trade['quantity'] * trade_deque[0]['quantity'] > 0:
                    trade_deque.append(new_trade)
                    break
                else:
                    if abs(new_trade['quantity']) == abs(trade_deque[0]['quantity']):
                        round_trips.append(generate_round_trip(trade_deque[0], new_trade, total_position))
                        trade_deque.popleft()
                        break
                    elif abs(new_trade['quantity']) < abs(trade_deque[0]['quantity']):
                        hedged_trade = dict(trade_deque[0])
                        hedged_trade['quantity'] = 0.0 - new_trade['quantity']
                        hedged_trade['transaction_cost'] = \
                            hedged_trade['quantity'] / trade_deque[0]['quantity'] * hedged_trade['transaction_cost']
                        round_trips.append(generate_round_trip(hedged_trade, new_trade, total_position))
                        trade_deque[0]['quantity'] = trade_deque[0]['quantity'] + new_trade['quantity']
                        trade_deque[0]['transaction_cost'] = \
                            trade_deque[0]['transaction_cost'] - hedged_trade['transaction_cost']
                        if trade_deque[0]['quantity'] == 0.0:
                            trade_deque.popleft()
                        break
                    else:
                        hedge_trade = dict(new_trade)
                        hedge_trade['quantity'] = 0.0 - trade_deque[0]['quantity']
                        hedge_trade['transaction_cost'] = \
                            hedge_trade['quantity'] / new_trade['quantity'] * hedge_trade['transaction_cost']
                        round_trips.append(generate_round_trip(trade_deque[0], hedge_trade, total_position))
                        new_trade['quantity'] = new_trade['quantity'] + trade_deque[0]['quantity']
                        new_trade['transaction_cost'] = new_trade['transaction_cost'] - hedge_trade['transaction_cost']
                        if len(trade_deque) > 0:
                            trade_deque.popleft()
                            continue
                        else:
                            trade_deque.append(new_trade)
                            break
    return round_trips


def add_closing_trade(trades, positions):
    last_position = positions.drop('cash', axis=1).iloc[-1]
    open_position = last_position.replace(0, np.nan).dropna()
    end_dt = open_position.name
    for order_book_id, value in last_position.iteritems():
        order_book_trade = trades[trades.order_book_id == order_book_id]
        ending_amount = order_book_trade.quantity.sum()
        if ending_amount == 0:
            continue
        ending_price = value / ending_amount
        closing_trade = {'order_book_id': order_book_id,
                         'quantity': -ending_amount,
                         'price': ending_price,
                         'transaction_cost': 0}
        closing_trade = pd.DataFrame(closing_trade, index=[end_dt])
        trades = trades.append(closing_trade)
    return trades


def generate_round_trips(trades, positions):
    trades = add_closing_trade(trades, positions)
    all_round_trips = []
    trades['date'] = [timestamp2int(item) for item in trades.index]
    positions['date'] = [timestamp2int(item) for item in positions.index]
    for order_book_id in list(set(trades['order_book_id'])):
        round_trips = handle_one_instrument(trades[trades['order_book_id'] == order_book_id], positions)
        for rt in round_trips:
            all_round_trips.append(rt)
    return all_round_trips
