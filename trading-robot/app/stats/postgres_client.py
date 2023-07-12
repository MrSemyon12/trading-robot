from datetime import datetime

from postgresql.client import PostgreSQLClient


class StatsPostgreSQLClient:
    def __init__(self):
        self.db_client = PostgreSQLClient()
        self.db_client.connect()
        self._create_tables()

    def _create_tables(self):
        self.db_client.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                figi TEXT,
                status TEXT,
                probability REAL,
                price REAL,
                quantity INTEGER,
                time_utc TIMESTAMP
            );
            """
        )
        self.db_client.execute(
            """
            CREATE TABLE IF NOT EXISTS credits (
                id SERIAL PRIMARY KEY,
                value_rub REAL,
                time_utc TIMESTAMP
            );

            INSERT INTO credits (value_rub, time_utc)
            SELECT 1000000, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM credits);
            """
        )

    def open_order(
            self,
            figi: str,
            probability: float,
            price: float,
            quantity: int,
            time_utc: datetime
    ):
        self.db_client.execute_insert(
            "INSERT INTO orders (figi, status, probability, price, quantity, time_utc) VALUES (%s, %s, %s, %s, %s, %s)",
            (figi, "OPEN", probability, price, quantity, time_utc),
        )

    def get_open_orders(self):
        return self.db_client.execute_select("SELECT * FROM orders WHERE status='OPEN'")

    def add_credit(self, value_rub: float, time_utc: datetime):
        self.db_client.execute_insert(
            "INSERT INTO credits (value_rub, time_utc) VALUES (%s, %s)",
            (value_rub, time_utc),
        )

    def get_last_credit(self):
        return self.db_client.execute_select("SELECT * FROM credits")[-1]

    def close_order(self, order_id: int):
        self.db_client.execute_update(
            "UPDATE orders SET status=%s WHERE id=%s",
            ("CLOSE", order_id),
        )
