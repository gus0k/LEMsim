import pickle
from copy import deepcopy
import numpy as np


class MarketResult(object):

    """Basic class to store market results
    and get statistics about them
    """

    def __init__(self, prosumer_list, broker_list, market_list):
        """


        """
        self.prosumers = deepcopy(prosumer_list)
        self.brokers = deepcopy(broker_list)
        self.markets = deepcopy(market_list)

    def get_aggregated_consumption_without_market(self):
        """
        Finds for each prosumer what they would have had
        done without the market with batteries
        """
        agg = np.array([p.profile_only_battery for p in self.prosumers])
        agg = agg.sum(axis=0)
        return agg

    def get_aggregated_consumption_no_battery(self):
        """
        Finds for each prosumer what they would have had
        done without the market and batteries.
        """
        agg = np.array([p.load for p in self.prosumers])
        agg = agg.sum(axis=0)
        return agg

    def get_aggregated_consumption_market(self):
        """
        Finds for each prosumer what they would have had
        done with the market and batteries.
        """
        agg = np.array([p.consumed_energy for p in self.prosumers])
        agg = agg.sum(axis=0)
        return agg
    def plot_aggregated(self):
        """
        Plots the 3 different aggregated plots

        :f: TODO
        :returns: TODO

        """
        fig, ax = plt.subplots()
        ax.plot(self.get_aggregated_consumption_market(), label='market')
        ax.plot(self.get_aggregated_consumption_without_market(), label='no market')
        ax.plot(self.get_aggregated_consumption_no_battery(), label='pure load')
        ax.legend()
        ax.set_xlabel('Timeslot')
        ax.set_ylabel('kWh')
        return fig, ax

def load_market_results(filename):
    """
    Load all the simulations of the market and instanciates
    the appropiates MarketResult classes
    """

    with open(filename, 'rb') as fh: data = pickle.load(fh)
    sims = []
    for s in data:
        mr = MarketResult(s[0], s[1], s[2])
        sims.append(mr)
    return sims
