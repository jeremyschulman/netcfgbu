import pytest
from click.testing import CliRunner
from unittest.mock import Mock

from netcfgbu.cli import inventory


@pytest.fixture(autouse=True)
def _always(netcfgbu_envars):
    pass


@pytest.fixture()
def mock_build(monkeypatch):
    monkeypatch.setattr(inventory, "build", Mock())
    return inventory.build


def test_cli_inventory_fail_noinventoryfile():
    runner = CliRunner()

    # isolate the file system so it doesn't accidentally pickup the sample
    # "netcfgbu.toml" in the project directory.

    with runner.isolated_filesystem():
        res = runner.invoke(inventory.cli_inventory_list, obj={})

    assert res.exit_code != 0
    assert "Inventory file does not exist" in res.output


def test_cli_inventory_pass(files_dir, monkeypatch):
    test_cfg = files_dir.joinpath("test-inventory-script-donothing.toml")
    test_inv = files_dir.joinpath("test-small-inventory.csv")

    monkeypatch.setenv("NETCFGBU_INVENTORY", str(test_inv))
    monkeypatch.setenv("SCRIPT_DIR", str(files_dir))
    monkeypatch.setenv("NETCFGBU_CONFIG", str(test_cfg))

    runner = CliRunner()
    res = runner.invoke(inventory.cli_inventory_list, obj={})
    assert res.exit_code == 0


def test_cli_inventory_fail_limits_zero(files_dir, monkeypatch):
    test_inv = files_dir.joinpath("test-small-inventory.csv")
    monkeypatch.setenv("NETCFGBU_INVENTORY", str(test_inv))

    runner = CliRunner()
    res = runner.invoke(
        inventory.cli_inventory_list, obj={}, args=["--exclude", "os_name=.*"]
    )

    assert res.exit_code != 0
    assert "No inventory matching limits" in res.output


def test_cli_inventory_fail_limits_invalid(files_dir, monkeypatch):
    test_inv = files_dir.joinpath("test-small-inventory.csv")
    monkeypatch.setenv("NETCFGBU_INVENTORY", str(test_inv))

    runner = CliRunner()
    res = runner.invoke(
        inventory.cli_inventory_list, obj={}, args=["--limit", "foo=bar"]
    )

    assert res.exit_code != 0
    assert "Invalid filter expression" in res.output


def test_cli_inventory_fail_build():
    runner = CliRunner()
    res = runner.invoke(inventory.cli_inventory_build, obj={})
    assert res.exit_code != 0
    assert "Configuration file required for use with build subcommand" in res.output


def test_cli_inventory_pass_build(files_dir, mock_build: Mock, monkeypatch):
    test_cfg = files_dir.joinpath("test-inventory-script-donothing.toml")

    monkeypatch.setenv("SCRIPT_DIR", str(files_dir))
    monkeypatch.setenv("NETCFGBU_CONFIG", str(test_cfg))

    runner = CliRunner()
    res = runner.invoke(inventory.cli_inventory_build, obj={})

    assert res.exit_code == 0
    assert mock_build.called is True
    inv_spec = mock_build.mock_calls[0].args[0]
    assert inv_spec.script.endswith("do-nothing.sh")


def test_cli_inventory_pass_build_name(files_dir, mock_build: Mock, monkeypatch):
    test_cfg = files_dir.joinpath("test-inventory-script-donothing.toml")

    monkeypatch.setenv("SCRIPT_DIR", str(files_dir))
    monkeypatch.setenv("NETCFGBU_CONFIG", str(test_cfg))

    runner = CliRunner()
    res = runner.invoke(inventory.cli_inventory_build, obj={}, args=["--name=dummy"])
    assert res.exit_code == 0
    assert mock_build.called is True
    inv_spec = mock_build.mock_calls[0].args[0]
    assert inv_spec.name == "dummy"


def test_cli_inventory_fail_build_badname(files_dir, monkeypatch):
    test_cfg = files_dir.joinpath("test-inventory-script-donothing.toml")

    monkeypatch.setenv("SCRIPT_DIR", str(files_dir))
    monkeypatch.setenv("NETCFGBU_CONFIG", str(test_cfg))

    runner = CliRunner()
    res = runner.invoke(inventory.cli_inventory_build, obj={}, args=["--name=noexists"])
    assert res.exit_code != 0
    assert (
        "Inventory section 'noexists' not defined in configuration file" in res.output
    )
