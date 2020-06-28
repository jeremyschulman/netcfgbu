from pathlib import Path

from netcfgbu import config_model
from netcfgbu import linter


def test_linters_pass_content(files_dir):
    good_content = files_dir.joinpath("test-content-config.txt").read_text()
    lint_spec = config_model.LinterSpec(
        config_starts_after="!Time:", config_ends_at="! end-test-marker"
    )

    lint_content = (
        """\
!Command: show running-config
!Time: Sat Jun 27 17:54:17 2020
"""
        + good_content
        + """
! end-test-marker"""
    )

    result = linter.lint_content(lint_spec=lint_spec, config_content=lint_content)
    assert result == good_content


def test_liners_pass_file(files_dir, tmpdir):
    exp_content = files_dir.joinpath("test-content-config.txt").read_text()
    lint_spec = config_model.LinterSpec(
        config_starts_after="!Time:", config_ends_at="! end-test-marker"
    )

    tmp_file = Path(tmpdir.join("content"))
    tmp_file.write_text(
        """\
!Command: show running-config
!Time: Sat Jun 27 17:54:17 2020
"""
        + exp_content
        + """
! end-test-marker"""
    )

    linter.lint_file(tmp_file, lint_spec=lint_spec)
    linted_content = tmp_file.read_text()
    assert linted_content == exp_content


def test_liners_pass_nochange(files_dir, tmpdir, log_vcr, monkeypatch):
    exp_content = files_dir.joinpath("test-content-config.txt").read_text()
    lint_spec = config_model.LinterSpec(
        config_starts_after="!Time:", config_ends_at="! end-test-marker"
    )

    tmp_file = Path(tmpdir.join("content"))
    tmp_file.write_text(exp_content)

    monkeypatch.setattr(linter, "log", log_vcr)

    changed = linter.lint_file(tmp_file, lint_spec=lint_spec)

    assert changed is False
    linted_content = tmp_file.read_text()
    assert linted_content == exp_content
    last_log = log_vcr.handlers[0].records[-1].msg
    assert "LINT no change on content" in last_log
