# -*- encoding: utf8 -*-
# © Toons

from arky.util import stats, getArkFiatPrice
from arky import cfg, api, slots, wallet, HOME
import os, json, math, datetime

import sys
print(sys.version)

while cfg.__NET__ != "ark":
	api.use("ark")

__daily_fees__ = 5./30  # daily server cost
__investments__ = "AUahWfkfr5J4tYakugRbfow7RWVTK35GPW"
__exchange__ = "APREAB1cyRLGRrTBs97BEXNv1AwAPpSQkJ"
__tx_fee__ = cfg.__FEES__["send"]/100000000.

# screen command line
from optparse import OptionParser
parser = OptionParser()
parser.set_usage("usage: %prog arg1 ....argN [options]")
parser.add_option("-s", "--secret", dest="secret", help="wallet secret you want to use")
parser.add_option("-k", "--keyring", dest="keyring", help="wallet file you want to use")
(options, args) = parser.parse_args()


def ARK2USD(value): return value * float(getArkFiatPrice("usd"))


def USD2ARK(value): return value / float(getArkFiatPrice("usd"))


if len(args) == 1 and os.path.exists(args[0]):
	in_ = open(args[0])
	content = in_.read()
	in_.close()
	conf = json.loads(content.decode() if isinstance(content, bytes) else content)
	wlt = wallet.Wallet(conf["forging"]["secret"][0])
elif options.secret:
	wlt = wallet.Wallet(options.secret)
elif options.keyring:
	wlt = wallet.open(options.keyring)
else:
	raise Exception("Can not do something for now !")

print(wlt.address)

logfile = os.path.join(HOME, "Payment", "%s.pay" % datetime.datetime.now().strftime("%y-%m-%d %Hh%M"))
try: os.makedirs(os.path.dirname(logfile))
except: pass
log = open(logfile, "w")

wlt.update()
if wlt.delegate["rate"] > 51:
	log.write("%s is not an active delegate right now !" % wlt.delegate["username"])
	log.close()
	raise Exception("%s is not an active delegate right now !" % wlt.delegate["username"])
	
elif wlt.balance < 200:
	log.write("%s does not have more than 200 Arks !" % wlt.delegate["username"])
	log.close()
	raise Exception("%s does not have more than 200 Arks !" % wlt.delegate["username"])

sys.stdout.write("Checking %s-day-true-vote-weight on transaction history...\n" % 7)
contributors = dict([address, stats.getVoteForce(address, 7)] for address in [v["address"] for v in wlt.voters if v["address"] not in [__investments__, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE"]])
k = 1.0/max(1, sum(contributors.values()))
contributors = dict((a, s*k) for a, s in contributors.items())

# # contributors = _getTrueVoteWeight([v["address"] for v in wlt.voters], delay=7)
amount = wlt.balance
log.write("delegate amount : A%.8f\n" % amount)
header = ["Date", datetime.datetime.now(), ""]
content = ["ARK amount", amount, ""]

# ARK to be exchanged for node fees payment
node_invest = 2*math.ceil(USD2ARK(__daily_fees__*7)) - __tx_fee__
log.write("node fees       : A%.8f\n" % node_invest)
header.append("Node fees")
content.append(node_invest)
wlt.sendArk(node_invest, __exchange__)

# part to be distributed
share = amount - node_invest
log.write("Share           : A%.8f\n" % share)

investments = 0.20 * share - __tx_fee__
log.write("For investments : A%.8f\n" % investments)
header.append("Investments")
content.append(investments)
wlt.sendArk(investments, __investments__)

voters = 0.80 * share
log.write("For voters      : A%.8f\n" % voters)

log.write("\nArky contributors : [checksum:%f]\n" % sum(contributors.values()))
header.append("")
content.append("")
for addr, ratio in sorted(contributors.items(), key=lambda i: i[1]):
	amount = voters*ratio - __tx_fee__
	if amount > 0.:
		wlt.sendArk(amount, addr, vendorField="Arky weekly interests. Thanks for your contribution !")
		log.write("%s [true weight:%f]: A%.8f\n" % (addr, contributors[addr], amount))
		header.append(addr)
		content.append(amount)
	else:
		log.write("%s [true weight:%f]: not enough ark to share\n" % (addr, contributors[addr]))
		header.append(addr)
		content.append("-")

out = open("accounting.csv", "a")
out.write(";".join(["%s" % e for e in header]) + "\n")
out.write(";".join(["%s" % e for e in content]) + "\n")
out.close()

wallet.mgmt.join()
log.close()
