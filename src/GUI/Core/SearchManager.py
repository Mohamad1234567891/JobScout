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

Manages one search space in the GUI.

The initial (and manual "Search now") scrapes run in a worker thread here and
their results are persisted to the shared state file. The periodic background
re-checks are done by the detached daemon, so they continue even after the
GUI closes; a store poller in the window picks up the daemon's updates.

"""

import os
import time

from PySide6.QtCore import QObject, Signal

from src.Core import SharedState
from src.Core.Daemon import ensure_daemon_running
from src.Core.DataAnalysis.match_service import match_search_space_job
from src.Core.Notifications import notifier
from src.GUI.Core.ScrapeWorker import ScrapeWorker


class SearchManager(QObject):
    """Runs a search now and keeps its state in the shared store.

    The store entry carries a "pending_run" marker with the app's pid while
    a search is running: if the app is closed mid-search, the detached
    daemon detects the dead pid and finishes the remaining jobs itself.

    Emits:
        job_found(search_space, job)     - per job, the moment it is extracted
        search_finished(search_space, jobs) - after every completed run
        status_changed(search_space, message)  - progress updates
        failed(search_space, error)
    """

    job_found = Signal(object, dict)
    search_finished = Signal(object, list)
    status_changed = Signal(object, str)
    failed = Signal(object, str)

    def __init__(self, search_space, parent=None):
        super().__init__(parent)
        self.search_space = search_space
        self._worker = None
        self._ran_once = False

    # ------------------------------------------------------------------ API

    def run_search(self):
        """Starts a scraping run when none is already running."""
        if self._worker is not None and self._worker.isRunning():
            return
        entry = self._load_entry()
        entry["pending_run"] = True
        entry["runner_pid"] = os.getpid()
        self._save_entry(entry)

        self.status_changed.emit(self.search_space, "Searching LinkedIn...")
        self._worker = ScrapeWorker(self.search_space)
        self._worker.job_found.connect(self._on_job_found)
        self._worker.finished.connect(self._on_finished)
        self._worker.interrupted.connect(self._on_interrupted)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def shutdown(self, wait_ms=5000):
        """Stops a running search and waits (bounded) - called on window close.

        The pending_run marker stays in the store, so the daemon takes over
        and finishes the remaining jobs after the app is gone.
        """
        if self._worker is None:
            return
        if self._worker.isRunning():
            self._worker.request_stop()
            if not self._worker.wait(wait_ms):
                self._worker.terminate()
                self._worker.wait(1000)

    def is_monitoring(self):
        """True when the daemon re-checks this search in the background."""
        entry = SharedState.load_searches().get(self.search_space.key, {})
        return entry.get("monitoring", True)

    def set_monitoring(self, monitoring):
        """Pauses/resumes the daemon's background re-checks for this search."""
        entry = self._load_entry()
        entry["monitoring"] = bool(monitoring)
        self._save_entry(entry)

    def set_interval_hours(self, hours):
        """Changes how often the daemon re-checks this search."""
        self.search_space.check_interval_hours = max(0.05, float(hours or 1))
        entry = self._load_entry()
        entry["space"] = self.search_space.to_dict()
        self._save_entry(entry)

    # ------------------------------------------------------------- internals

    def _load_entry(self):
        saved = SharedState.load_searches().get(self.search_space.key, {})
        return {
            "space": self.search_space.to_dict(),
            "seen_ids": saved.get("seen_ids") or [],
            "results": saved.get("results") or [],
            "new": saved.get("new") or [],
            "last_checked": saved.get("last_checked"),
            "monitoring": saved.get("monitoring", True),
            "pending_run": saved.get("pending_run", False),
            "runner_pid": saved.get("runner_pid"),
            "first_run_completed": saved.get("first_run_completed",
                                             saved.get("last_checked") is not None),
        }

    def _save_entry(self, entry):
        SharedState.update_search(self.search_space.key, entry)

    def _on_job_found(self, search_space, job):
        """Scores a job the moment it arrives and streams it to the window."""
        result = match_search_space_job(search_space, job)
        job["match_percentage"] = result["match_percentage"]
        job["match_breakdown"] = result.get("breakdown") or {}
        self.job_found.emit(search_space, job)

    def _on_finished(self, search_space, jobs, stats):
        # Jobs were already scored as they streamed in; just sort them and
        # detect the new ones (compared against the stored ids).
        jobs.sort(key=lambda job: (job.get("match_percentage") is None,
                                   -(job.get("match_percentage") or 0.0)))

        entry = self._load_entry()
        seen_ids = set(entry["seen_ids"])
        new_jobs = []
        for job in jobs:
            job_id = job.get("job_id")
            if not job_id or job_id in seen_ids:
                continue
            seen_ids.add(job_id)
            if self._ran_once:  # the very first run is never a "new job" event
                job["is_new"] = True
                new_jobs.append(job)
        self._ran_once = True

        entry["seen_ids"] = sorted(seen_ids)
        entry["results"] = jobs[-100:]
        entry["new"] = new_jobs[:50]
        entry["last_checked"] = time.time()
        entry["pending_run"] = False
        entry["first_run_completed"] = True
        self._save_entry(entry)

        # Make sure the daemon exists so monitoring continues after closing.
        ensure_daemon_running()

        # A manual re-run that surfaced previously-unseen jobs is a real
        # "new jobs" event: notify, but only for those jobs.
        if new_jobs:
            notifier.notify_new_jobs(search_space.label, len(new_jobs))

        self.search_finished.emit(search_space, jobs)
        self.status_changed.emit(search_space, f"Found {len(jobs)} jobs")

    def _on_interrupted(self, search_space, jobs):
        """The search stopped early (window closing): persist what we have.

        The pending_run marker stays set, so the daemon detects our dead pid
        after the app exits and finishes the remaining jobs silently.
        """
        entry = self._load_entry()
        seen_ids = set(entry["seen_ids"])
        for job in jobs:
            job_id = job.get("job_id")
            if job_id:
                seen_ids.add(job_id)
        entry["seen_ids"] = sorted(seen_ids)
        entry["results"] = jobs[-100:]
        entry["new"] = []
        # pending_run and runner_pid stay as they are - the daemon takes over.
        self._save_entry(entry)

    def _on_failed(self, search_space, error):
        self.status_changed.emit(search_space, f"Search failed: {error}")
        self.failed.emit(search_space, error)
