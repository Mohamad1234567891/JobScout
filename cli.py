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

JobScout entry point.

    python cli.py gui                        -> opens the GUI
    python cli.py "AI Engineer"              -> CLI search (recorded + monitored)
    python cli.py "AI Engineer" -s "Python" -e 4 -v
    python cli.py --list                     -> list the recorded searches
    python cli.py --show "AI Engineer"       -> show its latest results
    python cli.py --show 1 -v                -> same, with full details
    python cli.py --remove "AI Engineer"     -> stop tracking that search

Searches are recorded in the shared state file (~/.jobscout/searches.json),
monitored by a detached daemon that keeps running after JobScout closes, and
new jobs trigger a desktop notification. The GUI and the CLI share the same
state, so searches created in one mode appear in the other.

CLI commands: list | show <n|title> | search <title> | interval <n> <hours> |
pause <n|title> | resume <n|title> | remove <n|title> | gui | help | exit

"""

import argparse

from src.Constants import job_vocabulary as vocab
from src.Core import CLIRenderer
from src.Core.CliMonitor import CliMonitor
from src.Core.DataAcquisition import settings
from src.Core.SearchSpace import JobSearchSpace

_LANGUAGE_LEVELS = {"basic", "conversational", "fluent", "native"}
_WORKPLACE_OPTIONS = {"remote", "hybrid", "on-site", "onsite"}
_EDUCATION_LEVELS = {"high school", "associate", "bachelor", "master", "phd"}


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="JobScout",
        description="Search LinkedIn jobs and estimate how likely you are to be "
                    "accepted at each one. Pass 'gui' as the query for the interface.",
    )
    parser.add_argument("query", nargs="?", help="job title to search, or 'gui'")

    # Search settings (editable through CLI arguments)
    parser.add_argument("-l", "--location", default=None,
                        help="search location (auto-detected unless the search is remote)")
    parser.add_argument("-w", "--workplace", default=None,
                        help="comma-separated workplace preference: Remote, Hybrid, On-site")
    parser.add_argument("-i", "--interval", type=float, default=1.0,
                        help="background re-check interval in hours (default: 1)")
    parser.add_argument("-t", "--timeout", type=int, default=None,
                        help="seconds allowed for one scraping session")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the full extracted requirements of every job")

    # Profile arguments (enable the acceptance estimate)
    parser.add_argument("-e", "--experience", type=float, default=None,
                        help="your years of professional experience")
    parser.add_argument("-D", "--experience-domain", default=None,
                        help="comma-separated domains your experience is in")
    parser.add_argument("-d", "--education", type=str.lower, default=None,
                        choices=sorted(_EDUCATION_LEVELS),
                        help="your highest education level")
    parser.add_argument("-f", "--field", default=None, help="your field of study")
    parser.add_argument("-s", "--skills", default=None, help="comma-separated skills")
    parser.add_argument("-c", "--certificates", default=None, help="comma-separated certificates")
    parser.add_argument("-L", "--languages", default=None,
                        help="comma-separated Language:level pairs (e.g. English:fluent)")

    # Option browsing
    parser.add_argument("--list-options", choices=["skills", "certificates", "languages",
                                                   "education", "workplace"],
                        help="print the predefined options of a category and exit")

    # One-shot actions (run and exit, no interactive shell)
    parser.add_argument("--list", action="store_true", dest="list_searches",
                        help="list the recorded searches and exit")
    parser.add_argument("--show", metavar="SEARCH", dest="show_search", default=None,
                        help="show the latest results of a recorded search "
                             "(by number or title) and exit")
    parser.add_argument("--remove", metavar="SEARCH", dest="remove_search", default=None,
                        help="stop tracking a recorded search (by number or title) and exit")

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Parsing + validation of the profile arguments
# ---------------------------------------------------------------------------

def _split_csv(value):
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def _report_invalid(label, invalid, options):
    print(f"[!] Unknown {label}: {', '.join(invalid)}")
    shown = sorted({vocab.display_name(option) for option in options})
    preview = ", ".join(shown[:15])
    if len(shown) > 15:
        preview += f" ... (+{len(shown) - 15} more)"
    print(f"    Available {label}: {preview}")
    print(f"    Run 'python cli.py --list-options {label}' to see every option.")
    return False


def _parse_skills(value):
    """Validates skills against the vocabulary (aliases are canonicalized)."""
    skills = []
    invalid = []
    for part in _split_csv(value):
        key = part.casefold()
        if key in {skill.casefold() for skill in vocab.SKILLS} or \
                key in {skill.casefold() for skill in vocab.POPULAR_SKILLS}:
            skills.append(part)
            continue
        canonical = vocab.SKILL_ALIASES.get(key)
        if canonical:
            skills.append(canonical)
            continue
        invalid.append(part)
    if invalid:
        return None if _report_invalid("skills", invalid,
                                       vocab.SKILLS | set(vocab.POPULAR_SKILLS)) else None
    return skills


def _parse_certificates(value):
    certificates = []
    invalid = []
    options = vocab.CERTIFICATES | set(vocab.POPULAR_CERTIFICATES)
    for part in _split_csv(value):
        if part.casefold() in {option.casefold() for option in options}:
            certificates.append(part)
        else:
            invalid.append(part)
    if invalid:
        return None if _report_invalid("certificates", invalid, options) else None
    return certificates


def _parse_languages(value):
    languages = []
    invalid = []
    for part in _split_csv(value):
        if ":" in part:
            language, level = part.split(":", 1)
        else:
            language, level = part, "fluent"
        language, level = language.strip(), level.strip()
        if language.casefold() not in vocab.LANGUAGES:
            invalid.append(part)
            continue
        if level.casefold() not in _LANGUAGE_LEVELS:
            print(f"[!] Unknown language level '{level}' for '{language}'.")
            print(f"    Available levels: {', '.join(sorted(_LANGUAGE_LEVELS))}")
            return None
        languages.append((language.lower(), level.lower()))
    if invalid:
        return None if _report_invalid("languages", invalid, vocab.LANGUAGES) else None
    return languages


def _parse_workplace(value):
    workplace = []
    invalid = []
    for part in _split_csv(value):
        key = part.casefold()
        if key == "onsite":
            key = "on-site"
        if key in _WORKPLACE_OPTIONS:
            workplace.append("On-site" if key == "on-site" else key.title())
        else:
            invalid.append(part)
    if invalid:
        return None if _report_invalid("workplace", invalid, _WORKPLACE_OPTIONS) else None
    return workplace


def _build_space(job_title, args):
    """Builds a JobSearchSpace from the CLI arguments (None when invalid)."""
    skills = _parse_skills(args.skills) if args.skills else []
    certificates = _parse_certificates(args.certificates) if args.certificates else []
    languages = _parse_languages(args.languages) if args.languages else []
    workplace = _parse_workplace(args.workplace) if args.workplace else []

    if args.skills and skills is None or args.certificates and certificates is None or \
            args.languages and languages is None or args.workplace and workplace is None:
        return None

    return JobSearchSpace(
        job_title=job_title,
        experience_years=args.experience,
        experience_domains=_split_csv(args.experience_domain),
        education_level=args.education,
        education_field=args.field,
        skills=skills,
        certificates=certificates,
        languages=languages,
        workplace=workplace,
        location=args.location,
        check_interval_hours=max(0.05, float(args.interval or 1.0)),
    )


# ---------------------------------------------------------------------------
# --list-options
# ---------------------------------------------------------------------------

def print_options(category):
    if category == "skills":
        options = sorted(vocab.display_name(skill) for skill in vocab.SKILLS)
    elif category == "certificates":
        options = sorted(vocab.display_name(cert)
                         for cert in vocab.CERTIFICATES | set(vocab.POPULAR_CERTIFICATES))
    elif category == "languages":
        options = sorted(language.title() for language in vocab.LANGUAGES)
    elif category == "education":
        options = sorted(level.title() for level in _EDUCATION_LEVELS)
    else:  # workplace
        options = ["Hybrid", "On-site", "Remote"]
    print(f"Available {category} ({len(options)}):")
    print(", ".join(options))


# ---------------------------------------------------------------------------
# Interactive shell
# ---------------------------------------------------------------------------

def _pick_entry(monitor, tokens):
    """Resolves a command argument to a recorded search entry (index or title)."""
    entries = monitor.entries()
    if not tokens:
        return None
    first = tokens[0]
    if first.isdigit():
        index = int(first) - 1
        return entries[index] if 0 <= index < len(entries) else None
    title = " ".join(tokens).strip().casefold()
    for entry in entries:
        if entry["space"].key == title or entry["space"].key.startswith(title):
            return entry
    return None


def _show_results(entry, verbose):
    """Prints the results of one search as a table (plus details in verbose)."""
    results = entry.get("results") or []
    if not results:
        print("[-] No results yet for this search.")
        return
    CLIRenderer.render_jobs_table(results, title=entry["space"].label)
    if verbose:
        CLIRenderer.render_job_details(results)


def _run_search(monitor, space, verbose):
    """Runs one search with a live-updating results table.

    Jobs appear in the table the moment they are found; the final, complete
    table is drawn when the search finishes.
    """
    live = CLIRenderer.LiveJobsTable(title=space.label)
    entry = monitor.add_search(space, on_job=live.add)
    if entry is None or not entry.get("results"):
        live.finish([])
        print("[-] No jobs were found.")
        return
    live.finish(entry["results"])
    if verbose:
        CLIRenderer.render_job_details(entry["results"])


def _resolve_entry(monitor, value):
    """Resolves a --show/--remove argument to a recorded search entry.

    Accepts either a 1-based number (as shown by list/--list) or a job title
    (exact or prefix, case-insensitive).
    """
    entries = monitor.entries()
    value = (value or "").strip()
    if not value:
        return None
    if value.isdigit():
        index = int(value) - 1
        return entries[index] if 0 <= index < len(entries) else None
    key = value.casefold()
    for entry in entries:
        if entry["space"].key == key or entry["space"].key.startswith(key):
            return entry
    return None


def _command_loop(monitor, args):
    """Interactive shell: list / show / search / interval / pause / resume / ..."""
    print()
    print("Type 'help' for the available commands.")
    while True:
        try:
            command = input("JobScout> ").strip()
        except EOFError:
            return
        if not command:
            continue

        parts = command.split()
        cmd = parts[0].lower()

        if cmd in ("exit", "quit", "q"):
            print("[!] Stopped by user. The background monitor keeps checking your searches.")
            return
        if cmd == "gui":
            from src.GUI.Window.Window import start_gui
            start_gui()
            return
        if cmd == "help":
            print(_HELP_TEXT)
            continue
        if cmd == "list":
            CLIRenderer.render_searches_table(monitor.entries())
            continue
        if cmd == "show":
            entry = _pick_entry(monitor, parts[1:])
            if entry is None:
                print("[!] Unknown search. Use 'list' to see the recorded searches.")
                continue
            _show_results(entry, args.verbose)
            continue
        if cmd == "search":
            title = " ".join(parts[1:]).strip()
            if not title:
                print("[!] Usage: search <job title>")
                continue
            space = _build_space(title, args)
            if space is None:
                continue
            print(f"[*] Searching LinkedIn for '{title}'...")
            _run_search(monitor, space, args.verbose)
            continue
        if cmd == "interval":
            if len(parts) < 3:
                print("[!] Usage: interval <number or title> <hours>")
                continue
            try:
                hours = float(parts[-1])
            except ValueError:
                print("[!] The interval must be a number of hours.")
                continue
            entry = _pick_entry(monitor, parts[1:-1])
            if entry is None:
                print("[!] Unknown search. Use 'list' to see the recorded searches.")
                continue
            monitor.set_interval(entry["space"].key, hours)
            print(f"[+] Re-check interval for '{entry['space'].label}' set to {hours:g} hour(s).")
            continue
        if cmd in ("pause", "resume"):
            entry = _pick_entry(monitor, parts[1:])
            if entry is None:
                print("[!] Unknown search. Use 'list' to see the recorded searches.")
                continue
            monitor.set_monitoring(entry["space"].key, cmd == "resume")
            state = "resumed" if cmd == "resume" else "paused"
            print(f"[+] Background monitoring {state} for '{entry['space'].label}'.")
            continue
        if cmd == "remove":
            entry = _pick_entry(monitor, parts[1:])
            if entry is None:
                print("[!] Unknown search. Use 'list' to see the recorded searches.")
                continue
            monitor.remove(entry["space"].key)
            print(f"[+] Stopped tracking '{entry['space'].label}'.")
            continue
        print(f"[!] Unknown command '{cmd}'. Type 'help' for the available commands.")


_HELP_TEXT = """
Commands:
    list                    show the recorded searches
    show <number|title>     show the latest results of one search
    search <job title>      record and run a new search
    interval <number|title> <hours>
                            change the background re-check interval
    pause <number|title>    pause the background monitoring of one search
    resume <number|title>   resume it
    remove <number|title>   stop tracking one search
    gui                     open the graphical interface
    help                    show this help
    exit                    quit (the background monitor keeps running)
