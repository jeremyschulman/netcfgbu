# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, AnyStr
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
    active_jumphosts = list()

    def __init__(self, spec: JumphostSpec):
        self._spec = spec
        self.filters = list()
        self._conn = None

    @property
    def tunnel(self):
        return self._conn

    async def connect(self):
        proxy_parts = urlparse("ssh://" + self._spec.proxy)

        conn_args = dict(host=proxy_parts.hostname, known_hosts=None)
        if proxy_parts.username:
            conn_args["username"] = proxy_parts.username

        if proxy_parts.port:
            conn_args["port"] = proxy_parts.port

        async def connect_to_jh():
            self._conn = await asyncssh.connect(**conn_args)

        await asyncio.wait_for(connect_to_jh(), timeout=self._spec.timeout)
        self.__class__.active_jumphosts.append(self)

    def filter(self, inv_rec):
        return any(_f(inv_rec) for _f in self.filters)


# -----------------------------------------------------------------------------
#
#                               CODE BEGINS
#
# -----------------------------------------------------------------------------


async def init_jumphosts(jumphosts: List[JumphostSpec], field_names=List[str]):
    try:
        for jh_spec in jumphosts:
            await create_jumphost_client(jh_spec, field_names)
    except asyncssh.Error:
        raise RuntimeError("Failed to connect to jumphost(s)")


async def create_jumphost_client(
    jh_spec: JumphostSpec, field_names: List[AnyStr]
) -> asyncssh.SSHClientConnection:

    log = get_logger()
    jh = JumpHost(jh_spec)

    try:
        await jh.connect()
        log.info(f"JUMPHOST: connected to {jh_spec.name}")
    except asyncssh.Error as exc:
        log.error(f"JUMPHOST: connect to {jh_spec.name} failed: {str(exc)}")
        raise

    if jh_spec.include:
        jh.filters.append(
            create_filter(
                constraints=jh_spec.include, field_names=field_names, include=True
            )
        )

    if jh_spec.exclude:
        jh.filters.append(
            create_filter(
                constraints=jh_spec.exclude, field_names=field_names, include=False
            )
        )


def get_jumphost(inv_rec: dict) -> Optional[JumpHost]:
    """
    Return the jumphost instance that is used to tunnel the connection
    for the given inventory record.  If this record does not require the
    use of a jumphost, then return None.
    """
    return first(jh for jh in JumpHost.active_jumphosts if jh.filter(inv_rec))
