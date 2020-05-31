from functools import lru_cache
from importlib import import_module


@lru_cache()
def get_class(mod_cls):
    mod_name, _, cls_name = mod_cls.rpartition('.')
    mod_obj = import_module(mod_name)
    return getattr(mod_obj, cls_name)
