import unittest
from unittest.mock import patch
import finance_bot


class TestFinanceBot(unittest.TestCase):
    def test_get_currency_rate(self):
        with patch('finance_bot.requests.get') as mocked_get:
            values = [
                {'r030': 840, 'txt': 'Долар США',
                 'rate': 29.2549, 'cc': 'USD',
                 'exchangedate': '03.06.2022'}
            ]
            mocked_get.return_value.ok = True
            mocked_get.return_value.json.return_value = values
            rate = finance_bot.get_currency_rate('USD')
            mocked_get.assert_called_with('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode'
                                          '=USD&date=20220603&json')
            self.assertListEqual(rate, values)

            mocked_get.return_value.ok = False
            rate = finance_bot.get_currency_rate('AUD')
            mocked_get.assert_called_with('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode'
                                          '=AUD&date=20220603&json')
            self.assertEqual(rate, 'Bad response!')

    def test_get_previous_currency_rate(self):
        with patch('finance_bot.requests.get') as mocked_get:
            values = [
                {'r030': 840, 'txt': 'Долар США',
                 'rate': 3.9355, 'cc': 'USD',
                 'exchangedate': '03.06.1999'}
            ]
            mocked_get.return_value.ok = True
            mocked_get.return_value.json.return_value = values
            rate = finance_bot.get_previous_currency_rate('USD', '1999')
            mocked_get.assert_called_with('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode'
                                          '=USD&date=19990603&json')
            self.assertListEqual(rate, values)

            mocked_get.return_value.ok = False
            rate = finance_bot.get_previous_currency_rate('USD', '1999')
            mocked_get.assert_called_with('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode'
                                          '=USD&date=19990603&json')
            self.assertEqual(rate, 'Bad response!')


if __name__ == '__main__':
    unittest.main()
