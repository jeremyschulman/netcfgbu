from logging.config import dictConfig
from aiologger import Logger
from functools import lru_cache
from aiologger.formatters.base import Formatter

_LOG_CONFIG = None


def setup_logging(app_cfg):
    global _LOG_CONFIG
    if log_cfg := app_cfg.get('logging'):
        log_cfg['version'] = 1
        dictConfig(log_cfg)
        _LOG_CONFIG = log_cfg


@lru_cache()
def get_logger():
    lgr_name = __package__

    try:
        std_ldr = _LOG_CONFIG['loggers'][lgr_name]
        std_hdr = _LOG_CONFIG['handlers'][std_ldr['handlers'][0]]
        fmt_name = std_hdr['formatter']
        std_fmt = _LOG_CONFIG['formatters'][fmt_name]
        fmt = std_fmt['format']

    except KeyError:
        fmt = None

    return Logger.with_default_handlers(
        name=__package__,
        formatter=Formatter(fmt)
    )
