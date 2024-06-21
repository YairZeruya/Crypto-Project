from enums import TradeStatus

class Trade:
    _next_id: int = 0

    def __init__(self, symbol: str, cost: int, start_time: str, bot_name: str, start_price: str):
        print("Initializing Trade object")
        self.id: int = Trade._next_id
        Trade._next_id += 1
        
        self.bot_name: str = bot_name
        self.symbol: str = symbol
        self.cost: int = cost
        self.start_time: str = start_time
        self.start_price : str = start_price
        self.profit: str = 0.0
        self.end_time: str = None
        self.status: int = TradeStatus.open.value
        print("Trade object initialized successfully")

    def to_dict(self):
        return {
            "id": self.id,
            "bot_name": self.bot_name,
            "symbol": self.symbol,
            "cost": self.cost,
            "start_time": self.start_time,
            "profit": self.profit,
            "end_time": self.end_time,
            "status": self.status,
            "start_price" : self.start_price
        }
