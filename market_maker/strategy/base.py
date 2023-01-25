from abc import ABC

from market_maker.config import Config


class BaseStrategy(ABC):
    def __init__(self, config: Config):
        self.config = config

    def execute(self) -> None:
        pass
