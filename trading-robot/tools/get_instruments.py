import os
from typing import NamedTuple

from dotenv import load_dotenv
from tinkoff.invest import Client, InstrumentStatus

load_dotenv()


class Settings(NamedTuple):
    token: str = os.environ['TOKEN']


settings = Settings()


def get_instruments():
    with Client(settings.token) as client:
        return client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments


def get_currencies():
    with Client(settings.token) as client:
        return client.instruments.currencies(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments


if __name__ == "__main__":
    instruments = get_currencies()
    for instrument in instruments:
        print(f"name: {instrument.name}, figi: {instrument.figi}, ticker: {instrument.ticker}")
