import logging


def setup_logging(app_cfg):
    if log_cfg := app_cfg.get('logging'):
        log_cfg['version'] = 1
        from logging.config import dictConfig
        dictConfig(log_cfg)


def get_logger():
    return logging.getLogger(__package__)
