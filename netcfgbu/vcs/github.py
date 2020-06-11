# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
import os
from pathlib import Path
from datetime import datetime

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import pexpect

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcfgbu.config_model import AppConfig, GithubSpec

git_bin = "git"


def tag_name_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class GitRunner(object):
    def __init__(self, config: GithubSpec, repo_dir):
        self.user = config.username or os.environ["USER"]
        self.config = config
        self.repo_dir = repo_dir
        self.git_file = repo_dir.joinpath(".git", "config")

    @property
    def repo_exists(self):
        return self.git_file.exists()

    @property
    def is_repo_empty(self):
        return not any(self.repo_dir.iterdir())

    def run_noauth(self, cmd: str):
        output, rc = pexpect.run(
            command=f"{git_bin} {cmd}",
            withexitstatus=True,
            cwd=self.repo_dir,
            encoding="utf-8",
        )

        if rc != 0:
            raise RuntimeError(f"git {cmd} failed: %s" % output)

        return output

    # run with auth is an alias to be created by subclass if needed
    run_auth = run_noauth

    def run(self, cmd: str, authreq=False):
        return [self.run_noauth, self.run_auth][authreq](cmd)  # noqa


class GitTokenRunner(GitRunner):
    def run_auth(self, cmd):
        output, rc = pexpect.run(
            command=f"{git_bin} {cmd}",
            cwd=self.repo_dir,
            withexitstatus=True,
            encoding="utf-8",
            events={"Password for": self.config.token.get_secret_value() + "\n"},
        )

        if rc != 0:
            raise RuntimeError(output)

        return output


def git_runner(gh_cfg: GithubSpec, repo_dir: Path) -> GitRunner:

    if gh_cfg.token:
        return GitTokenRunner(gh_cfg, repo_dir)

    raise RuntimeError("No github runner")


# -----------------------------------------------------------------------------
#
#
#
# -----------------------------------------------------------------------------


def git_config(ghr: GitRunner):
    config = ghr.config

    config_opts = (
        ("user.email", config.email or ghr.user),
        ("user.name", ghr.user),
        ("push.default", "matching"),
    )

    for cfg_opt, cfg_val in config_opts:
        ghr.run(f"config --local {cfg_opt} {cfg_val}")
        # output, rc = pexpect.run(
        #     command=f"{git_bin} config --local {cfg_opt} {cfg_val}",
        #     withexitstatus=True,
        #     cwd=ghr.repo_dir,
        # )
        #
        # if rc != 0:
        #     raise RuntimeError(f"git config {cfg_opt} failed: %s" % output.decode())


def git_clone(ghr: GitRunner):
    config = ghr.config

    repo_url = f"https://{ghr.user}@{config.github}/{config.repo}.git"

    # need to use pexpect to interact with the password prompt so we do not
    # store the token value as plaintext in the .git/config file.
    ghr.run(f"clone {repo_url} {str(ghr.repo_dir)}", authreq=True)
    # output, rc = pexpect.run(
    #     command=f
    #     cwd=configs_dir,
    #     withexitstatus=True,
    #     timeout=10,
    #     events={"Password for": token + "\n"},
    # )
    #
    # if rc != 0:
    #     raise RuntimeError(output.decode())

    git_config(ghr)


# def with_token(cmd, configs_dir, token):
#     output, rc = pexpect.run(
#         command=f"{git_bin} {cmd}",
#         cwd=configs_dir,
#         withexitstatus=True,
#         events={"Password for": token + "\n"},
#     )
#
#     if rc != 0:
#         raise RuntimeError(output.decode())
#
#
# def without_pw(cmd, configs_dir):
#     output, rc = pexpect.run(
#         command=f"{git_bin} {cmd}", cwd=configs_dir, withexitstatus=True
#     )
#     if rc != 0:
#         raise RuntimeError(output.decode())
#
#     return output.decode()


def git_init(ghr: GitRunner):
    user = ghr.config.username or os.environ["USER"]

    repo_url = f"https://{user}@{ghr.config.github}/{ghr.config.repo}.git"

    commands = (
        ("init", False),
        (f"remote add origin {repo_url}", False),
        ("pull origin master", True),
    )

    for cmd, req_auth in commands:
        ghr.run(cmd, req_auth)
    #     # output, rc = pexpect.run(
    #     #     command=f"{git_bin} {cmd}", cwd=configs_dir, withexitstatus=True
    #     # )
    #     # if rc != 0:
    #     #     raise RuntimeError(output.decode())
    #
    # # need to use pexpect to interact with the password prompt so we do not
    # # store the token value as plaintext in the .git/config file.
    #
    # output, rc = pexpect.run(
    #     command=f"{git_bin} pull origin master",
    #     cwd=configs_dir,
    #     withexitstatus=True,
    #     events={"Password for": token + "\n"},
    # )
    #
    # if rc != 0:
    #     raise RuntimeError(output.decode())

    git_config(ghr)


# -----------------------------------------------------------------------------
#
#                             Github VCS Entrypoints
#
# -----------------------------------------------------------------------------


def vcs_update(app_cfg: AppConfig, tag_name: Optional[str] = None) -> bool:

    ghr = git_runner(
        gh_cfg=app_cfg.vcs["github"],
        repo_dir=Path(app_cfg.defaults.configs_dir).absolute(),
    )

    if not tag_name:
        tag_name = tag_name_timestamp()

    output = ghr.run("status")
    if "nothing to commit, working directory clean" in output:
        return False

    commands = (
        ("add -A", False),
        (f"commit -m {tag_name}", False),
        ("push", True),
        (f"tag -a {tag_name} -m {tag_name}", False),
        ("push --tags", True),
    )

    for cmd, req_auth in commands:
        ghr.run(cmd, req_auth)

    return True


def vcs_setup(app_cfg: AppConfig):

    ghr = git_runner(
        app_cfg.vcs["github"], Path(app_cfg.defaults.configs_dir).absolute()
    )

    if ghr.is_repo_empty:
        git_clone(ghr)
        return

    if ghr.repo_exists:
        # the git repo already exists
        return

    # configs_dir exists, is not empty, but not repo, so we need to setup
    git_init(ghr)