"""


def main():
    args = parse_arguments()

    if args.list_options:
        print_options(args.list_options)
        return

    if args.timeout is not None:
        settings.SCRAPE_TIME_LIMIT = args.timeout

    # One-shot actions: run the requested action and exit (no interactive
    # shell, no searching). They read the shared state kept fresh by the
    # background daemon.
    if args.list_searches:
        CLIRenderer.render_searches_table(CliMonitor().entries())
        return

    if args.show_search is not None:
        entry = _resolve_entry(CliMonitor(), args.show_search)
        if entry is None:
            print(f"[!] No recorded search matches '{args.show_search}'.")
            print("    Run 'python cli.py --list' to see the recorded searches.")
            return
        _show_results(entry, args.verbose)
        return

    if args.remove_search is not None:
        monitor = CliMonitor()
        entry = _resolve_entry(monitor, args.remove_search)
        if entry is None:
            print(f"[!] No recorded search matches '{args.remove_search}'.")
            print("    Run 'python cli.py --list' to see the recorded searches.")
            return
        monitor.remove(entry["space"].key)
        print(f"[+] Stopped tracking '{entry['space'].label}'.")
        return

    if (args.query or "").strip().lower() == "gui":
        from src.GUI.Window.Window import start_gui
        start_gui()
        return

    monitor = CliMonitor()
    try:
        if args.query:
            space = _build_space(args.query, args)
            if space is None:
                return
            print(f"[*] Searching LinkedIn for '{args.query}'...")
            _run_search(monitor, space, args.verbose)
        else:
            if monitor.entries():
                print(f"[*] Resumed {len(monitor.entries())} recorded search(es) - "
                      f"the background monitor keeps checking them.")
            else:
                print("[-] No job title given and no recorded searches.")
                print("    Run 'python cli.py gui' for the interface or "
                      "'python cli.py \"AI Engineer\"' for a CLI search.")
                return
        _command_loop(monitor, args)
    except KeyboardInterrupt:
        print("[!] Stopped by user. The background monitor keeps checking your searches.")
    finally:
        pass  # the daemon is detached - nothing to stop here


if __name__ == "__main__":
    main()
