"""
Intermediary between a consumer and the market
"""

from source.singlebidding import SingleBid

class ProsumerBroker:
    
    def __init__(self, prosumer, gain, strategy='truthful', r=None):
        """
        Instanciates a broker with the prosumer it will 
        work for. There is a % of desired gain over the normal
        prices
        Params:
            prosumer, prosumer: user to represent in the market
            strategy, str: 
                The strategy followed by the prosumer, can be
                truthfull, ZI or ZIp.
        """
        
        self.prosumer = prosumer
        self.strategy = strategy
        self.r = r
        self.gain = gain 
        
    def market_bid(self, time):
        """
        Calculates the market bid to submit in the market
        Params:
            time: external time
        Returns:
            bid, SingleBid: offered in the market
        """
        t = self.prosumer.time
        buy = self.prosumer.price_buy[t]
        sell = self.prosumer.price_sell[t]
        # The prosumer solves the control problem and returns
        # how much he expects to consume and at what price
        desired_q, expected_p = self.prosumer.estimate_consumption()
        bid_q = desired_q
        buying = True if bid_q > 0 else False
        
        if self.strategy == 'truthful':
            bid_p = expected_p
            # if bid_q > 0:
            #     bid_p = buy
            # else:
            #     bid_p = sell
        
        elif self.strategy == 'ZI':
            bid_p = self.r.uniform(sell, buy)
        
        # If buying, want to pay less. If selling, want to get more
        bid_p = (1 - self.gain) * expected_p if bid_q > 0 else (1 + self.gain) * expected_p
        #print('bidding', bid_q.round(), bid_p)
        
        # Final bid 
        #bid = SingleBid(self.prosumer.owner_id, time, (bid_q, bid_p, buying), self.market_callback)
        bid_q = round(bid_q, 4)
        bid = (abs(bid_q), bid_p, self.prosumer.owner_id, buying, time)

        return bid
    
    def market_callback(self, quantity, price, pb, ps):
        """
        Informs the consumer of the market result
        Params:
            market_results: result of the last market
            clearing_price: price at which the market cleared or None
            if no trade ocurred.
        """
        self.prosumer.process_market_results(quantity, price, pb, ps)
    
