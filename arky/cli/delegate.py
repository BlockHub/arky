# -*- encoding: utf8 -*-
# © Toons

"""
Usage: delegate link [<secret> <2ndSecret>]
	   delegate save <name>
	   delegate unlink
	   delegate status
	   delegate voters
	   delegate share <amount> [-c -b <blacklist> -d <delay> -l <lowest> -h <highest> <message>]

Options:
-b <blacklist> --blacklist <blacklist> ark addresses to exclude (comma-separated list or pathfile)
-h <highest> --highest <hihgest>       maximum payout in ARK
-l <lowest> --lowest <lowest>          minimum payout in ARK
-d <delay> --delay <delay>             number of fidelity-day [default: 30]
-c --complement                        share the amount complement

Subcommands:
	link   : link to delegate using secret passphrases. If secret passphrases
			 contains spaces, it must be enclosed within double quotes
			 ("secret with spaces"). If no secret given, it tries to link
			 with saved account(s).
	save   : save linked delegate to a *.tokd file.
	unlink : unlink delegate.
	status : show information about linked delegate.
	voters : show voters contributions ([address - vote] pairs).
	share  : share ARK amount with voters (if any) according to their
			 weight (1% mandatory fees). You can set a 64-char message.
"""

from .. import cfg, api, core, ROOT
from .. util import stats
from . import common

import io, os, sys

SHARE = False
ADDRESS = None
PUBLICKEY = None
KEY1 = None
KEY2 = None
USERNAME = None
DELEGATE = None

try:
	version_info = sys.version_info[:2]
	if version_info == (2, 7): from . import pshare27 as pshare
	elif version_info == (3, 5): from . import pshare35 as pshare
	elif version_info == (3, 6): from . import pshare36 as pshare
	SHARE = True
except ImportError:
	SHARE = False


def link(param):
	global ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE
	
	if param["<secret>"]:
		keys = core.getKeys(param["<secret>"].encode("ascii"))
		KEY1 = keys.signingKey
		PUBLICKEY = keys.public
		ADDRESS = core.getAddress(keys)
		USERNAME = _checkIfDelegate()

	else:
		choices = common.findTokens("tokd")
		if choices:
			ADDRESS, PUBLICKEY, KEY1 = common.loadToken(common.tokenPath(common.chooseItem("Delegate account(s) found:", *choices), "tokd"))
			USERNAME = _checkIfDelegate()
		else:
			sys.stdout.write("No token found\n")
			unlink({})
			return

	if not USERNAME:
		sys.stdout.write("Not a delegate\n")
		ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE = None, None, None, None, None, None
	elif param["<2ndSecret>"]:
		keys = core.getKeys(param["<2ndSecret>"].encode("ascii"))
		KEY2 = keys.signingKey
		
	if ADDRESS:
		common.BALANCES.register(ADDRESS)


def save(param):
	if KEY1 and PUBLICKEY and ADDRESS:
		common.dropToken(common.tokenPath(param["<name>"], "tokd"), ADDRESS, PUBLICKEY, KEY1)


def unlink(param):
	global ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE
	common.BALANCES.pop(ADDRESS, None)
	ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE = None, None, None, None, None, None


def status(param):
	if ADDRESS:
		common.prettyPrint(dict(DELEGATE, **api.Account.getAccount(ADDRESS, returnKey="account")))


def voters(param):
	if PUBLICKEY:
		accounts = api.Delegate.getVoters(common.hexlify(PUBLICKEY), returnKey="accounts")
		sum_ = 0.
		for addr, vote in ([c["address"],float(c["balance"])/100000000] for c in accounts):
			line = "    %s: %.3f\n" % (addr, vote)
			sys.stdout.write(line)
			sum_ += vote
		sys.stdout.write("    " + "-"*(len(line)-5) + "\n")
		sys.stdout.write("    %s: %.3f\n" % (("%d voters" % len(accounts)).rjust(len(addr)), sum_))


def share(param):
	global KEY1, KEY2, ADDRESS

	KEY2 = common.checkKeys(KEY1, KEY2, ADDRESS)
	if KEY2:
		if SHARE:
			if param["--blacklist"]:
				if os.path.exists(param["--blacklist"]):
					with io.open(param["--blacklist"], "r") as in_:
						blacklist = [e for e in in_.read().split() if e != ""]
				else:
					blacklist = param["--blacklist"].split(",")
			else:
				blacklist = []

			amount = common.floatAmount(param["<amount>"], ADDRESS)
			if param["--complement"]:
				amount = float(api.Account.getBalance(ADDRESS, returnKey="balance"))/100000000. - amount

			if param["--lowest"]: minimum = float(param["--lowest"]) + cfg.__FEES__["send"]/100000000.
			else: minimum = cfg.__FEES__["send"]/100000000.

			if param["--highest"] : maximum = float(param["--highest"]) + cfg.__FEES__["send"]/100000000.
			else: maximum = amount

			if amount > 1:
				# get contributions of ech voters
				delay = int(param["--delay"])
				delegate_pubk = common.hexlify(PUBLICKEY)
				accounts = api.Delegate.getVoters(delegate_pubk, returnKey="accounts")
				addresses = [a["address"] for a in accounts] # + hidden
				sys.stdout.write("Checking %s-day-true-vote-weight in transaction history...\n" % delay)
				contribution = dict([address, stats.getVoteForce(address, days=delay, delegate_pubk=delegate_pubk)] for address in [addr for addr in addresses if addr not in blacklist])
				
				# apply filters
				C = sum(contribution.values())
				max_C = C*maximum/amount
				cumul = 0
				# first filter
				for address,force in [(a, f) for a, f in contribution.items() if f >= max_C]:
					contribution[address] = max_C
					cumul += force - max_C
				# report cutted share
				untouched_pairs = sorted([(a,f) for a, f in contribution.items() if 0. < f < max_C], key=lambda e: e[-1], reverse=True)
				n, i = len(untouched_pairs), 0
				bounty = cumul / n
				for address,force in untouched_pairs:
					if force + bounty > max_C:
						i += 1
						n -= 1
						contribution[address] = max_C
						cumul -= abs(max_C - force)
						bounty = cumul / n
					else:
						break
				for address,force in untouched_pairs[i:]:
					contribution[address] += bounty

				# apply contribution
				k = 1.0/max(1, sum(contribution.values()))
				contribution = dict((a, s*k) for a,s in contribution.items())
				txgen = lambda addr, amnt, msg: common.generateColdTx(KEY1, PUBLICKEY, KEY2, type=0, amount=amnt, recipientId=addr, vendorField=msg)
				pshare.applyContribution(USERNAME, amount, minimum, param["<message>"], txgen, **contribution)

		else:
			sys.stdout.write("Share feature not available\n")


# --------------
def _whereami():
	if USERNAME:
		return "delegate[%s]" % USERNAME
	else:
		return "delegate"


def _checkIfDelegate():
	global DELEGATE
	search = [d for d in api.Delegate.getCandidates() if d['publicKey'] == common.hexlify(PUBLICKEY)]
	if len(search):
		DELEGATE = search[0]
		return DELEGATE["username"]
	else:
		return None
