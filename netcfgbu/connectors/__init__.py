from functools import lru_cache
from importlib import import_module

from .basic import BasicSSHConnector, set_max_startups


@lru_cache()
def get_connector_class(mod_cls_name=None):
    if not mod_cls_name:
        return BasicSSHConnector

    mod_name, _, cls_name = mod_cls_name.rpartition(".")
    mod_obj = import_module(mod_name)
    return getattr(mod_obj, cls_name)
