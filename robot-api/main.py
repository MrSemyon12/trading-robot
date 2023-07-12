import os
import psycopg2
from datetime import timedelta
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pandas import DataFrame
from ta.momentum import rsi, stoch, roc
from ta.trend import ema_indicator, macd
from ta.volatility import average_true_range
from tinkoff.invest import Client, CandleInterval
from tinkoff.invest.utils import now

from models import Order, Candle, Credit
from utils import quotation_to_float

from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title='Trading Robot')

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/candles', response_model=List[Candle])
def get_candles(max_len: int = 50, figi: str = "BBG0013HGFT4"):
    with Client(os.environ['TOKEN']) as client:
        candles = list(client.get_all_candles(
            figi=figi,
            from_=now() - timedelta(days=5),
            to=now(),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN
        ))

    if len(candles) < max_len:
        raise HTTPException(status_code=404, detail="Not enough candles")

    df = DataFrame([{
        'time': c.time.strftime('%H:%M:%S'),
        'volume': c.volume,
        'high': quotation_to_float(c.high),
        'low': quotation_to_float(c.low),
        'close': quotation_to_float(c.close),
    } for c in candles])

    df['ema'] = ema_indicator(close=df['close'], fillna=True)
    df['atr'] = average_true_range(
        high=df['high'], low=df['low'], close=df['close'], fillna=True)
    df['rsi'] = rsi(close=df['close'], fillna=True)
    df['stoch'] = stoch(high=df['high'], low=df['low'],
                        close=df['close'], fillna=True)
    df['roc'] = roc(close=df['close'], fillna=True)
    df['mcd'] = macd(close=df['close'], fillna=True)

    df = df.tail(max_len)
    return [
        Candle(
            time=row['time'],
            close=row['close'],
            ema=row['ema'],
            atr=row['atr'],
            rsi=row['rsi'],
            stoch=row['stoch'],
            roc=row['roc'],
            mcd=row['mcd'])
        for index, row in df.iterrows()
    ]


@app.get('/orders', response_model=List[Order])
def get_orders(limit: int = 10):
    orders = []
    with psycopg2.connect(
            host=os.environ['POSTGRES_HOST'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            database=os.environ['POSTGRES_DB']) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders ORDER BY time_utc DESC LIMIT %s", (limit,))
        for order in cursor.fetchall():
            orders.append(Order(id=order[0],
                                figi=order[1],
                                status=order[2],
                                probability=order[3],
                                price=order[4],
                                quantity=order[5],
                                time=order[6])
                          )

    return orders


@app.get('/credits', response_model=List[Credit])
def get_credits():
    credits = []
    with psycopg2.connect(
            host=os.environ['POSTGRES_HOST'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            database=os.environ['POSTGRES_DB']) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM credits")
        for credit in cursor.fetchall():
            credits.append(Credit(id=credit[0],
                                  value_rub=credit[1] - 1000000,
                                  time=credit[2])
                           )

    return credits
