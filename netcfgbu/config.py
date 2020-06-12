# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import toml

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .logger import setup_logging
from .config_model import AppConfig

__all__ = ["load"]


def validation_errors(filepath, errors):
    SP_4 = " " * 4
    as_human = ["Configuration errors", f"{SP_4}File:[{filepath}]"]

    for _err in errors:
        loc_str = ".".join(map(str, _err["loc"]))
        as_human.append(f"{SP_4}Section: [{loc_str}]: {_err['msg']}")

    return "\n".join(as_human)


def load(*, filepath=None, fileio=None) -> AppConfig:

    if filepath:
        app_cfg_file = Path(filepath)
        fileio = app_cfg_file.open()

    app_cfg = toml.load(fileio)

    setup_logging(app_cfg)

    app_defaults = app_cfg.get("defaults")
    if not app_defaults:
        app_cfg["defaults"] = dict(credentials={})

    try:
        cfg_obj = AppConfig.parse_obj(app_cfg)
    except ValueError as exc:
        raise RuntimeError(validation_errors(filepath=fileio.name, errors=exc.errors()))

    configs_dir: Path = cfg_obj.defaults.configs_dir
    if not configs_dir.is_dir():
        configs_dir.mkdir()

    return cfg_obj
