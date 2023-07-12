from typing import Dict

from strategies.base import BaseStrategy
from strategies.errors import UnsupportedStrategyError
from strategies.models import StrategyName
from strategies.neural_network.NeuralNetworkStrategy import NeuralNetworkStrategy

strategies: Dict[StrategyName, BaseStrategy.__class__] = {
    StrategyName.NEURAL_NETWORK: NeuralNetworkStrategy,
}


def resolve_strategy(strategy_name: StrategyName, figi: str, *args, **kwargs) -> BaseStrategy:
    if strategy_name not in strategies:
        raise UnsupportedStrategyError(strategy_name)
    return strategies[strategy_name](figi=figi, *args, **kwargs)
