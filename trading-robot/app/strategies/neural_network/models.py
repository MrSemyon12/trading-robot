from enum import Enum

from pydantic import BaseModel, Field


class NeuralNetworkStrategyConfig(BaseModel):
    days_back_to_consider: int = Field(10, g=0)
    quantity_limit: int = Field(10, ge=0)
    check_interval: int = Field(60, g=0)
    stop_loss_percentage: float = Field(0.1, ge=0.0, le=1.0)
    take_profit_percentage: float = Field(0.1, ge=0.0, le=1.0)


class Signal(Enum):
    HOLD = 0
    BUY = 1
    SELL = 2
