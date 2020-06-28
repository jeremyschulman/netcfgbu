"""
This file contains the Version Control System (VCS) integration
using Git as the backend.   The following functions are exported
for use:

   * vcs_prepare:
      Used to prepare the repo directory for VCS use.

   * vcs_save:
      Used to save files in the repo directory into VCS and tag the collection
      with a release tag.

   * vcs_status:
      Used to show the current target status of file changes.

"""
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

from netcfgbu.logger import get_logger
from netcfgbu.config_model import GitSpec

git_bin = "git"


def tag_name_timestamp() -> str:
    """
    Create the tag name using the current time with
    format <year><month#><day#>_<24hr><minute><sec>
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")  # pragma: no cover


# -----------------------------------------------------------------------------
#
#                             Git VCS Entrypoints
#
# -----------------------------------------------------------------------------


def vcs_save(gh_cfg: GitSpec, repo_dir: Path, tag_name: Optional[str] = None) -> bool:
    logr = get_logger()
    logr.info(f"VCS update git: {gh_cfg.repo}")

    ghr = git_runner(gh_cfg, repo_dir)
    if not tag_name:
        tag_name = tag_name_timestamp()

    output = ghr.run("status")
    if "nothing to commit" in output:
        logr.info("VCS no changes, skipping")
        return False

    logr.info(f"VCS saving changes, tag={tag_name}")

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


def vcs_prepare(spec: GitSpec, repo_dir: Path):
    logr = get_logger()
    logr.info(f"VCS prepare git: {spec.repo}")

    ghr = git_runner(spec, repo_dir)
    ghr.git_init()
    ghr.git_pull()


def vcs_status(spec: GitSpec, repo_dir: Path):
    logr = get_logger()
    logr.info(
        f"""
VCS diffs git: {spec.repo}
             dir: {str(repo_dir)}
"""
    )

    ghr = git_runner(spec, repo_dir)
    return ghr.run("status")


# -----------------------------------------------------------------------------
#
#                      Git Runners to perform commands
#
# -----------------------------------------------------------------------------


class GitRunner(object):
    """
    The GitRunner class is used to peform the specific `git` command
    operations requested for the VCS use cases.
    """

    def __init__(self, config: GitSpec, repo_dir):
        self.user = config.username or os.environ["USER"]
        self.config = config
        self.repo_dir = repo_dir
        self.git_file = repo_dir.joinpath(".git", "config")

        parsed = urlsplit(config.repo)
        if parsed.scheme == "https":
            self.repo_url = f"https://{self.user}@{parsed.netloc}{parsed.path}"
        else:
            self.repo_url = config.repo

    @property
    def repo_exists(self):
        return self.git_file.exists()

    @property
    def is_dir_empty(self):
        return not any(self.repo_dir.iterdir())

    def run_noauth(self, cmd: str):
        """
        Run the git command that does not require any user authentication
        """
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

    def git_init(self):
        output = self.run("remote -v") if self.repo_exists else ""
        if self.repo_url not in output:
            commands = (("init", False), (f"remote add origin {self.repo_url}", False))

            for cmd, req_auth in commands:
                self.run(cmd, req_auth)

        self.git_config()

    def git_pull(self):
        self.run("pull origin master", authreq=True)

    def git_config(self):
        config = self.config

        config_opts = (
            ("user.email", config.email or self.user),
            ("user.name", self.user),
            ("push.default", "matching"),
        )

        for cfg_opt, cfg_val in config_opts:
            self.run(f"config --local {cfg_opt} {cfg_val}")

    def git_clone(self):
        self.run(f"clone {self.repo_url} {str(self.repo_dir)}", authreq=True)
        self.git_config()


class GitAuthRunner(GitRunner):
    """
    Git Runner that is used for either User/Password or Token cases
    """

    PASSWORD_PROMPT = "Password for"

    def _get_secret(self):
        return self.config.token.get_secret_value()

    def run_auth(self, cmd):
        output, rc = pexpect.run(
            command=f"{git_bin} {cmd}",
            cwd=self.repo_dir,
            withexitstatus=True,
            encoding="utf-8",
            events={self.PASSWORD_PROMPT: self._get_secret() + "\n"},
        )

        if rc != 0:
            raise RuntimeError(output)

        return output


class GitTokenRunner(GitAuthRunner):
    # use the default password prompt value
    pass


class GitDeployKeyRunner(GitRunner):
    """
    Git Runner used with deployment keys without passphrase
    """

    def git_config(self):
        super().git_config()
        ssh_key = str(Path(self.config.deploy_key).absolute())
        self.run(
            f"config --local core.sshCommand 'ssh -i {ssh_key} -o StrictHostKeyChecking=no'"
        )


class GitSecuredDeployKeyRunner(GitDeployKeyRunner, GitAuthRunner):
    """
    Git Runner used when deployment key has passphrase configured
    """

    PASSWORD_PROMPT = "Enter passphrase for key"

    def _get_secret(self):
        return self.config.deploy_passphrase.get_secret_value()


def git_runner(gh_cfg: GitSpec, repo_dir: Path) -> GitRunner:
    """
    Used to select the Git Runner based on the configuration file
    settings.
    """
    if gh_cfg.token:
        return GitTokenRunner(gh_cfg, repo_dir)

    elif gh_cfg.deploy_key:
        if not gh_cfg.deploy_passphrase:
            return GitDeployKeyRunner(gh_cfg, repo_dir)
        else:
            return GitSecuredDeployKeyRunner(gh_cfg, repo_dir)

    # Note: this is unreachable code since the config-model validation should
    # have ensured the proper fields exist in the spec.

    raise RuntimeError("Git config missing authentication settings")  # pragma: no cover
