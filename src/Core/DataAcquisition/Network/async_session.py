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

Selects the HTTP engine.

Returns curl_cffi's AsyncSession
when it is installed (fast HTTP/2 requests that impersonate Chrome's TLS
fingerprint) and None otherwise, in which case the Fetcher falls back to the
headless browser for every page.

"""


def get_async_session():
    try:
        from curl_cffi.requests import AsyncSession  # fast HTTP with Chrome's fingerprint
        return AsyncSession

    except ImportError:  # still works without it, only slower (every page goes through the browser)
        return None
