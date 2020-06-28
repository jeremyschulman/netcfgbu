"""

References
----------

Logging in asyncio applications
   https://bit.ly/36WWgrf
"""
from typing import Set
import sys
import asyncio
from queue import SimpleQueue as Queue

from logging.config import dictConfig
from logging import getLogger
import logging
import logging.handlers


__all__ = ["setup_logging", "get_logger", "stop_aiologging"]


_g_quelgr_listener: logging.handlers.QueueListener


class LocalQueueHandler(logging.handlers.QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)

        except asyncio.CancelledError:
            raise

        except asyncio.QueueFull:
            self.handleError(record)


def setup_logging_queue(logger_names) -> None:
    """
    Move log handlers to a separate thread.

    Replace all configured handlers with a LocalQueueHandler, and start a
    logging.QueueListener holding the original handlers.
    """
    global _g_quelgr_listener
    queue = Queue()
    handlers: Set[logging.Handler] = set()
    que_handler = LocalQueueHandler(queue)

    for lname in logger_names:
        lgr = logging.getLogger(lname)
        lgr.addHandler(que_handler)
        for h in lgr.handlers[:]:
            if h is not que_handler:
                lgr.removeHandler(h)
                handlers.add(h)

    _g_quelgr_listener = logging.handlers.QueueListener(
        queue, *handlers, respect_handler_level=True
    )
    _g_quelgr_listener.start()


def setup_logging(app_cfg):
    log_cfg = app_cfg.get("logging") or {}
    log_cfg["version"] = 1

    dictConfig(log_cfg)
    setup_logging_queue(log_cfg.get("loggers") or [])


def stop_aiologging():
    _g_quelgr_listener.stop()
    sys.stdout.flush()


def get_logger():
    return getLogger(__package__)
