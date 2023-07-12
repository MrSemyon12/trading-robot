from pydantic import BaseModel
from datetime import datetime


class Candle(BaseModel):
    time: str
    close: float
    ema: float
    atr: float
    rsi: float
    stoch: float
    roc: float
    mcd: float


class Credit(BaseModel):
    id: int
    value_rub: float
    time: datetime


class Order(BaseModel):
    id: int
    figi: str
    status: str
    probability: float
    price: float
    quantity: int
    time: datetime
