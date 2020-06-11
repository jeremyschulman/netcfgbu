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


def load(*, filepath=None, fileio=None) -> AppConfig:

    if filepath:
        app_cfg_file = Path(filepath)
        fileio = app_cfg_file.open()

    app_cfg = toml.load(fileio)

    setup_logging(app_cfg)

    app_defaults = app_cfg.get("defaults")
    if not app_defaults:
        app_cfg["defaults"] = dict(credentials={})

    cfg_obj = AppConfig.parse_obj(app_cfg)
    configs_dir: Path = cfg_obj.defaults.configs_dir
    if not configs_dir.is_dir():
        configs_dir.mkdir()

    return cfg_obj
