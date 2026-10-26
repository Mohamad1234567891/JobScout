"""Selects the HTTP engine.

Adapted from ShopWise's AsyncSession module. Returns curl_cffi's AsyncSession
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
