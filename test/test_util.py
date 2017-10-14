import unittest
from arky.util import getTokenPrice, getArkFiatPrice, getArkPriceFromCryptoCompare, getAllCoinsFromCryptoCompare, \
    getArkPriceFromBittrex, getArkPriceFromCryptopia, getArkPriceFromLitebit, getArkPriceFromCryptomate, \
    getArkPriceFromCryptoCompareBis


class TestUtil(unittest.TestCase):
    """
    Unit tests on the functions inside the __init__ file inside the /util/ directory.
    """
    def test_getTokenPrice(self):
        ark_price = getTokenPrice("ark")
        self.assertTrue(0.00001 <= ark_price <= 1000.00000)

    def test_getArkFiatPrice(self):
        ark_price = float(getArkFiatPrice("usd"))
        self.assertTrue(0.00001 <= ark_price <= 1000.00000)
        self.assertRaises(AttributeError, getArkFiatPrice, "czk")

    def test_getArkPriceFromCryptoCompare(self):
        ark_price = getArkPriceFromCryptoCompare("usd")
        self.assertTrue(0.00 <= ark_price <= 1000.00)
        self.assertRaises(AttributeError, getArkFiatPrice, "czk")

    def test_getAllCoinsFromCryptoCompare(self):
        coins = getAllCoinsFromCryptoCompare()
        self.assertTrue(len(coins) > 0)

    def test_getArkPriceFromCryptoCompareBis(self):
        ark_price = getArkPriceFromCryptoCompareBis("usd", "btc", "eur")
        self.assertEqual(len(ark_price), 3)

    def test_getArkPriceFromBittrex(self):
        ark_price = getArkPriceFromBittrex()
        self.assertTrue(0.00000001 <= ark_price <= 1.00000000)

    def test_getArkPriceFromCryptopia(self):
        ark_price = getArkPriceFromCryptopia()
        self.assertTrue(0.00000001 <= ark_price <= 1.00000000)

    def test_getArkPriceFromLitebit(self):
        ark_price = float(getArkPriceFromLitebit())
        self.assertTrue(0.000001 <= ark_price <= 1000.000000)

    def test_getArkPriceFromCryptomate(self):
        ark_price = float(getArkPriceFromCryptomate())
        self.assertTrue(0.000001 <= ark_price <= 1000.000000)


if __name__ == '__main__':
    unittest.main()
