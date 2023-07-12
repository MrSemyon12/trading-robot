import os
from typing import NamedTuple

from dotenv import load_dotenv

load_dotenv()


class Settings(NamedTuple):
    token: str = os.environ['TOKEN']
    account_id: str = os.environ['ACCOUNT_ID']
    sandbox: bool = True


settings = Settings()
