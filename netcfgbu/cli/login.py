import asyncio

import click

from netcfgbu.logger import get_logger, stop_aiologging
from netcfgbu.aiofut import as_completed
from netcfgbu.os_specs import make_host_connector
from netcfgbu.connectors import set_max_startups


from .root import (
    cli,
    WithInventoryCommand,
    opt_config_file,
    opts_inventory,
    opt_batch,
    opt_debug_ssh,
    opt_timeout,
)

from .report import Report, err_reason
from netcfgbu import jumphosts
from netcfgbu.config_model import AppConfig


def exec_test_login(app_cfg: AppConfig, inventory_recs, cli_opts):

    login_tasks = {
        make_host_connector(rec, app_cfg).test_login(timeout=cli_opts["timeout"]): rec
        for rec in inventory_recs
    }

    if (batch_n := cli_opts["batch"]) is not None:
        set_max_startups(batch_n)

    total = len(login_tasks)

    report = Report()
    done = 0
    log = get_logger()

    async def process_batch():
        nonlocal done

        if app_cfg.jumphost:
            await jumphosts.connect_jumphosts()

        async for task in as_completed(login_tasks):
            done += 1
            coro = task.get_coro()
            rec = login_tasks[coro]
            msg = f"DONE ({done}/{total}): {rec['host']} "
            try:
                if login_user := task.result():
                    log.info(msg + f"with user {login_user}")
                    report.task_results[True].append(rec)
                else:
                    reason = "all credentials failed"
                    log.warning(msg + reason)
                    report.task_results[False].append((rec, reason))

            except asyncio.TimeoutError as exc:
                log.warning(msg + "Timeout")
                report.task_results[False].append((rec, exc))

            except Exception as exc:
                report.task_results[False].append((rec, exc))
                log.error(msg + f": {err_reason(exc)}")

    loop = asyncio.get_event_loop()
    report.start_timing()
    loop.run_until_complete(process_batch())
    report.stop_timing()
    stop_aiologging()
    report.print_report()


@cli.command(name="login", cls=WithInventoryCommand)
@opt_config_file
@opts_inventory
@opt_timeout
@opt_batch
@opt_debug_ssh
@click.pass_context
def cli_login(ctx, **cli_opts):
    """
    Verify SSH login to devices.
    """

    exec_test_login(ctx.obj["app_cfg"], ctx.obj["inventory_recs"], cli_opts)
