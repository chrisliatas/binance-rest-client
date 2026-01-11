# Example System Prompt Addition

## For LLM Agents: Binance REST Client Integration Instructions

When working with `binanceRestClient`, follow these critical patterns:

### 1. Environment Safety
- Default to `Exchange.BINANCE_TESTNET` unless user explicitly requests production.
- Avoid trading or wallet endpoints in production without explicit approval.

### 2. Mandatory Error Handling
- Most methods raise `BinanceAPIException` on non-2xx responses.
- Always wrap API calls with try/except.

```python
from binanceRestClient import BinanceRestClient, Exchange
from binanceRestClient.exceptions import BinanceAPIException

client = BinanceRestClient(exchange=Exchange.BINANCE_TESTNET)

try:
    info = client.get_exchange_info()
except BinanceAPIException as exc:
    print(f"API error: {exc}")
```

### 3. Required Imports and Setup
```python
import os
from binanceRestClient import BinanceRestClient, Exchange

client = BinanceRestClient(
    api_key=os.getenv("BINANCE_API_KEY"),
    api_secret=os.getenv("BINANCE_API_SECRET"),
    exchange=Exchange.BINANCE_TESTNET,
)
```

### 4. Signed Endpoint Rules
- Signed requests require `api_key` and `api_secret`.
- The client injects `timestamp` and `signature` automatically.
- Wallet endpoint `all_coins_info()` is signed.

### 5. User Data Stream
```python
listen_key = client.stream_listen_key()
client.stream_keepalive(listen_key)
client.stream_close(listen_key)
```

### 6. Requests Parameters
- Default timeout is 10 seconds.
- You can pass extra `requests` kwargs with `requests_params`.

```python
client = BinanceRestClient(
    requests_params={"proxies": {"https": "http://localhost:8080"}}
)
```

### 7. Async Klines (Multi-pair)
- Use `BinanceKlinesFetcher` for batch klines.
- Requires `aiohttp`.

```python
import asyncio
from binanceRestClient import BinanceKlinesFetcher

async def fetch():
    fetcher = BinanceKlinesFetcher(pairs=["ETH-USDT", "BTC-USDT"], interval="1m")
    return await fetcher.fetch_pairs_klines()

klines = asyncio.run(fetch())
```

### 8. Method Reference Categories
- **Market data**: `get_exchange_info`, `get_ticker`, `get_24hr_ticker`, `get_klines`
- **Order book**: `get_order_book`, `get_orderbook_tickers`
- **User data stream**: `stream_listen_key`, `stream_keepalive`, `stream_close`
- **Wallet**: `all_coins_info`
- **Utilities**: `req_weight_cost`, `get_server_time`, `ping`

### 9. Credential Handling
- Never hardcode API keys.
- Use environment variables or secrets store.
- You can override credentials per call using `api_key`/`api_secret` kwargs.

### 10. Use the Docs
Reference these files when generating code:
- `docs/BINANCE_INTEGRATION_GUIDE.md`
- `docs/examples.py`
- `docs/method_reference.py`
- `docs/api_reference.py`

Remember: This package is intentionally minimal. If an endpoint is missing,
add a method to `binanceRestClient/client.py` and update the docs.
