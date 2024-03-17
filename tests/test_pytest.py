from unittest.mock import patch

from binanceRestClient.client import BinanceRestClient


@patch("requests.Session")
def test_init_session(mock_session):
    client = BinanceRestClient(api_key="test_key", api_secret="test_secret")
    mock_session.assert_called_once()
    assert client.api_key == "test_key"
    assert client.api_secret == "test_secret"


@patch("requests.Session")
def test_get_exchange_info(mock_session):
    client = BinanceRestClient(api_key="test_key", api_secret="test_secret")
    mock_session.return_value.get.return_value.json.return_value = {"test": "data"}
    response = client.get_exchange_info()
    mock_session.return_value.get.assert_called_once_with(
        client.api_url + "/v3/exchangeInfo"
    )
    assert response == {"test": "data"}


@patch("requests.Session")
def test_get_symbol_info(mock_session):
    client = BinanceRestClient(api_key="test_key", api_secret="test_secret")
    mock_session.return_value.get.return_value.json.return_value = {
        "symbols": [{"symbol": "BTCUSDT", "status": "TRADING"}]
    }
    response = client.get_symbol_info("BTCUSDT")
    mock_session.return_value.get.assert_called_once_with(
        client.api_url + "/v3/exchangeInfo"
    )
    assert response == {"symbol": "BTCUSDT", "status": "TRADING"}


@patch("requests.Session")
def test_ping(mock_session):
    client = BinanceRestClient(api_key="test_key", api_secret="test_secret")
    mock_session.return_value.get.return_value.json.return_value = {}
    response = client.ping()
    mock_session.return_value.get.assert_called_once_with(client.api_url + "/v3/ping")
    assert response == {}


@patch("requests.Session")
def test_get_server_time(mock_session):
    client = BinanceRestClient(api_key="test_key", api_secret="test_secret")
    mock_session.return_value.get.return_value.json.return_value = {
        "serverTime": 1234567890
    }
    response = client.get_server_time()
    mock_session.return_value.get.assert_called_once_with(client.api_url + "/v3/time")
    assert response == {"serverTime": 1234567890}
