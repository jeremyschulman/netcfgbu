import os

from pathlib import Path
from subprocess import PIPE, run
from netcfgbu.config_model import AppConfig, GithubSpec

git_bin = "git"


def git_config(user: str, configs_dir: Path):

    run_args = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    args = [git_bin, "config", "--local", "user.email", user]
    run_args["cwd"] = str(configs_dir)
    proc = run(args, **run_args)
    assert proc.returncode == 0, "config user.email failed: %s" % proc.stderr

    args = [git_bin, "config", "--local", "user.name", user]
    proc = run(args, **run_args)
    assert proc.returncode == 0, "config user failed: %s" % proc.stderr

    args = [git_bin, "config", "--local", "push.default", "matching"]
    proc = run(args, **run_args)
    assert proc.returncode == 0, "config push.default failed: %s" % proc.stderr


def git_clone(gh_cfg: GithubSpec, configs_dir: Path):
    user = gh_cfg.username or os.environ["USER"]
    token = gh_cfg.token.get_secret_value()
    repo_url = f"https://{user}:{token}@{gh_cfg.github}/{gh_cfg.repo}.git"

    args = [git_bin, "clone", repo_url, str(configs_dir)]

    run_args = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    proc = run(args, **run_args)
    assert proc.returncode == 0, "failed to clone: %s" % proc.stderr

    git_config(user, configs_dir)


def git_init(gh_cfg: GithubSpec, configs_dir: Path):
    user = gh_cfg.username or os.environ["USER"]
    token = gh_cfg.token.get_secret_value()
    repo_url = f"https://{user}:{token}@{gh_cfg.github}/{gh_cfg.repo}.git"

    run_args = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True, cwd=configs_dir)
    args = [git_bin, "init"]

    proc = run(args, **run_args)
    assert proc.returncode == 0, "git init failed: %s" % proc.stderr

    args = [git_bin, 'remote', 'add', 'origin', repo_url]
    proc = run(args, **run_args)
    assert proc.returncode == 0, "git remote failed: %s" % proc.stderr

    args = [git_bin, 'pull', 'origin', 'master']
    proc = run(args, **run_args)
    assert proc.returncode == 0, "git pull failed: %s" % proc.stderr


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

