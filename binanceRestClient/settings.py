from dataclasses import dataclass

from binanceRestClient.enums import Exchange


@dataclass
class ExchangeSettings:
    ws_max_connections: int
    api_base_uri: str
    ws_base_uri: str
    ws_api_base_uri: str
    exchange_type: str


EXCHANGE_SETTINGS = {
    Exchange.BINANCE: ExchangeSettings(
        1024,
        "https://api.binance.com/api",
        "wss://stream.binance.com:9443/",
        "wss://ws-api.binance.com/ws-api/v3",
        "CEX",
    ),
    Exchange.BINANCE_TESTNET: ExchangeSettings(
        1024,
        "https://testnet.binance.vision/api",
        "wss://testnet.binance.vision/",
        "wss://testnet.binance.vision/ws-api/v3",
        "CEX",
    ),
    Exchange.BINANCE_WALLET: ExchangeSettings(
        0,
        "https://api.binance.com/sapi",
        "",
        "",
        "CEX",
    ),
    Exchange.BINANCE_MARGIN: ExchangeSettings(
        1024, "https://api.binance.com/api", "wss://stream.binance.com:9443/", "", "CEX"
    ),
    Exchange.BINANCE_MARGIN_TESTNET: ExchangeSettings(
        1024,
        "https://testnet.binance.vision/api",
        "wss://testnet.binance.vision/",
        "",
        "CEX",
    ),
    Exchange.BINANCE_ISOLATED_MARGIN: ExchangeSettings(
        1024, "https://api.binance.com/api", "wss://stream.binance.com:9443/", "", "CEX"
    ),
    Exchange.BINANCE_ISOLATED_MARGIN_TESTNET: ExchangeSettings(
        1024,
        "https://testnet.binance.vision/api",
        "wss://testnet.binance.vision/",
        "",
        "CEX",
    ),
    Exchange.BINANCE_FUTURES: ExchangeSettings(
        200, "https://api.binance.com/api", "wss://fstream.binance.com/", "", "CEX"
    ),
    Exchange.BINANCE_COIN_FUTURES: ExchangeSettings(
        200, "https://api.binance.com/api", "wss://dstream.binance.com/", "", "CEX"
    ),
    Exchange.BINANCE_FUTURES_TESTNET: ExchangeSettings(
        200,
        "https://testnet.binancefuture.com/fapi",
        "wss://stream.binancefuture.com/",
        "",
        "CEX",
    ),
    Exchange.BINANCE_US: ExchangeSettings(
        1024, "https://api.binance.us/api", "wss://stream.binance.us:9443/", "", "CEX"
    ),
    Exchange.TRBINANCE: ExchangeSettings(
        1024,
        "https://www.trbinance.com/api",
        "wss://stream-cloud.trbinance.com/",
        "",
        "CEX",
    ),
    Exchange.BINANCE_ORG: ExchangeSettings(
        1024, "", "wss://dex.binance.org/api/", "", "DEX"
    ),
    Exchange.BINANCE_ORG_TESTNET: ExchangeSettings(
        1024, "", "wss://testnet-dex.binance.org/api/", "", "DEX"
    ),
}
