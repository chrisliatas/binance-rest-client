# Binance REST Client Integration Guide

## Purpose

This package provides a small, opinionated wrapper around a subset of the Binance
REST API. It is best suited for:

- Market data lookups (tickers, klines, order book)
- User data stream listen keys
- Wallet coin configuration (`all_coins_info`)

It is **not** a full trading client. If you need missing endpoints, add methods
in `binanceRestClient/client.py` using the existing `_get/_post/_put/_delete` helpers.

## Quick Start

```python
import os
from binanceRestClient import BinanceRestClient, Exchange

client = BinanceRestClient(
    api_key=os.getenv("BINANCE_API_KEY"),
    api_secret=os.getenv("BINANCE_API_SECRET"),
    exchange=Exchange.BINANCE_TESTNET,
)

print(client.ping())
print(client.get_server_time())
```

## Authentication and Environments

- Use `Exchange.BINANCE_TESTNET` by default for development.
- Use `Exchange.BINANCE` or `Exchange.BINANCE_US` only for production.
- Signed endpoints require both `api_key` and `api_secret`.
- Public endpoints do **not** require auth, but the client always sends
  `X-MBX-APIKEY` if `api_key` is set.

Supported exchanges (subset):

- `Exchange.BINANCE`, `Exchange.BINANCE_TESTNET`
- `Exchange.BINANCE_US`
- Other exchange values exist in `binanceRestClient.enums.Exchange`

## Error Handling Patterns

The client raises exceptions for non-2xx responses by default:

- `BinanceAPIException` for HTTP errors
- `BinanceRequestException` for invalid JSON
- `AlreadyStoppedError` if you use a stopped instance

Example:

```python
from binanceRestClient import BinanceRestClient, Exchange
from binanceRestClient.exceptions import BinanceAPIException

client = BinanceRestClient(exchange=Exchange.BINANCE_TESTNET)

try:
    info = client.get_exchange_info()
except BinanceAPIException as exc:
    print(f"HTTP error: {exc}")
```

If you want to suppress HTTP exceptions, pass `throw_exception=False` on supported
methods (user data stream methods).

## Request Behavior and Parameters

- Default timeout is **10 seconds** for all requests.
- Extra `requests` parameters can be passed via `requests_params` in the constructor
  or via `requests_params` inside `data`.
- You can override credentials **per call** by passing `api_key` and `api_secret`
  in the method kwargs. This resets the session.

## Market Data

Common endpoints:

- `get_exchange_info()`
- `get_ticker(symbol="BTCUSDT")` or `get_all_tickers()`
- `get_24hr_ticker(symbol="BTCUSDT")`
- `get_order_book(symbol="BTCUSDT", limit=100)`
- `get_klines(symbol="BTCUSDT", interval="1m", limit=100)`

Example:

```python
prices = client.get_ticker(symbol="BTCUSDT")
book = client.get_order_book(symbol="BTCUSDT", limit=10)
```

## User Data Stream (Listen Keys)

This client supports listen key management (Spot user data stream):

- `stream_listen_key()` -> returns a listen key string
- `stream_keepalive(listenKey)` -> keepalive ping
- `stream_close(listenKey)` -> close stream

Example:

```python
listen_key = client.stream_listen_key()
client.stream_keepalive(listen_key)
client.stream_close(listen_key)
```

## Wallet Endpoint

`all_coins_info()` calls the Wallet API (`/sapi/v1/capital/config/getall`).
It is a signed endpoint and requires API credentials.

```python
coins = client.all_coins_info()
```

## Async Klines Fetcher

For multi-pair kline retrieval, use `BinanceKlinesFetcher`:

```python
import asyncio
from binanceRestClient import BinanceKlinesFetcher

async def fetch():
    fetcher = BinanceKlinesFetcher(pairs=["ETH-USDT", "BTC-USDT"], interval="1m")
    return await fetcher.fetch_pairs_klines()

klines = asyncio.run(fetch())
```

Notes:
- Requires `aiohttp` (not listed in `pyproject.toml`).
- Pairs are normalized by removing `-` for the API call.
- `fill_missing_pairs()` uses `ETH-USDT` as a base for reconstruction.

## Rate Limits and Weight

After a request, you can read the last weight cost:

```python
weights = client.req_weight_cost()
# {'weight': '123', 'timestamp': 1699999999.0, 'status_code': 200}
```

If you want to refresh the weight with a new request, call:

```python
client.req_weight_cost(new_req=True)
```

## Developer Onboarding

- Install: `poetry install`
- Run tests: `poetry run pytest` (install `pytest` if missing)
- Python: `^3.11`

## Adding New Endpoints

Pattern:

```python
def get_account_info(self) -> dict:
    return self._get("account", signed=True, data={})
```

After adding, update:
- `docs/method_reference.py`
- `docs/examples.py`
- `docs/README.md` if needed

## Safety Checklist for LLM Agents

- Default to testnet unless user explicitly requests prod.
- Never embed API keys in code.
- Use try/except around all requests that can raise `BinanceAPIException`.
- Avoid long-running loops without rate limiting.
