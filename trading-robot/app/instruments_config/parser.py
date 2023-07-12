import os

from instruments_config.models import InstrumentsConfig

CONFIG_PATH = os.path.abspath(os.path.join(
    __file__, "../../../instruments_config.json"))


def get_instruments(filename: str = CONFIG_PATH) -> InstrumentsConfig:
    return InstrumentsConfig.parse_file(filename)


instruments_config = get_instruments()
