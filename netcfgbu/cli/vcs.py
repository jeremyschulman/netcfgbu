import sys


import click

from netcfgbu import config as _config
from netcfgbu.config_model import AppConfig
from netcfgbu.vcs import git
from netcfgbu.logger import stop_aiologging

from .root import cli, get_spec_nameorfirst, opt_config_file

opt_vcs_name = click.option("--name", help="vcs name as defined in config file")


@cli.group(name="vcs")
def cli_vcs():
    """
    Version Control System subcommands.
    """
    pass


class VCSCommand(click.Command):
    def invoke(self, ctx):
        try:
            app_cfgs = ctx.obj["app_cfg"] = _config.load(fileio=ctx.params["config"])
            if not (spec := get_spec_nameorfirst(app_cfgs.git, ctx.params["name"])):
                cfgfile = ctx.params["config"].name
                sys.exit(f"No VCS found, check configuration file: {cfgfile}")

            ctx.obj["vcs_spec"] = spec

        except Exception as exc:
            ctx.fail(exc.args[0])

        super().invoke(ctx)
        stop_aiologging()


@cli_vcs.command(name="prepare", cls=VCSCommand)
@opt_config_file
@opt_vcs_name
@click.pass_context
def cli_vcs_setup(ctx, **_cli_opts):
    """
    Prepare your system with the VCS repo.

    This command is used to setup your `configs_dir` as the VCS repository
    so that when you execute the backup process the resulting backup files
    can be stored in the VCS system.
    """

    app_cfgs: AppConfig = ctx.obj["app_cfg"]
    git.vcs_prepare(ctx.obj["vcs_spec"], repo_dir=app_cfgs.defaults.configs_dir)


@cli_vcs.command(name="save", cls=VCSCommand)
@opt_config_file
@opt_vcs_name
@click.option("--tag-name", help="tag-release name")
@click.pass_context
def cli_vcs_get(ctx, **cli_opts):
    """
    Save changes into VCS repository.

    After you have run the config backup process you will need to push those
    changes into the VCS repository.  This command performs the necesssary
    steps to add changes to the repository and set a release tag.  The release
    tag by default is the timestamp in the form of
    "<year><month><day>_<hour><minute><second>"
    """
    app_cfgs: AppConfig = ctx.obj["app_cfg"]
    git.vcs_save(
        ctx.obj["vcs_spec"],
        repo_dir=app_cfgs.defaults.configs_dir,
        tag_name=cli_opts["tag_name"],
    )


@cli_vcs.command(name="status", cls=VCSCommand)
@opt_config_file
@opt_vcs_name
@click.pass_context
def cli_vcs_status(ctx, **_cli_opts):
    """
    Show VCS repository status.

    This command will show the status of the `configs_dir` contents so that you
    will know what will be changed before you run the `vcs save` command.
    """
    app_cfgs: AppConfig = ctx.obj["app_cfg"]
    output = git.vcs_status(ctx.obj["vcs_spec"], app_cfgs.defaults.configs_dir)
    print(output)
