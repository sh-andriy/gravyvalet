import asyncio
from itertools import chain
from typing import Awaitable


async def join[T](*awaitables: Awaitable[list[T]]) -> list[T]:
    return [*chain.from_iterable(await asyncio.gather(*awaitables))]
