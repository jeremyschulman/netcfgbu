from pathlib import Path
from unittest.mock import Mock
from operator import itemgetter

import pytest
from click.testing import CliRunner

from netcfgbu.cli import vcs


@pytest.fixture(scope="module")
def files_dir(request):
    return Path(request.module.__file__).parent.joinpath("files")


@pytest.fixture(scope="module")
def config_file(files_dir):
    return files_dir.joinpath("test-vcs.toml")


@pytest.fixture(autouse=True)
def _vcs_each_test(monkeypatch, netcfgbu_envars):
    # need to monkeypatch the logging to avoid a conflict with the Click test
    # runner also trying to stdout.
    monkeypatch.setenv("GIT_TOKEN", "dummy-token")
    monkeypatch.setattr(vcs, "stop_aiologging", Mock())


@pytest.fixture()
def mock_git(monkeypatch):
    # monkeypatch the git module so we can check the called parameters.
    monkeypatch.setattr(vcs, "git", Mock(spec=vcs.git))
    return vcs.git


def test_cli_vcs_fail_missingconfig_file():
    runner = CliRunner()

    # isolate the file system so it doesn't accidentally pickup the sample
    # "netcfgbu.toml" in the project directory.

    with runner.isolated_filesystem():
        res = runner.invoke(vcs.cli_vcs_status, obj={})

    assert res.exit_code != 0
    assert "No configuration file provided" in res.output


def test_cli_vcs_fail_missingconfig_section(files_dir, monkeypatch):

    # select a test inventory file that does not contain any vcs configuration
    cfg_file = files_dir.joinpath("test-config-logging.toml")

    runner = CliRunner()

    # isolate the file system so it doesn't accidentally pickup the sample
    # "netcfgbu.toml" in the project directory.

    with runner.isolated_filesystem():
        res = runner.invoke(vcs.cli_vcs_status, obj={}, args=["-C", str(cfg_file)])

    assert res.exit_code != 0
    assert "No vcs config section found" in res.output


def test_cli_vcs_pass_status(mock_git: Mock, config_file, monkeypatch):

    runner = CliRunner()
    res = runner.invoke(vcs.cli_vcs_status, obj={}, args=["-C", str(config_file)])

    assert res.exit_code == 0
    assert mock_git.vcs_status.called
    kwargs = mock_git.vcs_status.mock_calls[0].kwargs
    git_spec = kwargs["spec"]
    assert git_spec.repo == "git@dummy.git"
    assert git_spec.token.get_secret_value() == "dummy-token"


def test_cli_vcs_pass_prepare(mock_git: Mock, config_file, monkeypatch):
    # monkeypatch the git module so we can check the called parameters.
    monkeypatch.setenv("NETCFGBU_CONFIGSDIR", "/tmp/configs")

    runner = CliRunner()
    res = runner.invoke(vcs.cli_vcs_prepare, obj={}, args=["-C", str(config_file)])

    assert res.exit_code == 0
    assert mock_git.vcs_prepare.called
    kwargs = mock_git.vcs_prepare.mock_calls[0].kwargs
    git_spec, repo_dir = kwargs["spec"], kwargs["repo_dir"]
    assert git_spec.repo == "git@dummy.git"
    assert str(repo_dir) == "/tmp/configs"


def test_cli_vcs_pass_save_tag_notgiven(mock_git: Mock, config_file, monkeypatch):
    monkeypatch.setenv("NETCFGBU_CONFIGSDIR", "/tmp/configs")
    runner = CliRunner()
    res = runner.invoke(vcs.cli_vcs_save, obj={}, args=["-C", str(config_file)])

    assert res.exit_code == 0
    assert mock_git.vcs_save.called
    repo_dir, tag_name = itemgetter("repo_dir", "tag_name")(
        mock_git.vcs_save.mock_calls[0].kwargs
    )
    assert str(repo_dir) == "/tmp/configs"
    assert tag_name is None
