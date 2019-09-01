import pymarket as pm


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
        tr, _ = self.run(method, r=r)
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
            self.callbacks[k](q, p)
        return tr