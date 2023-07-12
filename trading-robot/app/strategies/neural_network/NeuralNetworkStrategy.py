import asyncio
import logging
from datetime import timedelta
from typing import List, Optional

from tinkoff.invest import CandleInterval, HistoricCandle, AioRequestError
from tinkoff.invest.utils import now

from client import client
from settings import settings
from stats.handler import StatsHandler
from strategies.base import BaseStrategy
from strategies.models import StrategyName
from strategies.neural_network.models import NeuralNetworkStrategyConfig, Signal
from strategies.neural_network.predictor import predictor
from utils.quotation import quotation_to_float

logger = logging.getLogger(__name__)


class NeuralNetworkStrategy(BaseStrategy):

    def __init__(self, figi: str, **kwargs):
        self.account_id = settings.account_id
        self.signal: Optional[tuple[Signal, float]] = None
        self.figi = figi
        self.config: NeuralNetworkStrategyConfig = NeuralNetworkStrategyConfig(
            **kwargs)
        self.stats_handler = StatsHandler(StrategyName.NEURAL_NETWORK, client)

    async def get_historical_data(self) -> List[HistoricCandle]:
        candles = []
        logger.debug(
            f"Start getting historical data for {self.config.days_back_to_consider} "
            f"days back from now. figi={self.figi}"
        )
        async for candle in client.get_all_candles(
                figi=self.figi,
                from_=now() - timedelta(days=self.config.days_back_to_consider),
                to=now(),
                interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            candles.append(candle)
        logger.debug(f"Found {len(candles)} candles. figi={self.figi}")
        return candles

    async def update_signal(self, candles) -> None:
        if len(candles) < 32:
            return
        values = list(
            map(lambda x: quotation_to_float(x.close), candles))[-32:]
        self.signal = predictor.predict(values)

    async def handle_close(self, last_price: float) -> None:
        orders = await self.stats_handler.get_open_orders()
        if len(orders) == 0:
            return

        logger.info(
            f"Found {len(orders)} open orders. Validating SL/TP"
        )
        asyncio.create_task(
            self.stats_handler.handle_close_orders(orders=orders, last_price=last_price,
                                                   stop_loss_percentage=self.config.stop_loss_percentage,
                                                   take_profit_percentage=self.config.take_profit_percentage)
        )

    async def handle_open(self, last_candle: HistoricCandle) -> None:
        logger.info(
            f"{'Buying' if self.signal[0] == Signal.BUY else 'Selling'} {self.config.quantity_limit} shares"
        )
        asyncio.create_task(
            self.stats_handler.handle_open_order(
                figi=self.figi,
                probability=self.signal[1],
                price=quotation_to_float(last_candle.close),
                quantity=self.config.quantity_limit,
                time_utc=last_candle.time
            )
        )

    async def ensure_market_open(self):
        trading_status = await client.get_trading_status(figi=self.figi)
        while not (
                trading_status.market_order_available_flag and trading_status.api_trade_available_flag
        ):
            logger.debug(f"Waiting for the market to open. figi={self.figi}")
            await asyncio.sleep(60)
            trading_status = await client.get_trading_status(figi=self.figi)

    async def main_cycle(self):
        while True:
            try:
                await self.ensure_market_open()
                candles = await self.get_historical_data()
                await self.update_signal(candles)

                last_candle = candles[-1]
                last_price = quotation_to_float(last_candle.close)

                await self.handle_close(last_price)

                logger.debug(
                    f"Last price {last_price} signal {self.signal[0].name} {self.signal[1]} % figi={self.figi}"
                )

                if self.signal and self.signal[0] != Signal.HOLD:
                    await self.handle_open(last_candle)

            except AioRequestError as are:
                logger.error(f"Client error {are}")

            await asyncio.sleep(self.config.check_interval)

    async def start(self):
        if self.account_id is None:
            try:
                self.account_id = (await client.get_accounts()).accounts.pop().id
            except AioRequestError as are:
                logger.error(
                    f"Error taking account id. Stopping strategy. {are}")
                return
        await self.main_cycle()
