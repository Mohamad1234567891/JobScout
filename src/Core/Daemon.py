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

JobScout background daemon.

Keeps re-checking every recorded search (per its interval) even after the GUI
and the CLI are closed, sends desktop notifications for new jobs, and keeps
the shared state file fresh for the next app launch. When an app is closed
mid-search, the daemon detects it (through the pending_run marker and the
dead runner pid) and silently finishes the remaining jobs itself.

Run it directly with:  python -m src.Core.Daemon
Apps normally spawn it detached via ensure_daemon_running().
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

from src.Core.DataAcquisition import scraper
from src.Core.DataAcquisition.LocationDetection import resolve_search_location
from src.Core.DataAnalysis.match_service import match_search_space_job
from src.Core import SharedState
from src.Core.Notifications import notifier
from src.Core.SearchSpace import JobSearchSpace

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DAEMON_LOG = os.path.join(SharedState.STATE_DIR, "daemon.log")

# Seconds between "is anything due?" checks (override with
# JOBSCOUT_DAEMON_TICK for testing).
TICK_SECONDS = float(os.environ.get("JOBSCOUT_DAEMON_TICK", "60"))
MIN_INTERVAL_HOURS = 0.05  # 3 minutes - the smallest allowed re-check interval

# Windows process creation flags (a detached process without a console).
_WIN_DETACHED = 0x00000008
_WIN_NEW_GROUP = 0x00000200
_WIN_NO_WINDOW = 0x08000000
_WIN_STILL_ACTIVE = 259


def _is_pid_alive(pid):
    """Cross-platform check whether a process is still running."""
    if not pid:
        return False

    if sys.platform == "win32":
        try:
            import ctypes
            handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))
            if not handle:
                return False
            exit_code = ctypes.c_ulong()
            ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            ctypes.windll.kernel32.CloseHandle(handle)
            return bool(ok) and exit_code.value == _WIN_STILL_ACTIVE
        except Exception:
            return True  # cannot verify -> assume alive (conservative)

    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False

    # A zombie process (killed but not yet reaped) still answers kill(0);
    # treat it as dead on Linux (macOS reaps automatically).
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as stat_file:
            fields = stat_file.read().split()
            state = fields[2] if len(fields) > 2 else ""
            return state != "Z"
    except Exception:
        return True


def is_daemon_running():
    return _is_pid_alive(SharedState.read_pid_file())


