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

Job page extraction.

Turns a LinkedIn job posting page into a dictionary with every important
field: title, company, location, posted date, applicant count, employment
type, seniority, industries, the full description, and the requirements the
employer asks for (experience, education, certificates, skills).

Follows a layered strategy: structured
data first (JSON-LD JobPosting / meta tags), visible DOM second, regex
fallbacks last.

"""

import re

from urllib.parse import urljoin, urlparse, parse_qs

from src.Constants import constants
from src.Constants import regex_constants as re_c
from src.Core.DataAcquisition.Extraction import requirements as req
from src.Operations import html_operations as ho
from src.Operations import json_operations as jo
from src.Operations import string_operations as so
from src.Operations import url_operations as uo


def is_authwall_url(url):
    """True when the URL is LinkedIn's sign-in wall (guest-blocked posting)."""
    return bool(url) and "/authwall" in url


def recover_url_from_authwall(url):
    """Recovers the original job URL from an authwall redirect.

    LinkedIn redirects guest-blocked postings to
    /authwall?...&sessionRedirect=<encoded original URL>.
    """
    try:
        redirects = parse_qs(urlparse(url).query).get("sessionRedirect")
        if redirects:
            return uo.clean_url(redirects[0])
    except Exception:
        pass
    return None


def _meta_tags(doc):
    """Maps normalized meta property/name keys to their content values."""
    metas = {}
    for meta in doc.xpath("//meta[@content]"):
        key = (meta.get("property") or meta.get("name") or meta.get("itemprop") or "").strip().lower()
        if key and key not in metas:
            metas[key] = meta.get("content")
    return metas


def _job_id_of(doc, page_url):
    """Returns the numeric job id from the page URL."""
    match = re_c.JOB_URL_RE.search(page_url)
    if match:
        return match.group("id")
    return None


def _comment_text(el):
    """Returns text stored inside HTML comments of an element."""
    from lxml import etree
    return " ".join(so.clean(c.text) or "" for c in el.iterchildren() if isinstance(c, etree._Comment))


def _job_id_from_comment(doc):
    """Reads the numeric id from the decoratedJobPostingId comment block."""
    for code in doc.xpath('//code[@id="decoratedJobPostingId"]'):
        text = _comment_text(code)
        match = re.search(r"(\d{5,})", text)
        if match:
            return match.group(1)
    return None


def _from_json_ld(doc):
    """Extracts job fields from a JSON-LD JobPosting block, if present."""
    data = {}
    for block in jo.json_ld_blocks(doc):
        for node, _ in jo.get_json_hierarchy(block):
            node_keys = {str(k).lower(): k for k in node.keys()}

            raw_types = [node.get(k) for k in ("@type", "type") if node.get(k)]
            types = set()
            for raw in raw_types:
                for value in raw if isinstance(raw, list) else [raw]:
                    if isinstance(value, str):
                        types.add(value.rsplit("/", 1)[-1].rsplit(":", 1)[-1].lower())
            if not (types & constants.JOB_TYPES or "jobposting" in types) and not (
                    types and set(node_keys) & constants.JOB_HINT_KEYS):
                continue

            # Direct values.
            for out_key, json_key in (
                    ("job_title", "title"), ("description", "description"),
                    ("employment_type", "employmenttype"), ("posted_date", "dateposted"),
                    ("valid_through", "validthrough")):
                value = node.get(json_key)
                if value is not None and out_key not in data:
                    data[out_key] = so.clean(value)

            org = node.get("hiringOrganization") or node.get("hiringorganization")
            if isinstance(org, dict) and "company_name" not in data:
                data["company_name"] = so.clean(org.get("name"))

            location = node.get("jobLocation") or node.get("joblocation")
            if isinstance(location, dict) and "location" not in data:
                address = location.get("address") or {}
                if isinstance(address, dict):
                    data["location"] = so.clean(" ".join(filter(None, (
                        address.get("addressLocality"), address.get("addressRegion"),
                        address.get("addressCountry")))))
                if not data.get("location"):
                    data["location"] = so.clean(location.get("name") or location.get("description"))

            # Requirements lists.
            for key in ("educationRequirements", "experienceRequirements", "qualifications", "skills",
                        "responsibilities"):
                value = node.get(key)
                if isinstance(value, str):
                    if key not in data:
                        data[key] = so.clean(value)
                elif isinstance(value, list):
                    items = []
                    for item in value:
                        if isinstance(item, str):
                            text = so.clean(item)
                        elif isinstance(item, dict):
                            text = so.clean(item.get("name") or item.get("description") or item.get("@type"))
                        else:
                            text = so.clean(item)
                        if text:
                            items.append(text)
                    if items and key not in data:
                        data[key] = items

    return data


