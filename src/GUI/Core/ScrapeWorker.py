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

Background thread that runs the scraping pipeline for one search space.

The scraper is asyncio-based (curl_cffi + Playwright), so the thread runs
its own event loop with asyncio.run - keeping the GUI responsive. Jobs are
streamed out one by one (job_found) so the cards appear while the search is
still running. The search location is resolved here (remote -> Worldwide,
otherwise the user's city is auto-detected) so the network/geo calls never
block the GUI thread.
"""

import asyncio
import threading

from PySide6.QtCore import QThread, Signal

from src.Core.DataAcquisition import scraper
from src.Core.DataAcquisition.LocationDetection import resolve_search_location


class ScrapeWorker(QThread):
    """Runs one scraping session and streams the extracted jobs as they come.

    When request_stop() is called (the window is closing), the search stops
    cooperatively after the current pages finish and emits `interrupted`
    with the jobs collected so far - the detached daemon then completes the
    remaining jobs in the background.
    """

    job_found = Signal(object, dict)          # search_space, job (the moment it is extracted)
    finished = Signal(object, list, object)   # search_space, jobs, stats
    interrupted = Signal(object, list)        # search_space, partial jobs (stopped early)
    failed = Signal(object, str)              # search_space, error message

    def __init__(self, search_space, parent=None):
        super().__init__(parent)
        self.search_space = search_space
        self._cancel_event = threading.Event()

    def request_stop(self):
        """Asks the running search to stop after the current pages finish."""
        self._cancel_event.set()

    def run(self):
        try:
            location = resolve_search_location(self.search_space.workplace,
                                               self.search_space.location)

            def on_job(job):
                # Runs inside this thread's event loop; Qt delivers the signal
                # to the GUI thread as a queued connection.
                self.job_found.emit(self.search_space, job)

            jobs, stats = asyncio.run(scraper.scrape_search_space(
                self.search_space.job_title,
                location=location,
                on_job=on_job,
                stop_check=self._cancel_event.is_set,
            ))

            if self._cancel_event.is_set():
                self.interrupted.emit(self.search_space, jobs)
            else:
                self.finished.emit(self.search_space, jobs, stats)
        except Exception as exc:  # never let a worker crash the app silently
            self.failed.emit(self.search_space, f"{type(exc).__name__}: {exc}")
