# -*- encoding -*-
from arky.util import getArkPrice
from arky import api, wallet, HOME
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
	wlt = wallet.Wallet(option.ssecret)
elif options.wallet:
	wlt = wallet.open(options.wallet)
else:
	raise Exception("Can not do something for now !")

# here you put ARK addresses except for voters... it is handled
payment = {
	"AX8fQaCX73LR8DT8bAQ9atst7yDxcVhEfp": 0.50,
	"APW7bFmpzSQr7s9p56oo93ec2s6boDFZQY": 0.35,
	"Voters": 0.25
}

if sum(payment.values()) > 1.0: raise Exception("Share is not fair enough")

contribution = wlt.contribution
fees = 0.1 * (len(contribution) + len(payment) - 1)
total = wlt.balance - fees

out = open("accounting.csv", "a")

header = [datetime.datetime.now()]
content = [total]

for addr,ratio in payment.items():
	if addr == "Voters":
		amount = total*ratio
		for a,r in  contribution.items():
			share = amount*r
			if share > 0.:
				wlt.sendArk(share, a, vendorField="your custom message to voters here")
				header.append(a)
				content.append(share)
	else:
		share = total*ratio
		wlt.sendArk(share, addr, vendorField="your custom message here")
		header.append(addr)
		content.append(share)

out.write(";".join(["%s"%e for e in header])  + "\n")
out.write(";".join(["%s"%e for e in content]) + "\n")
out.close()