from pathlib import Path

from .filtering import create_filter
from .filetypes import CommentedCsvReader


def load(app_cfg, limits=None, excludes=None):

    inventory_file = Path(app_cfg["defaults"]["inventory"])
    if not inventory_file.exists():
        raise RuntimeError(
            f"Inventory file does not exist: {inventory_file.absolute()}"
        )

    iter_recs = CommentedCsvReader(inventory_file.open())

    if limits:
        filter_fn = create_filter(constraints=limits)
        iter_recs = filter(filter_fn, iter_recs)

    if excludes:
        filter_fn = create_filter(constraints=excludes, include=False)
        iter_recs = filter(filter_fn, iter_recs)

    return list(iter_recs)
