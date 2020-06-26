import asyncio
from unittest.mock import Mock

from asynctest import CoroutineMock  # noqa
import pytest  # noqa

from netcfgbu import probe


@pytest.mark.asyncio
async def test_probe_pass(monkeypatch):
    mock_asyncio = Mock()
    mock_asyncio.TimeoutError = asyncio.TimeoutError
    mock_wait_for = CoroutineMock()

    mock_asyncio.wait_for = mock_wait_for
    monkeypatch.setattr(probe, "asyncio", mock_asyncio)

    ok = await probe.probe(host="1.2.3.4")
    assert ok is True


@pytest.mark.asyncio
async def test_probe_pass_timeout(monkeypatch):
    mock_asyncio = Mock()
    mock_asyncio.TimeoutError = asyncio.TimeoutError
    mock_wait_for = Mock()

    mock_asyncio.wait_for = mock_wait_for

    def raises_timeout(coro, timeout):  # noqa
        raise asyncio.TimeoutError

    mock_wait_for.side_effect = raises_timeout
    monkeypatch.setattr(probe, "asyncio", mock_asyncio)

    ok = await probe.probe(host="1.2.3.4")
    assert ok is False


@pytest.mark.asyncio
async def test_probe_pass_raises_timeout(monkeypatch):
    mock_asyncio = Mock()
    mock_asyncio.TimeoutError = asyncio.TimeoutError
    mock_wait_for = Mock()

    mock_asyncio.wait_for = mock_wait_for

    def raises_timeout(coro, timeout):  # noqa
        raise asyncio.TimeoutError

    mock_wait_for.side_effect = raises_timeout
    monkeypatch.setattr(probe, "asyncio", mock_asyncio)

    with pytest.raises(asyncio.TimeoutError):
        await probe.probe(host="1.2.3.4", raise_exc=True)
