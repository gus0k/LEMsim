import sys
import cplex
import random
import pandas as pd
import numpy as np
import docplex.mp.model as cpx
from collections import defaultdict
from cplex.exceptions import CplexSolverError


def asign_charges(batuse):
    """
    Determines how to assign the different
    charging points of the battery to the 
    discharging points of the battery using 
    the LP formulation.
    
    Parameters
    -----------
    
    batuse: np.ndarray
        An array with the battery action. Positive if
        charging, negative if discharging.
        
    Returns
    -------------
    asig : np.ndarray
        Assignament of the different charing points to the discharing
        times. 
    """
    
    opt_model = cpx.Model(name="Battery")
    
    N = batuse.shape[0]
    set_I = range(0, N)
    set_J = range(0, N)
    
    y = {j: -min(0, batuse[j]) for j in set_J}
    z = {i: max(0, batuse[i]) for i in set_I}
    
    x_vars  = {
        (i,j): opt_model.continuous_var(lb=0.0, name="x_{0}_{1}".format(i,j)) 
        for i in set_I for j in set_J
    }
    
    constraint1 = {
        j : opt_model.add_constraint(
        ct=opt_model.sum(x_vars[i,j] for i in set_I if i < j) == y[j],
        ctname="constraint1_{0}".format(j))
        for j in set_J}
    
    constraint2 = {
        i : opt_model.add_constraint(
        ct=opt_model.sum(x_vars[i,j] for j in set_J) <= z[i],
        ctname="constraint2_{0}".format(i))
        for i in set_I}
    
    objective = opt_model.sum(0)
    
    opt_model.minimize(objective)
    opt_model.solve()
    
    return x_vars
    
    
def find_price_timeslot(batuse, load, pb, e_ch):
    """
    Finds the price of electricity in the storage
    at each timeslot. It is usually the price of buying
    unless some of it was free from generation.

    Parameters
    -----------
    
    batuse: np.ndarray
        Positive if charging, negative if discharging
    load: np.ndarray
        Positive if consuming, negative if generating
    pb: np.ndarray
        Price of buying electricity from provider.
        
    Returns
    -------------    
    prices: np.ndarray
        Prices of actual energy in timeslots
        when the battery was charged.
    """
    prices = np.zeros_like(batuse)
    for t, (b, l) in enumerate(zip(batuse, load)):
        if b > 0:
            if l < 0:
                p_ = max((b / e_ch) + l , 0) * pb[t]
            else:
                p_ = (b / e_ch) * pb[t]
            p_ /= b
            prices[t] = p_
            
    return prices


def get_rps(batuse, load, pb, e_ch, e_dis):
    """
    Returns a dictionary for every timelot
    containting the price willing to pay for
    different quantities of energy. 
    
    Parameters
    ------------
    batuse : np.ndarray
        Usage of the battery
    load : np.ndarray
        Load of the player (negative if producing)
    pb : np.ndarray
        Prices for buying in each timeslot
    e_ch : float
        Efficieny while charging the battery
    e_dis:
        Efficiency while discharing the battery
    """
    
    rps = defaultdict(dict) 
    left = load.copy()
    
    prices = find_price_timeslot(batuse, load, pb, e_ch)
    xs = asign_charges(batuse)
    
    for (i, j), v in xs.items():
        v_ = v.solution_value * e_dis
        if v_ > 0:
            p_ = prices[i].round(5)
            left[j] -= v_
            if p_ in rps[j]:
                rps[j][p_] += v_
            else:
                rps[j][p_] = v_
                
            #rps[j].append((v_, p_))
        
    for j in range(len(batuse)):
        if pb[j] in rps[j]:
            rps[j][pb[j]] += left[j]
        else:
            rps[j][pb[j]] = left[j]
        #rps[j].append((left[j], pb[j]))
        
    return rps