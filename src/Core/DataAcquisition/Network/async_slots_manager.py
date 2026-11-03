"""
This file is part of JobScout, an open-source job-search and job-match
engine that scrapes LinkedIn and scores every posting against your profile.

Copyright (c) 2026 Muhammed Bekiroğlu and the JobScout contributors.

Original JobScout repository: https://github.com/Mohamad1234567891/JobScout

Muhammed Bekiroğlu (JobScout team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

Asynchronous slot manager that limits how many tasks run at the same time.

Priority-based asynchronous slot manager. When
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
