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

Text cleaning and tokenization utilities for the extraction pipeline.

Text workhorse helpers with standard Python naming
conventions and with the review-only helpers removed. Everything here is
generic text work: HTML-entity and invisible-character cleaning, international
number parsing, count suffixes, class/id tokenization, and a block-aware text
walker used for job descriptions.

"""

import re
import unicodedata

from functools import lru_cache
from html import unescape
from lxml import etree
from lxml import html as lxml_html

from src.Constants import constants
from src.Constants import regex_constants as re_c


def clean(value):
    """Cleans raw scraped HTML data into a clean single-line string.

    Handles lists, tuples and dicts by extracting the first valid value,
    decodes HTML entities, and removes extra whitespace, tabs and newlines.

    Examples:
        value = "  AI &amp; Machine&nbsp;Learning Engineer\\n  "
        output -> "AI & Machine Learning Engineer"
    """
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (list, tuple)):
        return clean(next((v for v in value if v not in (None, "")), None))

    if isinstance(value, dict):
        return clean(value.get("name") or value.get("@value") or value.get("value"))

    # Also strips zero-width space (U+200B) and zero-width no-break space
    # (U+FEFF): websites sprinkle them into text to break pattern matching.
    text = re.sub(r"\s+", " ", unescape(str(value)).replace("\u200b", "").replace("\ufeff", "")).strip()

    return text or None


def to_ascii_digits(text):
    """Converts non-ASCII digit characters into ASCII digits.

    Non-ASCII digits appear on pages from non-English speaking regions
    (e.g. Persian, Arabic-Indic digits).
    """
    if text.isascii():
        return text

    out = []
    for ch in text:
        digit = unicodedata.decimal(ch, None) if not ch.isascii() else None
        out.append(str(digit) if digit is not None else ch)

    return "".join(out).replace("\u066b", ".").replace("\u066c", ",")


def to_number(str_number):
    """Converts international number formats into a standard Python float.

    Examples:
        '4,6' -> 4.6
        '1.234' -> 1234
        '1,234.50' -> 1234.5
        '1 234' -> 1234
    """
    s = str_number.replace(" ", "").replace("'", "").replace("\u2019", "")

    if "." in s and "," in s:
        decimal = "." if s.rfind(".") > s.rfind(",") else ","
        s = s.replace("," if decimal == "." else ".", "").replace(decimal, ".")

    elif "." in s or "," in s:
        sep = "." if "." in s else ","
        parts = s.split(sep)

        if len(parts) > 2:
            s = "".join(parts) if len(parts[-1]) == 3 else "".join(parts[:-1]) + "." + parts[-1]
        else:
            head, tail = parts
            s = head + tail if (len(tail) == 3 and 0 < len(head) <= 3 and head != "0") else head + "." + tail

    try:
        return float(s)
    except ValueError:
        return None


def extract_numbers_from_text(text):
    """Extracts all numbers from a string, returning a list of floats.

    Examples:
        text = "The salary is 49.99 USD."
        output -> [49.99]
    """
    text = to_ascii_digits(str(text)).replace("\u00a0", " ").replace("\u202f", " ")

    return [n for n in (to_number(m.group(0)) for m in re_c.NUMBER_RE.finditer(text)) if n is not None]


def get_count(value):
    """Extracts an integer count (applicants, employees...) from a value.

    Examples:
        value = "1.234 applicants"
        output -> 1234
        value = "1.2K ratings"
        output -> 1200
    """
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return int(value) if value >= 0 else None

    text = to_ascii_digits(clean(value) or "")
    match = re_c.NUMBER_RE.search(text)
    if not match:
        return None

    number = to_number(match.group(0))
    if number is None:
        return None

    # Suffix within the next 5 characters: K/Bin/Mil (x1000) or M (x1.000.000).
    suffix = text[match.end():match.end() + 5].strip().lower()
    if re.match(r"(k|bin|mil)\b", suffix):
        number *= 1000
    elif re.match(r"m\b", suffix):
        number *= 1_000_000
    elif number != int(number):
        return None  # a count can never be a non-integer value

    return int(number)


def strip_html_tags(html):
    """Removes all HTML markup and returns only the text within it."""
    if "<" in html and ">" in html:
        try:
            return clean(lxml_html.fromstring(html).text_content())
        except (etree.ParserError, ValueError):
            pass
    return clean(html)


@lru_cache(maxsize=200_000)
def words_of_text(attrs):
    """Splits an attribute string into a frozenset of lowercase word tokens."""
    return frozenset(t for t in re.split(r"[\W_]+", re_c.CAMEL_RE.sub(r"\1 \2", attrs).lower()) if t)


def text_of(el):
    """Returns the cleaned visible text of an element (empty string if none)."""
    return clean(el.text_content()) or ""


def structured_text(root, block_tags=("li", "p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "ul", "ol",
                                       "section", "tr", "br")):
    """Returns the text of an element while preserving block boundaries.

    Unlike text_content(), this inserts a newline at every block-level
    element, so bullet lists in job descriptions stay one requirement per
    line - which is what the requirement parsers need. Unlike clean(), the
    newlines survive (clean collapses all whitespace).

    Args:
        root: The lxml element to walk.
        block_tags: Tags that force a line break in the output.

    Returns:
        str: The structured text, one block per line.
    """
    parts = []

    def walk(node):
        if node.tag in block_tags and parts:
            parts.append("\n")
        if node.text:
            parts.append(node.text)
        for child in node:
            if isinstance(child.tag, str):
                walk(child)
            if child.tail:
                parts.append(child.tail)
            if isinstance(child.tag, str) and child.tag in block_tags:
                parts.append("\n")

    walk(root)

    # Clean up per character while keeping line boundaries: decode entities,
    # drop invisible characters, normalize horizontal whitespace, then trim
    # repeated empty lines.
    text = unescape("".join(parts)).replace("\u200b", "").replace("\ufeff", "")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)

    return text.strip() or ""


def is_hash_part(part):
    """True when a class/id token is an auto-generated hash or build artifact.

    Examples:
        is_hash_part("KaU17BbDowCW") -> True
        is_hash_part("job-card")      -> False
    """
    if re_c.HASH_RE.match(part):
        return True
    if part.islower() or len(part) < 6:
        return False
    upper = sum(ch.isupper() for ch in part[1:])
    return upper >= 3 and upper / len(part) >= 0.25


def split_name(name):
    """Splits a compound class/id/hook name into lowercase word tokens,
    dropping hash segments and handling camelCase boundaries (cached)."""
    parts = [part for part in re.split(r"[\W_]+", name) if part and not is_hash_part(part)]
    return tuple(t for part in parts for t in re_c.CAMEL_RE.sub(r"\1 \2", part).lower().split() if t)


@lru_cache(maxsize=200_000)
def name_set(name):
    """Converts a raw class/attribute name into a frozenset of word tokens."""
    return frozenset(split_name(name))


def element_names(el):
    """Extracts all raw class strings and hint attributes from an element."""
    names = []
    for key, value in el.attrib.items():
        if key == "class":
            names += value.split()
        elif key in constants.HINT_ATTRIBUTES and key not in ("aria-label", "role"):
            names.append(value)
    return names


def name_tokens(el):
    """Returns ordered token sequences for each class/id/data-hook name."""
    return [split_name(n) for n in element_names(el)]


def name_words(el):
    """Returns a list of frozensets with the word tokens of each attribute."""
    return [name_set(n) for n in element_names(el)]


def is_counter_text(text):
    """True when a short text is a counter widget ('(87)', '70 applicants')"""
    return len(text) <= 40 and bool(
        re.fullmatch(r"\(\s*([\d.,]+)\s*[^\d()]{0,25}\)", text) or
        re.search(r"^\s*[\d.,]+\s*(?:applicants?|people|views?)\s*$", text, re.I))


def is_valid_text(text):
    """True when a text string looks like real prose worth extracting.

    Filters out counters, code snippets, UI boilerplate, and strings that are
    only numbers and punctuation.
    """
    return bool(text) and 2 <= len(text) <= 20000 and not re.fullmatch(r"[\d\W_]+", text) and \
        not is_counter_text(text) and not re.search(r"function\s*\(|=>\s*\{|\bvar\s+\w+\s*=|\{\s*\"\w+\"\s*:",
                                                    text)
