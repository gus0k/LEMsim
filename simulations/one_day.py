import sys
import os
import time
import datetime
sys.path.append(os.path.abspath('..'))

import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt

from source.market_interface import MarketInterface
from source.broker import ProsumerBroker
from source.prosumer import Prosumer

import concurrent.futures
from functools import partial

df = pd.read_csv('../data/ausgrid_proc.csv')
df = df.iloc[:, 1:]

def get_one_day_data(df, year, month, day):
    day = datetime.date(2012, 7, 15)
    nextday = datetime.timedelta(days=1) + day
    mask_day = df.datetime.between(str(day), str(nextday))
    tmp = df[mask_day][['datetime', 'Customer', '' 'net']]
    tmp = pd.pivot_table(tmp, index='datetime', columns='Customer', values='net')
    return tmp

def simulation_run(seed, strategy):

    r = np.random.RandomState(seed)
    prosumers = []
    brokers = []
    for i in range(N):
        LOAD = data.iloc[:, i + 1].values.copy()
        pro = Prosumer(i, BMAX, BMIN, EC, ED, DM, Dm, PRICE_B1, PRICE_S1, LOAD, PRICE_B1, PRICE_S1)
        prosumers.append(pro)
        broker = ProsumerBroker(pro, strategy, r=r)
        brokers.append(broker)

    market_sequence_1 = []
    for t in range(T):
        mi = MarketInterface()
        for i in range(N):
            mi.accept_bid(brokers[i].market_bid(t), brokers[i].market_callback)
        tr = mi.clear('muda', r=r)
        market_sequence_1.append(tr)
        
    return prosumers, brokers, market_sequence_1

data = get_one_day_data(df, 2012, 8, 6)

N = 50
T = 48
B0 = 0
BMIN = 0
BMAX = 3
EC = 0.95
ED = 0.95
DM = 1
Dm = -1

PRICE_B1 = np.ones(T) * 15.0
PRICE_B1[: T // 2] = 10.0
PRICE_S1 = np.ones(T) * 5.0



truth = partial(simulation_run, strategy='ZI')

start = time.time()

with concurrent.futures.ProcessPoolExecutor() as executor:
        res = list(executor.map(truth, range(50)))
        with open('res_zi2.pkl', 'wb') as fh:
            pickle.dump(res, fh)

end = time.time()

print('Elapsed time ', end - start)
