"""Job listing page extraction.

Turns a LinkedIn job search page into a list of job entries: URL, id, title,
company, location and posted date. Uses the same layered approach ShopWise
uses for product listings - structured JSON-LD first (ItemList), then the
visible job cards, then raw URL patterns and embedded JSON as fallbacks.
"""

import re

from urllib.parse import urljoin

from src.Constants import constants
from src.Constants import regex_constants as re_c
from src.Operations import html_operations as ho
from src.Operations import json_operations as jo
from src.Operations import string_operations as so
from src.Operations import url_operations as uo


def _add(found, url, title=None, company=None, location=None, posted_date=None):
    """Adds one job entry, deduplicating by numeric job id and merging data.

    Card URLs carry per-card tracking parameters (?position=N&refId=...) and
    country subdomains, so the numeric job id is the only stable identity.
    """
    if not isinstance(url, str) or not url.strip():
        return

    url = uo.clean_url(urljoin("https://www.linkedin.com", url.strip()))
    match = re_c.JOB_URL_RE.search(url)
    if not match or not url.startswith("http"):
        return

    job_id = match.group("id")
    canonical = f"https://www.linkedin.com/jobs/view/{match.group('slug')}-{job_id}/"

    entry = found.setdefault(job_id, {
        "job_url": canonical,
        "job_id": job_id,
        "title": None,
        "company": None,
        "location": None,
        "posted_date": None,
    })
    # Later sources (cards) are richer than earlier ones (raw URLs): fill gaps.
    if title and not entry["title"]:
        entry["title"] = title
    if company and not entry["company"]:
        entry["company"] = company
    if location and not entry["location"]:
        entry["location"] = location
    if posted_date and not entry["posted_date"]:
        entry["posted_date"] = posted_date


def _item_list_entries(doc):
    """Yields (url, title, company, location) from a JSON-LD ItemList block."""
    for block in jo.json_ld_blocks(doc):
        for node, _ in jo.get_json_hierarchy(block):
            if "itemlistelement" not in {str(k).lower() for k in node.keys()}:
                continue
            items = node.get("itemListElement") or node.get("itemlistelement")
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                yield (item.get("url"), so.clean(item.get("name")),
                       so.clean(item.get("disambiguatingDescription")),
                       so.clean(item.get("description")))


def _job_cards(doc):
    """Yields (url, title, company, location, posted_date) from the visible cards."""
    # Each card carries data-entity-urn="urn:li:jobPosting:<id>".
    for card in doc.xpath('//*[contains(@class,"base-search-card")][@data-entity-urn]'):
        anchor = card.xpath('.//a[contains(@class,"base-card__full-link")]/@href')
        title_el = card.xpath('.//*[contains(@class,"base-search-card__title")]')
        company_el = card.xpath('.//*[contains(@class,"base-search-card__subtitle")]')
        location_el = card.xpath('.//*[contains(@class,"job-search-card__location")]')
        time_el = card.xpath('.//time[@datetime]')

        if not anchor:
            continue

        title = so.clean(title_el[0].text_content()) if title_el else None
        company = so.clean(company_el[0].text_content()) if company_el else None
        location = so.clean(location_el[0].text_content()) if location_el else None
        posted_date = (time_el[0].get("datetime") or "").strip() if time_el else None

        yield anchor[0], title, company, location, posted_date


def _url_patterns(doc):
    """Fallback: every /jobs/view/<id> href on the page, in document order."""
    return [href for href in doc.xpath("//a/@href") if re_c.JOB_URL_RE.search(href or "")]


def _urls_from_json(blocks):
    """Fallback: /jobs/view/ URLs found inside embedded JSON blocks."""
    urls = []
    for block in blocks:
        for node, _ in jo.get_json_hierarchy(block):
            for key in constants.URL_KEYS:
                value = node.get(key)
                if isinstance(value, dict):
                    value = value.get("href") or value.get("url")
                if isinstance(value, str) and re_c.JOB_URL_RE.search(value):
                    urls.append(value)
                    break
    return urls


def extract_listing_links(html, page_url, captured=()):
    """Extracts all job entries from a LinkedIn search page.

    Args:
        html (str): Raw HTML of the search page.
        page_url (str): The absolute URL of the search page.
        captured (tuple): JSON payloads captured from XHR calls (optional).

    Returns:
        list[dict]: One dict per job with keys job_url, job_id, title,
        company, location, posted_date.
    """
    doc = ho.parse_html(html)
    found = {}

    # 1. JSON-LD ItemList (most reliable structure on LinkedIn search pages).
    for url, title, company, location in _item_list_entries(doc):
        _add(found, url, title=title, company=company, location=location)

    # 2. Visible job cards - they additionally carry the posted date.
    for url, title, company, location, posted_date in _job_cards(doc):
        _add(found, url, title=title, company=company, location=location, posted_date=posted_date)

    # 3. Raw /jobs/view/ URLs anywhere on the page.
    for url in _url_patterns(doc):
        _add(found, url)

    # 4. Embedded JSON blocks and captured XHR payloads.
    blocks = jo.embedded_json(doc) + [item["data"] for item in captured]
    for url in _urls_from_json(blocks):
        _add(found, url)

    return list(found.values())
