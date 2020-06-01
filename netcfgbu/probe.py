import asyncio

__all__ = ['probe']


async def probe(host, port=22, timeout=10) -> bool:
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

    Returns
    -------
    bool:
        True when the host/port is online,
        False when the host/port is offline
    """

    loop = asyncio.get_running_loop()
    coro = loop.create_connection(asyncio.BaseProtocol, host=host, port=port)

    try:
        await asyncio.wait_for(coro, timeout=timeout)
        return True

    except asyncio.TimeoutError:
        pass

    return False
