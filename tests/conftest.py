# pytest configuration file

import pytest


@pytest.fixture()
def fake_inventory_file(tmpdir):
    yield str(tmpdir.join("inventory.csv"))


@pytest.fixture()
def netcfgbu_envars(monkeypatch):
    monkeypatch.setenv("NETCFGBU_DEFAULT_USERNAME", "dummy-username")
    monkeypatch.setenv("NETCFGBU_DEFAULT_PASSWORD", "dummy-password")
    monkeypatch.setenv("NETCFGBU_INVENTORY", "/tmp/inventory.csv")