def ensure_daemon_running():
    """Spawns the detached daemon when it is not already running.

    The daemon is detached from the calling process (a new session on
    POSIX, DETACHED_PROCESS on Windows), so it keeps running after the app
    closes - on Linux, macOS and Windows alike.

    Returns True when a daemon is running afterwards (either already, or
    freshly spawned).
    """
    if is_daemon_running():
        return True

    try:
        os.makedirs(SharedState.STATE_DIR, exist_ok=True)
        log_file = open(DAEMON_LOG, "a", encoding="utf-8")
        popen_kwargs = {}
        if sys.platform == "win32":
            popen_kwargs["creationflags"] = _WIN_DETACHED | _WIN_NEW_GROUP | _WIN_NO_WINDOW
        else:
            popen_kwargs["start_new_session"] = True  # detach: survives the parent app closing
        subprocess.Popen(
            [sys.executable, "-m", "src.Core.Daemon"],
            cwd=str(PROJECT_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=log_file,
            **popen_kwargs,
        )
    except Exception as exc:
        print(f"[!] Could not start the background monitor: {exc}")
        return False

    # Give it a moment to write its pid file.
    for _ in range(20):
        if is_daemon_running():
            return True
        time.sleep(0.1)
    return is_daemon_running()


async def _process(space):
    """Scrapes, scores and sorts the jobs of one search space."""
    location = resolve_search_location(space.workplace, space.location)
    jobs, _stats = await scraper.scrape_search_space(space.job_title, location=location)

    for job in jobs:
        result = match_search_space_job(space, job)
        job["match_percentage"] = result["match_percentage"]
        job["match_breakdown"] = result.get("breakdown") or {}

    jobs.sort(key=lambda job: (job.get("match_percentage") is None,
                               -(job.get("match_percentage") or 0.0)))
    return jobs


async def _check_all():
    """One pass: completes interrupted searches and re-checks due ones."""
    searches = SharedState.load_searches()
    now = time.time()

    for key, entry in searches.items():
        if not entry.get("monitoring", True):
            continue
        try:
            space = JobSearchSpace.from_dict(entry.get("space"))
        except Exception:
            continue
        if not space.job_title:
            continue

        # ------------------------------------------------------------------
        # Takeover: an app was closed mid-search (its pid is dead) while the
        # pending_run marker was still set. Finish the search here, silently
        # (no notifications for the completion of the very first run).
        # ------------------------------------------------------------------
        if entry.get("pending_run"):
            if _is_pid_alive(entry.get("runner_pid")):
                continue  # the app is still running the search itself

            try:
                jobs = await _process(space)
            except Exception as exc:
                print(f"[daemon] takeover search for '{space.label}' failed: "
                      f"{type(exc).__name__}: {exc}", flush=True)
                continue

            seen_ids = set(entry.get("seen_ids") or [])
            new_jobs = []
            first_run_completed = entry.get("first_run_completed",
                                            entry.get("last_checked") is not None)
            for job in jobs:
                job_id = job.get("job_id")
                if not job_id or job_id in seen_ids:
                    continue
                seen_ids.add(job_id)
                if first_run_completed:
                    job["is_new"] = True
                    new_jobs.append(job)

            entry["seen_ids"] = sorted(seen_ids)
            entry["results"] = jobs[-100:]
            entry["new"] = new_jobs[:50]
            entry["pending_run"] = False
            entry["first_run_completed"] = True
            entry["last_checked"] = now
            SharedState.update_search(key, entry)

            if new_jobs:
                notifier.notify_new_jobs(space.label, len(new_jobs))
                print(f"[daemon] completed the interrupted search for '{space.label}' - "
                      f"{len(new_jobs)} new job(s) since it was interrupted.", flush=True)
            else:
                print(f"[daemon] completed the interrupted search for '{space.label}' "
                      f"({len(jobs)} jobs).", flush=True)
            continue

        # ------------------------------------------------------------------
        # Normal scheduled re-check.
        # ------------------------------------------------------------------
        interval = max(MIN_INTERVAL_HOURS, float(space.check_interval_hours or 1))
        last = entry.get("last_checked") or 0
        if now - last < interval * 3600:
            continue

        try:
            jobs = await _process(space)
        except Exception as exc:
            print(f"[daemon] search for '{space.label}' failed: {type(exc).__name__}: {exc}",
                  flush=True)
            continue

        seen_ids = set(entry.get("seen_ids") or [])
        new_jobs = []
        for job in jobs:
            job_id = job.get("job_id")
            if not job_id or job_id in seen_ids:
                continue
            seen_ids.add(job_id)
            job["is_new"] = True
            new_jobs.append(job)

        entry["seen_ids"] = sorted(seen_ids)
        entry["results"] = jobs[-100:]
        entry["new"] = new_jobs[:50]
        entry["first_run_completed"] = True
        entry["last_checked"] = now
        SharedState.update_search(key, entry)

        if new_jobs:
            notifier.notify_new_jobs(space.label, len(new_jobs))
            print(f"[daemon] {len(new_jobs)} new job(s) for '{space.label}'.", flush=True)


async def _run():
    print(f"[daemon] JobScout monitor started (tick={TICK_SECONDS:g}s).", flush=True)
    while True:
        try:
            await _check_all()
        except Exception as exc:
            print(f"[daemon] cycle failed: {type(exc).__name__}: {exc}", flush=True)
        await asyncio.sleep(TICK_SECONDS)


def main():
    SharedState.write_pid_file(os.getpid())
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        print("[daemon] stopped.", flush=True)


if __name__ == "__main__":
    main()
