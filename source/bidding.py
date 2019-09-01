"""
Implementation of the bid class used by players to interact with the auctioneer
"""

class Bid:
    """
    Basic bid used by players to bid in the auction
    """
    
    def __init__(self, player_id, created_at, callback):
        """
        
        Params:
            player_id: identifier of the player that created the bid
            created_at: a mark of the creation time, it can be time or a timeslot if using rounds
            callback: function to call when the bid is resolved, usually after the market clears
            
        """
        self.player_id = player_id
        self.created_at = created_at
        self.callback = callback
        
    def setid(self, identifier):
        """
        Sets a unique identifier for the bid
        """
        self.id_ = identifier
        
        
class MarketResult:
    """
    Basic interface for returning market results
    """
    
    def __init__(self, player_id, created_at):
        """
        
        Params:
            player_id: identifier of the player that created the bid
            created_at: a mark of the creation time, it can be time or a timeslot if using rounds
            
        """
        self.player_id = player_id
        self.created_at = created_at
        