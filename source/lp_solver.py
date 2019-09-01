"""
Solves the battery control problem using the LP
formulation
"""

import numpy as np
import pulp

def solve_lp(load, price_buy, price_sell, h, b_0, b_max, b_min, eff_c, eff_d, d_max, d_min, commitment=None, eps=1e-5):
    """
    Solves the LP asociated with controlling a battery
    Params:
        load, np.array: net consumption in KW (positive if consuming and negative if surplus or renewable)
            in each timeslot
        price_buy, np.array: price of buying each kWh in each timeslot
        price_sell, np.array: price of selling each kWh in each timeslot
        h, float: duration of each timeslot in hours
        b_0, float: initial energy in the battery in kWh
        b_max, float: maximum capacity of the battery in kWh
        b_min, float: minimum capacity of the battery in kWh
        eff_c, float: efficiency of charging the battery (0, 1]
        eff_d, float: efficiency of discharging the battery (0, 1]
        d_max, float: maximum amount of power that the battery can charge in kW
        d_min, float: maximum amount of power that the battery can discharge in kW
    
    Returns:
        
        
    """
    N = load.shape[0]
    energy_cons = load * h
    keys = [str(i) for i in range(N)]
    
    inv_ec = 1.0 / eff_c
    
    x_c = pulp.LpVariable.dicts('xc', keys, 0, d_max * h) # 0 <= xc <= d_max * h
    x_d = pulp.LpVariable.dicts('xd', keys, 0, -d_min * h) # 0 <= xc <= - d_min * h
    ts  = pulp.LpVariable.dicts('ts', keys)
    
    prob = pulp.LpProblem("Battery control",pulp.LpMinimize)
    
    prob += pulp.lpSum([ts[k] for k in keys]) # Objective functions E t_i
    
    for i in range(N):
        si = str(i)
        prob += (price_buy[i]  * (x_c[si] * inv_ec - x_d[si] * eff_d + energy_cons[i])) <= ts[si]
        prob += (price_sell[i] * (x_c[si] * inv_ec - x_d[si] * eff_d + energy_cons[i])) <= ts[si]
    
        prob += pulp.lpSum([x_c[str(j)] - x_d[str(j)] for j in range(i + 1)]) <= b_max - b_0
        prob += pulp.lpSum([x_c[str(j)] - x_d[str(j)] for j in range(i + 1)]) >= b_min - b_0
     
    i = 0
    si = '0'  
    if commitment is not None:
        if commitment > 0:
            prob += (x_c[si] * inv_ec - x_d[si] * eff_d + energy_cons[i]) >= (commitment - eps)
        else:
            prob += (x_c[si] * inv_ec - x_d[si] * eff_d + energy_cons[i]) <= (commitment + eps)
    
    prob.solve(pulp.GLPK(msg=0))
    #prob.solve()
    
    xs = np.array([x_c[k].varValue - x_d[k].varValue for k in keys])
    xc = np.array([x_c[k].varValue for k in keys])
    xd = np.array([x_d[k].varValue for k in keys])
        
    return pulp.LpStatus[prob.status], pulp.value(prob.objective), xs, xc, xd

    
    
    
