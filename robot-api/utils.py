import os
from datetime import timedelta
from typing import Union

from tinkoff.invest import Quotation, MoneyValue, Client, CandleInterval
from tinkoff.invest.utils import now


def quotation_to_float(quotation: Union[Quotation, MoneyValue]) -> float:
    return float(quotation.units + quotation.nano / 1e9)


def test_connection():
    with Client(os.environ['TOKEN']) as client:
        candles = client.get_all_candles(
            figi="BBG0013HGFT4",
            from_=now() - timedelta(days=2),
            to=now(),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN
        )
        print(list(candles))
