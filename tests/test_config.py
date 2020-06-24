from os import getenv
from io import StringIO


import pytest  # noqa
from first import first
import toml

from netcfgbu.config import load


def test_config_onlyenvars_pass(monkeypatch, netcfgbu_envars):
    """
    Execute a test where there is no configuration file.  In this
    case the NETCFGBU_<fieldname> environment variables must exist.
    """
    app_cfg = load()

    assert app_cfg.defaults.inventory == getenv("NETCFGBU_INVENTORY")
    assert app_cfg.defaults.credentials.username == getenv("NETCFGBU_DEFAULT_USERNAME")
    assert app_cfg.defaults.credentials.password.get_secret_value() == getenv(
        "NETCFGBU_DEFAULT_PASSWORD"
    )


def test_config_onlyenvars_fail_missing():
    """
    Execute a test where there is no configuration file.  Omit the default
    environment variables and ensure that an exception is raised as expected.
    """

    with pytest.raises(RuntimeError) as excinfo:
        load()

    exc_errmsg = excinfo.value.args[0]

    assert "defaults.inventory" in exc_errmsg
    assert "defaults.credentials.username" in exc_errmsg
    assert "defaults.credentials.password" in exc_errmsg


def test_config_onlyenvars_fail_bad_noinventory(monkeypatch):
    """
    Test the case where NETCFGBU_INVENTORY is set but empty, but the file does
    not exist; which would generate an exception message.
    """
    monkeypatch.setenv("NETCFGBU_INVENTORY", "")

    with pytest.raises(RuntimeError) as excinfo:
        load()

    exc_errmsgs = excinfo.value.args[0].splitlines()
    found = first([line for line in exc_errmsgs if "defaults.inventory" in line])
    assert found
    assert "inventory empty value not allowed" in found


def test_config_credentials_fail_missingvar(request, monkeypatch, fake_inventory_file):
    """
    Test the case where the [[credentials]] section is provided that uses
    an environment variable, and that environment variable is missing.
    """
    fileio = open(f"{request.fspath.dirname}/config_files/test-credentials.toml")

    with pytest.raises(RuntimeError) as excinfo:
        load(fileio=fileio)

    exc_errmsgs = excinfo.value.args[0].splitlines()
    found = first([line for line in exc_errmsgs if "credentials.0.password" in line])
    assert found
    assert 'Environment variable "ENABLE_PASSWORD" missing' in found


def test_config_credentials_fail_empytvar(request, monkeypatch, netcfgbu_envars):
    """
    Test the case where the [[credentials]] section is provided that uses an
    environment variable, and that environment variable exists, but it the
    empty-string.
    """

    fileio = open(f"{request.fspath.dirname}/config_files/test-credentials.toml")
    monkeypatch.setenv("ENABLE_PASSWORD", "")

    with pytest.raises(RuntimeError) as excinfo:
        load(fileio=fileio)

    exc_errmsgs = excinfo.value.args[0].splitlines()
    found = first([line for line in exc_errmsgs if "credentials.0.password" in line])
    assert found
    assert 'Environment variable "ENABLE_PASSWORD" empty' in found


def test_config_credentials_pass_usesvar(request, monkeypatch, netcfgbu_envars):
    """
    Test the case where the [[credentials]] section is provided that uses an
    environment variable, and that environment variable exists, and it is set
    to a non-empty value.
    """

    fileio = open(f"{request.fspath.dirname}/config_files/test-credentials.toml")
    monkeypatch.setenv("ENABLE_PASSWORD", "foobaz")
    app_cfg = load(fileio=fileio)
    assert app_cfg.credentials[0].password.get_secret_value() == "foobaz"


def test_config_git_pass(request, netcfgbu_envars, monkeypatch):
    """
    Test the case where a [[git]] section is properly configured.
    """
    monkeypatch.setenv("GIT_TOKEN", "fake-token")
    monkeypatch.setenv("GITKEY_PASSWORD", "fake-password")

    fileio = open(f"{request.fspath.dirname}/config_files/test-gitspec.toml")
    app_cfg = load(fileio=fileio)

    assert app_cfg.git[0].token.get_secret_value() == "fake-token"
    assert app_cfg.git[2].deploy_passphrase.get_secret_value() == "fake-password"


def test_config_git_fail_badrepo(request, netcfgbu_envars, monkeypatch):
    """
    Test the case where a [[git]] section has an improper GIT URL.
    """
    fileio = open(f"{request.fspath.dirname}/config_files/test-gitspec-badrepo.toml")
    with pytest.raises(RuntimeError) as excinfo:
        load(fileio=fileio)

    exc_errmsgs = excinfo.value.args[0].splitlines()
    found = first([line for line in exc_errmsgs if "git.0.repo" in line])
    assert found
    assert "Bad repo URL" in found


def test_config_inventory_pass(request, netcfgbu_envars):
    """
    Test the case where an [[inventory]] section is properly configured.
    """
    fileio = open(f"{request.fspath.dirname}/config_files/test-inventory.toml")
    load(fileio=fileio)


def test_config_inventory_fail_noscript(request, netcfgbu_envars):
    """
    Test the case where an [[inventory]] section defined a script, but the
    script does not actually exist.
    """
    fileio = open(f"{request.fspath.dirname}/config_files/test-inventory-fail.toml")
    with pytest.raises(RuntimeError) as excinfo:
        load(fileio=fileio)

    exc_errmsgs = excinfo.value.args[0].splitlines()
    found = first([line for line in exc_errmsgs if "inventory.0.script" in line])
    assert found
    assert "File not found:" in found


def test_config_inventory_fail_script_noexec(netcfgbu_envars, tmpdir):
    """
    Test the case where an [[inventory]] section defines a script, the script
    file exists, but the script file is not executable.
    """
    fake_script = tmpdir.join("dummy-script.sh")
    fake_script.ensure()

    config_data = {"inventory": [{"name": "foo", "script": str(fake_script)}]}

    strio = StringIO()
    strio.name = "fake-file"
    toml.dump(config_data, strio)
    strio.seek(0)

    with pytest.raises(RuntimeError) as excinfo:
        load(fileio=strio)

    exc_errmsgs = excinfo.value.args[0].splitlines()
    found = first([line for line in exc_errmsgs if "inventory.0.script" in line])
    assert found
    assert "is not executable" in found


def test_config_linter_pass(netcfgbu_envars, request):
    """
    Test the case where an [os_name] section defines a linter, and that
    linter exists; no errors expected.
    """
    fileio = open(f"{request.fspath.dirname}/config_files/test-linter.toml")
    app_cfg = load(fileio=fileio)

    assert app_cfg.os_name["ios"]
    assert app_cfg.os_name["ios"].linter == "ios"
    assert app_cfg.linters["ios"]


def test_config_linter_fail(netcfgbu_envars, request):
    """
    Test the case where an [os_name] section defines a linter, but that
    linter is not defined in the configuration.
    """
    fileio = open(f"{request.fspath.dirname}/config_files/test-linter-fail.toml")

    with pytest.raises(RuntimeError) as excinfo:
        load(fileio=fileio)

    exc_errmsgs = excinfo.value.args[0].splitlines()
    found = first([line for line in exc_errmsgs if "os_name" in line])
    assert 'OS spec "ios" using undefined linter "ios"' in found
