"""
Implementation of the single bid class, the simplest kind of bid: one quantity and one price
"""
from source.bidding import Bid, MarketResult

class SingleBid(Bid):
    """
    Implements a SingleBid. A single bid is a bid in which the bid 
    is a tuples of the shape(quantity, price).
    """
    
    def __init__(self, player_id, created_at, singlebid, callback= lambda *args: True):
        """
        
        Params:
            player_id: identifier of the player that created the bid
            created_at: a mark of the creation time, it can be time or a timeslot if using rounds
            singlebid: a tuple (quantity, price, buying), representing the bid of the player. 
            buying is a boolean
            The price is the price of 1 unit, not for the whole quantity.
            
        """
        super().__init__(player_id, created_at, callback)
        self.quantity = singlebid[0]
        self.price = singlebid[1]
        self.buying = singlebid[2]
    
    def __str__(self):
        action = 'buying' if self.buying else 'selling'
        s = f"Player {self.player_id} is {action} at time {self.created_at:03f} bidded quantity {self.quantity:03.1f} at price {self.price:03.1f}"
        return s
        

def sort_biding_list(bids, smallest_first=False):
    """
    Sorts the bid by price. The list is modified
    Params:
        bids: list of bids to sort
        smallest_first: True if the smallest item of the list has the smaller price
    Return:
        None
    """
    
    sorted_bids = sorted(bids, key=lambda bid: (bid.price, -bid.quantity), reverse= not smallest_first) 
    return sorted_bids


class SingleMarketResult(MarketResult):
    """
    Response of the market to a single bid
    """
    
    def __init__(self, player_id, created_at, traded_quantity, traded_price):
        """
        
        Params:
            player_id: identifier of the player that created the bid
            created_at: a mark of the creation time, it can be time or a timeslot if using rounds
            traded_quantity: quantity that was finally traded
            trading_price: the price at which it was traded. The price is the price of 1 unit, 
                not for the whole quantity.
            
        """
        super().__init__(player_id, created_at)
        self.quantity = traded_quantity
        self.price = traded_price