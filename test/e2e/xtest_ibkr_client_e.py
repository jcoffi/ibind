import os
import warnings
from unittest import TestCase

from ibind.client.ibkr_client import IbkrClient
from ibind.client.ibkr_utils import StockQuery
from test.integration.client import ibkr_responses


class TestIbkrClientE(TestCase):
    def setUp(self):
        warnings.filterwarnings('ignore', message="Unverified HTTPS request is being made to host 'localhost'")

        self.url = 'https://localhost:5000/v1/api/'
        # self.account_id = os.getenv('TEST_IBKR_ACCOUNT_ID')
        self.account_id = os.getenv('IBIND_ACCOUNT_ID')
        self.timeout = 8
        self.max_retries = 4
        self.client = IbkrClient(
            url=self.url,
            account_id=self.account_id,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

        self.query = [
            StockQuery(symbol='CDN', contract_conditions={}),
            StockQuery(symbol='CFC', contract_conditions={}),
            'SCHW',
            'GOOG',
            'TEAM',
            'SAN',
            'BBVA',
            'MSFT',
            'AAPL',
            'META',
            'HUBS',
        ]

    def tearDown(self):
        warnings.filterwarnings('default', message="Unverified HTTPS request is being made to host 'localhost'")

    def test_get_conids(self):
        result = self.client.stock_conid_by_symbol(self.query)
        self.assertEqual(result.data, ibkr_responses.responses['conids'])

    def test_get_stocks(self):
        result = self.client.security_stocks_by_symbol(self.query, default_filtering=False)
        self.assertEqual(result.data, ibkr_responses.responses['stocks'])

    def test_live_marketdata_snapshot(self):
        self.client.receive_brokerage_accounts()
        result = self.client.live_marketdata_snapshot('265598', ['55'])
        print(result)

    def test_historical_marketdata_beta(self):
        self.client.receive_brokerage_accounts()
        result = self.client.historical_marketdata_beta(265598, '1d', '1hrs', outside_rth=True, bar_type='Ask')
        print(result)

        print(result)

    def test_positions2(self):
        result = self.client.positions2()
        print(result)

    def test_live_orders(self):
        result = self.client.live_orders()
        print(result)

    def test_cancel_all_orders(self):
        print(self.client.portfolio_accounts())
        result = self.client.live_orders(filters=[])

        if 'orders' not in result.data or not result.data['orders']:
            print('No orders to cancel')
            return

        for order in result.data['orders']:
            try:
                print(self.client.cancel_order(order['orderId']))
            except Exception as e:
                print(e)
