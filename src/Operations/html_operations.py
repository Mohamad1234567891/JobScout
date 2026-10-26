"""HTML parsing and semantics for the job pipeline.

Adapted from ShopWise's HTMLOperations with standard Python naming and with
the product-card (price-based) discovery removed - job cards have their own
logic in extraction/job_listing.py. Kept here: lxml parsing, encoding
detection, microdata/Schema.org extraction, visibility checks and internal
link collection.
"""

import re

from lxml import etree
from lxml import html as lxml_html
from urllib.parse import urljoin, urlparse

from src.Constants import constants
from src.Constants import regex_constants as re_c
from src.Operations import string_operations as so
from src.Operations import url_operations as uo


def extract_semantic(el):
    """Extracts semantic keyword tokens from an element's HTML attributes.

    Examples:
        # <div id="job-card" class="base-search-card">...
        output -> {'job', 'card', 'base', 'search'}
    """
    return so.words_of_text(" ".join(v for k, v in el.attrib.items() if k in constants.HINT_ATTRIBUTES))


def parse_html(html):
    """Parses HTML bytes/str into an lxml document tree (empty doc on failure)."""
    try:
        return lxml_html.document_fromstring(html.encode("utf-8", "replace"),
                                             parser=lxml_html.HTMLParser(encoding="utf-8",
                                                                         remove_comments=True))
    except (etree.ParserError, ValueError):
        return lxml_html.document_fromstring(b"<html><body></body></html>")


def decode_body(content, content_type):
    """Decodes raw HTTP response bytes into a unicode string.

    The charset is detected from the Content-Type header, HTML meta tags,
    or common fallback encodings.

    Args:
        content (bytes): Raw response body bytes.
        content_type (str): HTTP Content-Type header value.

    Returns:
        str: The decoded response body.
    """
    match = re.search(r"charset=([\w\-]+)", content_type or "", re.I)
    charset = match.group(1) if match else None

    if not charset:
        meta = re.search(rb"<meta[^>]+charset=[\"']?\s*([A-Za-z0-9_\-]+)", content[:4096], re.I)
        charset = meta.group(1).decode("ascii", "ignore") if meta else None

    for encoding in (charset, "utf-8"):
        if encoding:
            try:
                return content.decode(encoding)
            except (LookupError, UnicodeDecodeError):
                pass

    return content.decode("utf-8", errors="replace")


def microdata_value(el):
    """Extracts the underlying value of an HTML5 microdata element.

    Returns the content attribute when present, href for links, src/data-src
    for media elements, datetime for time tags, or the text content otherwise.
    """
    tag = el.tag.lower() if isinstance(el.tag, str) else ""
    if el.get("content") is not None:
        return el.get("content")
    if tag in ("a", "link", "area"):
        return el.get("href")
    if tag in ("img", "source", "video", "audio", "iframe", "embed"):
        src = el.get("src") or ""
        return el.get("data-src") if (not src or src.startswith("data:")) and el.get("data-src") else src
    if tag in ("data", "meter"):
        return el.get("value")
    if tag == "time":
        return el.get("datetime") or el.text_content()
    return el.text_content()


def microdata_item(scope, depth=0):
    """Parses an itemscope/itemtype element tree into a dictionary resembling
    JSON-LD objects (bounded recursion, iteratively walked).

    Args:
        scope: The lxml element marked with itemscope.
        depth: Current recursion depth used to limit nested item parsing.

    Returns:
        dict: Structured microdata of the scope.
    """
    node = {"@type": (scope.get("itemtype") or "").split()[0] if scope.get("itemtype") else ""}
    stack = [child for child in reversed(scope) if isinstance(child.tag, str)]

    while stack:
        el = stack.pop()
        nested = el.get("itemscope") is not None
        if el.get("itemprop"):
            value = microdata_item(el, depth + 1) if nested and depth < 5 else microdata_value(el)
            if value not in (None, ""):
                for name in el.get("itemprop").split():
                    if name in node:
                        node[name] = (node[name] if isinstance(node[name], list) else [node[name]]) + [value]
                    else:
                        node[name] = value

        if not nested:
            stack.extend(child for child in reversed(el) if isinstance(child.tag, str))

    return node


def is_hidden(el):
    """True when an element is hidden from view (hidden attribute, display:none,
    visibility:hidden, or semantic hidden classes outside responsive breakpoints)."""
    style = (el.get("style") or "").replace(" ", "").lower()
    if el.get("hidden") is not None or el.get("aria-hidden") == "true" or "display:none" in style or \
            "visibility:hidden" in style:
        return True

    return any(({"hidden", "hide", "invisible"} & w and not w & {"xs", "sm", "md", "lg", "xl", "mobile",
                                                                "desktop", "tablet", "print"})
               or {"sr", "only"} <= w for w in so.name_words(el))


def site_links(root, page_url, site):
    """Extracts internal site links from an element tree.

    Resolves relative URLs, filters out anchors, javascript, mailto links,
    and junk path patterns.

    Args:
        root: The root lxml element tree.
        page_url (str): The absolute URL of the current page.
        site (str): The target domain so only internal links are kept.

    Returns:
        list[tuple[etree.Element, str]]: (anchor element, absolute URL) pairs.
    """
    links = []
    for a in root.xpath("descendant-or-self::a[@href]"):
        href = (a.get("href") or "").strip()
        if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
            url = uo.clean_url(urljoin(page_url, href))
            if url.startswith("http") and uo.get_domain_from_url(url) == site and \
                    not re_c.JUNK_PATH_RE.search(urlparse(url).path):
                links.append((a, url))
    return links


def is_rich(a):
    """True when an anchor looks like a detailed listing item (contains an
    image, substantial link text, or a title attribute)."""
    return bool(a.xpath(".//img") or len(so.text_of(a)) >= 15 or len(a.get("title") or "") >= 10)
