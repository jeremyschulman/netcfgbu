from .root import cli

from .inventory import cli_inventory  # noqa
from .probe import cli_check  # noqa
from .login import cli_login  # noqa
from .backup import cli_backup  # noqa
from .vcs import cli_vcs  # noqa


def run():
    cli(obj={})
