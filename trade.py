from enums import TradeStatus

class Trade:
    _next_id: int = 0

    def __init__(self, id: int, symbol: str, cost: int, start_time: str, bot_name: str, start_price: str):
        print("Initializing Trade object")
        self.id: int = id
        self.bot_name: str = bot_name
        self.symbol: str = symbol
        self.cost: int = cost
        self.start_time: str = start_time
        self.start_price: str = start_price
        self.end_price: str = 0.0
        self.profit: str = 0.0
        self.end_time: str = None
        self.status: int = TradeStatus.open.value
        print("Trade object initialized successfully")

    @staticmethod
    def generate_id():
        trade_id = Trade._next_id
        Trade._next_id += 1
        return trade_id

    @classmethod
    def create_trade(cls, symbol: str, cost: int, start_time: str, bot_name: str, start_price: str):
        trade_id = cls.generate_id()
        return cls(trade_id, symbol, cost, start_time, bot_name, start_price)

    # @staticmethod
    # def get_trade_by_id(trade_id: int, db):
    #     trade_data = db.get_trade_by_id(trade_id)
    #     if trade_data:
    #         return Trade(
    #             trade_data["id"],
    #             trade_data["symbol"],
    #             trade_data["cost"],
    #             trade_data["start_time"],
    #             trade_data["strategy"],
    #             trade_data["start_price"]
    #         )
    #     else:
    #         return None

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
            "start_price": self.start_price
        }
