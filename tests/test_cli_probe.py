import asyncio


import pytest
from click.testing import CliRunner
from unittest.mock import Mock
from asynctest import CoroutineMock
from netcfgbu.cli import probe


@pytest.fixture(autouse=True)
def _always(netcfgbu_envars, files_dir, monkeypatch):
    test_inv = files_dir.joinpath("test-small-inventory.csv")
    monkeypatch.setenv("NETCFGBU_INVENTORY", str(test_inv))


def test_cli_probe_pass(monkeypatch):
    mock_probe = Mock()
    monkeypatch.setattr(probe, "exec_probe", mock_probe)

    runner = CliRunner()
    res = runner.invoke(probe.cli_check, obj={})

    assert res.exit_code == 0
    assert mock_probe.called
    call_args = mock_probe.mock_calls[0].args
    inv_rec = call_args[0]
    assert len(inv_rec) == 6


def test_cli_probe_pass_exec(monkeypatch, log_vcr):
    mock_probe = CoroutineMock()
    monkeypatch.setattr(probe, "probe", mock_probe)
    monkeypatch.setattr(probe, "get_logger", Mock(return_value=log_vcr))

    runner = CliRunner()
    res = runner.invoke(probe.cli_check, obj={})
    assert res.exit_code == 0
    logs = log_vcr.handlers[0].records[1:]
    assert all("PASS" in log.msg for log in logs)


def test_cli_probe_fail_exec(monkeypatch, log_vcr):
    mock_probe = CoroutineMock()
    mock_probe.side_effect = asyncio.TimeoutError
    monkeypatch.setattr(probe, "probe", mock_probe)
    monkeypatch.setattr(probe, "get_logger", Mock(return_value=log_vcr))

    runner = CliRunner()
    res = runner.invoke(probe.cli_check, obj={})
    assert res.exit_code == 0
    logs = log_vcr.handlers[0].records[1:]
    assert all("FAIL" in log.msg for log in logs)
