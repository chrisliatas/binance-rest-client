import hashlib
import hmac
import logging
import platform
from datetime import datetime
from operator import itemgetter
from time import time
from typing import Any

import requests

from binanceRestClient.exceptions import (
    AlreadyStoppedError,
    BinanceAPIException,
    BinanceRequestException,
)
from binanceRestClient.settings import EXCHANGE_SETTINGS, Exchange

lgr = logging.getLogger(__name__)

__app_name__: str = "cl-binance-rest-api"
__version__: str = "0.1.0"


def get_user_agent(name: str, version: str) -> str:
    return f"{name}_{version}-python_{str(platform.python_version())}"


user_agent = get_user_agent(__app_name__, __version__)


def currentTsMillis() -> int:
    return int(round(time() * 1000))


class BinanceRestClient:
    API_VERSION = "v3"

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        requests_params: dict | None = None,
        exchange: str | None = Exchange.BINANCE,
        debug: bool = False,
    ) -> None:
        """Binance REST API Client constructor"""
        self.sigterm = False
        self.session = None
        if self.sigterm is False:
            if exchange not in Exchange:
                lgr.critical(
                    f"{self.cls_name}.__init__ - Exchange {exchange} is not "
                    f"supported."
                )
                raise ValueError(f"Exchange {exchange} is not supported.")
            self.exchange = Exchange(exchange)
            self.debug = debug
        self.api_url = EXCHANGE_SETTINGS[self.exchange].api_base_uri
        self.api_key = api_key
        self.api_secret = api_secret
        self.requests_params = requests_params
        self.resp = None
        self.session = self._init_session()
        self.ts_offset = 0

    @property
    def cls_name(self):
        return self.__class__.__name__

    def __enter__(self):
        lgr.debug(f"{self.cls_name}.__enter__ - Entering `with-context` ...")
        if self.sigterm is True:
            info = (
                f"{self.cls_name}.__enter__ - Instance has already"
                f" been stopped and cannot be used."
            )
            lgr.critical(info)
            raise AlreadyStoppedError(info)
        return self

    def __exit__(self, exc_type, exc_value, error_traceback):
        lgr.debug(f"{self.cls_name}.__exit__ - Leaving `with-context` ...")
        self.stop_manager()
        if exc_type:
            lgr.critical(
                f"{self.cls_name}.__exit__ - An exception occurred: {exc_type} - "
                f"{exc_value} - {error_traceback}"
            )

    def _init_session(self) -> requests.Session:
        """Initialize requests session"""
        session = requests.session()
        session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": user_agent,
                "X-MBX-APIKEY": str(self.api_key),
            }
        )
        return session

    def _create_api_uri(self, path: str, signed=True, version=API_VERSION) -> str:
        # v = self.PRIVATE_API_VERSION if signed else version
        return self.api_url + "/" + version + "/" + path

    @staticmethod
    def _order_params(data: dict[str, Any]) -> list[tuple[str, str]]:
        """
        Convert params to list with signature as last element
        Args:
            data (dict): The request parameters.
        """
        has_signature = False
        params = []
        for key, value in data.items():
            if key == "signature":
                has_signature = True
            else:
                params.append((key, value))
        # sort parameters by key
        params.sort(key=itemgetter(0))
        if has_signature:
            params.append(("signature", data["signature"]))
        return params

    def _generate_signature(self, data: dict[str, Any]) -> str:
        """Generate request signature."""
        if not self.api_secret:
            raise BinanceAPIException("Api secret not configured")
        order_data = self._order_params(data)
        query_string = "&".join(["{}={}".format(d[0], d[1]) for d in order_data])
        m = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        )
        return m.hexdigest()

    def _handle_response(self, throw_exception=True) -> dict:
        """
        Handle API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.

        """
        if throw_exception is True:
            if not (200 <= self.response.status_code < 300):
                raise BinanceAPIException(self.response)
        try:
            return self.response.json()
        except ValueError:
            raise BinanceRequestException("Invalid Response: %s" % self.response.text)

    def _request(
        self,
        method: str,
        uri: str,
        signed: bool,
        force_params=False,
        throw_exception=True,
        **kwargs,
    ) -> dict:
        if self.sigterm is True:
            info = (
                f"{self.cls_name}._request() - instance has already been stopped and "
                "cannot be used."
            )
            lgr.critical(info)
            raise AlreadyStoppedError(info)

        # if an api_secret and api_key are provided update & reset session
        try:
            api_key = kwargs.pop("api_key")
            api_secret = kwargs.pop("api_secret")
        except KeyError:
            api_key = None
            api_secret = None
        if api_key and api_secret:
            lgr.debug(
                f"{self.cls_name}._request() - Got `api_key` and `api_secret` via "
                f"`**kwargs`, resetting request session."
            )
            self.api_key = api_key
            self.api_secret = api_secret
            if self.session:
                self.session.close()
            self.session = self._init_session()

        # set default requests timeout
        kwargs["timeout"] = 10

        # add our global requests params
        if self.requests_params:
            kwargs.update(self.requests_params)

        data = kwargs.get("data", None)
        if data and isinstance(data, dict):
            kwargs["data"] = data

            # find any requests params passed and apply them
            if "requests_params" in kwargs["data"]:
                # merge requests params into kwargs
                kwargs.update(kwargs["data"].pop("requests_params"))

        if signed:
            # generate signature
            kwargs["data"]["timestamp"] = int(currentTsMillis() + self.ts_offset)
            kwargs["data"]["signature"] = self._generate_signature(kwargs["data"])

        # sort get and post params to match signature order
        if data:
            # sort post params
            kwargs["data"] = self._order_params(kwargs["data"])
            # Remove any arguments with values of None.
            null_args = [
                i for i, (key, value) in enumerate(kwargs["data"]) if value is None
            ]
            for i in reversed(null_args):
                del kwargs["data"][i]

        # if get request assign data array to params value for requests lib
        if data and (method == "get" or force_params):
            kwargs["params"] = "&".join(
                "%s=%s" % (data[0], data[1]) for data in kwargs["data"]
            )
            del kwargs["data"]

        self.response = getattr(self.session, method)(uri, **kwargs)

        return self._handle_response(throw_exception=throw_exception)

    def _request_api(
        self,
        method: str,
        path: str,
        signed=False,
        version=API_VERSION,
        throw_exception=True,
        **kwargs,
    ) -> dict:
        uri = self._create_api_uri(path, signed, version)

        return self._request(
            method, uri, signed, throw_exception=throw_exception, **kwargs
        )

    def _get(self, path, signed=False, version=API_VERSION, **kwargs) -> dict | list:
        return self._request_api("get", path, signed, version, **kwargs)

    def _post(
        self, path, signed=False, version=API_VERSION, throw_exception=True, **kwargs
    ) -> dict:
        return self._request_api(
            "post", path, signed, version, throw_exception, **kwargs
        )

    def _put(self, path, signed=False, version=API_VERSION, **kwargs) -> dict:
        return self._request_api("put", path, signed, version, **kwargs)

    def _delete(self, path, signed=False, version=API_VERSION, **kwargs) -> dict:
        return self._request_api("delete", path, signed, version, **kwargs)

    def get_exchange_info(self, **params) -> dict:
        """Current exchange trading rules and symbol information"""
        return self._get("exchangeInfo", data=params)

    def get_symbol_info(self, symbol) -> dict | None:
        """Current exchange trading rules and symbol information"""
        res = self._get("exchangeInfo")

        for item in res["symbols"]:
            if item["symbol"] == symbol.upper():
                return item

        return None

    def ping(self) -> bool:
        """Test connectivity to the Rest API. Returns empty dictionary {}"""
        res = self._get("ping")
        if res == {}:
            return True
        return False

    def get_server_time(self) -> int:
        """Returns the current server time
        {
            "serverTime": 1499827319559
        }
        """
        res = self._get("time")
        if "serverTime" in res:
            return res["serverTime"]
        return 0

    def get_ticker(self, **params) -> dict | list:
        """Latest price for a symbol or symbols."""
        return self._get("ticker/price", data=params)

    def get_all_tickers(self) -> list[dict]:
        """Latest price for all symbols."""
        return self._get("ticker/price")

    def get_24hr_ticker(self, **params) -> dict:
        """24 hour price change statistics."""
        return self._get("ticker/24hr", data=params)

    def get_orderbook_tickers(self) -> dict:
        """Best price/qty on the order book for all symbols."""
        return self._get("ticker/bookTicker")

    def get_rol_w_price(self, **params) -> dict:
        """Rolling window price change statistics"""
        return self._get("ticker", data=params)

    def get_order_book(self, **params) -> dict:
        """Get the Order Book for the market
        {
            "lastUpdateId": 1027024,
            "bids": [
                [
                    "4.00000000",     // PRICE
                    "431.00000000",   // QTY
                    []                // Can be ignored
                ]
            ],
            "asks": [
                [
                    "4.00000200",
                    "12.00000000",
                    []
                ]
            ]
        }
        """
        return self._get("depth", data=params)

    def get_historical_trades(self, **params) -> dict:
        """Get older market trades. Required params symbol, limit, fromId.
        {
            "id": 28457,
            "price": "4.00000100",
            "qty": "12.00000000",
            "quoteQty": "48.000012",
            "time": 1499865549590,
            "isBuyerMaker": true,
            "isBestMatch": true
        }
        """
        return self._get("historicalTrades", data=params)

    def get_klines(self, **params) -> list[list[str]]:
        """Kline/candlestick bars for a symbol. Klines are uniquely identified by their
        open time. required params symbol, interval
        {
            "openTime": 1499040000000,
            "open": "0.01634790",
            "high": "0.80000000",
            "low": "0.01575800",
            "close": "0.01577100",
            "volume": "148976.11427815",
            "closeTime": 1499644799999,
            "quoteAssetVolume": "2434.19055334",
            "trades": 308,
            "takerBaseAssetVolume": "1756.87402397",
            "takerQuoteAssetVolume": "28.46694368",
            "ignored": "0"
        }
        """
        return self._get("klines", data=params)

    def _get_earliest_valid_timestamp(self, symbol, interval) -> int:
        """Get earliest valid timestamp for a symbol"""
        kline = self.get_klines(
            symbol=symbol, interval=interval, limit=1, startTime=0, endTime=None
        )
        return kline[0][0]

    def req_weight_cost(self, new_req=False) -> dict:
        """Get the weight cost of the last request. If `new_req` is True, then
        make a new request to 'exchangeInfo' and update the weight cost.
        Returns a dict with the following keys:
            weight: int
            timestamp: float
            status_code: int
        """
        resp_status = {}
        if new_req:
            self.get_exchange_info()
        resp_status["weight"] = self.response.headers.get("X-MBX-USED-WEIGHT", 0)
        resp_status["status_code"] = self.response.status_code
        try:
            dt = datetime.strptime(
                self.response.headers.get("Date"), "%a, %d %b %Y %H:%M:%S %Z"
            )
        except ValueError:
            resp_status["timestamp"] = 0.0
            return resp_status
        resp_status["timestamp"] = dt.timestamp()
        return resp_status

    def stream_close(self, listenKey: str, throw_exception=True, **kwargs) -> dict:
        """Close out a user data stream by deleting the respective `listenKey`.

        Ref: https://binance-docs.github.io/apidocs/spot/en/#listen-key-spot
        Args:
            listenKey (str): The listen key.
            throw_exception (bool, optional): Whether to throw an exception if the
                response status code is not 200. Defaults to True.

        """
        params = {"listenKey": listenKey}
        return self._delete(
            "userDataStream",
            False,
            version=self.API_VERSION,
            data=params,
            throw_exception=throw_exception,
            **kwargs,
        )

    def stream_listen_key(
        self, output="listenKey", throw_exception=True, **kwargs
    ) -> dict | str:
        """Start a new user data stream and return the listen key.

        Ref: https://binance-docs.github.io/apidocs/spot/en/#listen-key-spot
        Args:
            output (str, optional): The output to return. Set to "listenKey" to
            get the plain listen key string, but can also be set to "response" to get
            the full response. Defaults to "listenKey".
            throw_exception (bool, optional): Whether to throw an exception if the
                response status code is not 200. Defaults to True.
        Returns:
            dict | str: The response or the listen key.
        """
        res = self._post(
            "userDataStream",
            False,
            version=self.API_VERSION,
            data={},
            throw_exception=throw_exception,
            **kwargs,
        )
        if output == "listenKey":
            return res["listenKey"]
        return res

    def stream_keepalive(self, listenKey: str, throw_exception=True, **kwargs) -> dict:
        """Keepalive a user data stream to prevent a time out (PING).

        Ref: https://binance-docs.github.io/apidocs/spot/en/#listen-key-spot
        Args:
            listenKey (str): The listen key.
            throw_exception (bool, optional): Whether to throw an exception if the
                response status code is not 200 or return raw response.
                Defaults to True.
        Returns:
            dict: The response, which should be an empty dict.
        """
        params = {"listenKey": listenKey}
        return self._put(
            "userDataStream",
            False,
            version=self.API_VERSION,
            data=params,
            throw_exception=throw_exception,
            **kwargs,
        )

    def stop(self) -> bool:
        """Stop the BinanceRestManager."""
        lgr.info(f"{self.cls_name}.stop() - Stopping BinanceRestManager ...")
        self.sigterm = True
        if self.session:
            self.session.close()
        return True
