# -*- encoding -*-
from arky import api, wallet, __PY3__
import os, json, datetime
api.use("ark")

# screen command line
from optparse import OptionParser
parser = OptionParser()
parser.set_usage("usage: %prog [JSON] [options]")
parser.add_option("-s", "--secret", dest="secret", help="wallet secret you want to use")
parser.add_option("-w", "--wallet", dest="wallet", help="wallet file you want to use")
(options, args) = parser.parse_args()

if len(args) == 1 and os.path.exists(args[0]):
	in_ = open(args[0])
	content = in_.read()
	in_.close()
	conf = json.loads(content.decode() if isinstance(content, bytes) else content)
	wlt = wallet.Wallet(conf["forging"]["secret"][0])
elif options.secret:
	wlt = wallet.Wallet(options.secret)
elif options.wallet:
	wlt = wallet.open(options.wallet)
else:
	raise Exception("Can not do something for now !")

if wlt.delegate["rate"] > 51:
	raise Exception("%s is not an active delegate right now !" % wlt.delegate["username"])

relays = api.Delegate.getCandidates()[52:]
vote_sum = max(1, sum([float(d.get("vote", 0.)) for d in relays]))
dist = dict([(r["address"], float(r.get("vote", 0.))/vote_sum) for r in relays])
balance = wlt.balance

for address, ratio in dist.items():
	amount = (balance * ratio) - 0.1
	if amount > 1.0:
		wlt.sendArk(amount, address, vendorField="your custom message to voters here")

wallet.mgmt.join()
