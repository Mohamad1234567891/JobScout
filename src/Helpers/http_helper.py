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

Anti-bot detection.

looks_blocked(...) recognizes
bot-blocked responses by status code and by known challenge signatures
(Cloudflare, Akamai, DataDome, PerimeterX...) so the Fetcher can fall back to
the browser for that page.

"""

from src.Constants import regex_constants as re_c


def looks_blocked(status, html):
    """Detects whether an HTTP response indicates anti-bot protection,
    rate-limiting, or a CAPTCHA challenge.

    Args:
        status (int): The HTTP response status code.
        html (str): The raw HTML response body content.

    Returns:
        bool: True when the response looks blocked or challenged.
    """
    # Typical blocking status codes, or suspiciously short 503 error pages.
    if status in (401, 403, 407, 429) or (status == 503 and len(html) < 100_000):
        return True

    # Known anti-bot keyword signatures in the leading portion of small/medium pages.
    return len(html) < 400_000 and bool(re_c.BLOCK_RE.search(html[:200_000]))
