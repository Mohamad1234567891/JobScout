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

The fetching engine.

Downloads pages
with impersonated HTTP requests first and falls back to a headless Playwright
browser when a site blocks plain HTTP; per-site and per-browser-tab
concurrency is limited by slot managers, and safe_call bounds every
Playwright operation so a hung browser can never stall the run.

"""

import asyncio
import json
import sys
import time

from src.Core.DataAcquisition import settings
from src.Core.DataAcquisition.BrowserScripts import javascripts as js
from src.Constants import constants
from src.Constants import regex_constants as re_c
from src.Core.DataAcquisition.Network.async_session import get_async_session
from src.Core.DataAcquisition.Network.async_slots_manager import AsyncSlotsManager
from src.Helpers import http_helper as hh
from src.Operations import html_operations as ho
from src.Operations import url_operations as uo

# Playwright's shutdown and launch can occasionally stall. Every close/launch
# below is bounded by these timeouts, so a stalled browser can never keep the
# app "loading" forever.
CLOSE_TIMEOUT = 10          # seconds allowed for closing the browser / HTTP session
BROWSER_START_TIMEOUT = 60  # seconds allowed for launching the browser
PAGE_CALL_TIMEOUT = 30      # seconds allowed for a single page operation (evaluate/content/new tab...)


async def safe_call(coro, timeout=PAGE_CALL_TIMEOUT):
    """Awaits a coroutine with a hard timeout and returns None on timeout/error.

    The installed Playwright version sends evaluate/content/new_page/close/
    cookies WITHOUT any default timeout, so a hung browser tab used to block
    the whole app forever. Every such call goes through here now."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except Exception:
        return None


