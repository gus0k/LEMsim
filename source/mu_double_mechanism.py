"""
Mechanism to clear a Multi Unit Double Auction as described in

P.Huang - Design of a Multi–Unit Double Auction E–Market 

TODO:

* Group togethers bids with the same price

"""
import numpy as np
import pandas as pd
from source.singlebidding import SingleBid, SingleMarketResult, sort_biding_list
from source.market_utils import intersect_stepwise_functions

def remove_threshold(l, gap):
    """
    Implements the case described in the footnote
    where the amount to substract is less than the quantity
    original bidded. Returns the list of the only participants that trade.
    Params: 
        l: nx2 matrix with the index and quantity bided
        threshold: quantity to remove from each of the bids
    """
    end = False
    l_ = l.copy()
    while not end:
        v_min = l_[:, 1].min()
        if v_min < gap:
            l_ = np.delete(l_, l_[:, 1].argmin(), 0)
            gap += (gap - v_min) / (l_.shape[0])
            end = False
        else:
            end = True
    return l_, gap

class MultiUnitDoubleAuction:
    """
    Class to clear the multiunit double auction
    """
    
    def __init__(self, bids):
        """
        Params:
            bids: A list of buying and selling bids
        """
        
        buying_list = [b for b in bids if b.buying]
        selling_list = [b for b in bids if not b.buying]
        
        self.selling = sort_biding_list(selling_list, smallest_first=True) 
        self.buying = sort_biding_list(buying_list) 
        self.results = {}
        for b in buying_list:
            self.results[(b.player_id, b.created_at)] = (0, -1)
        for s in selling_list:
            self.results[(s.player_id, s.created_at)] = (0, -1)
            
        
        ## Accumulated curve (x axis is quantity)
        self.Nb = len(self.buying) 
        self.Ns = len(self.selling) 
        
        self.acc_buying = []
        for i in range(self.Nb + 1):
            q = 0 if i == 0 else self.buying[i - 1].quantity + self.acc_buying[-1][0]
            p = self.buying[i].price if i < self.Nb else 0
            self.acc_buying.append((q, p))
        
        self.acc_selling = []
        for i in range(self.Ns + 1):
            q = 0 if i == 0 else self.selling[i - 1].quantity + self.acc_selling[-1][0]
            p = self.selling[i].price if i < self.Ns else max(self.buying[0].price, self.selling[-1].price) + 1
            self.acc_selling.append((q, p))
            
    def clear_market(self):
        """
        Determine the quantity and the price traded for each of the bids available.
        """
        if self.buying[0].price <= self.selling[0].price: # Degenerate curves
            self.selling_price = None
            self.buying_price = None
            self.equilibrium_quantity = None
            self._prepare_results()
            return
        
        q_ast, q_b, q_s = intersect_stepwise_functions(self.acc_buying, self.acc_selling)
        bl, sl = self.acc_buying, self.acc_selling
        ss = self.selling
        bb = self.buying
        
        K, L = 0, 0
        while not (bl[K][0] == q_b):
            K += 1
        while not (sl[L][0] == q_s):
            L += 1
        

        if bl[K][0] >= sl[L][0]: # Equation 9
            gap = (bl[K][0] - sl[L][0]) / K
            print(L)
            for i in range(self.Ns):
                if i < L:
                    self.results[(ss[i].player_id, ss[i].created_at)] = (ss[i].quantity, sl[L][1])
            l = np.array([(i, bb[i].quantity) for i in range(K)])
            l, gap_ = remove_threshold(l, gap)
            for ii in l:
                ii_ = int(ii[0])
                self.results[(bb[ii_].player_id, bb[ii_].created_at)] = (bb[ii_].quantity - gap_, bl[K][1])
        else:
            print(L)
            gap = (sl[L][0] - bl[K][0]) / L
            l = np.array([(i, ss[i].quantity) for i in range(L)])
            l, gap_ = remove_threshold(l, gap)
            for ii in l:
                ii_ = int(ii[0])
                self.results[(ss[ii_].player_id, ss[ii_].created_at)] = (ss[ii_].quantity - gap_, sl[L][1])
            for i in range(self.Nb):
                if i < K:
                    self.results[(bb[i].player_id, bb[i].created_at)] = (bb[i].quantity, bl[K][1])
                
        self.selling_price = sl[L][1]
        self.buying_price = bl[K][1]
        self.equilibrium_quantity = q_ast
        results = self._prepare_results()
        #return q_ast, K, L
        return results
    
    def _prepare_results(self):
        """
        Creates a descriptive panda dataframe with all the bids
        """
        rows = []
        results = {}
        for b in (self.buying + self.selling):
            id_ = b.player_id
            ca_ = b.created_at
            action = 'Buying' if b.buying else 'Selling'
            bid_q = b.quantity
            bid_p = b.price
            res_q = self.results[(id_, ca_)][0]
            res_p = self.results[(id_, ca_)][1]
            r = [id_, ca_, action, bid_q, bid_p, res_q, res_p]
            rows.append(r)
            
            mr = SingleMarketResult(id_, ca_, res_q, res_p)
            results[b.id_] = mr
            
        columns = ['Id', 'Timestamp', 'Action', 'Bid Q', 'Bid P', 'Final Q', 'Final P']
        df = pd.DataFrame(rows, columns=columns)
        df = df.set_index('Id')
        df.iloc[:, 2:] *= 1.0 # Make them floats
        self.df = df.sort_index()
        
        return results