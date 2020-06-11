import os

from pathlib import Path
from netcfgbu.config_model import AppConfig, GithubSpec
import pexpect

git_bin = "git"


def git_config(user: str, gh_cfg: GithubSpec, configs_dir: Path):

    config_opts = (
        ("user.email", user),
        ("user.name", user),
        ("push.default", "matching"),
    )

    for cfg_opt, cfg_val in config_opts:
        output, rc = pexpect.run(
            command=f"{git_bin} config --local {cfg_opt} {cfg_val}",
            withexitstatus=True,
            cwd=configs_dir,
        )

        if rc != 0:
            raise RuntimeError(f"config {cfg_opt} failed: %s" % output.decode())


def git_clone(gh_cfg: GithubSpec, configs_dir: Path):
    user = gh_cfg.username or os.environ["USER"]
    token = gh_cfg.token.get_secret_value()

    repo_url = f"https://{user}@{gh_cfg.github}/{gh_cfg.repo}.git"

    # need to use pexpect to interact with the password prompt so we do not
    # store the token value as plaintext in the .git/config file.

    output, rc = pexpect.run(
        command=f"{git_bin} clone {repo_url} {str(configs_dir)}",
        cwd=configs_dir,
        withexitstatus=True,
        timeout=10,
        events={"Password for": token + "\n"},
    )

    if rc != 0:
        raise RuntimeError(output.decode())

    git_config(user, gh_cfg, configs_dir)


def git_init(gh_cfg: GithubSpec, configs_dir: Path):
    user = gh_cfg.username or os.environ["USER"]
    token = gh_cfg.token.get_secret_value()
    repo_url = f"https://{user}@{gh_cfg.github}/{gh_cfg.repo}.git"

    commands = ("init", f"remote add origin {repo_url}")

    for cmd in commands:
        output, rc = pexpect.run(
            command=f"{git_bin} {cmd}", cwd=configs_dir, withexitstatus=True
        )
        if rc != 0:
            raise RuntimeError(output.decode())

    # need to use pexpect to interact with the password prompt so we do not
    # store the token value as plaintext in the .git/config file.

    output, rc = pexpect.run(
        command=f"{git_bin} pull origin master",
        cwd=configs_dir,
        withexitstatus=True,
        events={"Password for": token + "\n"},
    )

    if rc != 0:
        raise RuntimeError(output.decode())

    git_config(user, gh_cfg, configs_dir)


def vcs_setup(app_cfg: AppConfig):
    configs_dir = Path(app_cfg.defaults.configs_dir).absolute()
    git_file = configs_dir.joinpath(".git", "config")
    gh_cfg = app_cfg.vcs["github"]

    is_empty = not any(configs_dir.iterdir())

    if is_empty:
        git_clone(gh_cfg, configs_dir)
        return

    if git_file.exists():
        # the git repo already exists
        return

    # configs_dir exists, is not empty, but not repo, so we need to setup
    git_init(gh_cfg, configs_dir)
