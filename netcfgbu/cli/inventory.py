import sys
from collections import Counter
from operator import itemgetter
from textwrap import indent

import click
from tabulate import tabulate

from netcfgbu.config_model import AppConfig

from .root import (
    cli,
    get_spec_nameorfirst,
    WithInventoryCommand,
    WithConfigCommand,
    opt_config_file,
    opts_inventory,
)

from .report import LN_SEP, SPACES_4


# -----------------------------------------------------------------------------
#                                Inventory Commands
# -----------------------------------------------------------------------------


@cli.group(name="inventory")
def cli_inventory():
    """
    Inventory subcommands.
    """
    pass


@cli_inventory.command("list", cls=WithInventoryCommand)
@opt_config_file
@opts_inventory
@click.option("--brief", "-b", is_flag=True)
@click.pass_context
def cli_inventory_list(ctx, **cli_opts):
    inventory_recs = ctx.obj["inventory_recs"]
    os_names = Counter(rec["os_name"] for rec in inventory_recs)

    os_name_table = indent(
        tabulate(
            headers=["os_name", "count"],
            tabular_data=sorted(os_names.items(), key=itemgetter(1), reverse=True),
        ),
        SPACES_4,
    )

    print(LN_SEP)
    print(
        f"""
SUMMARY: TOTAL={len(inventory_recs)}

{os_name_table}
"""
    )

    if cli_opts["brief"] is True:
        return

    field_names = inventory_recs[0].keys()

    print(
        tabulate(
            headers=field_names, tabular_data=[rec.values() for rec in inventory_recs],
        )
    )


@cli_inventory.command("build", cls=WithConfigCommand)
@opt_config_file
@click.option("--name", "-n", help="inventory name as defined in config file")
@click.option("--brief", is_flag=True)
@click.pass_context
def cli_inventory_build(ctx, **cli_opts):
    """
    Build the inventory file.

    If the netcfgbu configuraiton file contains inventory definitions then you
    can use this command to the script to build the inventory.
    """
    from netcfgbu.inventory import build

    app_cfg: AppConfig = ctx.obj["app_cfg"]

    if not (spec := get_spec_nameorfirst(app_cfg.inventory, cli_opts["name"])):
        cfgfile = ctx.params["config"].name
        sys.exit(f"Inventory not defined in configuration file: {cfgfile}")

    build(spec)
