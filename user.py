
class User:
    _next_id : int = 0

    def __init__(self):
        self.id : int = User._next_id
        _next_id += 1
        self.money : int = 1000
        self.trades : list = []
        self.total_profit : float = 0.0