# pytest configuration file

import pytest
import logging
from pathlib import Path


@pytest.fixture()
def fake_inventory_file(tmpdir):
    yield str(tmpdir.join("inventory.csv"))


@pytest.fixture()
def netcfgbu_envars(monkeypatch):
    monkeypatch.setenv("NETCFGBU_DEFAULT_USERNAME", "dummy-username")
    monkeypatch.setenv("NETCFGBU_DEFAULT_PASSWORD", "dummy-password")
    monkeypatch.setenv("NETCFGBU_INVENTORY", "/tmp/inventory.csv")


class RecordsCollector(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture()
def log_vcr():
    lgr = logging.getLogger()
    lgr.setLevel(logging.DEBUG)
    lgr_vcr = RecordsCollector()
    lgr.handlers[0] = lgr_vcr
    return lgr


@pytest.fixture(scope="module")
def files_dir(request):
    return Path(request.module.__file__).parent / "files"
