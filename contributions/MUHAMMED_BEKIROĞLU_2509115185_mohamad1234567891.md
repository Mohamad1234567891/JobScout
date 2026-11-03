# Contribution Report — Muhammed Bekiroğlu

**Student Name:** MUHAMMED BEKİROĞLU  
**Student ID:** 2509115185  
**GitHub Username:** [mohamad1234567891](https://github.com/mohamad1234567891)  
**Project:** JobScout  
**Role:** **Team Leader** — Data Acquisition, Web Scraping, CLI & Project Architecture

---

## Overview

As the team leader of JobScout, I was responsible for organizing the team, distributing work according to each member's capabilities, assigning daily tasks, and mentoring teammates whenever they needed help. On the technical side, I designed and implemented the **core web-scraping and data-acquisition engine** that powers the entire application, together with the shared utility libraries, the search-space model, the background monitoring system, the job cards, the command-line interface and its renderer.

The engine I built is what makes JobScout what it is: it searches LinkedIn for the jobs the user is looking for, defends itself against anti-bot protections, extracts what every employer asks for from pages of any structure, estimates how likely the user is to be accepted at each job, and keeps re-checking in the background so the user is notified whenever a new job appears.

---

## 1. Project Leadership & Team Coordination

- **Organized the team and distributed the work** among members according to each member's strengths and capabilities.
- **Planned and assigned the everyday tasks** for every member, tracked their progress, and made sure the work stayed on schedule.
- **Mentored and supported teammates** — debugging their code, explaining parts of the codebase, and reviewing their work before it was merged.
- **Owned the project's architecture** — designed the folder structure, the module boundaries, and how the pieces connect to each other.
- Coordinated the team.

---

## 2. Data-Acquisition Engine — `src/Core/DataAcquisition/`

I designed and implemented the entire data-acquisition engine from scratch. It is the heart of the application.

### `Network/Fetcher.py` — the dual-transport fetching engine
- Fetches pages with **ultra-fast HTTP requests first**, and automatically falls back to a **headless Chromium browser (Playwright)** whenever LinkedIn's anti-bot protection blocks plain requests.
- Uses `curl_cffi` to **impersonate Google Chrome's TLS fingerprint**, so anti-bot systems see a normal browser instead of a script.
- Applies stealth countermeasures in the browser: disables the `AutomationControlled` flag, overrides `navigator.webdriver`, builds a realistic user agent from the real browser version, and shares cookies from the browser back into the HTTP session.
- Blocks heavy media and tracking/analytics requests to make pages load faster.
- Implements automatic **block detection** (`403`, `429`, CAPTCHA/Cloudflare challenge pages) and per-domain browser escalation.

### `Network/AsyncSession.py` & `Network/AsyncSlotsManager.py` — concurrency & rate control
- A session factory that gracefully degrades when `curl_cffi` is not installed.
- A priority-based **async slot manager**: limits the number of simultaneous requests per site (like a browser does) and orders waiting tasks by priority, so work for jobs already in progress always finishes first.

### `BrowserScripts/JavaScripts.py` — in-page browser automation
- JavaScript snippets that **scroll pages step-by-step** to trigger lazy-loaded jobs and click the "see more jobs" button until the listing is fully loaded.

### `Extraction/` — the extraction brain
- **`job_listing.py`** — extracts every job from the LinkedIn search page using the structured `ItemList` block, the visible job cards (title, company, location, posted date), raw URL patterns and embedded JSON, deduplicating everything by the numeric job id.
- **`job_page.py`** — the job-page extraction pipeline: reads the title, company, location, posted date, applicants, seniority, employment type, industries and the full description, then merges meta-tag and DOM fallbacks into one record.
- **`requirements.py`** — extracts what each employer asks for from the description: years of experience, education degrees, certificates, mentioned skills and language requirements.

### `scraper.py` — orchestration & location
- The scraping pipeline shared by the CLI and the GUI: navigates the listing, extracts job links, falls back to the browser when raw HTML has nothing, limits the number of jobs, processes all job pages concurrently, and gracefully isolates failures so one broken page never stops the others.
- `LocationDetection.py` — decides where to search: **remote** searches run worldwide, otherwise the user's **city** is auto-detected via IP geolocation (`ipapi.co`); an explicit location always wins.
- `settings.py` — the central runtime configuration with sensible defaults for every knob of the engine.

---

## 3. Data Analysis Support

Abdulrab Almusali owns the data-analysis module; I contributed the parts that connect it to the rest of the system:

- **`SearchSpace.py`** — the structured job search space (title, experience, education, skills, certificates, languages, workplace, location, re-check interval) shared by the GUI, the CLI, the daemon and the matcher.
- **`match_service.py`** — the adapter that bridges the human-readable extracted requirements ("6+ years of professional software development experience", "Master's degree in Computer Science") and the matcher's clean inputs, including the related-skill and related-certificate maps used for partial credit.
- Helped review and test the matcher (`job_matcher.py`).

---

## 4. Background Monitoring, Shared State & Notifications

- **`SharedState.py`** — the single state file (`~/.jobscout/searches.json`) shared by the GUI, the CLI and the daemon, so searches made in one mode appear in the other and survive restarts.
- **`Daemon.py`** — the detached background monitor that keeps re-checking every search on its own interval **even after the app is closed**, and notifies the user whenever new jobs appear; includes pid-file liveness checks and a spawn helper used by both modes.
- **`CliMonitor.py`** — the CLI client over the shared store and the daemon: records searches, runs the first search, and exposes interval/pause/resume/remove management.
- Helped Abdulmalik Mahmoud with the notification system (`Notifications/notifier.py`), keeping it exception-safe so a missing notification backend never breaks the app.

---

## 5. GUI Contributions — Job Cards

- **`GUI/Components/JobCard.py`** — the job result cards shown next to the sidebar: title, company, location, posted date, the acceptance estimate badge, a requirement snippet and the **"View Job" button** that opens the full posting in the browser.
- Helped wire the GUI to the engine — the `GUI/Core/SearchManager.py` and `GUI/Core/ScrapeWorker.py` background workers that keep the interface responsive, and the shared-store integration in the main window.

---

## 6. Command-Line Interface & Renderer

- **`cli.py`** — the application entry point: `python cli.py GUI` opens the graphical interface, a job title runs a CLI search, and the interactive `JobScout>` shell provides `list`, `show`, `search`, `interval`, `pause`, `resume`, `remove`, `gui`, `help` and `exit` commands, plus one-shot `--list` / `--show` / `--remove` actions.
- Full command-line reference with **short flags** for every search input (`-l`, `-w`, `-i`, `-m`, `-t`, `-e`, `-D`, `-d`, `-f`, `-s`, `-c`, `-L`, `-v`), **validation** of skills, certificates, languages and workplace against the predefined options, and `--list-options` to browse them.
- **`CLIRenderer.py`** — the dependency-free terminal table renderer: job results and recorded searches as clean ASCII tables with an `Accept %` column, plus the verbose per-job requirement details.

---

## 7. Shared Libraries — `src/Constants/`, `src/Helpers/`, `src/Operations/`

I created and maintain the shared foundation used by the whole team:

### `Constants/`
- **`constants.py`** — job semantic word sets (seniority, employment type, requirement sections...) and the priority constants.
- **`job_vocabulary.py`** — the option vocabulary used by the panel dropdowns, the CLI validation and the matcher: **800+ skills and 300+ certificates across every job field**, degrees, fields of study, languages, related-skill and related-certificate maps, and the display formatting helpers.
- **`regex_constants.py`** — the project's regex library: job URLs, experience/education/certificate patterns, tracking-parameter stripping, block-page detection, junk-path detection and heavy-media/tracker filters.

### `Helpers/`
- **`http_helper.py`** — detects anti-bot blocks from status codes and challenge-page signatures (Cloudflare, Akamai, DataDome, PerimeterX, Imperva).

### `Operations/`
| Module | Purpose |
| ------ | ------- |
| `url_operations.py` | URL cleaning (tracking-parameter removal), canonical sorting, ID extraction, search-URL detection |
| `html_operations.py` | HTML parsing, semantic extraction, microdata, link discovery |
| `string_operations.py` | Text cleaning, number extraction, name tokens, structured text |
| `json_operations.py` | Embedded JSON & JSON-LD traversal and extraction |
| `dictionary_operations.py` | Dictionary helpers |

---

## 8. Code Reuse from ShopWise

Because we wrote **high-quality, modular code** in our previous project (ShopWise), we were able to **reuse so much of the ShopWise code** in this project — the entire fetching engine with its anti-bot bypass techniques, the concurrency slot managers, the block detection, the in-page browser scripts, and the Operations/Helpers/Constants utility libraries all carried over with only the job-specific parts rewritten. This **boosted our productivity enormously**, and we were able to **finish this project in a very short time**.

---

## 9. Setup, Testing & Documentation

- **`Setup.py`** — a fully automated, cross-platform setup script (standard library only) that creates the virtual environment, installs the dependencies and the Playwright Chromium browser, and verifies every dependency imports correctly.
- Continuously tested the engine against real LinkedIn searches and diagnosed failures from the verbose logs; fixed pipeline-level problems found during testing (authwall-redirected postings, deduplication by job id, encoding edge cases, daemon lifecycle issues).
- Maintained the project documentation (`README.md`), the `LICENSE` file, and the attribution headers in every source file.