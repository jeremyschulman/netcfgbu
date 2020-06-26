from pathlib import Path
import os


from .logger import get_logger
from .filtering import create_filter
from .filetypes import CommentedCsvReader
from .config_model import AppConfig, InventorySpec


def load(app_cfg: AppConfig, limits=None, excludes=None):

    inventory_file = Path(app_cfg.defaults.inventory)
    if not inventory_file.exists():
        raise FileNotFoundError(
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


def build(inv_def: InventorySpec) -> int:
    lgr = get_logger()

    # the script field is required so therefore it exists from
    # config-load-validation.

    script = inv_def.script
    lgr.info(f"Executing script: [{script}]")

    # Note: if you want to check the pass/fail of this call os.system() will
    # return 0 or non-zero as the exit code from the underlying script.  There
    # is no exception handling.  If you want to do exception handling, then
    # you'll need to use subprocess.call in place of os.system.

    rc = os.system(script)
    if rc != 0:
        lgr.warning(f"inventory script returned non-zero return code: {rc}")

    return rc
