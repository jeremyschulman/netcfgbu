import asyncio

import click

from netcfgbu.logger import get_logger, stop_aiologging
from netcfgbu.aiofut import as_completed
from netcfgbu.probe import probe

from .root import (
    cli,
    WithInventoryCommand,
    opt_config_file,
    opts_inventory,
    opt_timeout,
)

from .report import Report


def exec_probe(inventory, timeout=None):
    inv_n = len(inventory)
    log = get_logger()
    log.info(f"Checking SSH reachability on {inv_n} devices ...")

    tasks = dict()
    loop = asyncio.get_event_loop()

    tasks = {
        probe(
            rec.get("ipaddr") or rec.get("host"), timeout=timeout, raise_exc=True
        ): rec
        for rec in inventory
    }

    report = Report()

    async def proces_check():
        async for probe_task in as_completed(tasks):
            task_coro = probe_task.get_coro()
            rec = tasks[task_coro]

            try:
                probe_ok = probe_task.result()
                report.task_results[probe_ok].append((rec, probe_ok))

            except (asyncio.TimeoutError, OSError) as exc:
                probe_ok = False
                report.task_results[False].append((rec, exc))

            log.info(f"{rec['host']}: probe {'PASS' if probe_ok else 'FAIL'}")

    report.start_timing()
    loop.run_until_complete(proces_check())
    report.stop_timing()
    stop_aiologging()
    report.print_report()


@cli.command(name="probe", cls=WithInventoryCommand)
@opt_config_file
@opts_inventory
@opt_timeout
@click.pass_context
def cli_check(ctx, **cli_opts):
    """
    Probe device for SSH reachablility.

    The probe check determines if the device is reachable and the SSH port
    is available to receive connections.
    """
    exec_probe(ctx.obj["inventory_recs"], timeout=cli_opts["timeout"])
