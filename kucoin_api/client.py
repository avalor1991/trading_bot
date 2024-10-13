import requests
import time
import hmac
import hashlib
import base64  # Add this import for base64 encoding
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class KuCoinClient:
    def __init__(self, api_key, api_secret, api_passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.session = requests.Session()

        logging.info("KuCoinClient initialized successfully with API key.")

    def get_ticker(self, symbol):
        url = f'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}'
        response = self.session.get(url,
                                    headers=self._headers('GET', f'/api/v1/market/orderbook/level1?symbol={symbol}',
                                                          ''))
        response.raise_for_status()
        return response.json()['data']

    def get_balance(self):
        url = 'https://api.kucoin.com/api/v1/accounts'
        headers = self._headers('GET', '/api/v1/accounts', '')
        response = self.session.get(url, headers=headers)

        logging.info(f"Response Status Code: {response.status_code}")
        logging.info(f"Response Content: {response.content}")

        response.raise_for_status()
        balances = response.json()['data']

        # Process balances to group by account type
        account_balances = {}
        for balance in balances:
            account_type = balance['type']
            currency = balance['currency']
            available = balance['available']
            balance_info = f"{currency}: {available}"
            if account_type not in account_balances:
                account_balances[account_type] = []
            account_balances[account_type].append(balance_info)

        logging.info(f"Processed Account Balances: {account_balances}")
        return account_balances

    def _headers(self, method, endpoint, body):
        now = int(time.time() * 1000)
        str_to_sign = str(now) + method + endpoint + body
        logging.info(f"String to Sign: {str_to_sign}")  # Debug
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
        )
        logging.info(f"Signature: {signature}")  # Debug

        headers = {
            'KC-API-KEY': self.api_key,
            'KC-API-SIGN': signature.decode('utf-8'),
            'KC-API-TIMESTAMP': str(now),
            'KC-API-PASSPHRASE': self.api_passphrase,
            'Content-Type': 'application/json'
        }
        logging.info(f"Headers: {headers}")  # Debug
        return headers


    def _get_headers(self, endpoint, method, body=''):
        now = int(time.time() * 1000)
        str_to_sign = str(now) + method + endpoint + body
        signature = hmac.new(self.api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()
        signature_b64 = base64.b64encode(signature).decode('utf-8')

        passphrase = hmac.new(self.api_secret.encode('utf-8'), self.api_passphrase.encode('utf-8'),
                              hashlib.sha256).digest()
        passphrase_b64 = base64.b64encode(passphrase).decode('utf-8')

        headers = {
            "KC-API-KEY": self.api_key,
            "KC-API-SIGN": signature_b64,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-PASSPHRASE": passphrase_b64,
            "Content-Type": "application/json"
        }
        return headers

    def _send_request(self, method, endpoint, params=None):
        url = self.api_base_url + endpoint
        headers = self._get_headers(endpoint, method)
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=params)
        return response.json()

    def get_account(self):
        return self._send_request('GET', '/api/v1/accounts')

    def get_historical_ohlcv(self, symbol, start_time, end_time, candle_type='1min'):
        params = {
            'symbol': symbol,
            'startAt': start_time,
            'endAt': end_time,
            'type': candle_type
        }
        return self._send_request('GET', '/api/v1/market/candles', params)

    def place_order(self, symbol, side, price, size, type='market'):
        endpoint = '/api/v1/orders'
        params = {
            'clientOid': str(uuid.uuid4()),
            'side': side,
            'symbol': symbol,
            'type': type,
            'price': price,
            'size': size
        }
        return self._send_request('POST', endpoint, params)

    # Add other methods as needed
