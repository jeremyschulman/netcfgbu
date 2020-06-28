"""
This module contains the code providing jump host feature functionality
so that any device in inventory that requires a proxy server can use
the netcfgbu tool.
"""

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, Dict, AnyStr
import asyncio
from urllib.parse import urlparse

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import asyncssh
from first import first

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .config_model import JumphostSpec
from .filtering import create_filter
from .logger import get_logger


class JumpHost(object):
    """
    A JumpHost instance is used to provide a tunnel connection so that any
    device in the inventory that requires one can use it.
    """

    available = list()

    def __init__(self, spec: JumphostSpec, field_names: List[AnyStr]):
        """
        Prepare a jump host instance for potential use.  This method
        does not connect to the proxy system.
        Parameters
        ----------
        spec:
            The jumphost configuraiton

        field_names:
            List of inventory field names that are used to prepare any
            necessary filtering functionality
        """
        self._spec = spec
        self.filters = list()
        self._conn = None
        self._init_filters(field_names)

    @property
    def tunnel(self):
        """
        Returns the SSH client connection of the jump-host for use as `tunnel` when
        connecting to a target device.  If the SSH client does not exist, then raise
        a RuntimeError.
        """
        if not self.is_active:
            raise RuntimeError(
                f"Attempting to use JumpHost {self.name}, but not connected"
            )
        return self._conn

    @property
    def name(self):
        """ Returns the string-name of the jump host"""
        return self._spec.name

    @property
    def is_active(self):
        """ Return True if the jumphost is connected, False otherwise """
        return bool(self._conn)

    def _init_filters(self, field_names):
        """ Called only by init, prepares the jump host filter functions to later use """
        include, exclude = self._spec.include, self._spec.exclude
        if include:
            self.filters.append(
                create_filter(
                    constraints=include, field_names=field_names, include=True
                )
            )

        if exclude:
            self.filters.append(
                create_filter(
                    constraints=exclude, field_names=field_names, include=False
                )
            )

    async def connect(self):
        """
        Connects to the jumphost system so that it can be used later as the
        tunnel to connect to other devices.
        """
        proxy_parts = urlparse("ssh://" + self._spec.proxy)

        conn_args = dict(host=proxy_parts.hostname, known_hosts=None)
        if proxy_parts.username:
            conn_args["username"] = proxy_parts.username

        if proxy_parts.port:
            conn_args["port"] = proxy_parts.port

        async def connect_to_jh():
            """ obtain the SSH client connection """
            self._conn = await asyncssh.connect(**conn_args)

        await asyncio.wait_for(connect_to_jh(), timeout=self._spec.timeout)

    def filter(self, inv_rec):
        """
        This function returns True if this jump host is required to support the given
        inventory record.  Returns False otherwise.
        """
        return any(_f(inv_rec) for _f in self.filters)


# -----------------------------------------------------------------------------
#
#                               CODE BEGINS
#
# -----------------------------------------------------------------------------


def init_jumphosts(jumphost_specs: List[JumphostSpec], inventory: List[Dict]):
    """
    Initialize the required set of Jump Host instances so that they can be used
    when netcfgbu attempts to access devices that require the use of jump
    hosts.

    Parameters
    ----------
    jumphost_specs:
        List of jump host specs from the app config instance

    inventory:
        List of inventory records; these are used to determine which, if any,
        of the configured jump hosts are actually required for use given any
        provided inventory filtering.
    """
    field_names = inventory[0].keys()

    # create a list of jump host instances so that we can determine which, if
    # any, will be used during the execution of the command.

    jh_list = [JumpHost(spec, field_names=field_names) for spec in jumphost_specs]

    req_jh = {
        use_jh
        for rec in inventory
        if (use_jh := first(jh for jh in jh_list if jh.filter(rec)))
    }

    JumpHost.available = list(req_jh)


async def connect_jumphosts():
    """
    This coroutine is used to connect to all of the required jump host servers.  This
    should be called before attempting to run any of the SSH device tasks, such as
    login or backup.

    Returns
    -------
    True if all required jump host servers are connected.
    False otherwise; check log errors for details.
    """
    log = get_logger()
    ok = True

    for jh in JumpHost.available:
        try:
            await jh.connect()
            log.info(f"JUMPHOST: connected to {jh.name}")

        except (asyncio.TimeoutError, asyncssh.Error) as exc:
            errmsg = str(exc) or exc.__class__.__name__
            log.error(f"JUMPHOST: connect to {jh.name} failed: {errmsg}")
            ok = False

    return ok


def get_jumphost(inv_rec: dict) -> Optional[JumpHost]:
    """
    Return the jumphost instance that is used to tunnel the connection
    for the given inventory record.  If this record does not require the
    use of a jumphost, then return None.
    """
    return first(jh for jh in JumpHost.available if jh.filter(inv_rec))
