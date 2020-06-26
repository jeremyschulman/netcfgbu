import pytest  # noqa

from netcfgbu import connectors


def test_connectors_pass():
    conn_cls = connectors.get_connector_class()
    assert conn_cls == connectors.BasicSSHConnector


def test_connectors_pass_named():
    name = "netcfgbu.connectors.ssh.LoginPromptUserPass"
    conn_cls = connectors.get_connector_class(name)
    from netcfgbu.connectors.ssh import LoginPromptUserPass

    assert conn_cls == LoginPromptUserPass


def test_connectors_fail_named(tmpdir):
    with pytest.raises(ModuleNotFoundError):
        connectors.get_connector_class(str(tmpdir))
