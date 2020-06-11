# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
import os
from urllib.parse import urlsplit
from pathlib import Path
from datetime import datetime

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import pexpect

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcfgbu.config_model import GithubSpec

git_bin = "git"


def tag_name_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class GitRunner(object):
    def __init__(self, config: GithubSpec, repo_dir):
        self.user = config.username or os.environ["USER"]
        self.config = config
        self.repo_dir = repo_dir
        self.git_file = repo_dir.joinpath(".git", "config")

        parsed = urlsplit(config.repo)
        if parsed.scheme == "https":
            self._mode = "https"
            self.repo_url = f"https://{self.user}@{parsed.netloc}{parsed.path}"
        else:
            self._mode = "ssh"
            self.repo_url = config.repo

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


def git_clone(ghr: GitRunner):
    ghr.run(f"clone {ghr.repo_url} {str(ghr.repo_dir)}", authreq=True)
    git_config(ghr)


def git_init(ghr: GitRunner):
    commands = (
        ("init", False),
        (f"remote add origin {ghr.repo_url}", False),
        ("pull origin master", True),
    )

    for cmd, req_auth in commands:
        ghr.run(cmd, req_auth)

    git_config(ghr)


# -----------------------------------------------------------------------------
#
#                             Github VCS Entrypoints
#
# -----------------------------------------------------------------------------


def vcs_update(
    gh_cfg: GithubSpec, repo_dir: Path, tag_name: Optional[str] = None
) -> bool:

    ghr = git_runner(gh_cfg, repo_dir)

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


def vcs_prepare(gh_cfg: GithubSpec, repo_dir: Path):

    ghr = git_runner(gh_cfg, repo_dir)

    if ghr.is_repo_empty:
        git_clone(ghr)
        return

    if ghr.repo_exists:
        # the git repo already exists
        return

    # repo directory exists and is not empty, but the .git/ is missing, so we
    # need to pull down the github repo to initialize the .git/ directory.

    git_init(ghr)
