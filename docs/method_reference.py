"""
Structured method reference for LLM consumption.
Provides signatures, descriptions, and examples.
"""

from typing import Any, Dict

METHOD_SIGNATURES: Dict[str, Any] = {
    "BinanceRestClient": {
        "initialization": {
            "signature": "BinanceRestClient(api_key: str | None = None, api_secret: str | None = None, requests_params: dict | None = None, exchange: str | None = Exchange.BINANCE, debug: bool = False) -> None",
            "required_imports": [
                "from binanceRestClient import BinanceRestClient, Exchange"
            ],
            "example": "client = BinanceRestClient(exchange=Exchange.BINANCE_TESTNET)",
            "description": "Initialize the synchronous Binance REST client",
            "parameters": {
                "api_key": "API key string (optional for public endpoints)",
                "api_secret": "API secret string (required for signed endpoints)",
                "requests_params": "Optional requests kwargs (proxies, timeout, etc)",
                "exchange": "Exchange enum or string, e.g., Exchange.BINANCE_TESTNET",
                "debug": "Enable debug flag (stored on instance)",
            },
        },
        "market_data": {
            "get_exchange_info": {
                "signature": "get_exchange_info(**params) -> dict",
                "description": "Exchange rules and symbol information",
                "example": "info = client.get_exchange_info()",
            },
            "get_symbol_info": {
                "signature": "get_symbol_info(symbol: str) -> dict | None",
                "description": "Single symbol info from exchangeInfo",
                "example": "btc = client.get_symbol_info('BTCUSDT')",
            },
            "ping": {
                "signature": "ping() -> bool",
                "description": "Test REST API connectivity",
                "example": "ok = client.ping()",
            },
            "get_server_time": {
                "signature": "get_server_time() -> int",
                "description": "Server time in milliseconds",
                "example": "server_ms = client.get_server_time()",
            },
            "get_ticker": {
                "signature": "get_ticker(**params) -> dict | list",
                "description": "Latest price for a symbol or symbols",
                "example": "price = client.get_ticker(symbol='BTCUSDT')",
            },
            "get_all_tickers": {
                "signature": "get_all_tickers() -> list[dict]",
                "description": "Latest price for all symbols",
                "example": "prices = client.get_all_tickers()",
            },
            "get_24hr_ticker": {
                "signature": "get_24hr_ticker(**params) -> dict",
                "description": "24 hour ticker statistics",
                "example": "stats = client.get_24hr_ticker(symbol='BTCUSDT')",
            },
            "get_orderbook_tickers": {
                "signature": "get_orderbook_tickers() -> dict",
                "description": "Best bid/ask for all symbols",
                "example": "book = client.get_orderbook_tickers()",
            },
            "get_rol_w_price": {
                "signature": "get_rol_w_price(**params) -> dict",
                "description": "Rolling window price change statistics",
                "example": "roll = client.get_rol_w_price(symbol='BTCUSDT', windowSize='1h')",
            },
            "get_order_book": {
                "signature": "get_order_book(**params) -> dict",
                "description": "Order book depth for a symbol",
                "example": "book = client.get_order_book(symbol='BTCUSDT', limit=10)",
            },
            "get_historical_trades": {
                "signature": "get_historical_trades(**params) -> dict",
                "description": "Older market trades",
                "example": "trades = client.get_historical_trades(symbol='BTCUSDT', limit=100)",
            },
            "get_klines": {
                "signature": "get_klines(**params) -> list[list[str]]",
                "description": "Candlestick/kline data for a symbol",
                "example": "klines = client.get_klines(symbol='BTCUSDT', interval='1m')",
            },
        },
        "user_data_stream": {
            "stream_listen_key": {
                "signature": "stream_listen_key(output: str = 'listenKey', throw_exception: bool = True, **kwargs) -> dict | str",
                "description": "Create a user data stream and return a listen key",
                "example": "listen_key = client.stream_listen_key()",
                "parameters": {
                    "output": "'listenKey' for string or 'response' for full response",
                    "throw_exception": "Raise on non-2xx when True",
                },
            },
            "stream_keepalive": {
                "signature": "stream_keepalive(listenKey: str, throw_exception: bool = True, **kwargs) -> dict",
                "description": "Keepalive a listen key",
                "example": "client.stream_keepalive(listen_key)",
            },
            "stream_close": {
                "signature": "stream_close(listenKey: str, throw_exception: bool = True, **kwargs) -> dict",
                "description": "Close a listen key",
                "example": "client.stream_close(listen_key)",
            },
        },
        "wallet": {
            "all_coins_info": {
                "signature": "all_coins_info() -> list[dict] | dict",
                "description": "Wallet API: get all coin information",
                "example": "coins = client.all_coins_info()",
            },
        },
        "utilities": {
            "req_weight_cost": {
                "signature": "req_weight_cost(new_req: bool = False) -> dict",
                "description": "Read the weight cost of the last request",
                "example": "weights = client.req_weight_cost()",
            },
            "stop": {
                "signature": "stop() -> bool",
                "description": "Stop the client and close session",
                "example": "client.stop()",
            },
        },
        "notes": {
            "per_call_credentials": "You can pass api_key/api_secret in kwargs to override credentials for a single call.",
            "timeout": "All requests default to 10 seconds unless overridden via requests_params.",
        },
    },
    "BinanceKlinesFetcher": {
        "initialization": {
            "signature": "BinanceKlinesFetcher(pairs: list[str], interval: str = '1s', fromTime: int | None = 0, toTime: int | None = 0, n_mins: float | None = 5.0, pair_retries: int = 3, pair_timeout: int | None = None, init_backoff: float = 1.0, logger: logging.Logger | None = None)",
            "required_imports": ["from binanceRestClient import BinanceKlinesFetcher"],
            "example": "fetcher = BinanceKlinesFetcher(pairs=['ETH-USDT', 'BTC-USDT'], interval='1m')",
            "description": "Async kline fetcher for multiple pairs",
        },
        "methods": {
            "fetch_pairs_klines": {
                "signature": "fetch_pairs_klines() -> dict[str, list[list[float]]]",
                "description": "Fetch klines for all pairs asynchronously",
                "example": "responses = await fetcher.fetch_pairs_klines()",
            },
            "fetch_and_fill_klines": {
                "signature": "fetch_and_fill_klines() -> dict[str, list[list[float]]]",
                "description": "Fetch and fill missing pairs using ETH-USDT as base",
                "example": "responses = await fetcher.fetch_and_fill_klines()",
            },
            "fill_missing_pairs": {
                "signature": "fill_missing_pairs() -> None",
                "description": "Fill missing pairs by combining with ETH-USDT",
                "example": "fetcher.fill_missing_pairs()",
            },
        },
    },
}
