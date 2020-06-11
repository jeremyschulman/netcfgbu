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

    # for var_name, var_value in app_defaults.items():
    #     if isinstance(var_value, str):
    #         app_defaults[var_name] = expandvars(var_value)

    # load_creds(app_cfg)

    configs_dir = Path(cfg_obj.defaults.configs_dir).absolute()
    if not configs_dir.is_dir():
        configs_dir.mkdir()

    return cfg_obj


# TODO: remove
# def load_creds(app_cfg):
#     log = get_logger()
#
#     creds = list()
#
#     # default credentials
#
#     creds.append((app_cfg["defaults"]["credentials"],))
#
#     # global credentials [optional]
#
#     if gl_creds := app_cfg.get("credentials"):
#         creds.append(gl_creds)
#
#     # per os_name credentials
#
#     os_creds_list = set()
#     for os_name, os_spec in app_cfg.get("os_name").items():
#         if os_creds := os_spec.get("credentials"):
#             os_creds_list.add(os_name)
#             creds.append(os_creds)
#
#     # expand the used environment variables; checking to see if any are used
#     # that are defined in the Users in the environment.
#
#     for cred in chain.from_iterable(creds):
#         for key, value in cred.items():
#             new_value = cred[key] = expandvars(value)
#             if new_value.startswith("$") and new_value == value:
#                 msg = f'credential "{cred["username"]}" using undefined variable "{value}", aborting.'
#                 log.error(msg)
#                 raise RuntimeError(msg)
#
#     # now remove any credentials that did not expand correctly.
#
#     if gl_creds:
#         app_cfg["credentials"] = list(filter(None, gl_creds))
#
#     for os_name in os_creds_list:
#         app_cfg["os_name"][os_name]["credentials"] = list(
#             filter(None, app_cfg["os_name"][os_name]["credentials"])
#         )
