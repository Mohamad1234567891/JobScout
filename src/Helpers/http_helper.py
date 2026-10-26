"""Anti-bot detection.

Adapted from ShopWise's HTTPHelper module. looks_blocked(...) recognizes
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
