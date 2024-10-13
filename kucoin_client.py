import requests
import logging
import time


class KuCoinClient:
    def __init__(self, api_key, api_secret, api_passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.base_url = 'https://api.kucoin.com'
        logging.info("KuCoinClient initialized")

    def get_ticker(self, symbol):
        endpoint = f'/api/v1/market/orderbook/level1?symbol={symbol}'
        response = self._request('GET', endpoint)
        return response

    def get_balance(self):
        endpoint = '/api/v1/accounts'
        response = self._request('GET', endpoint)
        return response

    def get_account(self):
        endpoint = '/api/v1/accounts'
        response = self._request('GET', endpoint)
        return response

    def _request(self, method, endpoint, params=None):
        url = self.base_url + endpoint
        headers = self._build_headers()
        response = requests.request(method, url, headers=headers, params=params)
        self._handle_rate_limits(response)
        logging.info("Request made to %s with params %s", {url}, {params})
        return response.json()

    def _build_headers(self):
        headers = {
            "KC-API-KEY": self.api_key,
            "KC-API-SIGN": self.api_secret,
            "KC-API-PASSPHRASE": self.api_passphrase,
        }
        return headers

    def _handle_rate_limits(self, response):
        if response.status_code == 429:  # Too many requests
            retry_after = int(response.headers.get('Retry-After', 1))
            logging.warning("Rate limit exceeded. Retrying after %d seconds...", retry_after)
            time.sleep(retry_after)