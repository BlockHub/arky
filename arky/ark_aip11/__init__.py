# -*- encoding: utf8 -*-
# © Toons

__all__ = []

from .. import rest
from .. import cfg

def init():
    network = rest.GET.api.loader.autoconfigure(returnKey="network")
    cfg.headers["version"] = network.pop("version")
    cfg.headers["nethash"] = network.pop("nethash")
    cfg.__dict__.update(network)
