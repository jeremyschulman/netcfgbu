from pathlib import Path
import os


from .logger import get_logger
from .filtering import create_filter
from .filetypes import CommentedCsvReader
from .config_model import AppConfig, InventorySpec


def load(app_cfg: AppConfig, limits=None, excludes=None):

    try:
        inventory_file = Path(app_cfg.defaults.inventory)
    except KeyError:
        raise RuntimeError("No inventory provided")

    if not inventory_file.exists():
        raise RuntimeError(
            f"Inventory file does not exist: {inventory_file.absolute()}"
        )

    iter_recs = CommentedCsvReader(inventory_file.open())
    field_names = iter_recs.fieldnames

    if limits:
        filter_fn = create_filter(constraints=limits, field_names=field_names)
        iter_recs = filter(filter_fn, iter_recs)

    if excludes:
        filter_fn = create_filter(
            constraints=excludes, field_names=field_names, include=False
        )
        iter_recs = filter(filter_fn, iter_recs)

    return list(iter_recs)


def build(inv_def: InventorySpec):
    lgr = get_logger()

    if not (script := inv_def.script):
        lgr.warning("No script defined for this inventory")
        return

    # script = expandvars(script)
    lgr.info(f"Executing script: [{script}]")

    # Note: if you want to check the pass/fail of this call os.system() will
    # return 0 or non-zero as the exit code from the underlying script.  There
    # is no exception handling.  If you want to do exception handling, then
    # you'll need to use subprocess.call in place of os.system.

    os.system(script)
