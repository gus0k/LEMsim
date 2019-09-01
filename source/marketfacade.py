from source.mu_double_mechanism import MultiUnitDoubleAuction

MECHANISMS = {
    'double_auction': MultiUnitDoubleAuction
}

class MarketFacade:
    """
    Implements a common interface for all the market
    mechanisms and interacts with the brokers
    """
    
    def __init__(self):
        """
        The ids is a common and unique identifier used
        while the current_bids is the list of active bids.
        """
        self.ids = 0
        self.current_bids = []
    
    def accept_bids(self, bid):
        """
        Assigns a unique identifier to the new bid
        and adds it to the list of active bids.
        Params:
            bid: A bid
        """
        bid.setid(self.ids)
        self.current_bids.append(bid)
        self.ids += 1
        
    def clear_market(self, method='double_auction'):
        """
        Clears the market with the available bids and the chosen
        mehtod.
        Params:
            method: one of the implemented methods to clear the market
        """
        bids = self.current_bids
        mec = MECHANISMS[method](bids)
        market_results = mec.clear_market()

        self.outcome = market_results
        self.ids = 0
        
        ## This should be async and parallel
        for b in bids:
            b.callback(market_results[b.id_])
            
        self.current_bids = []
        
        
        
    