# -*- encoding: utf8 -*-
# © Toons

from .. import rest
from .. import cfg

def init():
    cfg.headers["version"] = rest.GET.api.peers.version(returnKey="version")
    cfg.headers["nethash"] = rest.GET.api.blocks.getNethash(returnKey="nethash")
