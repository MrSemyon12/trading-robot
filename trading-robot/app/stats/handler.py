from datetime import datetime
from typing import List

from client import TinkoffClient
# from stats.sqlite_client import StatsSQLiteClient
from stats.postgres_client import StatsPostgreSQLClient
from strategies.models import StrategyName


class StatsHandler:
    def __init__(self, strategy: StrategyName, broker_client: TinkoffClient):
        self.strategy = strategy
        # self.db = StatsSQLiteClient(db_name="stats.db")
        self.db = StatsPostgreSQLClient()
        self.broker_client = broker_client

    async def handle_open_order(self, figi, probability, price, quantity, time_utc) -> None:
        self.db.open_order(
            figi=figi,
            probability=probability,
            price=price,
            quantity=quantity,
            time_utc=time_utc
        )

    async def handle_close_orders(self, orders, last_price, stop_loss_percentage, take_profit_percentage) -> None:
        for order in orders:
            order_id, _, _, _, price, quantity, _ = order
            if (last_price - price) / price * 100 >= take_profit_percentage:
                await self.calculate_credit((last_price - price) * quantity)
                self.db.close_order(order_id=order_id)
            elif (price - last_price) / price * 100 >= stop_loss_percentage:
                await self.calculate_credit((last_price - price) * quantity)
                self.db.close_order(order_id=order_id)

    async def get_open_orders(self) -> List:
        return self.db.get_open_orders()

    async def calculate_credit(self, income: float):
        _, value_rub, _ = self.db.get_last_credit()
        self.db.add_credit(value_rub + income, datetime.utcnow())
