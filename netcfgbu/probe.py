"""
This module contains the probe corutine used to validate that a target device
has a given port open.
"""

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import asyncio


__all__ = ["probe"]


# -----------------------------------------------------------------------------
#
#                              CODE BEGINS
#
# -----------------------------------------------------------------------------


async def probe(host, port=22, timeout=10, raise_exc=False) -> bool:
    """
    Coroutine used to determine if a host port is online and available.

    Parameters
    ----------
    host: str
        The host name or IP address

    port: int
        The port to check, defaults to SSH(22)

    timeout: int
        The connect timeout in seconds.  If the probe done doen connect
        within this timeout then the probe returns False

    raise_exc: bool
        When the probe fails:
            When True the asyncio.TimeoutError will be raised
            When False, return False
    """

    loop = asyncio.get_running_loop()
    coro = loop.create_connection(asyncio.BaseProtocol, host=host, port=port)

    try:
        await asyncio.wait_for(coro, timeout=timeout)
        return True

    except asyncio.TimeoutError:
        if raise_exc:
            raise

    return False
