# 💼 JobScout

> **Search a job once. JobScout keeps watching LinkedIn for you — scraping every posting, scoring it against your profile, and notifying you the moment a new one appears.**

JobScout is a job-search and job-match engine that finds the job you are looking for on LinkedIn, scrapes each posting and extracts what the employer asks for (experience, education, certificates, skills, languages), scores every job against your profile, and then keeps re-searching in the background so you are notified whenever new jobs appear.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/Status-University%20Project-important)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Automatic Setup (Recommended)](#automatic-setup-recommended)
- [Manual Setup](#manual-setup)
- [Usage](#usage)
  - [Running JobScout](#running-jobscout)
  - [Command-Line Reference](#command-line-reference)
  - [Examples](#examples)
- [How Jobs Are Scored](#how-jobs-are-scored)
- [Location & Search Behavior](#location--search-behavior)
- [Team](#team)
- [License](#license)

---

## Overview

JobScout automates the entire job-search workflow:

1. You **describe your search space** — the job title plus your profile (experience, education, skills, certificates, languages) — in the GUI panel or as CLI arguments.
2. It **decides where to search** — worldwide for remote jobs, otherwise your city (auto-detected by IP geolocation).
3. It **scrapes every job posting** on LinkedIn, bypassing anti-bot protection with Chrome-impersonating HTTP requests and a stealth headless browser fallback.
4. It **extracts what each employer asks for** — required years of experience, degrees, certificates, skills and language requirements.
5. It **estimates how likely you are to be accepted** at each job by comparing your profile with the posted requirements, and ranks the jobs.
6. It **keeps watching in the background** through a detached daemon — even after the app is closed — and notifies you whenever a new job appears.

---

## Features

- 🧭 **Smart location detection** — remote searches run worldwide; otherwise JobScout finds your **city** via IP geolocation and searches there.
- ⚡ **Dual fetching engine** — ultra-fast HTTP requests that impersonate Google Chrome (`curl_cffi`), with automatic fallback to a stealth headless browser (Playwright/Chromium) whenever LinkedIn's anti-bot protection blocks plain requests.
- 🧲 **Deep requirement extraction** — pulls the job title, company, location, posted date, seniority, employment type, and the requirements from the description: years of experience, education degrees, certificates, skills and language requirements.
- 🎯 **Acceptance estimate** — every job earns an **acceptance percentage** (with a per-criterion breakdown) by comparing your profile against the posted requirements, including partial credit for related skills and certificates.
- ⏰ **Background monitoring that survives app close** — a detached daemon re-checks every search on its own interval and sends desktop notifications for new jobs, in both GUI and CLI modes.
- 🔄 **Shared state across modes** — the GUI and the CLI read and write the same state file, so searches made in one mode appear in the other, across restarts.
- 🖥️ **Rich CLI** — clean ASCII tables, an `Accept %` column, short flags (`-v`, `-m`, `-s`...), validation against predefined options, one-shot `--list` / `--show` / `--remove` actions, and an interactive command shell.
- 🎨 **Modern GUI** — a polished PySide6 desktop interface with a search panel, sidebar search items, job cards with a "View Job" button, loading states, and searchable multi-select dropdowns.
- 🛡️ **Anti-bot resilience** — Chrome fingerprinting, realistic user agents, `navigator.webdriver` masking, referer spoofing, cookie sharing between the browser and HTTP sessions, and automatic block detection.

---

## How It Works

```
Search space ──► Location decision (Remote → Worldwide, else your city) ──► LinkedIn search
                                                     │
                                                     ▼
    Ranked results ◄── Acceptance scoring ◄── Job-page scraping & requirement extraction
        │
        ▼
 Shared state file ──► Detached daemon re-checks on interval ──► New-job desktop notifications
```

1. **Build the search space** — the job title and your profile are read from the GUI panel or the CLI arguments.
2. **Decide the location** — `Remote` searches run worldwide; otherwise the user's city is resolved via `ipapi.co`; an explicit location always wins.
3. **Scrape the listing** — the LinkedIn search page is fetched (fast HTTP first, headless Chromium fallback), lazy-loaded jobs are scrolled in, and every job link is extracted.
4. **Process the jobs** — every job page is fetched concurrently; title, company, location, posted date, seniority, employment type and the full requirement section are extracted.
5. **Score** — the extracted requirements are compared with your profile dimension by dimension (experience, skills, education, certificates, languages) and combined into one acceptance percentage.
6. **Rank & display** — results are sorted by the acceptance estimate and rendered as cards (GUI) or a table (CLI).
7. **Monitor** — the search is recorded in the shared state file and a detached daemon re-checks it every interval (default: every hour), notifying you about new jobs even after the app closes.

---

## Tech Stack

| Layer            | Technology |
| ---------------- | ---------- |
| Language         | Python 3.10+ (`asyncio`, `argparse`, `dataclasses`, `threading`) |
| Fast HTTP        | `curl_cffi` (Chrome impersonation) |
| Browser fallback | `Playwright` (headless Chromium, stealth flags) |
| HTML parsing     | `lxml` |
| GUI              | `PySide6` (Qt for Python) |
| Desktop notifications | `desktop-notifier` |
| CLI rendering    | dependency-free ASCII tables (`src/Core/CLIRenderer.py`) |

---

## Project Structure

```
JobScout/
├── contributions/                          # Individual team-member contribution reports
│   └── MUHAMMED_BEKIROĞLU_2509115185_mohamad1234567891.md   # Muhammed Bekiroğlu (team lead)
├── cli.py                                  # Entry point — GUI keyword, CLI search & command shell
├── Setup.py                                # One-command, cross-platform setup script
├── requirements.txt                        # Python dependencies
├── LICENSE                                 # MPL-2.0 + Additional Attribution Terms
├── .gitignore
├── README.md
└── src/
    ├── Constants/
    │   ├── constants.py                    # Job semantic word sets & priority constants
    │   ├── job_vocabulary.py               # Skills, certificates, degrees, languages, related-item maps
    │   └── regex_constants.py              # Experience/education/certificate/block-detection regexes
    ├── Core/
    │   ├── SearchSpace.py                  # The user's job search space (shared model)
    │   ├── SharedState.py                  # Shared state file used by the GUI, CLI and daemon
    │   ├── Daemon.py                       # Detached background monitor (survives app close)
    │   ├── CliMonitor.py                   # CLI client over the shared store + daemon
    │   ├── CLIRenderer.py                  # Terminal tables & job/search rendering
    │   ├── DataAcquisition/
    │   │   ├── scraper.py                  # Scraping pipeline shared by the CLI and the GUI
    │   │   ├── settings.py                 # Runtime tunables and their defaults
    │   │   ├── LocationDetection.py        # City-level IP geolocation & search-location decision
    │   │   ├── Network/
    │   │   │   ├── async_session.py        # Chrome-impersonating HTTP session factory
    │   │   │   ├── async_slots_manager.py  # Priority-based concurrency slot limiter
    │   │   │   └── fetcher.py              # HTTP-first fetching with browser fallback
    │   │   ├── BrowserScripts/
    │   │   │   └── javascripts.py          # In-page JS (scrolling, see-more-jobs)
    │   │   └── Extraction/
    │   │       ├── job_listing.py          # Search-page job links & card extraction
    │   │       ├── job_page.py             # Job-page data extraction
    │   │       └── requirements.py         # Experience/education/certificates/skills/languages
    │   ├── DataAnalysis/
    │   │   ├── job_matcher.py              # Per-criterion scoring functions (pure, tested)
    │   │   ├── match_service.py            # Adapts extracted jobs + search space to the matcher
    │   │   └── test_job_matcher.py         # Matcher test suite
    │   └── Notifications/
    │       └── notifier.py                 # Cross-platform desktop notifications
    ├── GUI/
    │   ├── Components/
    │   │   ├── Action_item.py              # Sidebar search item (click, options, badge)
    │   │   ├── Button.py                   # Styled button that opens URLs
    │   │   ├── Drop_down.py                # Dropdowns (single & searchable multi-select)
    │   │   ├── emoji_icon.py               # Draws emojis into QIcons (window icon)
    │   │   ├── JobCard.py                  # Job result card with the View Job button
    │   │   ├── Loading.py                  # Animated loading indicator
    │   │   ├── panel.py                    # The search-space input panel
    │   │   ├── Scroll.py                   # Scrollable containers for cards & sidebar
    │   │   ├── SearchBar.py                # Search bar with suggestions & signals
    │   │   └── Sidebar.py                  # Sidebar holding one item per search
    │   ├── Core/
    │   │   ├── SearchManager.py            # Per-search manager (runs & persists searches)
    │   │   └── ScrapeWorker.py             # Background thread running the scraping engine
    │   └── Window/
    │       └── Window.py                   # Main application window & GUI entry point
    ├── Helpers/
    │   └── http_helper.py                  # Anti-bot / block-page detection
    └── Operations/
        ├── dictionary_operations.py        # Dictionary helper functions
        ├── html_operations.py              # HTML parsing, semantics & microdata
        ├── json_operations.py              # Embedded JSON & JSON-LD extraction
        ├── string_operations.py            # Text cleaning, numbers & names
        └── url_operations.py               # URL cleaning, IDs & link patterns
```

> Generated folders such as `.venv/`, `__pycache__/` and `.idea/` are git-ignored and intentionally not shown.

---

## Prerequisites

- **Python 3.10 or newer** ([python.org](https://www.python.org/downloads/))
- **Git** ([git-scm.com](https://git-scm.com/downloads))
- An **internet connection** (job searches use LinkedIn)

---

## Automatic Setup (Recommended)

The fastest way to get JobScout running is the bundled [`Setup.py`](Setup.py) script. It performs the entire setup for you and **prints everything that is happening** to the terminal as it runs. It is **cross-platform** (Windows, macOS and Linux) and uses **only Python's standard library**, so nothing needs to be installed to run it.

After cloning the repository, simply run:

```bash
cd JobScout
python3 Setup.py
```

> On Windows, use `python Setup.py` (or `py Setup.py`).

The script will:

1. Pick a suitable Python interpreter (3.10 or newer).
2. Create the virtual environment `.venv`.
3. Upgrade `pip` inside the environment.
4. Install all dependencies from `requirements.txt`.
5. Install the Playwright **Chromium** browser used by the scraper.
6. Verify that every dependency imports correctly.

When the script finishes, the setup is complete — activate the environment and run JobScout as described in [Running JobScout](#running-jobscout).

> ✋ **Prefer to do everything by hand?** You can skip this section entirely and follow the [manual setup instructions](#manual-setup) below — `Setup.py` simply automates those same steps.

> ⚠️ **Seeing a `ModuleNotFoundError: No module named ...` when running JobScout?**
>
> It means the virtual environment is **not active** — the packages were installed inside `.venv`, so Python must run from inside it. Activate the environment first:
>
> **Linux / macOS — bash / zsh**
>
> ```bash
> source .venv/bin/activate
> ```
>
> **Windows — Command Prompt (cmd)**
>
> ```cmd
> .venv\Scripts\activate
> ```
>
> **Windows — PowerShell**
>
> ```powershell
> .venv\Scripts\Activate.ps1
> ```

---

## Manual Setup

If you prefer to run every step yourself (or want to know exactly what `Setup.py` does), follow the instructions below.

### 1. Clone the repository

```bash
git clone https://github.com/Mohamad1234567891/JobScout.git
cd JobScout
```

### 2. Create a virtual environment

> If the `python` command is not found, use `python3` (Linux/macOS) or `py` (Windows) instead.

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

#### 🐧 Linux — bash / zsh

```bash
source .venv/bin/activate
```

#### 🐧 Linux — fish

```fish
source .venv/bin/activate.fish
```

#### 🍎 macOS — bash / zsh (default terminal)

```bash
source .venv/bin/activate
```

#### 🍎 macOS — fish

```fish
source .venv/bin/activate.fish
```

#### 🪟 Windows — Command Prompt (cmd)

```cmd
.venv\Scripts\activate
```

#### 🪟 Windows — PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

> **Note:** if PowerShell blocks the activation script, allow it once with:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

When the environment is active, your prompt is prefixed with `(.venv)`. To leave it at any time, run `deactivate`.

### 4. Install the Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Install the browser used by the scraper

```bash
playwright install
```

> JobScout only drives **Chromium**, so installing just that browser is enough and faster:
> `playwright install chromium`

---

## Usage

### Running JobScout

Make sure the virtual environment is **active** and you are in the repository root, then run:

```bash
python cli.py GUI                     # opens the graphical user interface
python cli.py "AI Engineer"           # runs in the terminal (CLI mode)
```

or, on systems where Python 3 is invoked as `python3`:

```bash
python3 cli.py GUI                    # opens the graphical user interface
python3 cli.py "AI Engineer"          # runs in the terminal (CLI mode)
```

> 💡 **For the best results, always fill all the parameters** — the more of your profile you provide, the more dimensions the acceptance estimate can score. For more information, read the [examples](#examples).

| Command | What it does |
| ------- | ------------ |
| `python cli.py GUI` | Opens the graphical user interface (desktop application window) |
| `python cli.py <jobTitle>` | Searches for the job and shows the ranked results in a terminal table (CLI mode) |

> `GUI` is the keyword that launches the interface, and it is case-insensitive — `gui`, `Gui` and `GUI` all work.

> 💡 **Tip — fill in your profile for accurate estimates.** The acceptance percentage is only as good as the profile you provide. Add your experience (`-e`), education (`-d`), skills (`-s`), certificates (`-c`) and languages (`-L`) — every missing field simply means that dimension is not scored, never that it scores zero.

---

### Command-Line Reference

```
usage: python cli.py [-h] [-l LOCATION] [-w WORKPLACE] [-i INTERVAL]
                     [-t TIMEOUT] [-v] [-e EXPERIENCE] [-D EXPERIENCE_DOMAIN]
                     [-d {associate,bachelor,high school,master,phd}] [-f FIELD]
                     [-s SKILLS] [-c CERTIFICATES] [-L LANGUAGES]
                     [--list-options {skills,certificates,languages,education,workplace}]
                     [--list] [--show SEARCH] [--remove SEARCH]
                     [query]

positional arguments:
  query                 job title to search, or 'gui'

options:
  -h, --help            show this help message and exit
  -l, --location        search location (auto-detected unless the search is remote)
  -w, --workplace       comma-separated workplace preference: Remote, Hybrid, On-site
  -i, --interval        background re-check interval in hours (default: 1)
  -t, --timeout         seconds allowed for one scraping session
  -v, --verbose         print the full extracted requirements of every job
  -e, --experience      your years of professional experience
  -D, --experience-domain
                        comma-separated domains your experience is in
  -d, --education       your highest education level
  -f, --field           your field of study
  -s, --skills          comma-separated skills
  -c, --certificates    comma-separated certificates
  -L, --languages       comma-separated Language:level pairs (e.g. English:fluent)
  --list-options        print the predefined options of a category and exit
  --list                list the recorded searches and exit
  --show SEARCH         show the latest results of a recorded search and exit
  --remove SEARCH       stop tracking a recorded search and exit
```

Skills, certificates, languages and workplace are validated against the predefined options; invalid values print the available options. Browse every option with `--list-options skills|certificates|languages|education|workplace`.

### Examples

```bash
# Search for AI Engineer jobs in the terminal (CLI mode)
python cli.py "AI Engineer"

# Open the graphical user interface (case-insensitive keyword)
python cli.py GUI

# Every argument that shapes a search, all in one command
# (each of these is a panel input in the GUI):
python cli.py "AI Engineer" \
    -l "Berlin" \
    -w "Hybrid" \
    -i 2 \
    -t 240 \
    -e 4 \
    -D "machine learning, nlp" \
    -d bachelor \
    -f "Computer Science" \
    -s "Python,Machine Learning,Docker" \
    -c "AWS Certified" \
    -L "English:fluent,Turkish:native" \
    -v
```

What each argument does:

- `-l "Berlin"` — where to search. Omit it and JobScout auto-detects your city (unless the search is remote).
- `-w "Hybrid"` — workplace preference: `Remote` searches worldwide, `Hybrid`/`On-site` search the location above.
- `-i 2` — how often the background monitor re-checks this search, in hours (default: `1`).
- `-t 240` — seconds allowed for one scraping session.
- `-e 4` — your years of professional experience.
- `-D "machine learning, nlp"` — the domains that experience is in.
- `-d bachelor` — your highest education level (`high school`, `associate`, `bachelor`, `master`, `phd`).
- `-f "Computer Science"` — your field of study.
- `-s "Python,Machine Learning,Docker"` — your skills (comma-separated, validated).
- `-c "AWS Certified"` — your certificates (comma-separated, validated).
- `-L "English:fluent,Turkish:native"` — your languages with levels (`basic`, `conversational`, `fluent`, `native`).
- `-v` — print the full extracted requirements of every job, not just the table.

```bash
# Remote search, re-checked every 2 hours
python cli.py "Backend Developer" -w Remote -i 2

# Manage recorded searches without opening the interactive shell
python cli.py --list
python cli.py --show "AI Engineer"
python cli.py --remove "AI Engineer"

# Browse the predefined skills (also: certificates, languages, education, workplace)
python cli.py --list-options skills
```

> Job titles with spaces can be written with or without quotes — `ai engineer` and `"ai engineer"` are equivalent.

> Every argument above mirrors one panel input in the GUI, and everything except the job title is optional: the more of your profile you provide, the more dimensions the acceptance estimate can score. See [How Jobs Are Scored](#how-jobs-are-scored) for how each input is used.

> **No job limits, live results.** JobScout processes **every** job it finds, and results stream in live: each job appears in the table (CLI) or as a card (GUI) the moment it is scraped, and the list keeps updating until the search finishes.

Inside the CLI, after the first search you get an interactive `JobScout>` shell with these commands: `list`, `show <number|title>`, `search <title>`, `interval <number> <hours>`, `pause <number|title>`, `resume <number|title>`, `remove <number|title>`, `gui`, `help` and `exit`.

---

## How Jobs Are Scored

Every job earns an **acceptance estimate** — the percentage of the posted requirements your profile satisfies, weighted by how important each dimension is:

1. **Experience (30%)** — your years are compared with the required years (partial credit when you are close), and the domain of your experience is matched against the posting.
2. **Skills (28%)** — each required skill is checked against your skills; a related skill (PyTorch ↔ TensorFlow, React ↔ Vue...) earns partial credit.
3. **Education (18%)** — your highest degree level is compared with the required one, together with the field of study; "or equivalent experience" postings credit your experience.
4. **Certificates (8%)** — exact matches score fully, related certificates partially (AWS ↔ Azure ↔ GCP...).
5. **Languages (8%)** — required languages are compared by level (basic < conversational < fluent < native).

The final percentage is the weighted average over the **active** dimensions (a dimension is active only when both your profile and the job provide data for it). The result is an estimate based on the posted requirements — not a guarantee — and it is the number used to rank the jobs from most to least likely.

---

## Location & Search Behavior

- **Remote** searches run **worldwide**.
- Otherwise JobScout auto-detects your **city** via IP geolocation and searches there.
- An explicit `--location` / panel location always wins.

Every search is **recorded** in `~/.jobscout/searches.json` (shared by the GUI and the CLI, across restarts) and re-checked in the background by a **detached daemon** on its own interval — default: every hour, editable per search. New jobs trigger a desktop notification even after the app is closed. The daemon's log lives in `~/.jobscout/daemon.log`.

**Interrupted searches are finished in the background:** closing the app mid-search (Ctrl+C in the CLI, closing the window in the GUI) never loses the remaining jobs — the daemon detects the interruption and completes the search itself, silently, on Linux, macOS and Windows.

---

## Team

| Member | Contribution |
| ------ | ------------ |
| **Muhammed Bekiroğlu** *(team lead)* | Data acquisition and all of its systems; helped in the data analysis, the notification system, the GUI and the job cards; the CLI and the CLI renderer |
| **Abdulrab Almusali** | Data analysis |
| **Ömer Ağaoğlu** | GUI window panel and every element of the panel |
| **Yusuf Rayan** | GUI sidebar and every element of the sidebar |
| **Abdulmalik Mahmoud** | Notification system |

Individual, detailed contribution reports are available in the [`contributions/`](contributions/) directory.

---

## License

JobScout is licensed under the **Mozilla Public License 2.0** together with the **Additional Attribution Terms** set out in the [`LICENSE`](LICENSE) file. In short: you may use, modify, and distribute JobScout — including in commercial products — but changes to JobScout's own files must be shared under the same license, and any software built on JobScout must display the following credit:

> **Built on the open-source JobScout project — Copyright (c) 2026 Muhammed Bekiroğlu and the JobScout contributors.**
>
> **Original JobScout repository:** [https://github.com/Mohamad1234567891/JobScout](https://github.com/Mohamad1234567891/JobScout)
>
> **Muhammed Bekiroğlu (JobScout team leader and top contributor) YouTube channel:** [https://www.youtube.com/@ALShajaraComputerScienceInstit](https://www.youtube.com/@ALShajaraComputerScienceInstit)

See the [`LICENSE`](LICENSE) file for the full terms, including where these credits must appear (every README/documentation file, a credits or about screen in GUIs, and on every run of CLI applications) and how they apply to modified JobScout files.
