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

In-page JavaScript snippets executed by the headless browser.

Progressive scrolling to trigger
lazy-loaded content and DOM element counting are carried over unchanged; the
review-specific clickers were replaced by a "see more jobs" clicker used on
LinkedIn search pages.

"""

# Scroll down step by step (lazy-loaded jobs appear) and end at the bottom.
SCROLL_JS = """async () => {  // scroll down step by step (lazy-loaded jobs appear), end at the bottom
    const height = () => document.documentElement.scrollHeight;
    const steps = Math.min(8, Math.max(2, Math.ceil(height() / window.innerHeight)));
    for (let i = 0; i < steps; i++) {
        window.scrollBy(0, Math.max(window.innerHeight, height() / steps));
        await new Promise(r => setTimeout(r, 150));
    }
    window.scrollTo(0, height()); }"""

COUNT_JS = "document.getElementsByTagName('*').length"

# Words used to recognize a "show more jobs" button across languages.
MORE_WORDS_JS = (r"more|show more|see more|load more|fazla|daha|mehr|weitere|plus|más|mas|altri|mais|meer|"
                 r"więcej|еще|ещё|もっと|更多|더보기|المزيد|all|tüm|alle|tous|todas|tutte")

CLICKABLE_JS = """const clickable = () => Array.from(document.querySelectorAll(
        'button, [role="tab"], [role="button"], a[href^="#"], a[href^="javascript"], summary'))
    .filter(el => el.offsetParent !== null && (el.innerText || '').trim().length > 0 && (el.innerText || '').trim().length < 60);
const isMore = /more|show more|see more|load more|fazla|daha|mehr|weitere|plus|más|mas|altri|mais|meer|więcej|еще|ещё|もっと|更多|더보기|المزيد/i;"""

# Clicks one "see more jobs" button; returns the element count before the
# click (-1 = no button found). Prefers LinkedIn's dedicated button, then
# falls back to text matching.
CLICK_MORE_JOBS_JS = """() => { """ + CLICKABLE_JS + """
    const dedicated = document.querySelector('button.infinite-scroller__show-more-button, ' +
        'button[data-control-name="infinite-scroller_show-more"], button[aria-label*="more jobs" i]');
    const target = dedicated || clickable().find(el => isMore.test(el.innerText) &&
        (/job/i.test(el.innerText) || /job/i.test(el.className || '') || el.closest('[class*="job" i]')));
    if (!target) return -1;
    const before = document.getElementsByTagName('*').length;
    target.click();
    return before; }"""
