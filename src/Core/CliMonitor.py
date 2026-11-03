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

CLI client for searches.

The CLI records searches in the shared state file and runs the first search
itself; the detached daemon takes over the periodic re-checks afterwards
(including after the CLI exits). The daemon keeps the state file fresh, so
the CLI re-reads it before every command.

"""

import asyncio
import os
import time

from src.Core import SharedState
from src.Core.Daemon import ensure_daemon_running
from src.Core.DataAcquisition.LocationDetection import resolve_search_location
from src.Core.DataAcquisition import scraper
from src.Core.DataAnalysis.match_service import match_search_space_job
from src.Core.Notifications import notifier
from src.Core.SearchSpace import JobSearchSpace


class CliMonitor:
    """Thin client over the shared store + daemon."""

    def __init__(self):
        self.searches = {}  # key -> entry ({"space": ..., results, new, ...})
        self.refresh()

    # ------------------------------------------------------------- state sync

    def refresh(self):
        """Re-reads the shared state (the daemon may have updated it)."""
        stored = SharedState.load_searches()
        refreshed = {}
        for key, saved in stored.items():
            try:
                space = JobSearchSpace.from_dict(saved.get("space"))
            except Exception:
                continue
            if not space.job_title:
                continue
            refreshed[key] = {
                "space": space,
                "seen_ids": set(saved.get("seen_ids") or []),
                "results": saved.get("results") or [],
                "new": saved.get("new") or [],
                "last_checked": saved.get("last_checked"),
                "monitoring": saved.get("monitoring", True),
            }
        self.searches = refreshed
        return self.searches

    def _save_entry(self, key):
        entry = self.searches.get(key)
        if entry is None:
            return
        SharedState.update_search(key, {
            "space": entry["space"].to_dict(),
            "seen_ids": sorted(entry["seen_ids"]),
            "results": entry["results"][-100:],
            "new": entry["new"][:50],
            "last_checked": entry.get("last_checked"),
            "monitoring": entry.get("monitoring", True),
            "pending_run": entry.get("pending_run", False),
            "runner_pid": entry.get("runner_pid"),
            "first_run_completed": entry.get("first_run_completed",
                                             entry.get("last_checked") is not None),
        })

    # ------------------------------------------------------------- public API

    def entries(self):
        self.refresh()
        return list(self.searches.values())

    def add_search(self, space, run_now=True, on_job=None):
        """Records a search, runs it now, and makes sure the daemon monitors it.

        on_job, when given, is called with each job as it streams in.
        """
        key = space.key
        entry = self.searches.setdefault(key, {
            "space": space, "seen_ids": set(), "results": [], "new": [],
            "last_checked": None, "monitoring": True,
        })
        entry["space"] = space
        entry["monitoring"] = True
        entry["pending_run"] = True
        entry["runner_pid"] = os.getpid()
        self._save_entry(key)

        ensure_daemon_running()

        if run_now:
            self._run_once(key, on_job=on_job)

        return self.searches.get(key)

    def set_interval(self, key, hours):
        entry = self.searches.get(key)
        if entry is None:
            return False
        entry["space"].check_interval_hours = max(0.05, float(hours))
        self._save_entry(key)
        return True

    def set_monitoring(self, key, monitoring):
        entry = self.searches.get(key)
        if entry is None:
            return False
        entry["monitoring"] = bool(monitoring)
        self._save_entry(key)
        return True

    def remove(self, key):
        self.searches.pop(key, None)
        return SharedState.remove_search(key)

    def _run_once(self, key, on_job=None):
        """Blocking in-process search (first run / manual refresh).

        on_job, when given, is called with each job the moment it is
        extracted and scored - the CLI streams results through it.
        """
        entry = self.searches.get(key)
        if entry is None:
            return None
        space = entry["space"]
        first_run = entry.get("last_checked") is None

        try:
            jobs = asyncio.run(self._process(space, on_job=on_job))
        except Exception as exc:
            print(f"[!] Search for '{space.label}' failed: {type(exc).__name__}: {exc}")
            return None

        new_jobs = []
        for job in jobs:
            job_id = job.get("job_id")
            if not job_id or job_id in entry["seen_ids"]:
                continue
            entry["seen_ids"].add(job_id)
            if not first_run:
                job["is_new"] = True
                new_jobs.append(job)

        entry["results"] = jobs
        entry["new"] = new_jobs
        entry["last_checked"] = time.time()
        entry["pending_run"] = False
        entry["first_run_completed"] = True
        self._save_entry(key)

        if new_jobs:
            notifier.notify_new_jobs(space.label, len(new_jobs))
            print(f"\n[*] {len(new_jobs)} new job(s) for '{space.label}'.")
        return entry

    @staticmethod
    async def _process(space, on_job=None):
        location = resolve_search_location(space.workplace, space.location)

        async def _on_job(job):
            result = match_search_space_job(space, job)
            job["match_percentage"] = result["match_percentage"]
            job["match_breakdown"] = result.get("breakdown") or {}
            if on_job is not None:
                on_job(job)

        jobs, _stats = await scraper.scrape_search_space(space.job_title, location=location,
                                                          on_job=_on_job)

        jobs.sort(key=lambda job: (job.get("match_percentage") is None,
                                   -(job.get("match_percentage") or 0.0)))
        return jobs
