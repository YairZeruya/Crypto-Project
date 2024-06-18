from enums import TradeStatus

class Trade:
    _next_id : int = 0

    def init(self,symbol,duration,cost,start_time,user_id):
        self.id : int = Trade._next_id
        _next_id += 1

        self.symbol : str = symbol
        self.duration : str = duration
        self.cost : str = cost
        self.start_time : str = start_time
        self.user_id : int = user_id
        
        self.profit : str = 0.0
        self.end_time : str = None
        self.status : int = TradeStatus.open.value