def _from_dom(doc, metas):
    """Extracts job fields from the visible page markup."""
    data = {}

    # Title: <h1 class="top-card-layout__title">.
    for el in doc.xpath('//h1[contains(@class,"top-card-layout__title")]'):
        data["job_title"] = so.clean(el.text_content())
        break

    # Company: <a class="topcard__org-name-link">.
    for el in doc.xpath('//a[contains(@class,"topcard__org-name-link")]'):
        data["company_name"] = so.clean(el.text_content())
        break

    # Location: <span class="sub-nav-cta__meta-text">.
    for el in doc.xpath('//span[contains(@class,"sub-nav-cta__meta-text")]'):
        data["location"] = so.clean(el.text_content())
        break

    # Posted: <span class="posted-time-ago__text"> ("3 days ago").
    for el in doc.xpath('//span[contains(@class,"posted-time-ago__text")]'):
        data["posted_time_ago"] = so.clean(el.text_content())
        break

    # Applicants: <span/figcaption class="num-applicants__caption"> ("70 applicants").
    for el in doc.xpath('//*[contains(@class,"num-applicants__caption")]'):
        data["applicants"] = so.clean(el.text_content())
        break

    # Criteria list: seniority level / employment type / job function / industries.
    criteria = {}
    for item in doc.xpath('//li[contains(@class,"description__job-criteria-item")]'):
        header = item.xpath('.//*[contains(@class,"description__job-criteria-subheader")]')
        value = item.xpath('.//*[contains(@class,"description__job-criteria-text")]')
        if header and value:
            criteria[so.clean(header[0].text_content()).lower()] = so.clean(value[0].text_content())

    if criteria.get("seniority level"):
        data["seniority_level"] = criteria["seniority level"]
    if criteria.get("employment type"):
        data["employment_type"] = criteria["employment type"]
    if criteria.get("job function"):
        data["job_function"] = criteria["job function"]
    if criteria.get("industries"):
        data["industries"] = criteria["industries"]

    # Description: <div class="show-more-less-html__markup">, preserving block structure.
    for el in doc.xpath('//div[contains(@class,"show-more-less-html__markup")]'):
        text = so.structured_text(el)
        if text:
            data["description"] = text
            break

    # Fallbacks from meta tags.
    og_title = metas.get("og:title")
    if og_title:
        match = re_c.OG_TITLE_RE.match(og_title)
        if match:
            if not data.get("company_name"):
                data["company_name"] = match.group("company").strip()
            if not data.get("job_title"):
                data["job_title"] = match.group("title").strip()
            if not data.get("location"):
                data["location"] = match.group("location").strip()

    if not data.get("description"):
        data["description"] = metas.get("og:description") or metas.get("description")

    # Posted time from the meta description ("Posted 5:43:49 PM.").
    meta_desc = metas.get("description") or metas.get("og:description") or ""
    match = re_c.POSTED_META_RE.search(meta_desc)
    if match:
        data["posted_at"] = match.group(1)

    return data


def extract_job_page(html, page_url, captured=()):
    """Extracts all important fields from a LinkedIn job posting page.

    Args:
        html (str): Raw HTML of the job page.
        page_url (str): The absolute URL of the job page.
        captured (tuple): JSON payloads captured from XHR calls (optional).

    Returns:
        dict: The extracted job with keys like job_title, company_name,
        location, description, experience_requirements,
        education_requirements, certificates, skills...
    """
    # Guest-blocked postings: nothing to extract, recover the original URL.
    if is_authwall_url(page_url):
        return {"job_url": recover_url_from_authwall(page_url) or page_url, "requires_login": True}

    doc = ho.parse_html(html)
    metas = _meta_tags(doc)

    data = _from_json_ld(doc)
    dom = _from_dom(doc, metas)

    # The visible DOM is fresher than any structured block; use it to fill gaps.
    for key, value in dom.items():
        if value and not data.get(key):
            data[key] = value
    for key, value in data.items():
        if not value and dom.get(key):
            data[key] = dom[key]

    # Job id: URL first, then the decoratedJobPostingId comment.
    data["job_id"] = _job_id_of(doc, page_url) or _job_id_from_comment(doc)
    data["job_url"] = uo.clean_url(page_url)

    # Page title fallback for the title/company pair.
    if not data.get("job_title"):
        page_title = so.clean(doc.findtext(".//title"))
        match = re_c.PAGE_TITLE_RE.match(page_title or "")
        if match:
            data["job_title"] = match.group("title").strip()
            if not data.get("company_name"):
                data["company_name"] = match.group("company").strip()

    # Seniority fallback from the title (e.g. "Senior AI Engineer").
    if not data.get("seniority_level") and data.get("job_title"):
        words = so.words_of_text(data["job_title"])
        seniority = sorted(words & constants.SENIORITY_WORDS, key=lambda w: data["job_title"].lower().find(w))
        if seniority:
            data["seniority_level"] = seniority[0].title()

    # Employment type fallback from description text.
    if not data.get("employment_type") and data.get("description"):
        words = set(re.findall(r"[\w-]+", data["description"].lower()))
        types = sorted(words & constants.EMPLOYMENT_TYPE_WORDS,
                       key=lambda w: data["description"].lower().find(w))
        if types:
            data["employment_type"] = types[0].title()

    # Applicants count as an integer when possible.
    if data.get("applicants"):
        match = re_c.APPLICANTS_RE.search(data["applicants"])
        if match:
            data["applicant_count"] = so.get_count(match.group(1))
        if data.get("applicant_count") is None:
            data.pop("applicant_count", None)

    # Requirements: parsed out of the description.
    description = data.get("description") or ""
    requirement_lines = req.extract_requirement_sections(description)
    requirement_text = "\n".join(requirement_lines)

    data["description"] = so.clean(description)
    data["requirement_section"] = requirement_text or None
    data["experience_requirements"] = req.extract_experience_requirements(requirement_text)
    data["education_requirements"] = req.extract_education_requirements(requirement_text)
    data["certificates"] = req.extract_certificates(requirement_text)
    data["skills"] = req.extract_skills(requirement_text)
    data["languages"] = req.extract_languages(requirement_text)

    return data
