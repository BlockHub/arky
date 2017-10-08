# -*- encoding: utf8 -*-
# © Toons

# __all__ = []

from .. import setInterval
from .. import rest
from .. import cfg

from . import crypto

import random

def init():
	network = rest.GET.api.loader.autoconfigure(returnKey="network")
	cfg.headers["version"] = network.pop("version")
	cfg.headers["nethash"] = network.pop("nethash")
	cfg.__dict__.update(network)
	cfg.fees = rest.GET.api.blocks.getFees(returnKey="fees")

def sendTransaction(**kw):
	tx = crypto.bakeTransaction(**dict([k,v] for k,v in kw.items() if v))
	result = rest.POST.peer.transactions(peer=cfg.peers[0], transactions=[tx])
	success = 1 if result["success"] else 0
	for peer in cfg.peers[1:]:
		if rest.POST.peer.transactions(peer=peer, transactions=[tx])["success"]:
			success += 1
	result["broadcast"] = "%.1f%%" % (100.*success/len(cfg.peers))
	return result

def sendToken(amount, recipientId, vendorField, secret, secondSecret=None):
	return sendTransaction(
		amount=amount,
		recipientId=recipientId,
		vendorField=VendorField,
		secret=secret,
		secondSecret=secondSecret
	)

def registerSecondPublicKey(secondPublicKey, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	return sendTransaction(
		type=1,
		publicKey=keys["publicKey"],
		asset={"signature":{"publicKey":secondPublicKey}},
		privateKey=keys["privateKey"],
		secondSecret=secondSecret
	)

def registerSecondPassphrase(secondPassphrase, secret, secondSecret=None):
	secondKeys = crypto.getKeys(secondPassphrase)
	return registerSecondPublicKey(secondKeys["publicKey"], secret, secondSecret)

def registerDelegate(username, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	return sendTransaction(
		type=2,
		publicKey=keys["publicKey"],
		asset={"delegate":{"username":username, "publicKey":keys["publicKey"]}},
		privateKey=keys["privateKey"],
		secondSecret=secondSecret
	)

def upVoteDelegate(username, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	address = crypto.getAddress(keys)
	req = rest.GET.api.delegates.get(username=username)
	if req["success"]:
		return sendTransaction(
			type=3,
			publicKey=keys["publicKey"],
			recipientId=address,
			asset={"votes":["+%s"%req["delegate"]["publicKey"]]},
			privateKey=keys["privateKey"],
			secondSecret=secondSecret
		)

def downVoteDelegate(username, secret, secondSecret=None):
	keys = crypto.getKeys(secret)
	address = crypto.getAddress(keys)
	req = rest.GET.api.delegates.get(username=username)
	if req["success"]:
		return sendTransaction(
			type=3,
			publicKey=keys["publicKey"],
			recipientId=address,
			asset={"votes":["-%s"%req["delegate"]["publicKey"]]},
			privateKey=keys["privateKey"],
			secondSecret=secondSecret
		)

def selectPeers():
	peers = [p for p in rest.GET.api.peers().get("peers", []) if p.get("status", "") == "OK" and p.get("delay", 0) <= cfg.timeout*1000]
	selection = []
	for i in range(min(cfg.broadcast, len(peers))):
		selection.append("http://%(ip)s:%(port)s" % random.choice(peers))
	if len(selection):
		cfg.peers = selection

# select peers
selectPeers()
@setInterval(8*51)
def rotatePeers():
	selectPeers()
_daemon = rotatePeers()
