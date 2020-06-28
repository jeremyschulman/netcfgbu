import click

from netcfgbu import config as _config
from netcfgbu.vcs import git
from netcfgbu.logger import stop_aiologging

from .root import cli, get_spec_nameorfirst, opt_config_file

opt_vcs_name = click.option("--name", help="vcs name as defined in config file")


@cli.group(name="vcs")
def cli_vcs():
    """
    Version Control System subcommands.
    """
    pass  # pragma: no cover


class VCSCommand(click.Command):
    def invoke(self, ctx):
        cfg_fileopt = ctx.params["config"]

        try:
            app_cfgs = ctx.obj["app_cfg"] = _config.load(fileio=cfg_fileopt)
            if not (spec := get_spec_nameorfirst(app_cfgs.git, ctx.params["name"])):
                err_msg = (
                    "No configuration file provided, required for vcs support"
                    if not cfg_fileopt
                    else f"No vcs config section found in configuration file: {cfg_fileopt.name}"
                )
                raise RuntimeError(err_msg)

            ctx.obj["vcs_spec"] = spec
            super().invoke(ctx)
            stop_aiologging()

        except Exception as exc:
            ctx.fail(exc.args[0])


@cli_vcs.command(name="prepare", cls=VCSCommand)
@opt_config_file
@opt_vcs_name
@click.pass_context
def cli_vcs_prepare(ctx, **_cli_opts):
    """
    Prepare your system with the VCS repo.

    This command is used to setup your `configs_dir` as the VCS repository
    so that when you execute the backup process the resulting backup files
    can be stored in the VCS system.
    """

    git.vcs_prepare(
        spec=ctx.obj["vcs_spec"], repo_dir=ctx.obj["app_cfg"].defaults.configs_dir
    )


@cli_vcs.command(name="save", cls=VCSCommand)
@opt_config_file
@opt_vcs_name
@click.option("--tag-name", help="tag-release name")
@click.pass_context
def cli_vcs_save(ctx, **cli_opts):
    """
    Save changes into VCS repository.

    After you have run the config backup process you will need to push those
    changes into the VCS repository.  This command performs the necesssary
    steps to add changes to the repository and set a release tag.  The release
    tag by default is the timestamp in the form of
    "<year><month><day>_<hour><minute><second>"
    """
    git.vcs_save(
        ctx.obj["vcs_spec"],
        repo_dir=ctx.obj["app_cfg"].defaults.configs_dir,
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
    output = git.vcs_status(
        spec=ctx.obj["vcs_spec"], repo_dir=ctx.obj["app_cfg"].defaults.configs_dir
    )
    print(output)
