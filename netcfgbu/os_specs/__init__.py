from netcfgbu.connectors import get_connector_class


def make_host_os_spec(rec, app_cfg):
    os_name = rec["os_name"]
    os_spec_def = app_cfg.get("os_name", {}).get(os_name) or {}
    conn_name = os_spec_def.get("connection")
    os_spec_cls = get_connector_class(conn_name)
    return os_spec_cls(host_cfg=rec, os_spec=os_spec_def, app_cfg=app_cfg)
