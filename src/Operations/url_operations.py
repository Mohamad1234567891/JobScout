"""URL cleaning and link intelligence.

Adapted from ShopWise's URLOperations with standard Python naming. Strips
tracking parameters, builds canonical comparable URLs, detects search-result
URLs, extracts IDs, resolves the real site domain (including two-part country
domains) and picks the best link from a set of anchors.
"""

import re

from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl, urljoin

from src.Constants import constants
from src.Constants import regex_constants as re_c
from src.Operations import html_operations as ho
from src.Operations import string_operations as so


def clean_url(url):
    """Cleans a URL from junk like trackers (Google Analytics, Microsoft Ads...).

    Examples:
        url = "https://www.linkedin.com/jobs/view/ai-engineer-123?position=1&refId=xyz&utm_source=google"
        output -> "https://www.linkedin.com/jobs/view/ai-engineer-123?position=1"
    """
    parsed = urlparse(url)
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
             if not re_c.TRACKING_PARAM_RE.match(k)]

    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.params, urlencode(query), ""))


def clean_sort_url(url):
    """Builds a canonical comparable URL: ignores http/https, 'www.', trailing
    slash and tracking parameters, and sorts the query alphabetically."""
    parsed = urlparse(clean_url(url))

    host = parsed.netloc.lower()
    host = host[4:] if host.startswith("www.") else host

    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))

    return f"{host}{parsed.path.rstrip('/')}" + (f"?{query}" if query else "")


def looks_like_search_url(url):
    """True when the URL points to a site's search-results page."""
    parsed = urlparse(url)
    query_keys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & {"q", "s", "k", "text", "query", "keywords", "search", "search_query", "nkw", "_nkw"}:
        return True
    return bool(re.search(
        r"/(?:search|jobs|sr|ara|arama|arar|sch|suche|recherche|busqueda|busca|ricerca)(?:/|$|\.html)",
        parsed.path.lower()))


def extract_ids(url, extra=()):
    """Detects and extracts IDs from a URL path and optional extra metadata.

    Examples:
        url = "https://www.linkedin.com/jobs/view/ai-engineer-4482734200"
        output -> {'urlLast': '4482734200', 'urlFirst': 'ai'}
    """
    ids = {}
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", urlparse(url).path) if len(p) >= 5 and re.search(r"\d", p)]
    if parts:
        ids["urlLast"] = parts[-1]
        ids["urlFirst"] = parts[0]

    for key, value in extra:
        if isinstance(value, (str, int)) and not isinstance(value, bool) and len(str(value).strip()) >= 5:
            ids[key] = str(value).strip()
    return ids


def get_domain_from_url(url):
    """Extracts the registrable domain from a URL.

    Examples:
        https://www.linkedin.com/jobs -> linkedin.com
        https://www.example.com.tr/x -> example.com.tr
    """
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in constants.SECOND_LEVEL and len(parts[-1]) == 2:
        return ".".join(parts[-3:])

    return ".".join(parts[-2:])


def first_url(value, base_url):
    """Extracts and resolves the first valid URL from strings, lists or dicts
    holding URL keys, relative to a base URL."""
    for _ in range(3):
        if isinstance(value, list):
            value = value[0] if value else None
        elif isinstance(value, dict):
            value = value.get("url") or value.get("contentUrl") or value.get("src") or value.get("@id")

    if isinstance(value, str) and value.strip() and not value.strip().startswith("data:"):
        return urljoin(base_url, value.strip())

    return None


def primary_link(links):
    """Scores candidate links (images, link text length, title attributes) and
    returns the absolute URL with the highest score."""
    scores, urls = {}, {}
    for a, url in links:
        key = clean_sort_url(url)
        urls.setdefault(key, url)
        scores[key] = (
            scores.get(key, 0) + 1 +
            2 * bool(a.xpath(".//img")) +
            2 * (len(so.text_of(a)) >= 10) +
            bool(a.get("title"))
        )
    return urls[max(scores, key=lambda k: scores[k])] if scores else None


def pattern_links(doc, page_url):
    """Fallback link extraction: identifies rich anchor links that repeat the
    same URL structural pattern across the page (a listing grid), excluding
    menus."""
    groups = {}
    for a, url in ho.site_links(doc, page_url, get_domain_from_url(page_url)):
        if not ho.is_rich(a) or any(
                x.tag in ("header", "footer", "nav") or ho.extract_semantic(x) & {
                    "menu", "nav", "navigation", "megamenu", "breadcrumb", "footer"}
                for x in a.iterancestors()):
            continue

        parts = [p for p in urlparse(url).path.split("/") if p]
        shape = "/".join(parts[:-1]) + ("/*" if parts else "/")
        group = groups.setdefault(shape, {})
        group.setdefault(clean_sort_url(url), (url, len(so.text_of(a) or a.get("title") or "")))

    scored = [(len(g) * (sum(t for _, t in g.values()) / len(g)), g) for g in groups.values() if len(g) >= 3]
    return [url for url, _ in max(scored, key=lambda x: x[0])[1].values()] if scored else []
