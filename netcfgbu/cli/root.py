from importlib import metadata
from pathlib import Path

import click
from functools import reduce
from first import first

import netcfgbu
from netcfgbu import config as _config
from netcfgbu import inventory as _inventory
from netcfgbu import jumphosts


VERSION = metadata.version(netcfgbu.__package__)


# -----------------------------------------------------------------------------
#
#                           CLI Custom Click Commands
#
# -----------------------------------------------------------------------------


class WithConfigCommand(click.Command):
    def invoke(self, ctx):
        try:
            ctx.obj["app_cfg"] = _config.load(fileio=ctx.params["config"])
            super().invoke(ctx)

        except Exception as exc:
            ctx.fail(str(exc))


class WithInventoryCommand(click.Command):
    def invoke(self, ctx):

        try:
            app_cfg = ctx.obj["app_cfg"] = _config.load(fileio=ctx.params["config"])

            if debug_ssh_lvl := ctx.params.get("debug_ssh"):  # pragma: no cover
                from asyncssh import logging as assh_lgr
                import logging

                assh_lgr.set_log_level(logging.DEBUG)
                assh_lgr.set_debug_level(debug_ssh_lvl)

            if ctx.params["inventory"]:
                ctx.obj["app_cfg"].defaults.inventory = ctx.params["inventory"]

            inv = ctx.obj["inventory_recs"] = _inventory.load(
                app_cfg=app_cfg,
                limits=ctx.params["limit"],
                excludes=ctx.params["exclude"],
            )

            if not inv:
                raise RuntimeError(
                    f"No inventory matching limits in: {app_cfg.defaults.inventory}"
                )

            # if there is jump host configuraiton then prepare for later use.
            if app_cfg.jumphost:
                jumphosts.init_jumphosts(jumphost_specs=app_cfg.jumphost, inventory=inv)

            super().invoke(ctx)

        except Exception as exc:
            ctx.fail(str(exc))


# -----------------------------------------------------------------------------
#
#                                CLI Options
#
# -----------------------------------------------------------------------------


def get_spec_nameorfirst(spec_list, spec_name=None):
    if not spec_list:
        return None

    if not spec_name:
        return first(spec_list)

    return first(spec for spec in spec_list if getattr(spec, "name", "") == spec_name)


def check_for_default(ctx, opt, value):
    if value or Path("netcfgbu.toml").exists():
        return value

    return None


opt_config_file = click.option(
    "-C",
    "--config",
    envvar="NETCFGBU_CONFIG",
    type=click.File(),
    callback=check_for_default
    # required=True,
    # default="netcfgbu.toml",
)

# -----------------------------------------------------------------------------
# Inventory Options
# -----------------------------------------------------------------------------

opt_inventory = click.option(
    "--inventory", "-i", help="Inventory file-name", envvar="NETCFGBU_INVENTORY"
)

opt_limits = click.option(
    "--limit", "-l", "--include", multiple=True, help="limit/include in inventory",
)

opt_excludes = click.option(
    "--exclude", "-e", multiple=True, help="exclude from inventory",
)


def opts_inventory(in_fn_deco):
    return reduce(
        lambda _d, fn: fn(_d), [opt_inventory, opt_limits, opt_excludes], in_fn_deco
    )


opt_batch = click.option(
    "--batch",
    "-b",
    type=click.IntRange(1, 500),
    help="inevntory record processing batch size",
)

opt_timeout = click.option(
    "--timeout", "-t", help="timeout(s)", type=click.IntRange(0, 5 * 60)
)

opt_debug_ssh = click.option(
    "--debug-ssh", help="enable SSH debugging", type=click.IntRange(1, 3)
)


@click.group()
@click.version_option(version=VERSION)
def cli():
    pass  # pragma: no cover
