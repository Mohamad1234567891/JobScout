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

The job scraping pipeline.

Searches LinkedIn for a job title,
extracts the job links from the listing page (HTTP first, browser fallback),
then fetches and extracts every job page concurrently. Returns the extracted
job list and the session statistics.

"""

import asyncio
import inspect
import json
import time

from urllib.parse import quote

from src.Core.DataAcquisition import settings
from src.Constants import constants
from src.Core.DataAcquisition.Extraction import job_listing
from src.Core.DataAcquisition.Extraction import job_page
from src.Core.DataAcquisition.Network.fetcher import Fetcher

# The LinkedIn job search URL template. sortBy=DD puts the most recently
# posted jobs first; the location defaults to Worldwide and can be overridden
# per search (the GUI passes the user's location when given).
SEARCH_URL_TEMPLATE = ("https://www.linkedin.com/jobs/search?keywords={query}"
                       "&location={location}&sortBy=DD")


def build_search_url(query, location="Worldwide"):
    """Builds the LinkedIn search URL for a job title query and location."""
    return SEARCH_URL_TEMPLATE.format(query=quote(query.strip()),
                                      location=quote((location or "Worldwide").strip()))


async def process_job(fetcher, listing_url, index, entry, results, progress, on_job=None, stop_check=None):
    """Fetches one job page, extracts its data and appends it to results.

    Mirrors the per-product processing step: fetch via HTTP with the
    listing page as referer, escalate to the browser when HTTP missed key
    fields, and merge what the browser found.

    Args:
        fetcher: The Fetcher instance.
        listing_url: URL of the search page (used as referer).
        index: Position of the job in the listing (stable ordering).
        entry: Listing dict (job_url, job_id, title, company, location, posted_date).
        results: Shared list where extracted jobs are appended as (index, dict).
        progress: Shared dict tracking done/total.
        on_job: Optional callback invoked with each extracted job the moment
            it is ready (streaming results to the GUI/CLI).
        stop_check: Optional callable returning True when the search should
            stop (the app is closing - the daemon takes over the rest).
    """
    if stop_check and stop_check():
        return
    try:
        url = entry["job_url"]
        page = await fetcher.get(url, referer=listing_url, render_options={"scroll": True},
                                 priority=constants.NEXT)

        if not page["html"] or page["blocked"] or page["status"] >= 400:
            reason = page.get("error") or ("blocked by the site" if page["blocked"] else f"HTTP {page['status']}")
            if settings.VERBOSE:
                print(f"  -> Error processing job page {url}: {reason}")
            return

        # Guest-blocked posting: LinkedIn redirected us to the sign-in wall.
        # The browser cannot get past a login wall either, so keep the listing
        # data and the recovered posting URL, and skip the browser escalation.
        authwall = job_page.is_authwall_url(page["url"])

        data = job_page.extract_job_page(page["html"], page["url"], page["json"])

        # Fallback: when raw HTTP missed key fields due to JS rendering,
        # escalate to the headless browser.
        if not authwall and page["via"] == "http" and not data.get("job_title") and \
                not data.get("description") and not fetcher.browser_failed:
            rendered = await fetcher.fetch_data_through_browser(url, scroll=True)
            if rendered["html"] and not rendered["blocked"]:
                more = job_page.extract_job_page(rendered["html"], rendered["url"], rendered["json"])
                for key, value in more.items():
                    if not data.get(key) and value:
                        data[key] = value
                page = rendered

        # Listing data fills the gaps the job page did not provide.
        for listing_key, data_key in (("title", "job_title"), ("company", "company_name"),
                                      ("location", "location"), ("posted_date", "posted_date")):
            if not data.get(data_key) and entry.get(listing_key):
                data[data_key] = entry[listing_key]
        if entry.get("job_id") and not data.get("job_id"):
            data["job_id"] = entry["job_id"]

        results.append((index, data))
        progress["done"] += 1

        if on_job is not None:
            result = on_job(data)
            if inspect.isawaitable(result):
                await result

        if settings.VERBOSE:
            print(f"=== Processed Job {progress['done']}/{progress['total']} ===")
            print(json.dumps(data, indent=4, ensure_ascii=False, default=str))
            print("-" * 50)

    except Exception as e:
        if settings.VERBOSE:
            print(f"  -> Error processing job page {entry.get('job_url')}: {type(e).__name__}: {e}")


async def scrape_search_space(job_title, location=None, on_job=None, stop_check=None):
    """Searches LinkedIn for a job title and returns (jobs, stats).

    Every job found is processed - there is no job limit. Each extracted job
    is passed to the optional on_job callback the moment it is ready, so the
    GUI and the CLI can show results while the search is still running.

    Args:
        job_title (str): The job the user is searching for.
        location (str | None): Search location (defaults to Worldwide).
        on_job: Optional callback invoked with each job as it is extracted
            (may be async).
        stop_check: Optional callable returning True when the search should
            stop early (the app is closing; the daemon completes the rest).
            Already-collected jobs are still returned.

    Returns:
        tuple[list[dict], dict]: The extracted job list (listing order) and
        the session statistics.
    """
    if not job_title or not job_title.strip():
        print("[-] Please enter the job you are searching for")
        return [], {}

    url = build_search_url(job_title, location)
    progress = {"done": 0, "total": 0}
    results = []

    if settings.VERBOSE:
        print(f"[*] Navigating to the listing page: {url}")

    print(f"[*] Searching LinkedIn for '{job_title.strip()}'...")

    async with Fetcher() as fetcher:
        try:
            # Phase 1 - the listing page. Scroll and click "see more jobs" so
            # the browser mode loads as many cards as possible.
            listing = await fetcher.get(url, render_options={"scroll": True, "load_more": True})

            if not listing["html"] or listing["blocked"] or listing["status"] >= 400:
                reason = listing.get("error") or ("blocked by the site" if listing["blocked"]
                                                  else f"HTTP {listing['status']}")
                print(f"[!] Error fetching the listing page: {reason}")
                return [], fetcher.stats

            entries = job_listing.extract_listing_links(listing["html"], listing["url"], listing["json"])

            # Fallback: if raw HTTP missed the content due to client-side JS
            # rendering, escalate to the headless browser.
            if not entries and listing["via"] == "http" and not fetcher.browser_failed:
                if settings.VERBOSE:
                    print("[*] No jobs in the raw HTML (rendered via JS) -> switching to the browser...")
                rendered = await fetcher.fetch_data_through_browser(url, scroll=True, load_more=True)
                if rendered["html"] and not rendered["blocked"]:
                    listing = rendered
                    entries = job_listing.extract_listing_links(listing["html"], listing["url"], listing["json"])

            print(f"[+] Found {len(entries)} jobs. Scraping each job page...")

            if not entries:
                print("[!] No job links found on the listing page")
                return [], fetcher.stats

            progress["total"] = len(entries)

            # Phase 2 - a watchdog around the whole scraping session.
            # If anything gets stuck (or the app is closing), show what was
            # collected so far.
            gather_task = asyncio.ensure_future(asyncio.gather(*(
                process_job(fetcher, listing["url"], index, entry, results, progress, on_job, stop_check)
                for index, entry in enumerate(entries, start=1))))
            deadline = time.monotonic() + settings.SCRAPE_TIME_LIMIT
            while True:
                done_tasks, pending_tasks = await asyncio.wait({gather_task}, timeout=0.5)
                if not pending_tasks:
                    break
                if (stop_check and stop_check()) or time.monotonic() > deadline:
                    gather_task.cancel()
                    try:
                        await gather_task
                    except (asyncio.CancelledError, Exception):
                        pass
                    if stop_check and stop_check():
                        print("[*] Stopping early - the background monitor will finish the rest.")
                    else:
                        print(f"[!] Scraping exceeded {settings.SCRAPE_TIME_LIMIT}s - "
                              f"showing the jobs collected so far.")
                    break

        except (asyncio.CancelledError, KeyboardInterrupt):
            print("[!] Stopped by user (jobs collected so far are shown).")

    # Keep listing order. Jobs whose page failed are still returned with the
    # listing data so the user sees everything the search found.
    extracted = dict(results)
    jobs = []
    for index, entry in enumerate(entries, start=1):
        if index in extracted:
            jobs.append(extracted[index])
        else:
            jobs.append({
                "job_id": entry.get("job_id"),
                "job_url": entry.get("job_url"),
                "job_title": entry.get("title"),
                "company_name": entry.get("company"),
                "location": entry.get("location"),
                "posted_date": entry.get("posted_date"),
                "failed": True,
            })
    return jobs, fetcher.stats
