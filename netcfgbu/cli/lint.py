# def exec_lint(app_cfg, inventory):
#
#     lint_hosts = [
#         (rec, os_spec["linter"])
#         for rec in inventory
#         if "linter" in (os_spec := get_os_spec(rec, app_cfg))
#     ]
#
#     try:
#         configs_dir = Path(app_cfg["defaults"]["configs_dir"])
#     except IndexError:
#         configs_dir = Path().cwd()
#
#     log = get_logger()
#
#     report = Report()
#
#     report.start_timing()
#     for rec, linter in lint_hosts:
#         lint_spec = app_cfg["linters"][linter]
#         config_fileobj = configs_dir.joinpath(rec["host"] + ".cfg")
#         if not config_fileobj.exists():
#             log.warning(f"File not found: {config_fileobj.name}, skipping.")
#             report.task_results[False].append(
#                 (rec, FileNotFoundError(config_fileobj.name))
#             )
#             continue
#
#         try:
#             lint_file(config_fileobj, lint_spec)
#         except RuntimeWarning as exc:
#             log.warning(exc.args[0])
#             # do not count as failure
#             report.task_results[True].append((rec, exc))
#
#         log.info(f"LINTED: {config_fileobj.name}")
#         report.task_results[True].append((rec,))
#
#     report.stop_timing()
#     stop_aiologging()
#     report.print_report()

# -----------------------------------------------------------------------------
#                            Lint Commands
# -----------------------------------------------------------------------------

# TODO: Not included as the linting process is automatically done as
#       part of the get-config process.  That said, in the future we may
#       provide as --no-lint option for get-config and then provide
#       lint commands for User post-processing.
# @cli.command(name="lint", cls=WithInventoryCommand)
# @opt_config_file
# @opts_inventory
# @click.pass_context
# def cli_lint(ctx, **_cli_opts):
#     """
#     Remove unwanted content from network config files.
#     """
#     exec_lint(
#         app_cfg=ctx.obj["app_cfg"], inventory=ctx.obj["inventory_recs"],
#     )
