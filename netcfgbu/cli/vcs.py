import sys
from pathlib import Path


import click

from netcfgbu.config_model import AppConfig
from netcfgbu.vcs import github


from .root import cli, get_spec_nameorfirst, WithConfigCommand, opt_config_file

opt_vcs_name = click.option("--name", help="vcs name as defined in config file")


@cli.group(name="vcs")
def cli_vcs():
    """
    Version Control System subcommands.
    """
    pass


@cli_vcs.command(name="prepare", cls=WithConfigCommand)
@opt_config_file
@opt_vcs_name
@click.pass_context
def cli_vcs_setup(ctx, **cli_opts):
    """
    Prepare your system with the VCS repo.

    This command is used to setup your `configs_dir` as the VCS repository
    so that when you execute the backup process the resulting backup files
    can be stored in the VCS system.
    """

    app_cfgs: AppConfig = ctx.obj["app_cfg"]

    if not (spec := get_spec_nameorfirst(app_cfgs.vcs, cli_opts["name"])):
        cfgfile = ctx.params["config"].name
        sys.exit(f"No VCS found, check configuration file: {cfgfile}")

    repo_dir = Path(app_cfgs.defaults.configs_dir).absolute()
    github.vcs_prepare(spec, repo_dir=repo_dir)


@cli_vcs.command(name="update", cls=WithConfigCommand)
@opt_config_file
@opt_vcs_name
@click.pass_context
def cli_vcs_get(ctx, **cli_opts):
    """
    Update the VCS repository with changes to network config files.

    After you have run the config backup process you will need to push those
    changes into the VCS repository.  This command performs the necesssary
    steps to add changes to the repository and set a release tag.  The release
    tag by default is the timestamp in the form of
    "<year><month><day>_<hour><minute><second>"
    """
    app_cfgs: AppConfig = ctx.obj["app_cfg"]

    if not (spec := get_spec_nameorfirst(app_cfgs.vcs, cli_opts["name"])):
        cfgfile = ctx.params["config"].name
        sys.exit(f"No VCS found, check configuration file: {cfgfile}")

    repo_dir = Path(app_cfgs.defaults.configs_dir).absolute()
    github.vcs_update(spec, repo_dir=repo_dir)
