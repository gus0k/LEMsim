import pymarket as pm
import numpy as np


class MarketInterface(pm.Market):
    """
    Extends a normal market to add
    the ability to recieve a callback.
    It is assumed that only one bid will be recieved
    for each broker

    """

    def __init__(self):
        super().__init__()
        self.callbacks = {}

    def accept_bid(self, bid, callback):
        id_ = super().accept_bid(*bid)
        self.callbacks[id_] = callback
        return id_

    
    def clear(self, method='muda', r=None):
        tr, ex = self.run(method, r=r)
        clearing_price = []
        if method == 'muda':
            if 'price_left' in ex:
                clearing_price.append(ex['price_left'])
            if 'price_right' in ex:
                clearing_price.append(ex['price_right'])
        cp = np.array(clearing_price)
        if cp.shape[0] > 0 and np.isfinite(cp).all():
            cp = cp.mean()
        else:
            cp = None

        bids = self.bm.get_df()
        tr = tr.get_df()
        for k in self.callbacks:
            #print(k)
            tmp = tr[tr.bid == k]
            if tmp.shape[0] == 0:
                q, p = 0, 0
            else:
                q = tmp.quantity.sum()
                p = tmp.apply(lambda x: x.quantity * x.price, axis=1).sum()
                buying = bids.loc[k,'buying']
                if not buying:
                    q = - q
            self.callbacks[k](q, p, cp)
        return tr
