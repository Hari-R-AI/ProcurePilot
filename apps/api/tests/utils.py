"""Backend test utilities and helpers."""

import asyncio
from typing import Callable, Awaitable


def run_async(coro: Awaitable):
    """Run async function in sync context."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)
