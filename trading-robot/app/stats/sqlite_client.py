from datetime import datetime

from sqlite.client import SQLiteClient


class StatsSQLiteClient:
    def __init__(self, db_name: str):
        self.db_client = SQLiteClient(db_name)
        self.db_client.connect()
        self._create_tables()

    def _create_tables(self):
        self.db_client.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                figi str,
                status str,
                probability REAL,
                price REAL,
                quantity int,
                time_utc TIME
            )
            """
        )
        self.db_client.execute(
            """
            CREATE TABLE IF NOT EXISTS credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value_rub REAL,
                time_utc TIME
            )
            """
        )
        # self.db_client.execute_insert(
        #     "INSERT INTO credits (value_rub, time_utc) VALUES (?, ?)", (1000000, datetime.utcnow())
        # )

    def open_order(
            self,
            figi: str,
            probability: float,
            price: float,
            quantity: int,
            time_utc: datetime
    ):
        self.db_client.execute_insert(
            "INSERT INTO orders (figi, status, probability, price, quantity, time_utc) VALUES (?, ?, ?, ?, ?, ?)",
            (figi, "OPEN", probability, price, quantity, time_utc),
        )

    def get_open_orders(self):
        return self.db_client.execute_select("SELECT * FROM orders WHERE status='OPEN'")

    def add_credit(self, value_rub: float, time_utc: datetime):
        self.db_client.execute_insert(
            "INSERT INTO credits (value_rub, time_utc) VALUES (?, ?)",
            (value_rub, time_utc),
        )

    def get_last_credit(self):
        return self.db_client.execute_select("SELECT * FROM credits")[-1]

    def close_order(self, order_id: int):
        self.db_client.execute_update(
            "UPDATE orders SET status=? WHERE id=?",
            ("CLOSE", order_id),
        )
