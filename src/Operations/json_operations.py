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

JSON extraction helpers.

Safely
loads JSON wrapped in comments/CDATA or slightly broken (trailing commas,
several objects in one script), walks nested structures with a bounded DFS,
and pulls Schema.org JSON-LD blocks and embedded frontend state out of pages.

"""

import json
import re

from src.Constants import regex_constants as re_c


def get_json_hierarchy(data, max_nodes=300_000):
    """Iterates a nested JSON structure (dicts and lists) using a depth-first
    search stack, yielding every dictionary with its parent.

    Args:
        data: The JSON-structured data to walk.
        max_nodes: Bounds the number of processed nodes to prevent runaway loops.

    Yields:
        tuple[node, parent]: The current dict and the dict/list containing it
        (None for the root).
    """
    stack, seen = [(data, None)], 0

    while stack and seen < max_nodes:
        node, parent = stack.pop()
        seen += 1

        if isinstance(node, dict):
            yield node, parent
            stack.extend((v, node) for v in reversed(list(node.values())) if isinstance(v, (dict, list)))

        elif isinstance(node, list):
            stack.extend((v, parent) for v in reversed(node) if isinstance(v, (dict, list)))


def load_json(text):
    """A json.loads that survives HTML comments, CDATA, trailing commas and
    several objects inside one script block."""
    if not text:
        return []

    text = re.sub(r"^\s*(?:<!--|//\s*<!\[CDATA\[)|(?:-->|//\s*\]\]>)\s*$", "", text.strip()).strip()

    for candidate in (text, re.sub(r",\s*([}\]])", r"\1", text)):
        try:
            return [json.loads(candidate, strict=False)]
        except ValueError:
            pass

    out, decoder, i = [], json.JSONDecoder(strict=False), 0

    while True:
        starts = [p for p in (text.find("{", i), text.find("[", i)) if p != -1]
        if not starts:
            return out
        try:
            obj, i = decoder.raw_decode(text, min(starts))
            out.append(obj)
        except ValueError:
            i = min(starts) + 1


def json_ld_blocks(doc):
    """Extracts and parses all Schema.org JSON-LD script blocks from an HTML
    document tree (case-insensitive type matching).

    Returns:
        list: Parsed JSON-LD data objects.
    """
    blocks = []
    for script in doc.xpath('//script[contains(translate(@type,"LDJSON","ldjson"),"ld+json")]'):
        blocks.extend(load_json(script.text))
    return blocks


def embedded_json(doc):
    """Extracts parsed JSON data blocks from inline <script> tags.

    Supports __NEXT_DATA__/application/json blocks and window/state variable
    assignments inside JavaScript.

    Returns:
        list: Parsed JSON objects found in the scripts.
    """
    blocks, decoder = [], json.JSONDecoder(strict=False)
    for script in doc.xpath("//script[not(@src)]"):
        text, kind = script.text or "", (script.get("type") or "").lower()
        if "ld+json" in kind or len(text) < 40 or len(text) > 25_000_000:
            continue
        if "json" in kind:
            blocks.extend(load_json(text))
        elif not kind or "javascript" in kind or kind == "module":
            tries = 0
            for match in re_c.ASSIGN_RE.finditer(text):
                start = match.start()
                if start == 0 or text[start - 1] in "=!<>+-*/%&|^?:":  # '==', '<=', '+=' are not assignments
                    continue
                name = re_c.VARIABLE_BEFORE_RE.search(text, max(0, start - 80), start)
                if not name or not re_c.STATE_NAME_RE.search(name.group(1)):
                    continue
                tries += 1
                try:
                    blocks.append(decoder.raw_decode(text, match.end() - 1)[0])
                except ValueError:
                    pass
                if tries >= 40:
                    break
    return blocks
