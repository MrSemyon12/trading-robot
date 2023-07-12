import json
import math
import os
from datetime import timedelta
from typing import NamedTuple, List

import numpy as np
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from pandas import DataFrame
from tinkoff.invest import Quotation, CandleInterval
from tinkoff.invest.sandbox.client import Client
from tinkoff.invest.utils import now

from app.strategies.neural_network.models import Signal

load_dotenv()
TOKEN = os.environ['TOKEN']


class Pivot(NamedTuple):
    idx: int
    value: float
    signal: Signal


def cast_money(quotation: Quotation) -> float:
    return quotation.units + quotation.nano / 1e9


def load_candles() -> DataFrame:
    """max days = 150 for 15 minutes"""
    with Client(TOKEN) as client:
        candles = client.get_all_candles(
            figi='BBG0013HGFT4',
            from_=now() - timedelta(days=10),
            interval=CandleInterval.CANDLE_INTERVAL_15_MIN,
        )
        df = DataFrame([{
            'time': c.time,
            'volume': c.volume,
            'open': cast_money(c.open),
            'close': cast_money(c.close),
            'high': cast_money(c.high),
            'low': cast_money(c.low),
        } for c in candles])

    return df


def zig_zag(values: np.ndarray, delta: float) -> List[Pivot]:
    last = Pivot(0, values[0], Signal.HOLD)
    going_up = False
    going_down = False
    pivots = []

    for i in range(1, len(values)):
        cur = Pivot(i, values[i], Signal.HOLD)
        if cur.value - last.value >= delta:
            if going_down:
                pivots.append(Pivot(last.idx, last.value, Signal.BUY))
                going_down = False

            going_up = True
            last = cur

        elif last.value - cur.value >= delta:
            if going_up:
                pivots.append(Pivot(last.idx, last.value, Signal.SELL))
                going_up = False

            going_down = True
            last = cur

        elif cur.value > last.value and going_up or cur.value < last.value and going_down:
            last = cur

    if pivots[-1].idx != last.idx:
        pivots.append(Pivot(last.idx, last.value,
                            Signal.BUY if pivots[-1].signal == Signal.SELL else Signal.SELL))

    for i in range(1, len(pivots)):
        cur = pivots[i]
        prev = pivots[i - 1]
        new_idx = (cur.idx + prev.idx) // 2
        pivots.append(Pivot(new_idx, values[new_idx], Signal.HOLD))

    return pivots


def show_pivots(values: np.ndarray, pivots: List[Pivot]):
    plt.plot(values)
    for pivot in pivots:
        match pivot.signal:
            case Signal.SELL:
                plt.plot(pivot.idx, pivot.value, 'go', markersize=10)

            case Signal.BUY:
                plt.plot(pivot.idx, pivot.value, 'ro', markersize=10)

            case Signal.HOLD:
                plt.plot(pivot.idx, pivot.value, 'o',
                         color='orange', markersize=10)

    plt.title('Точки разворота тренда для пары USD/RUB')
    plt.grid(True)
    plt.legend()
    plt.show()


def write_to_json(data, filepath: str):
    jsn = json.dumps(data)
    with open(filepath, 'w') as file:
        json.dump(jsn, file)


def read_from_json(filepath: str) -> dict:
    with open(filepath, 'r') as file:
        data = json.load(file)
        data = json.loads(data)
    return data


def create_image(values: np.ndarray) -> np.ndarray:
    size = int(math.sqrt(len(values)))
    iterator = np.nditer(values)
    image = np.zeros((size, size), float)

    for cnt in range(size * 2 - 1, 0, -2):
        row, col = (cnt // 2, size - 1 - cnt // 2)
        image[row][col] = next(iterator)
        for step in range(1, cnt // 2 + 1):
            image[row][col + step] = next(iterator)
            image[row - step][col] = next(iterator)

    return image


def create_gaf(all_ts: np.ndarray, window_size: int) -> np.ndarray:
    rescaled_ts = np.zeros((window_size, window_size), float)
    min_ts, max_ts = np.min(all_ts), np.max(all_ts)
    diff = max_ts - min_ts
    if diff != 0:
        rescaled_ts = (all_ts - min_ts) / diff
    else:
        return np.zeros((1, window_size, window_size), float)

    this_gam = np.zeros((1, window_size, window_size), float)
    sin_ts = np.sqrt(np.clip(1 - rescaled_ts ** 2, 0, 1))

    this_gam[0] = np.outer(rescaled_ts, rescaled_ts) - np.outer(sin_ts, sin_ts)

    return this_gam


def create_df(values: np.ndarray, pivots: list, image_size: int) -> list:
    return [{
        "signal": pivot.signal.value,
        "history": values[pivot.idx - image_size ** 2 + 1:pivot.idx + 1].tolist()
    } for pivot in pivots if pivot.idx >= image_size ** 2]


def main():
    signal = Signal.BUY

    print(signal == signal.BUY)
    # candles = load_candles()
    #
    # pivots = zig_zag(candles['close'].values, 0.4)
    # show_pivots(candles['close'].values, pivots)

    # df = create_df(candles['close'].values, pivots, 5)
    #
    # image = create_gaf(df[0]['history'], 5)
    # print(image)

    # write_to_json(df, 'USDRUB.json')
    # read_from_json('USDRUB.json')

    # plt.plot(candles['close'].values)
    # plt.show()

    return 0


if __name__ == '__main__':
    main()
