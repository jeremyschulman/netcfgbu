from typing import AsyncIterable, Iterable, Coroutine, Optional
import asyncio
from asyncio import Task

__all__ = ["as_completed"]


async def as_completed(
    aws: Iterable[Coroutine], timeout: Optional[int] = None
) -> AsyncIterable[Task]:
    """
    This async generator is used to "mimic" the behavior of the
    concurrent.futures.as_completed functionality. Usage of this as_completed
    generator is slightly different from the builtin asyncio version; see
    example below.

    The builtin asyncio.as_completed yields futures such that the originating
    coroutine can not be retrieved.  In order to obtain the originating
    coroutine these must be wrapped in futures as explained in this Stack
    Overflow: https://bit.ly/2AsPtJE

    Parameters
    ----------
    aws:
        An interable of coroutines that will be wrapped into futures and
        executed through the asyncio on_completed builtin.

    timeout: int
        (same as asyncio.as_completed):
        If provided an asyncio.TimeoutError will be raised if all of the
        coroutines have not completed within the timeout value.

    Yields
    ------
    asyncio.Task

    Examples:
    ---------

        # create a dictionary of key=coroutine, value=dict, where the value will
        # be used later when the coroutine completes

        tasks = {
            probe(rec.get('ipaddr') or rec.get('host')): rec
            for rec in inventory
        }

        async for probe_task in as_completed(tasks):
            try:
                # obtain the originating coroutine so we can use it as an index
                # into the tasks dictionary and obtain the associated inventory
                # record

                task_coro = probe_task.get_coro()
                rec = tasks[task_coro]

                # now obtain the coroutine return value using the `result`
                # method.

                probe_ok = 'OK' if probe_task.result() else 'FAIL'
                report[probe_ok].append(rec)

            except OSError as exc:
                probe_ok = 'ERROR'
                report['ERROR'].append((rec, exc))

            print(f"{rec['host']}: {probe_ok}")
    """
    loop = asyncio.get_running_loop()

    # The main gist is to "wrap" the coroutine into
    # "[futureW[futureO[coroutine]]]" where the outer futureW is what is handed
    # into the builtin asyncio.as_completed.  The inner futureO that wraps the
    # originating coroutine will call the futureW.set_result() when the
    # original futureO[coroutine] completes.  The call to set_result triggers
    # the event causing the futureW to be done, which is what results in the
    # builtin on_completed to yield the results.

    def wrap_coro(coro):
        fut = asyncio.ensure_future(coro)
        wrapper = loop.create_future()
        fut.add_done_callback(wrapper.set_result)
        return wrapper

    for next_completed in asyncio.as_completed(
        [wrap_coro(coro) for coro in aws], timeout=timeout
    ):
        yield await next_completed
