from collections import deque
import numpy as np
import pandas as pd
from datetime import date
import numba

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


def holding_days_calculate(open_date, close_date):
    open_date = int(open_date)
    close_date = int(close_date)
    close = date(int(close_date / 10000), int((close_date % 10000) / 100), int(close_date % 100))
    open = date(int(open_date / 10000), int((open_date % 10000) / 100), int(open_date % 100))
    return (close - open).days


def generate_round_trip(open_trade, close_trade, total_position):
    pnl = 0 - (
        np.dot(open_trade['price'], open_trade['quantity']) + np.dot(close_trade['price'], close_trade['quantity']))
    return {
        'order_book_id': open_trade['order_book_id'],
        'open_date': open_trade['date'],
        'close_date': close_trade['date'],
        'pnl': pnl,
        'transaction_cost': open_trade['transaction_cost'] + close_trade['transaction_cost'],
        'return': pnl / total_position,
        'holding_days': holding_days_calculate(open_trade['date'], close_trade['date'])
    }


def generate_round_trips1(trades, positions):
    trades = add_closing_trade(trades, positions)
    trades['date'] = trades.index.strftime('%Y%m%d')
    positions['date'] = positions.index.strftime('%Y%m%d')
    deques = {order_book_id: deque() for order_book_id in set(trades['order_book_id'])}
    round_trips = []
    for index, row in trades.iterrows():
        total_position = positions[positions['date'] == row.date].iloc[0].drop('date').sum()
        if len(deques[row.order_book_id]) == 0:
            deques[row.order_book_id].append(row)
            continue
        if row.date == deques[row.order_book_id][-1].date:
            last_row = deques[row.order_book_id][-1]
            quantity = row.quantity + last_row.quantity
            price = (row.price * row.quantity + last_row.price * last_row.quantity) / quantity
            deques[row.order_book_id][-1] = \
                pd.Series(dict(order_book_id=row.order_book_id,
                               price=price,
                               quantity=quantity,
                               transaction_cosst=row.transaction_cost + last_row.transaction_cost,
                               date=row.date))
            continue
        if row.quantity * deques[row.order_book_id][0].quantity > 0:
            deques[row.order_book_id].append(row)
            continue
        for i in range(len(deques[row.order_book_id])):
            first_row = deques[row.order_book_id][0]
            if abs(row.quantity) == abs(first_row.quantity):
                round_trips.append(generate_round_trip(first_row, row, total_position))
                deques[row.order_book_id].popleft()
                break
            elif abs(row.quantity) < abs(first_row.quantity):
                hedged_trade = dict(first_row)
                hedged_trade['quantity'] = 0.0 - row.quantity
                hedged_trade['transaction_cost'] = hedged_trade['quantity'] / first_row.quantity * hedged_trade[
                    'transaction_cost']
                round_trips.append(generate_round_trip(hedged_trade, row, total_position))
                deques[row.order_book_id][0].quantity = first_row.quantity + row.quantity
                deques[row.order_book_id][0].transaction_cost = first_row.transaction_cost - hedged_trade[
                    'transaction_cost']
                if deques[row.order_book_id][0].transaction_cost == 0.0:
                    deques[row.order_book_id].popleft()
                break
            else:
                hedge_trade = dict(row)
                hedge_trade['quantity'] = 0.0 - first_row['quantity']
                hedge_trade['transaction_cost'] = hedge_trade['quantity'] / row.quantity * hedge_trade[
                    'transaction_cost']
                round_trips.append(generate_round_trip(first_row, hedge_trade, total_position))
                row.quantity = row.quantity + first_row.quantity
                row.transaction_cost = row.transaction_cost - hedge_trade['transaction_cost']
                if len(deques[row.order_book_id]) > 0:
                    deques[row.order_book_id].popleft()
                    continue
                else:
                    deques[row.order_book_id].append(row)
                    break
    return round_trips

@numba.jit
def generate_round_trips(trades, positions):
    trades = add_closing_trade(trades, positions)
    trades['date'] = trades.index.strftime('%Y%m%d')
    positions['date'] = positions.index.strftime('%Y%m%d')
    deques = {order_book_id: deque() for order_book_id in set(trades['order_book_id'])}
    round_trips = []
    trades_dict = trades.to_dict('records')

    for index, row in enumerate(trades_dict):
        date_position = positions.ix[row['date']].to_dict('records')[0]
        del date_position['date']
        total_position = sum(date_position.values())
        if len(deques[row['order_book_id']]) == 0:
            deques[row['order_book_id']].append(row)
            continue
        if row['date'] == deques[row['order_book_id']][-1]['date']:
            last_row = deques[row['order_book_id']][-1]
            quantity = row['quantity'] + last_row['quantity']
            price = (row['price'] * row['quantity'] + last_row['price'] * last_row['quantity']) / quantity
            deques[row['order_book_id']][-1] = \
                dict(order_book_id=row['order_book_id'],
                     price=price,
                     quantity=quantity,
                     transaction_cosst=row['transaction_cost'] + last_row['transaction_cost'],
                     date=row['date'])
            continue
        if row['quantity'] * deques[row['order_book_id']][0]['quantity'] > 0:
            deques[row['order_book_id']].append(row)
            continue
        for i in range(len(deques[row['order_book_id']])):
            first_row = deques[row['order_book_id']][0]
            if abs(row['quantity']) == abs(first_row['quantity']):
                round_trips.append(generate_round_trip(first_row, row, total_position))
                deques[row['order_book_id']].popleft()
                break
            elif abs(row['quantity']) < abs(first_row['quantity']):
                hedged_trade = dict(first_row)
                hedged_trade['quantity'] = 0.0 - row['quantity']
                hedged_trade['transaction_cost'] = hedged_trade['quantity'] / first_row['quantity'] * hedged_trade[
                    'transaction_cost']
                round_trips.append(generate_round_trip(hedged_trade, row, total_position))
                deques[row['order_book_id']][0]['quantity'] = first_row['quantity'] + row['quantity']
                deques[row['order_book_id']][0]['transaction_cost'] = first_row['transaction_cost'] - hedged_trade[
                    'transaction_cost']
                if deques[row['order_book_id']][0]['transaction_cost'] == 0.0:
                    deques[row['order_book_id']].popleft()
                break
            else:
                hedge_trade = row
                hedge_trade['quantity'] = 0.0 - first_row['quantity']
                hedge_trade['transaction_cost'] = hedge_trade['quantity'] / row['quantity'] * hedge_trade[
                    'transaction_cost']
                round_trips.append(generate_round_trip(first_row, hedge_trade, total_position))
                row['quantity'] = row['quantity'] + first_row['quantity']
                row['transaction_cost'] = row['transaction_cost'] - hedge_trade['transaction_cost']
                if len(deques[row['order_book_id']]) > 0:
                    deques[row['order_book_id']].popleft()
                    continue
                else:
                    deques[row['order_book_id']].append(row)
                    break
    return round_trips
