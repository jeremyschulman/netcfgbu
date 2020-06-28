import pytest  # noqa
from first import first

from netcfgbu import inventory
from netcfgbu import config


def test_inventory_pass(request, monkeypatch, netcfgbu_envars):
    """
    Test the use-case where there is a small inventory file that is properlly
    formatted.  Load the entire inventory as one subtest.  Load a filtered
    set of records as another subtest.
    """
    inventory_fpath = f"{request.fspath.dirname}/files/test-small-inventory.csv"
    monkeypatch.setenv("NETCFGBU_INVENTORY", inventory_fpath)
    app_cfg = config.load()

    # all records
    inv_recs = inventory.load(app_cfg)
    assert len(inv_recs) == 6

    # filter records
    inv_recs = inventory.load(
        app_cfg, limits=["os_name=eos"], excludes=["host=switch1"]
    )
    assert len(inv_recs) == 1
    assert inv_recs[0]["host"] == "switch2"


def test_inventory_fail_nofilegiven(tmpdir, netcfgbu_envars):
    """
    Test the use-case where the inventory is given in configuration file,
    but the inventory file does not actually exist.
    """
    app_cfg = config.load()

    with pytest.raises(FileNotFoundError) as excinfo:
        inventory.load(app_cfg)

    errmsg = excinfo.value.args[0]
    assert "Inventory file does not exist" in errmsg


def test_inventory_pass_build(request, monkeypatch, netcfgbu_envars):
    """
    Test the use-case where the configuraiton contains an inventory build
    script.  The script exists, it runs without error.
    """
    files_dir = request.fspath.dirname + "/files"
    monkeypatch.setenv("SCRIPT_DIR", files_dir)
    config_fpath = files_dir + "/test-inventory-script-donothing.toml"
    app_cfg = config.load(filepath=config_fpath)
    inv_def = app_cfg.inventory[0]
    rc = inventory.build(inv_def)
    assert rc == 0


def test_inventory_fail_build_exitnozero(request, monkeypatch, netcfgbu_envars):
    """
    Test the use-case where the configuraiton contains an inventory build
    script.  The script exists, it runs but exists with non-zero return code.
    """
    files_dir = request.fspath.dirname + "/files"
    monkeypatch.setenv("SCRIPT_DIR", files_dir)
    config_fpath = files_dir + "/test-inventory-script-fails.toml"

    app_cfg = config.load(filepath=config_fpath)
    inv_def = app_cfg.inventory[0]
    rc = inventory.build(inv_def)

    assert rc != 0


def test_inventory_fail_build_noscript(request, netcfgbu_envars):
    """
    Test the use-case where the configuraiton contains an inventory build
    script.  The script exists, it runs without error.
    """
    config_fpath = f"{request.fspath.dirname}/files/test-inventory-noscript.toml"
    with pytest.raises(RuntimeError) as excinfo:
        config.load(filepath=config_fpath)

    exc_errmsgs = excinfo.value.args[0].splitlines()
    found = first([line for line in exc_errmsgs if "inventory.0.script" in line])
    assert found
    assert "field required" in found
