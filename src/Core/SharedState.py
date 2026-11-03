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

Shared persistence for searches, used by the GUI, the CLI and the daemon.

Everything lives in one JSON file (~/.jobscout/searches.json) so all modes
see the same searches and the same results, and the daemon keeps the file
fresh while the apps are closed.

Entry format per search key:
    {
        "space":        JobSearchSpace.to_dict(),
        "seen_ids":     [job ids already seen],
        "results":      [latest scored job dicts],
        "new":          [jobs found by the last re-check],
        "last_checked": unix timestamp,
        "monitoring":   bool (whether the daemon re-checks this search),
    }

"""

import json
import os
import threading

STATE_DIR = os.path.join(os.path.expanduser("~"), ".jobscout")
STATE_PATH = os.path.join(STATE_DIR, "searches.json")

_lock = threading.RLock()


def _read():
    try:
        with open(STATE_PATH, encoding="utf-8") as file:
            data = json.load(file)
        return (data or {}).get("searches", {})
    except Exception:
        return {}


def load_searches():
    """Returns the stored searches as {key: entry-dict}."""
    with _lock:
        return _read()


def save_searches(searches):
    """Persists {key: entry-dict}. Best-effort: never raises."""
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        payload = {"searches": searches}
        with open(STATE_PATH, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def update_search(key, entry):
    """Updates (or inserts) one search entry and saves."""
    with _lock:
        searches = _read()
        searches[key] = entry
        return save_searches(searches)


def remove_search(key):
    with _lock:
        searches = _read()
        removed = searches.pop(key, None)
        save_searches(searches)
        return removed is not None


def mtime():
    """Modification time of the state file (None when it does not exist)."""
    try:
        return os.path.getmtime(STATE_PATH)
    except OSError:
        return None


def read_pid_file():
    try:
        with open(os.path.join(STATE_DIR, "daemon.pid"), encoding="utf-8") as file:
            return int(file.read().strip())
    except Exception:
        return None


def write_pid_file(pid):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(os.path.join(STATE_DIR, "daemon.pid"), "w", encoding="utf-8") as file:
            file.write(str(pid))
    except Exception:
        pass
