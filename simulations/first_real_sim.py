import sys
import os
import time
import datetime
import numpy as np
import pandas as pd
import pickle

import matplotlib.pyplot as plt
sys.path.append(os.path.abspath('.'))
from source.constants import TMPDIR, PROJECTDIR
from copy import deepcopy
from source.market_interface import MarketInterface
from source.broker import ProsumerBroker
from source.prosumer import Prosumer
import concurrent.futures
from functools import partial


df = pd.read_csv(TMPDIR + 'all_customers.csv')

N = 50
T = 48
B0 = 0
BMIN = 0
BMAX = 5
EC = 0.95
ED = 0.95
DM = 2
Dm = -2

PRICE_B1 = np.ones(T) * 15.0
PRICE_B1[: T // 2] = 10.0
PRICE_S1 = np.ones(T) * 5.0

PRICE_B2 = np.ones(T) * 12.0

def get_one_day_data(df, day):
    nextday = datetime.timedelta(days=1) + day
    mask_day = df['date'].between(str(day), str(nextday))
    tmp = df[mask_day]
    tmp = pd.pivot_table(tmp, index='date', columns='customer', values='power')
    return tmp


if __name__ == '__main__':

    UPDATE_TYPE = sys.argv[1]
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    day = int(sys.argv[4])
    seed = int(sys.argv[5])
    algo = str(sys.argv[6]).strip()
    horizon = bool(int(sys.argv[7]))

    r = np.random.RandomState(seed)
    day_ = datetime.date(year, month, day)
    data = get_one_day_data(df, day_)
    solar = np.zeros_like(data)
    for t in range(15, 30):
        solar[t, :N //2] = r.uniform(-1, 0, N//2)
    data += solar

    start = time.time()

    prosumers = []
    brokers = []
    mid_p = 0.5 * (PRICE_B1 + PRICE_S1)
    for i in range(N):
        PB = PRICE_B1 if i % 2 == 0 else PRICE_B2
        LOAD = data.iloc[:, i + 1].values.copy()
        pro = Prosumer(i, BMAX, BMIN, EC, ED, DM, Dm, PB, PRICE_S1, LOAD, PB, PRICE_S1, UPDATE_TYPE, horizon)
        prosumers.append(pro)
        broker = ProsumerBroker(pro, r.uniform(0, 0.1), 'truthful', r=r)
        brokers.append(broker)

    market_sequence_1 = []
    renames = []
    for t in range(T):
        rename_ = {}
        print(t, '-' * 100)
        mi = MarketInterface()
        kk = 0
        for i in range(N):
                b_ = brokers[i].market_bid(t)
                c_ = brokers[i].market_callback
                if b_[0] > 0.001:
                    print('Who is who', i, kk)
                    b_1 = (b_[0], b_[1], kk, b_[3], b_[4])
                    mi.accept_bid(b_1, c_)
                    rename_[i] = kk
                    kk += 1
                else:
                    print('No trade', i)
                    c_(0, 0, prosumers[i].price_buy[t], prosumers[i].price_sell[t])
        renames.append(rename_)

        try:
            tr = mi.clear(algo, r=r)
        except TypeError:
            mi.plot_method('huang')
            assert 1 == 0
        market_sequence_1.append(deepcopy(mi))

    end = time.time()


    NAME = f"simres_8_{algo}_{UPDATE_TYPE}_1day_{year}_{month}_{day}_{seed}_{horizon}.pkl"
    with open(TMPDIR + NAME, "wb") as fh: pickle.dump([prosumers, brokers, market_sequence_1, renames], fh)


    print('Elapsed time ', end - start)