class Fetcher:
    """Fetches webpages from a URL using http requests; if an http request is
    blocked it launches a headless browser to fetch the page instead, but it
    always tries http requests first as they are much faster.

    It always tries its best to hide that it is an automatic system and to
    trick anti-bots into thinking this is a human.
    """

    def __init__(self):
        self.http_requestor = None
        self.playwright = self.browser = self.context = None
        self.site_slots_managers = {}  # one gate per site: HTTP_PER_SITE downloads at the same time
        self.tabs = AsyncSlotsManager(settings.BROWSER_TABS)
        self.browser_lock = asyncio.Lock()
        self.browser_failed = False
        self.browser_only = set()
        self.stats = {"http": 0, "browser": 0}

    async def __aenter__(self):
        AsyncSession = get_async_session()
        if AsyncSession is not None:
            # Mimic Google Chrome's fingerprint, HTTP/2 headers and handshakes
            # to trick anti-bots into seeing a normal Chrome browser.
            self.http_requestor = AsyncSession(impersonate="chrome", timeout=settings.REQUEST_TIMEOUT,
                                               max_clients=64)
        return self

    async def __aexit__(self, *exc):
        # Every close gets a hard timeout: a stalled shutdown must never
        # block the results from being shown.
        for closer in (self.context, self.browser):
            try:
                if closer:
                    await asyncio.wait_for(closer.close(), timeout=CLOSE_TIMEOUT)
            except Exception:
                pass
        if self.playwright:
            try:
                await asyncio.wait_for(self.playwright.stop(), timeout=CLOSE_TIMEOUT)
            except Exception:
                pass
        if self.http_requestor:
            try:
                await asyncio.wait_for(self.http_requestor.close(), timeout=CLOSE_TIMEOUT)
            except Exception:
                pass

    def initiate_slot_manager_for_site(self, url):
        """Creates (or returns) an AsyncSlotsManager for the site of a URL."""
        domain = uo.get_domain_from_url(url)
        if domain not in self.site_slots_managers:
            self.site_slots_managers[domain] = AsyncSlotsManager(settings.HTTP_PER_SITE)
        return self.site_slots_managers[domain]

    async def get(self, url, referer=None, render_options=None, priority=constants.NOW):
        """Returns the webpage data of a URL as a dictionary like:
        {"html", "url", "status", "via", "json", "blocked", "error"}.

        It uses the ultra-fast http requests first; if the request was blocked
        by an anti-bot it proceeds with the headless browser.

        Args:
            url: The URL to fetch.
            referer: URL of the previous page. Many sites check the referer
                header and treat an empty one as a bot signal, so we set it.
            render_options: Extra browser options (scroll, load_more).
            priority: Slot priority for the waiting lists.
        """
        domain = uo.get_domain_from_url(url)

        if self.http_requestor is None or domain in self.browser_only:
            return await self.fetch_data_through_browser(url, priority=priority, **(render_options or {}))

        page = await self.fetch_data_through_http_request(url, referer=referer, priority=priority)

        dropped = page["status"] == 0 and "resolve host" not in (
                page.get("error") or "")  # no successful connection happened, likely an anti-bot blocked us
        if (page["blocked"] or dropped) and not self.browser_failed:
            if domain not in self.browser_only:
                if settings.VERBOSE:
                    print(f"  [!] {domain} blocks plain HTTP requests -> using the browser for this site")
                self.browser_only.add(domain)  # remember so the next time we go straight to the browser

            data = await self.fetch_data_through_browser(url, priority=priority, **(render_options or {}))

            # If no html came back, page holds the error (e.g. "403 forbidden")
            # which is more useful than an empty string.
            return data if data["html"] else page

        return page

    async def fetch_data_through_http_request(self, url, referer=None, want_json=False, retries=1,
                                              priority=constants.NOW):
        """Tries to fetch a webpage through an http request.

        Returns a dictionary with keys: html, url, status, via, json, blocked, error.

        Args:
            url: The webpage URL.
            referer: URL of the previous page (many sites treat an empty
                referer as a bot signal).
            want_json: Whether the caller wants JSON payloads.
            retries: Amount of retries if the first attempt fails.
            priority: Slot priority for the waiting list.
        """
        headers = {"Accept-Language": "en-US,en;q=0.9"}

        if referer:
            headers["Referer"] = referer
        if want_json:
            headers["Accept"] = "application/json, text/plain, */*"

        error = None
        for attempt in range(retries + 1):

            # Delay before retrying: retrying without a pause risks bot detection.
            wait = 0.5 * (attempt + 1)

            async with self.initiate_slot_manager_for_site(url).use_slot(priority):
                try:
                    response = await self.http_requestor.get(url, headers=headers, allow_redirects=True)
                    self.stats["http"] += 1
                    html = ho.decode_body(response.content,
                                          response.headers.get("content-type", ""))
                    status = response.status_code
                    if status == 429 and attempt < retries:  # "too many requests": wait, then retry
                        retry_after = response.headers.get("retry-after", "")
                        wait = min(float(retry_after), 10) if retry_after.isdigit() else 2 * (attempt + 1)

                    elif status < 500 or attempt == retries:
                        # Status < 500 means either success or a definitive
                        # client error (403 forbidden, 404 not found...). The
                        # caller decides what to do with the data.
                        return {"html": html, "url": str(response.url), "status": status, "via": "http",
                                "json": [], "blocked": hh.looks_blocked(status, html)}

                except Exception as e:  # timeout, DNS, connection reset...
                    error = str(e)

                    # "resolve host" means the DNS lookup failed: retrying is pointless.
                    if "resolve host" in error:
                        break

            await asyncio.sleep(wait)

        return {"html": "", "url": url, "status": 0, "via": "http", "json": [], "blocked": False, "error": error}

    async def start_browser(self):
        """Starts a headless browser with flags that hide the automation."""
        async with self.browser_lock:

            # Already running, or a previous attempt failed permanently.
            if self.browser or self.browser_failed:
                return self.browser is not None
            try:
                if settings.VERBOSE:
                    print("[*] Starting the browser")
                from playwright.async_api import async_playwright

                self.playwright = await asyncio.wait_for(async_playwright().start(),
                                                         timeout=BROWSER_START_TIMEOUT)

                # Flags that make the browser act like a normal one:
                # --disable-blink-features=AutomationControlled -> hide automation flags.
                # --no-sandbox -> sandboxes sometimes crash headless browsers.
                # --disable-dev-shm-usage -> avoid shared-memory exhaustion crashes.
                args = ["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]

                try:  # full Chromium in "new headless" mode looks like a normal browser to websites
                    self.browser = await asyncio.wait_for(
                        self.playwright.chromium.launch(headless=True, channel="chromium", args=args),
                        timeout=BROWSER_START_TIMEOUT)
                except Exception:
                    self.browser = await asyncio.wait_for(
                        self.playwright.chromium.launch(headless=True, args=args),
                        timeout=BROWSER_START_TIMEOUT)  # no system chromium -> bundled build

                major = self.browser.version.split(".")[0]  # extract the browser's major version

                system = {"darwin": "Macintosh; Intel Mac OS X 10_15_7", "win32": "Windows NT 10.0; Win64; x64"}

                system_info = (f"Mozilla/5.0 ({system.get(sys.platform, 'X11; Linux x86_64')}) AppleWebKit/537.36 "
                               f"(KHTML, like Gecko) Chrome/{major}.0.0.0 Safari/537.36")

                self.context = await safe_call(self.browser.new_context(user_agent=system_info, locale="en-US",
                                                                        viewport={"width": 1366, "height": 900}),
                                               BROWSER_START_TIMEOUT)
                if self.context is None:
                    raise RuntimeError("creating the browser context timed out")

                # Inject a script before pages load that makes navigator.webdriver
                # return undefined instead of true (automation detector).
                await safe_call(self.context.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"), 10)

                # Intercept heavy media (videos, fonts...) and tracker software
                # (Google Analytics, Facebook pixels...) to load pages faster.
                await safe_call(self.context.route(re_c.HEAVY_RE, lambda route: route.abort()), 10)
                await safe_call(self.context.route(re_c.TRACKER_RE, lambda route: route.abort()), 10)
                return True

            except Exception as e:
                self.browser_failed = True
                print(f"[!] The browser could not start ({e}). Run: playwright install chromium")
                return False

    async def fetch_data_through_browser(self, url, scroll=True, load_more=False, priority=constants.NOW):
        """Starts a headless browser, opens the page, and extracts its data.

        Returns a dictionary with keys: html, url, status, via, json, blocked, error.

        Args:
            url: The webpage URL.
            scroll: Whether to scroll through the page (loads lazy content).
            load_more: Whether to click "see more jobs" style buttons.
            priority: Slot priority for the browser-tab waiting list.
        """
        if not await self.start_browser():
            return {"html": "", "url": url, "status": 0, "via": "browser", "json": [], "blocked": False}

        async with self.tabs.use_slot(priority):
            try:
                page = await safe_call(self.context.new_page(), PAGE_CALL_TIMEOUT)
                if page is None:
                    return {"html": "", "url": url, "status": 0, "via": "browser", "json": [], "blocked": False,
                            "error": "opening a browser tab timed out"}
            except Exception as e:  # the browser crashed or was closed
                return {"html": "", "url": url, "status": 0, "via": "browser", "json": [], "blocked": False,
                        "error": str(e)}

            captured, pending, inflight = [], [], {}

            async def keep_json(response):
                try:
                    body = await response.text()
                    if 20 < len(body) < 10_000_000:
                        captured.append({"url": response.url, "method": response.request.method,
                                         "data": json.loads(body)})
                except Exception:
                    pass

            def on_response(response):
                if len(pending) < 150 and response.request.resource_type in ("xhr", "fetch") and \
                        "json" in (response.headers.get("content-type") or ""):
                    pending.append(asyncio.ensure_future(keep_json(response)))

            def on_request(request):
                inflight[request] = time.perf_counter()

            page.on("response", on_response)
            page.on("request", on_request)
            page.on("requestfinished", lambda request: inflight.pop(request, None))
            page.on("requestfailed", lambda request: inflight.pop(request, None))

            try:
                response = await page.goto(url, wait_until="domcontentloaded",
                                           timeout=(settings.REQUEST_TIMEOUT + 10) * 1000)

                status = response.status if response else 0

                await self.load_all_page_elements(page, inflight, scroll, load_more)
                html = await self.content(page)

                for _ in range(5):  # letting JavaScript challenges clear by themselves
                    if not hh.looks_blocked(status, html):
                        break
                    await page.wait_for_timeout(2000)
                    html = await self.content(page)
                    if not hh.looks_blocked(200, html):
                        status = 200
                        await self.load_all_page_elements(page, inflight, scroll, load_more)
                        html = await self.content(page)

                if pending:
                    await asyncio.wait(pending, timeout=3)
                self.stats["browser"] += 1

                if not hh.looks_blocked(status, html) and self.http_requestor is not None:
                    # Share the browser's cookies with the http session so
                    # future requests stay on the fast http path.
                    for cookie in (await safe_call(self.context.cookies(), 10) or []):
                        self.http_requestor.cookies.set(cookie["name"], cookie["value"],
                                                        domain=cookie.get("domain", ""),
                                                        path=cookie.get("path", "/"))

                return {"html": html, "url": page.url, "status": status, "via": "browser", "json": captured,
                        "blocked": hh.looks_blocked(status, html)}

            except Exception as e:
                return {"html": "", "url": url, "status": 0, "via": "browser", "json": captured, "blocked": False,
                        "error": str(e)}

            finally:
                await safe_call(page.close(), 10)

    @staticmethod
    async def wait_until_page_loads(page, inflight, max_seconds, quiet_seconds=0.5):
        """Waits for a page to load without ever waiting forever.

        Args:
            page: The Playwright page.
            inflight: Dict tracking the currently active network requests.
            max_seconds: Hard cap on waiting time.
            quiet_seconds: How long the page must stay stable (no network
                activity and no DOM changes) to be considered loaded.
        """
        end, last, quiet_since, idle_since = time.perf_counter() + max_seconds, -1, None, None
        while True:
            count = await safe_call(page.evaluate(js.COUNT_JS), PAGE_CALL_TIMEOUT)
            if count is None:  # the page is navigating and changing (still loading)
                return

            now = time.perf_counter()

            busy = any(now - started < 4.0 for started in inflight.values())

            idle_since = None if busy else (idle_since or now)
            quiet_since = None if (busy or count != last) else (quiet_since or now)

            # Exit when the page is quiet long enough, or the time cap hits,
            # or the page idles: otherwise this could run forever.
            if (quiet_since and now - quiet_since >= quiet_seconds) or now >= end or (
                    idle_since and now - idle_since >= 1.0):
                return

            last = count
            await asyncio.sleep(0.1)  # pause 100ms between polls

    async def load_all_page_elements(self, page, inflight, scroll, load_more):
        """Loads everything on the page, including lazy-loaded content, by
        scrolling and clicking "see more" buttons.

        Args:
            page: The Playwright page.
            inflight: Dict tracking the active network requests.
            scroll: Whether to scroll through the page.
            load_more: Whether to click "see more jobs" buttons.
        """
        await self.wait_until_page_loads(page, inflight, 5.0)
        try:
            # Some sites load only parts of the page until you scroll, so we
            # scroll through it to load everything.
            if scroll:
                await safe_call(page.evaluate(js.SCROLL_JS), PAGE_CALL_TIMEOUT)
                await self.wait_until_page_loads(page, inflight, 3.0, 0.4)

            # Job search pages reveal more results through "see more" buttons.
            if load_more:
                clicked = False
                for _ in range(settings.LOAD_MORE_CLICKS or 5):
                    before_clicking = await safe_call(page.evaluate(js.CLICK_MORE_JOBS_JS), PAGE_CALL_TIMEOUT)
                    if before_clicking is None or before_clicking < 0:  # no button, or the tab stopped responding
                        break

                    clicked = True
                    await self.wait_until_page_loads(page, inflight, 4.0, 0.6)

                    # If the element count did not grow, the click did nothing.
                    current_count = await safe_call(page.evaluate(js.COUNT_JS), PAGE_CALL_TIMEOUT)
                    if current_count is None or current_count <= before_clicking:
                        break

                if clicked:
                    await safe_call(page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)"),
                                    PAGE_CALL_TIMEOUT)
                    await self.wait_until_page_loads(page, inflight, 2.0, 0.4)

        except Exception:
            pass

    @staticmethod
    async def content(page):
        """Returns the page's HTML content.

        Retries a few times when the page is still loading, returning an empty
        string if it never settles.
        """
        for _ in range(3):
            html = await safe_call(page.content(), PAGE_CALL_TIMEOUT)
            if html is not None:
                return html

            await safe_call(page.wait_for_load_state("domcontentloaded"), 10)

        return ""
