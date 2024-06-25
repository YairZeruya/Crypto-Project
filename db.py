import sqlite3
from threading import local

class DB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.local = local()  # Thread-local storage for SQLite connection

    def get_connection(self):
        # Check if there's already a connection for this thread
        if not hasattr(self.local, 'conn'):
            # Create a new SQLite connection for this thread
            self.local.conn = sqlite3.connect(self.db_name)
            self.create_trades_table()  # Ensure trades table exists in this connection

        return self.local.conn

    def create_trades_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                strategy TEXT,
                start_time TEXT,
                end_time TEXT DEFAULT NULL,
                cost INTEGER,
                start_price REAL DEFAULT NULL,
                end_price REAL DEFAULT NULL,
                return REAL DEFAULT 0
            )
        ''')
        conn.commit()

    def save_trade(self, trade, start_price):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades (symbol, strategy, start_time, cost, start_price)
            VALUES (?, ?, ?, ?, ?)
        ''', (trade.symbol, trade.bot_name, trade.start_time, trade.cost, start_price))
        conn.commit()
        print("Trade saved successfully")

    def update_trade(self, trade_id, end_price, end_time, return_value):
        conn = self.get_connection()
        cursor = conn.cursor()
        print(trade_id,end_price,end_time,return_value)
        cursor.execute('''
                UPDATE trades 
                SET end_price=?, end_time=?, "return"=?
                WHERE id=?
            ''', (end_price, end_time, return_value, trade_id))
        conn.commit()
        print(f"Trade with ID {trade_id} updated successfully")
        print(f'updated trade from db: {DB.get_trade_by_id(self,trade_id=trade_id)}')


    def get_trade_by_id(self, trade_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM trades WHERE id=?
        ''', (trade_id,))
        trade_data = cursor.fetchone()
        if trade_data:
            return {
                "id": trade_data[0],
                "symbol": trade_data[1],
                "strategy": trade_data[2],
                "start_time": trade_data[3],
                "end_time": trade_data[4],
                "cost": trade_data[5],
                "start_price": trade_data[6],
                "end_price": trade_data[7],
                "return": trade_data[8]
            }
        else:
            return None

    def close_connection(self):
        if hasattr(self.local, 'conn'):
            self.local.conn.close()
            del self.local.conn
