import asyncio
import logging
from datetime import datetime, timedelta, timezone
from timeit import default_timer as timer

import aiohttp

# ----------------- Binance K-lines -----------------


class BinanceKlinesFetcher:
    """Fetch Binance k-lines for multiple pairs asynchronously."""

    base_url = "https://api.binance.com/api/v3/klines"

    def __init__(
        self,
        pairs: list[str],
        interval: str = "1s",
        fromTime: int | None = 0,
        toTime: int | None = 0,
        n_mins: float | None = 5.0,
        pair_retries: int = 3,
        pair_timeout: int | None = None,
        init_backoff: float = 1.0,
        logger: logging.Logger | None = None,
    ):
        self.lgr = logger or logging.getLogger("BinanceKlinesFetcher")
        self.pairs = pairs
        self.lgr.info(
            f"{self.cls_name}.__init__ - Will be getting klines for {self.pairs}"
        )
        self.interval = interval
        # we need either fromTime and toTime or n_mins, check and raise if not:
        if not (fromTime and toTime) and not n_mins:
            raise ValueError("fromTime and toTime or n_mins are required.")
        self.fromTime = fromTime
        self.toTime = toTime
        self.n_mins = n_mins
        self.pair_retries = pair_retries
        self.pair_timeout = pair_timeout
        self.init_backoff = init_backoff
        self.responses: dict[str, list[list[float]]] = {}

    @property
    def cls_name(self) -> str:
        return self.__class__.__name__

    def create_klines_urls(self, start: int, end: int) -> list[str]:
        """Create a list of k-lines URLs for multiple pairs."""
        return [
            (
                f"{self.base_url}?symbol={p}&interval={self.interval}"
                f"&startTime={start}&endTime={end}"
            )
            for p in [p.replace("-", "") for p in self.pairs]
        ]

    def get_backwards_range(self) -> tuple[int, int]:
        """Get the backwards range for the k-lines, provided the number of minutes."""
        if not self.n_mins:
            if self.fromTime and self.toTime:
                return self.fromTime, self.toTime
            else:
                raise ValueError("fromTime and toTime or n_mins are required.")
        utcNow = datetime.now(tz=timezone.utc) - timedelta(milliseconds=500)
        toTime = int(utcNow.timestamp() * 1000)
        fromTime = int((utcNow - timedelta(minutes=self.n_mins)).timestamp() * 1000)
        return fromTime, toTime

    async def get_single_pair(
        self,
        session: aiohttp.ClientSession,
        url: str,
        pair: str,
    ) -> None:
        for attempt in range(self.pair_retries):
            try:
                async with session.get(url, timeout=self.pair_timeout) as response:
                    resp = await response.json()
                    break
            except asyncio.TimeoutError:
                self.lgr.warning(
                    f"{self.cls_name}.get_single_pair - Timeout, retrying "
                    f"{attempt + 1}/{self.pair_retries} for {pair}"
                )
            except Exception as ex:
                self.lgr.error(f"{self.cls_name}.get_single_pair - Exception: {ex}")
                resp = []
                break
            # add an exponential backoff for each retry
            await asyncio.sleep(self.init_backoff * (2**attempt))
        else:
            self.lgr.error(
                f"{self.cls_name}.get_single_pair - Failed to get {pair} "
                f"after {self.pair_retries} retries."
            )
            resp = []
        if isinstance(resp, dict):
            resp = []
        if resp:
            # keep only the OHLC and 6th (close time) columns
            resp = [
                [float(r[1]), float(r[2]), float(r[3]), float(r[4]), r[6]] for r in resp
            ]
        self.responses[pair] = resp

    async def fetch_pairs_klines(self) -> dict[str, list[list[float]]]:
        """Fetch multiple pairs klines from Binance."""
        self.responses = {}
        fromTime, toTime = self.get_backwards_range()
        urls = self.create_klines_urls(fromTime, toTime)
        async with aiohttp.ClientSession() as session:
            tasks = []
            _timer_start = timer()
            for i, p in enumerate(self.pairs):
                task = asyncio.create_task(self.get_single_pair(session, urls[i], p))
                tasks.append(task)

            await asyncio.gather(*tasks)
            self.lgr.info(
                f"{self.cls_name}.fetch_pairs_klines - Download k-lines took: "
                f"{timedelta(seconds=timer() - _timer_start)}"
            )
        return self.responses

    def fill_missing_pairs(self) -> None:
        """Fill missing pairs klines by combining the close prices of the existing
        pairs."""
        try:
            eth_usdt = self.responses["ETH-USDT"]
        except KeyError:
            self.lgr.error(f"{self.cls_name}.fill_missing_pairs - ETH-USDT is missing")
            raise
        # find pairs with no data
        q_l = len(eth_usdt)
        missing_pairs = [p for p, v in self.responses.items() if not v]
        for p in missing_pairs:
            base = p.split("-")[0]
            # find the pair with the same base
            for k, v in self.responses.items():
                if (base in k) and (k not in missing_pairs):
                    # we combine the close prices of the existing pair with eth_usdt
                    rows = v[:q_l] if len(v) > q_l else v  # prevent `out of range` err
                    base_eth = [
                        [round(r[0] / eth_usdt[i][0], 9), eth_usdt[i][1]]
                        for i, r in enumerate(rows)
                    ]
                    self.responses[p] = base_eth
                    break

    async def fetch_and_fill_klines(self) -> dict[str, list[list[float]]]:
        """Fetch and fill missing pairs klines."""
        await self.fetch_pairs_klines()
        self.fill_missing_pairs()
        return self.responses
