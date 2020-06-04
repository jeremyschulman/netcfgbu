from functools import lru_cache
from importlib import import_module

_default_ssh_connection_name = __package__ + ".netcfgbu_ssh.ConfigBackupSSHSpec"


@lru_cache()
def get_class(mod_cls):
    mod_name, _, cls_name = mod_cls.rpartition(".")
    mod_obj = import_module(mod_name)
    return getattr(mod_obj, cls_name)


def make_host_os_spec(rec, app_cfg):
    os_name = rec["os_name"]
    os_spec_def = app_cfg.get("os_specs", {}).get(os_name) or {}
    conn_name = os_spec_def.get("connection") or _default_ssh_connection_name
    os_spec_cls = get_class(conn_name)
    return os_spec_cls(host_cfg=rec, os_spec=os_spec_def, app_cfg=app_cfg)
