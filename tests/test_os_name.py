from netcfgbu import os_specs
from netcfgbu import config
from netcfgbu.connectors import BasicSSHConnector


def test_os_name_pass(netcfgbu_envars):
    rec = {"host": "dummy", "os_name": "dummy"}
    app_cfg = config.load()

    conn = os_specs.make_host_connector(rec, app_cfg)

    assert isinstance(conn, BasicSSHConnector)
    assert conn.name == "dummy"
    creds_d = conn.creds[0]
    assert creds_d.username == "dummy-username"
    assert creds_d.password.get_secret_value() == "dummy-password"


def test_os_name_pass_namefound(netcfgbu_envars, request):
    filepath = str(request.fspath.dirname + "/files/test-config-os_name.toml")
    app_cfg = config.load(filepath=filepath)

    rec = {"host": "dummy", "os_name": "ios"}

    conn = os_specs.make_host_connector(rec, app_cfg)
    assert conn.os_spec.get_config == "fake show running-config"
