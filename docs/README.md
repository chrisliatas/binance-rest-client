# Documentation Index

This directory contains documentation for integrating `binanceRestClient` with LLM agents and external projects.

## Files Overview

### Core Documentation

- **[BINANCE_INTEGRATION_GUIDE.md](BINANCE_INTEGRATION_GUIDE.md)** - Full integration guide with patterns and safety notes
- **[example_prompt.md](example_prompt.md)** - System prompt template for LLM agents
- **[api_reference.py](api_reference.py)** - API usage patterns and snippets
- **[method_reference.py](method_reference.py)** - Structured method signatures and metadata
- **[examples.py](examples.py)** - Concrete usage examples

## Quick Start for LLM Integration

Use these files in order:

1. **Start with**: `example_prompt.md` - Add to the system prompt
2. **Reference**: `BINANCE_INTEGRATION_GUIDE.md` - Comprehensive patterns
3. **Examples**: `examples.py` - Copy/paste ready code
4. **Method lookup**: `method_reference.py` - Exact method signatures
5. **Patterns**: `api_reference.py` - Common snippets

## Key Integration Points

### Authentication and Environments
- **Default**: Use `Exchange.BINANCE_TESTNET` for development
- **Production**: `Exchange.BINANCE` or `Exchange.BINANCE_US` only when explicitly required
- **Signed endpoints**: Require `api_key` and `api_secret`

### Critical Patterns
```python
from binanceRestClient import BinanceRestClient, Exchange

client = BinanceRestClient(
    api_key=os.getenv("BINANCE_API_KEY"),
    api_secret=os.getenv("BINANCE_API_SECRET"),
    exchange=Exchange.BINANCE_TESTNET,
)

# Always wrap calls that can throw BinanceAPIException
try:
    prices = client.get_all_tickers()
except Exception as exc:
    print(f"API error: {exc}")
```

### Main Method Categories
- **Market data**: `get_exchange_info`, `get_ticker`, `get_24hr_ticker`, `get_klines`
- **Order book**: `get_order_book`, `get_orderbook_tickers`
- **User data stream**: `stream_listen_key`, `stream_keepalive`, `stream_close`
- **Wallet**: `all_coins_info`
- **Utilities**: `req_weight_cost`, `get_server_time`, `ping`

## Security Considerations

- **Never commit API keys**. Load them from env vars.
- Use testnet by default for any action that might touch balances.
- Signed endpoints require a timestamp and signature; the client handles this.

## Performance Guidelines

- Reuse a single `BinanceRestClient` instance per process.
- Use `async_tools.BinanceKlinesFetcher` for multi-pair kline retrieval.
- Note: `aiohttp` is required for async tools and is not in `pyproject.toml`.

## Developer Onboarding

- Install: `poetry install`
- Run tests: `poetry run pytest` (install `pytest` if missing)
- Python: `^3.11`

## Support Notes

This client covers a subset of the Binance REST API. If a required endpoint is
missing, add a method in `binanceRestClient/client.py` using `_get`, `_post`,
`_put`, or `_delete`, then update `method_reference.py` and `examples.py`.
