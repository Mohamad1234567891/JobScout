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

Cross-platform desktop notifications for JobScout.

Uses the optional `desktop-notifier` package when it is installed (Windows,
macOS, Linux); falls back to a console line when it is missing or the
notification fails, so the rest of the app never breaks because of it.

"""


def send_notification(title, message):
    """Shows a desktop notification. Returns True when it was really shown."""
    try:
        from desktop_notifier.sync import DesktopNotifierSync

        notifier = DesktopNotifierSync(app_name="JobScout")
        notifier.send(title=title, message=message)
        return True
    except Exception:
        print(f"[JobScout] {title}: {message}")
        return False


def notify_new_jobs(search_title, count):
    """Notifies the user that a background search found new jobs."""
    if count <= 0:
        return False
    noun = "job" if count == 1 else "jobs"
    return send_notification(
        "New jobs found",
        f"JobScout found {count} new {noun} for '{search_title}'.",
    )


if __name__ == "__main__":
    send_notification("New Job Found", "JobScout found a new job for you!")
