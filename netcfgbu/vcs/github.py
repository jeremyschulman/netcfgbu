import os

from pathlib import Path
from subprocess import Popen, PIPE, run
from netcfgbu.config_model import AppConfig


def vcs_open(app_cfg: AppConfig):
    user = os.environ["USER"]
    gh_cfg = app_cfg.vcs["github"]
    token = gh_cfg.token.get_secret_value()

    configs_dir = Path(app_cfg.defaults.configs_dir).absolute()
    git_file = configs_dir.joinpath(".git", "config")

    git_bin = "git"

    if not git_file.exists():
        repo_url = f"https://{user}:{token}@{gh_cfg.github}/{gh_cfg.repo}.git"

        args = [git_bin, "clone", repo_url, str(configs_dir)]
        run_args = dict(universal_newlines=True)
        proc = run(args, **run_args)
        assert proc.returncode == 0, "failed to clone: %s" % proc.stderr

        args = [git_bin, "config", '--local', "user.email", user]
        run_args['cwd'] = str(configs_dir)
        proc = run(args, **run_args)
        assert proc.returncode == 0, "config user.email failed: %s" % proc.stderr

        args = [git_bin, "config", '--local', "user.name", user]
        proc = run(args, **run_args)
        assert proc.returncode == 0, "config user failed: %s" % proc.stderr

        args = [git_bin, "config", '--local', "push.default", "matching"]
        proc = run(args, **run_args)
        assert proc.returncode == 0, "config push.default failed: %s" % proc.stderr
