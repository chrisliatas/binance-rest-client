"""
Example usage patterns for common operations.

These are lightweight examples for LLM agents to adapt.
"""

import asyncio
import os
from typing import Any

from binanceRestClient import BinanceKlinesFetcher, BinanceRestClient, Exchange
from binanceRestClient.exceptions import BinanceAPIException


def example_public_market_data() -> dict[str, Any]:
    """Fetch public market data from testnet."""
    client = BinanceRestClient(exchange=Exchange.BINANCE_TESTNET)
    try:
        info = client.get_exchange_info()
        price = client.get_ticker(symbol="BTCUSDT")
        klines = client.get_klines(symbol="BTCUSDT", interval="1m", limit=10)
        return {
            "success": {
                "symbols": len(info.get("symbols", [])),
                "price": price,
                "klines": klines,
            }
        }
    except BinanceAPIException as exc:
        return {"error": str(exc)}


def example_env_based_setup() -> dict[str, Any]:
    """Initialize client from environment variables."""
    env = {
        "api_key": os.getenv("BINANCE_API_KEY"),
        "api_secret": os.getenv("BINANCE_API_SECRET"),
        "exchange": os.getenv("BINANCE_EXCHANGE", "BINANCE_TESTNET"),
    }
    if not env["api_key"] or not env["api_secret"]:
        return {"error": "Missing BINANCE_API_KEY or BINANCE_API_SECRET"}

    client = BinanceRestClient(
        api_key=env["api_key"],
        api_secret=env["api_secret"],
        exchange=Exchange[env["exchange"]],
    )

    try:
        listen_key = client.stream_listen_key()
        return {"success": {"listen_key": listen_key}}
    except BinanceAPIException as exc:
        return {"error": str(exc)}


def example_user_data_stream() -> dict[str, Any]:
    """Create, ping, and close a user data stream."""
    client = BinanceRestClient(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
        exchange=Exchange.BINANCE_TESTNET,
    )
    try:
        listen_key = client.stream_listen_key()
        client.stream_keepalive(listen_key)
        client.stream_close(listen_key)
        return {"success": True}
    except BinanceAPIException as exc:
        return {"error": str(exc)}


def example_wallet_info() -> dict[str, Any]:
    """Fetch wallet coin configuration (signed endpoint)."""
    client = BinanceRestClient(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
        exchange=Exchange.BINANCE,
    )
    try:
        coins = client.all_coins_info()
        return {"success": {"coins_count": len(coins)}}
    except BinanceAPIException as exc:
        return {"error": str(exc)}


def example_async_klines() -> dict[str, Any]:
    """Fetch klines for multiple pairs using async helper."""

    async def _run() -> dict[str, list[list[float]]]:
        fetcher = BinanceKlinesFetcher(pairs=["ETH-USDT", "BTC-USDT"], interval="1m")
        return await fetcher.fetch_pairs_klines()

    responses = asyncio.run(_run())
    return {"success": {"pairs": list(responses.keys())}}
