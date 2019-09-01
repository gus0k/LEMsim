"""
Prosumer class, extendes the battery controler
"""
import numpy as np
from source.batterycontroller import BatteryController

class Prosumer(BatteryController):
    
    def __init__(self, owner_id, b_max, b_min, eff_c, eff_d, d_max, d_min, price_buy, price_sell, load, expected_price_buy, expected_price_sell):
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
    
        ## Solve default usage
        xs = self.find_optimal_step(load, price_buy, price_sell, None)
        self.profile_only_battery = xs + load #* self.resolution
        # self.cost_only_battery = xs[1]

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
    
    def process_market_results(self, traded_quantity, traded_price):
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
        
        #print(traded_quantity)
        
        # Respect the quantity to be traded in the market
        commitment = traded_quantity if not np.allclose(traded_quantity, 0, atol=1e-5) else None
        #print(commitment)
        
        xs = self.find_optimal_step(load, pb, ps, commitment) # battery usage
        xf = xs[0]
        # Update the battery with the new action
        self.update_charge(xf)
        
        q = xf / self.eff_c if xf > 0 else xf * self.eff_d
        #print(q, load[0])
        q += load[0] #* self.resolution
        p = pb[0] if q > 0 else ps[0]
        
        
        
        #print(traded_quantity, commitment, q)
        cost = traded_quantity * traded_price + (q - traded_quantity) * p
        
        self.incurred_costs[t] = cost
        self.consumed_energy[t] = q
