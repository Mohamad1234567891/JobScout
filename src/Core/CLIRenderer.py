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

Terminal output layer for the CLI.

Renders jobs and searches as clean Unicode-box tables (no external
dependencies), prints the per-job details behind verbose, and provides a
live-updating table that grows as jobs are streamed in while a search runs.
"""

import re
import shutil
import sys
import textwrap

# Per-column width limits for the job table.
_JOB_LIMITS = {"#": 5, "Accept %": 10, "Job Title": 34, "Company": 22,
               "Location": 20, "Posted": 12, "URL": 44}
_SEARCH_LIMITS = {"#": 5, "Job Title": 30, "Location": 18, "Workplace": 16,
                  "Interval": 9, "Jobs": 6, "New": 5}

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"


def terminal_width(default=110):
    """Returns the terminal width (falls back to a sane default)."""
    return shutil.get_terminal_size((default, 24)).columns


def is_tty():
    return sys.stdout.isatty()


def _visible(text):
    """Length of a string without the ANSI color codes."""
    return ANSI_RE.sub("", str(text))


def _colorize(text, color):
    if not is_tty():
        return text
    return f"\x1b[{color}m{text}{RESET}"


def _wrap(text, width):
    text = str(text)
    if not text:
        return [""]
    return textwrap.wrap(text, width=max(8, width)) or [""]


def _pad(text, width, right):
    pad = max(0, width - len(_visible(text)))
    return (" " * pad + text) if right else (text + " " * pad)


def _table_lines(headers, rows, limits=None, right_align=("#", "Accept %"), truncate=("URL",)):
    """Builds a Unicode-boxed table as a list of lines."""
    limits = limits or {}
    headers = [str(header) for header in headers]
    columns = len(headers)
    if not rows:
        rows = [["-"] * columns]

    # Natural width of every column, capped by its limit.
    widths = []
    for index, header in enumerate(headers):
        content_max = max(len(_visible(row[index])) if index < len(row) else 0 for row in rows)
        widths.append(max(len(header), content_max, 6))
        if header in limits:
            widths[-1] = min(widths[-1], limits[header])

    # Shrink the widest columns until the table fits the terminal.
    terminal = terminal_width()
    total = sum(widths) + 3 * (columns - 1) + 2
    if total > terminal:
        overflow = total - terminal
        for index in sorted(range(columns), key=lambda i: -widths[i]):
            if overflow <= 0:
                break
            reducible = max(0, widths[index] - 8)
            take = min(reducible, overflow)
            widths[index] -= take
            overflow -= take

    def render_row(cells, header_row=False):
        prepared = []
        for col in range(columns):
            text = str(cells[col] if col < len(cells) else "")
            if headers[col] in truncate and len(_visible(text)) > widths[col]:
                visible_text = _visible(text)
                text = visible_text[:max(1, widths[col] - 1)] + "…"
            prepared.append(text)
        lines = [_wrap(prepared[i], widths[i]) for i in range(columns)]
        height = max(len(line) for line in lines)
        output = []
        for line_index in range(height):
            parts = []
            for col in range(columns):
                text = lines[col][line_index] if line_index < len(lines[col]) else ""
                cell = _pad(text, widths[col], right=headers[col] in right_align)
                if header_row and is_tty():
                    cell = BOLD + cell + RESET
                parts.append(f" {cell} ")
            output.append("│" + "│".join(parts) + "│")
        return output

    top = "┌" + "┬".join("─" * (width + 2) for width in widths) + "┐"
    header_sep = "├" + "┼".join("─" * (width + 2) for width in widths) + "┤"
    row_sep = "├" + "┼".join("─" * (width + 2) for width in widths) + "┤"
    bottom = "└" + "┴".join("─" * (width + 2) for width in widths) + "┘"

    lines = [top]
    lines.extend(render_row(headers, header_row=True))
    lines.append(header_sep)
    for row_index, row in enumerate(rows):
        lines.extend(render_row(row))
        if row_index < len(rows) - 1:
            lines.append(row_sep)
    lines.append(bottom)
    return lines


def print_table(headers, rows, limits=None, right_align=("#", "Accept %")):
    """Prints a Unicode-boxed table that fits the terminal."""
    for line in _table_lines(headers, rows, limits, right_align):
        print(line)


def _heading(text):
    width = min(terminal_width(), len(text) + 4)
    bar = "─" * max(6, width)
    if is_tty():
        return BOLD + text + RESET + "\n" + DIM + bar + RESET
    return text + "\n" + bar


def _short(value, limit=44):
    value = str(value or "")
    return value if len(value) <= limit else value[:limit - 1] + "…"


def _accept_cell(job):
    percentage = job.get("match_percentage")
    if percentage is None:
        return _colorize("-", "90")
    text = f"{percentage:.0f}%"
    if percentage >= 70:
        color = "32"
    elif percentage >= 45:
        color = "33"
    else:
        color = "31"
    return _colorize(text, color)


def _job_row(index, job):
    return [
        str(index),
        _accept_cell(job),
        job.get("job_title") or "-",
        job.get("company_name") or "-",
        job.get("location") or "-",
        job.get("posted_date") or job.get("posted_time_ago") or "-",
        job.get("job_url") or "-",
    ]


def render_jobs_table(jobs, title=None):
    """Prints the found jobs as a table (the same info the GUI cards show).

    The Accept % column is the estimated likelihood that the user gets
    accepted at the job, based on how well their profile matches the posted
    requirements.
    """
    heading = f"Jobs for '{title}'" if title else "Job results"
    print()
    print(_heading(f"{heading} — {len(jobs)} found"))
    print()
    print_table(
        ["#", "Accept %", "Job Title", "Company", "Location", "Posted", "URL"],
        [_job_row(index, job) for index, job in enumerate(jobs, start=1)],
        limits=_JOB_LIMITS,
    )


def render_job_details(jobs):
    """Prints the full extracted requirements of every job (verbose only)."""
    print()
    for index, job in enumerate(jobs, start=1):
        print(f"─" * 78)
        print(f"#{index}  {job.get('job_title') or 'N/A'} — {job.get('company_name') or 'N/A'}")
        print(f"    URL: {job.get('job_url') or 'N/A'}")
        if job.get("match_percentage") is not None:
            print(f"    Estimated acceptance: {job['match_percentage']:.2f}%")
        if job.get("failed"):
            print("    (the job page could not be fetched - only listing data)")
            continue
        if job.get("requires_login"):
            print("    (requires a LinkedIn sign-in to view - only listing data)")
            continue

        def items(label, values, cap=5):
            values = values or []
            print(f"    {label}:")
            for value in values[:cap]:
                print(f"        - {value}")
            if len(values) > cap:
                print(f"        - ... (+{len(values) - cap} more)")

        items("Experience", job.get("experience_requirements"))
        items("Education", job.get("education_requirements"))
        items("Certificates", job.get("certificates"))
        skills = job.get("skills") or []
        if skills:
            print(f"    Skills: {', '.join(skills[:14])}"
                  + (f" ... (+{len(skills) - 14} more)" if len(skills) > 14 else ""))
        languages = job.get("languages") or []
        if languages:
            items("Languages", [f"{entry['language'].title()} ({entry.get('level') or 'required'})"
                                for entry in languages], cap=8)
        snippet = _short((job.get("experience_requirements") or [None])[0], 100)
        if snippet:
            print(f"    Requires: {snippet}")
    print("─" * 78)


def _location_label(space):
    """How the search location is shown in the searches table."""
    if space.location:
        return space.location
    if "remote" in {str(value).lower() for value in (space.workplace or [])}:
        return "Worldwide"
    return "Auto (city)"


def render_searches_table(searches):
    """Prints the recorded searches (title, location, workplace, interval...)."""
    print()
    print(_heading(f"Recorded searches — {len(searches)}"))
    print()
    print_table(
        ["#", "Job Title", "Location", "Workplace", "Interval", "Jobs", "New"],
        [
            [
                str(index),
                entry["space"].label,
                _location_label(entry["space"]),
                ", ".join(entry["space"].workplace) or "-",
                f"{entry['space'].check_interval_hours:g}h",
                str(len(entry.get("results") or [])),
                str(len(entry.get("new") or [])),
            ]
            for index, entry in enumerate(searches, start=1)
        ],
        limits=_SEARCH_LIMITS,
    )


def _job_sort_key(job):
    return (job.get("match_percentage") is None, -(job.get("match_percentage") or 0.0))


def _compact_row(index, job):
    """One-line job summary used while streaming into a non-TTY terminal."""
    percentage = job.get("match_percentage")
    accept = f"{percentage:.0f}%" if percentage is not None else "  -"
    title = _short(job.get("job_title"), 36)
    company = _short(job.get("company_name"), 22)
    location = _short(job.get("location"), 18)
    return f"  #{index:<3} {accept:>5}  {title} — {company} · {location}"


class LiveJobsTable:
    """A results table that grows while jobs stream in.

    On a real terminal it redraws itself in place every time a new job
    arrives; on a pipe it prints one compact line per job and the full table
    at the end (keeps logs readable).
    """

    def __init__(self, title=""):
        self.title = title
        self.rows = []
        self._tty = is_tty()
        self._lines_printed = 0

    def add(self, job):
        self.rows.append(job)
        self.rows.sort(key=_job_sort_key)
        if self._tty:
            self._redraw()
        else:
            print(_compact_row(len(self.rows), job), flush=True)

    def finish(self, jobs=None):
        """Draws the final table (the full job list, streaming completed)."""
        if jobs is not None:
            self.rows = list(jobs)
            self.rows.sort(key=_job_sort_key)
        if self._tty:
            self._redraw()
            print()
        else:
            render_jobs_table(self.rows, title=self.title)

    def _redraw(self):
        if self._lines_printed:
            sys.stdout.write(f"\033[{self._lines_printed}A")
        lines = [_heading(f"Jobs for '{self.title}' — {len(self.rows)} found so far"), ""]
        lines += _table_lines(
            ["#", "Accept %", "Job Title", "Company", "Location", "Posted", "URL"],
            [_job_row(index, job) for index, job in enumerate(self.rows, start=1)],
            limits=_JOB_LIMITS,
        )
        text = "\n".join(lines) + "\n"
        sys.stdout.write("\033[J" + text)
        sys.stdout.flush()
        self._lines_printed = text.count("\n")
