"""Asynchronous slot manager that limits how many tasks run at the same time.

Adapted from ShopWise's AsyncSlotsManager with standard Python naming. When
all slots are occupied, new tasks wait in a priority queue (smaller priority
number = higher priority; equal priorities run in arrival order).
"""

import heapq
import asyncio

from contextlib import asynccontextmanager

from src.Constants import constants


class AsyncSlotsManager:
    """Limits concurrent task slots; overflow tasks wait in a priority heap."""

    def __init__(self, max_slots):
        self.free = max_slots
        self.waiting = []  # heap of (priority, arrival number, future)
        self.arrivals = 0

    @asynccontextmanager
    async def use_slot(self, priority=constants.NOW):
        """Takes a free slot, or queues the task until one is released.

        Args:
            priority: Int priority; smaller is higher.
        """
        if self.free > 0 and not self.waiting:
            self.free -= 1
        else:
            future = asyncio.get_running_loop().create_future()
            self.arrivals += 1
            heapq.heappush(self.waiting, (priority, self.arrivals, future))
            try:
                await future
            except asyncio.CancelledError:
                if future.done() and not future.cancelled():
                    self.release()  # the slot was handed over just as this task was cancelled
                else:
                    # Still queued: mark the future cancelled so release() skips it.
                    # Without this, release() hands the slot to a dead task and
                    # that slot is leaked forever, eventually deadlocking the app.
                    future.cancel()
                raise
        try:
            yield
        finally:
            self.release()

    def release(self):
        """Starts the next waiting task, or returns a slot if none wait."""
        while self.waiting:
            future = heapq.heappop(self.waiting)[2]
            if not future.done():  # skip cancelled futures
                future.set_result(True)
                return

        self.free += 1
