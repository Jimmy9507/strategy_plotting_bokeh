from round_trips import generate_round_trips
import rqportal as rp
import numpy as np
run_id = 5233
rp.init()

trades = rp.trades(run_id).tz_localize('utc')
positions = rp.positions(run_id).tz_localize('utc')
portfolio = rp.portfolio(run_id).tz_localize('utc')


round_trips = generate_round_trips(trades, positions)
for item in round_trips:
    print(item)

print('round_trip中手续费总和', np.sum([item['transaction_cost'] for item in round_trips]))
print('transaction中手续费总和', trades.transaction_cost.sum())
print('round_trip中pnl总和', np.sum([item['pnl'] for item in round_trips]))
print(portfolio.pnl.sum())
