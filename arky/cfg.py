# -*- encoding: utf8 -*-
# © Toons

from . import ArkyDict, __PY3__
if __PY3__: import queue
else: import Queue as queue

__NET__ = ""
__NB_THREAD__ = 2
__LOG__ = queue.Queue()

# Global containers available for arky package
__NETWORK__ = ArkyDict()
__HEADERS__ = ArkyDict()
__URL_BASE__ = ""

# ARK fees according to transactions in SATOSHI
__FEES__ = ArkyDict({
	"send": 10000000,
	"vote": 100000000,
	"delegate": 2500000000,
	"secondsignature": 500000000,
	"multisignature": 500000000,
	"dapp": 2500000000
})
