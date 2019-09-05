"""
Prosumer class, extendes the battery controler
"""
import numpy as np
from source.batterycontroller import BatteryController

class Prosumer(BatteryController):
    
    def __init__(self, owner_id, b_max, b_min, eff_c, eff_d, d_max, d_min, price_buy, price_sell, load, expected_price_buy, expected_price_sell, update_type):
        super().__init__(owner_id, b_max, b_min, eff_c, eff_d, d_max, d_min)
        self.price_buy = price_buy
        self.expected_price_buy = expected_price_buy
        self.price_sell = price_sell
        self.expected_price_sell = expected_price_sell
        self.load = load
        self.time = -1
        self.incurred_costs = np.zeros(len(load))
        self.consumed_energy = np.zeros(len(load))
        self.incurred_costs_wm = np.zeros(len(load))
        self.consumed_energy_wm = np.zeros(len(load))
        self.update_type = update_type

        ## Solve default usage
        #xs = self.find_optimal_step(load, price_buy, price_sell, None)
        #xs = np.array([x / self.eff_c if x > 0 else x * self.eff_d for x in xs])
        #self.profile_only_battery = xs + load #* self.resolution
        # self.cost_only_battery = xs[1]
        cons = []
        for t in range(len(load)):
            xs = self.find_optimal_step(load[t:], price_buy[t:], price_sell[t:], None)
            self.update_charge(xs[0])
            cons.append(xs[0] / eff_c if xs[0] > 0 else xs[0] * eff_d)
        self.profile_only_battery = np.array(cons) + load
        self.reset()

    def estimate_consumption(self):
        """
        Estimate the consumption of the next timeslot
        Returns:
            q: quantity wanted to be traded in the market
            p: price at which it would normall be traded
        """
        self.time += 1
        t = self.time
        #print(t)
        load = self.load[t:].copy()
        pb = self.expected_price_buy[t:].copy()
        #print(len(pb))
        ps = self.expected_price_sell[t:].copy()
        
        xs = self.find_optimal_step(load, pb, ps, None) # battery usage
        
        # Convert from battery usage to energy seen from outside
        q = xs[0] / self.eff_c if xs[0] > 0 else xs[0] * self.eff_d 
        q += load[0] #* self.resolution
        p = pb[0] if q > 0 else ps[0]
        
        self.incurred_costs_wm[t] = q * p
        self.consumed_energy_wm[t] = q
        
        #print(q)
        
        return q, p
    def update_expected_price(self, tq, tp, cp, cost, q):
        """
        Depending on the selected strategy, updates the expected
        trading price accordingly
        Parameters
        -----------
        tq: traded quantity
        tp: traded price
        cp: clearing price, can be None
        cost: what was paid 
        q: the quantity bought or sold
        """
        t = self.time
        ut = self.update_type
        if ut == 'donothing':
            new_sp = self.expected_price_sell[t + 1]
            new_bp = self.expected_price_buy[t + 1]
        elif ut == 'lastcp':
            new_sp = cp if cp is not None else self.expected_price_sell[t + 1]
            new_bp = cp if cp is not None else self.expected_price_buy[t + 1]
        elif ut == 'lastpaid':
            new_sp = np.abs(cost / q)
            new_bp = np.abs(cost / q)
        self.expected_price_buy[t + 1] = new_bp
        self.expected_price_sell[t + 1] = new_sp

    def process_market_results(self, traded_quantity, traded_price, clearing_price):
        """
        Process the market result and takes the appropiate
        action to move forward
        Params:
            traded_quantity, amount of energy that was finally traded
            in the market
            traded_price: price at which it was traded.
        """
        #print('entre', self.owner_id)     
        t = self.time
        load = self.load[t:].copy()
        pb = self.expected_price_buy[t:].copy()
        ps = self.expected_price_sell[t:].copy()
        
        pb[0] = self.price_buy[t]
        ps[0] = self.price_sell[t]
        
        #print(self.profile_only_battery[t] - self.load[t], traded_quantity)
        
        # Respect the quantity to be traded in the market
        commitment = traded_quantity if not np.allclose(traded_quantity, 0, atol=1e-5) else None
        #print(commitment)
        #print(self.charge)        
        xs = self.find_optimal_step(load, pb, ps, commitment) # battery usage
        xf = xs[0]
        # Update the battery with the new action
        self.update_charge(xf)
        
        q = xf / self.eff_c if xf > 0 else xf * self.eff_d
        #print(q, xf)
        #print(q, load[0])
        q += load[0] #* self.resolution
        p = pb[0] if q > 0 else ps[0]
        
        #print(q, '--------\n') 
        
        #print(traded_quantity, commitment, q)
        cost = traded_quantity * traded_price + (q - traded_quantity) * p
        
        self.incurred_costs[t] = cost
        self.consumed_energy[t] = q
        if t < len(self.load) - 1:
            self.update_expected_price(traded_quantity, traded_price, clearing_price, cost, q)
