from enum import Enum, EnumMeta


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseStrEnum(str, Enum, metaclass=MetaEnum):
    pass


class Exchange(BaseStrEnum):
    BINANCE = "binance.com"
    BINANCE_TESTNET = "binance.com-testnet"
    BINANCE_MARGIN = "binance.com-margin"
    BINANCE_MARGIN_TESTNET = "binance.com-margin-testnet"
    BINANCE_ISOLATED_MARGIN = "binance.com-isolated_margin"
    BINANCE_ISOLATED_MARGIN_TESTNET = "binance.com-isolated_margin-testnet"
    BINANCE_FUTURES = "binance.com-futures"
    BINANCE_COIN_FUTURES = "binance.com-coin_futures"
    BINANCE_FUTURES_TESTNET = "binance.com-futures-testnet"
    BINANCE_US = "binance.us"
    TRBINANCE = "trbinance.com"
    BINANCE_ORG = "binance.org"
    BINANCE_ORG_TESTNET = "binance.org-testnet"