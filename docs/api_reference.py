"""
Binance REST Client - API Reference for LLM Integration

This file provides common usage patterns and snippets for `binanceRestClient`.
Use it as context for LLM agents working on integration tasks.
"""

from typing import Any

from binanceRestClient import BinanceKlinesFetcher, BinanceRestClient, Exchange
from binanceRestClient.exceptions import BinanceAPIException


class BinanceIntegrationPatterns:
    """Essential patterns for LLM agents working with binanceRestClient."""

    @staticmethod
    def basic_client_setup() -> str:
        return """
        import os
        from binanceRestClient import BinanceRestClient, Exchange

        client = BinanceRestClient(
            api_key=os.getenv("BINANCE_API_KEY"),
            api_secret=os.getenv("BINANCE_API_SECRET"),
            exchange=Exchange.BINANCE_TESTNET,
        )
        """

    @staticmethod
    def market_data_pattern() -> str:
        return """
        from binanceRestClient.exceptions import BinanceAPIException

        try:
            prices = client.get_ticker(symbol="BTCUSDT")
            klines = client.get_klines(symbol="BTCUSDT", interval="1m", limit=100)
        except BinanceAPIException as exc:
            print(f"API error: {exc}")
        """

    @staticmethod
    def signed_wallet_pattern() -> str:
        return """
        # Wallet endpoint - requires api_key and api_secret
        try:
            coins = client.all_coins_info()
        except BinanceAPIException as exc:
            print(f"Wallet error: {exc}")
        """

    @staticmethod
    def user_data_stream_pattern() -> str:
        return """
        # Spot user data stream listen key
        listen_key = client.stream_listen_key()
        client.stream_keepalive(listen_key)
        client.stream_close(listen_key)
        """

    @staticmethod
    def request_params_pattern() -> str:
        return """
        # Pass custom requests params via constructor
        client = BinanceRestClient(
            requests_params={"timeout": 20, "proxies": {"https": "http://proxy"}}
        )
        """

    @staticmethod
    def weight_cost_pattern() -> str:
        return """
        # Weight cost for the last request
        client.get_exchange_info()
        weights = client.req_weight_cost()
        print(weights)
        """

    @staticmethod
    def async_klines_pattern() -> str:
        return """
        import asyncio
        from binanceRestClient import BinanceKlinesFetcher

        async def fetch():
            fetcher = BinanceKlinesFetcher(pairs=["ETH-USDT", "BTC-USDT"], interval="1m")
            return await fetcher.fetch_pairs_klines()

        klines = asyncio.run(fetch())
        """


def safe_get_exchange_info(client: BinanceRestClient) -> dict[str, Any] | None:
    """Example helper to wrap a call that may raise BinanceAPIException."""
    try:
        return client.get_exchange_info()
    except BinanceAPIException:
        return None


__all__ = ["BinanceIntegrationPatterns", "safe_get_exchange_info"]
