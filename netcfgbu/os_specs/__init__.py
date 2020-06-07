from netcfgbu.connectors import get_connector_class


def get_os_spec(rec, app_cfg):
    os_name = rec["os_name"]
    return app_cfg.get("os_name", {}).get(os_name) or {}


def make_host_connector(rec, app_cfg):
    os_spec_def = get_os_spec(rec, app_cfg)
    conn_name = os_spec_def.get("connection")
    os_spec_cls = get_connector_class(conn_name)
    return os_spec_cls(host_cfg=rec, os_spec=os_spec_def, app_cfg=app_cfg)
