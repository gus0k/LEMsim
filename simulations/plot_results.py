import sys
import os
import time
import glob
import datetime
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
sys.path.append(os.path.abspath('.'))
from source.constants import TMPDIR, PROJECTDIR
from source.market_interface import MarketInterface
from source.market_results import *
from source.broker import ProsumerBroker
from source.prosumer import Prosumer
from functools import partial

SIM_NAME = 'simres_9'

res = []
for f in glob.glob(f'temporal/{SIM_NAME}*'):
    r = deepcopy(load_one_result(f))
    res.append((f, r))


def filter_day(x, year, month, day):
    if f'{year}_{month}_{day}' in x[0]:
        return True
    else:
        return False

def nice_plot(data):

    net_load = data[0][1].get_aggregated_consumption_no_battery()
    only_bat = data[0][1].get_aggregated_consumption_without_market()
    lastcp_true = []
    lastpaid_true = []
    lastcp_false = []
    lastpaid_false = []
    tot = 0
    for name, r in data:
        cons = r.get_aggregated_consumption_market()
        if 'lastcp' in name and 'False' in name:
            lastcp_false.append(cons.copy())
            tot +=1
        elif 'lastcp' in name and 'True' in name:
            lastcp_true.append(cons.copy())
            tot +=1
        elif 'lastpaid' in name and 'False' in name:
            lastpaid_false.append(cons.copy())
            tot +=1
        elif 'lastpaid' in name and 'True' in name:
            lastpaid_true.append(cons.copy())
            tot +=1

    strategies = [lastcp_true, lastcp_false, lastpaid_true, lastpaid_false]

    fig, ax = plt.subplots()
    count = 0
    for s in strategies:
        for inst in s:
            count += 1
            label_ = 'Net load with strategy' if count == tot else ''
            ax.plot(inst, c='k', label=label_)
    ax.plot(net_load, c='b', label='Net load without batteries', linewidth=2.0)
    ax.plot(only_bat, c='r', label='Net load with batteries and no market', linewidth=2.0)


    ax.set_xlabel('Time slots')
    ax.set_ylabel('Net load (kWh)')
    ax.set_title('Impact of different strategies on a given day')
    ax.legend()

    return fig, ax


for i, date in enumerate([(2013, 1, 24), (2013, 5, 24)]):
    f = partial(filter_day, year=date[0], month=date[1], day=date[2])
    data = list(filter(f, res))
    fig, ax = nice_plot(data)
    if i == 1:
        ax.scatter(42, 50.7, marker='*', s=150, c='m')
    fig.savefig(f'temporal/finalfig_{i}.pdf', dpi=1000)



#### Spike formation

r = load_one_result(f'temporal/{SIM_NAME}_huang_lastcp_1day_2013_5_24_2210_True.pkl')
r1 = load_one_result(f'temporal/{SIM_NAME}_huang_donothing_1day_2013_5_24_2210_False.pkl')

## Users who contributed to the gap
usrgap = []
for i in range(50):
    p = r.prosumers[i]
    cm = p.consumed_energy[42]
    cwm = p.profile_only_battery[42]
    if np.abs(cm - cwm) > 0.1:
        usrgap.append((i, round(cm - cwm, 2)))
df_gap = pd.DataFrame(usrgap)
df_gap.columns = ['User', 'Gap (kWh)']
print(df_gap.to_latex(index=False))


print(r.markets[41].extra)

costs = []
for i, _ in usrgap:
    cs = r.prosumers[i].incurred_costs.sum()
    cost = 0
    for t in range(48):
        l = r.prosumers[i].profile_only_battery[t]
        if l > 0:
            cost += r.prosumers[i].price_buy[t] * l
        else:
            cost += r.prosumers[i].price_sell[t] * l
    cwm = r1.prosumers[i].incurred_costs.sum()
    costs.append((i, round(cs, 1), round(cost,1)))
df_cost = pd.DataFrame(costs)
df_cost.columns = ['User', 'Cost Strategy', 'Cost Do Nothing']
print(df_cost.to_latex(index=False))
