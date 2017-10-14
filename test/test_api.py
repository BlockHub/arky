import unittest
from arky.api import Block


class TestBlockAPI(unittest.TestCase):
    def test_getBlocks(self, **params):
        req = Block.getBlocks(**params)
        self.assertEqual(req['success'], True)

    #def test_getBlock(self, blockId, **params):
    #    print(Block.getBlock("10062678361179004045", **params))

    def test_getNetHash(self, **params):
        req = Block.getNethash(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainFee(self, **params):
        req = Block.getBlockchainFee(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainFees(self, **params):
        req = Block.getBlockchainFees(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainHeight(self, **params):
        req = Block.getBlockchainHeight(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainEpoch(self, **params):
        req = Block.getBlockchainEpoch(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainMilestone(self, **params):
        req = Block.getBlockchainMilestone(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainReward(self, **params):
        req = Block.getBlockchainReward(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainSupply(self, **params):
        req = Block.getBlockchainSupply(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainStatus(self, **params):
        req = Block.getBlockchainStatus(**params)
        self.assertEqual(req['success'], True)

    #def test_getForgedByAccount(self, publicKey, **params):
    #    print(Block.getForgedByAccount("038e82be3e92018374c9b53a25a428799602366635d5270c5154d945ac60216ffe", **params))


if __name__ == '__main__':
    unittest.main()