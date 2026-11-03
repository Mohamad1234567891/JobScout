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

Parses job description text into structured requirement fields.

Extracts what the employer asks for: years of experience, education degrees,
certificates, and (as a bonus for later scoring) mentioned skills. Each
extractor returns lists of human-readable strings found in the text.

"""

import re

from src.Constants import constants
from src.Constants import job_vocabulary
from src.Constants import regex_constants as re_c
from src.Operations import string_operations as so


def _clean_lines(text):
    """Splits a description into cleaned, non-empty lines."""
    if not text:
        return []
    return [line for line in (so.clean(line) for line in re.split(r"[\n•·]+", text)) if line]


def extract_experience_requirements(text):
    """Finds every experience statement in the text.

    Detects "X+ years", "X-Y years", "at least X years", month-based
    experience, and explicit "no experience required" statements.

    Args:
        text (str): The job description text.

    Returns:
        list[str]: The experience requirement sentences/mentions found.
    """
    lines = _clean_lines(text)
    found, seen = [], set()

    for line in lines:
        # Skip lines where a year count is unlikely to be an employer ask
        # (e.g. "the company was founded 3 years ago").
        if not re.search(r"(?i)experience|years?|yrs?", line):
            continue

        hits = []
        for match in re_c.YEARS_EXPERIENCE_RE.finditer(line):
            hit = match.group(0).strip()
            # A bare "3+ years" only counts when the surrounding text talks
            # about experience (within ~40 characters of the match), or when
            # it reads as "X years <doing something>" ("5+ years building and
            # deploying machine learning systems").
            if "experience" not in hit.lower():
                window = line[max(0, match.start() - 40):match.end() + 60]
                if "experience" not in window.lower() and \
                        not re.search(r"years?\s+(?:of\s+)?[a-z]+ing\b", window, re.I):
                    continue
            hits.append(hit)
        for match in re_c.EXPERIENCE_LEAD_RE.finditer(line):
            hits.append(match.group(0).strip())
        for match in re_c.MONTHS_EXPERIENCE_RE.finditer(line):
            hits.append(match.group(0).strip())
        if re_c.NO_EXPERIENCE_RE.search(line):
            hits.append(re_c.NO_EXPERIENCE_RE.search(line).group(0).strip())

        for hit in hits:
            hit = so.clean(hit)
            key = hit.lower()
            if hit and key not in seen and 3 <= len(hit) <= 160:
                seen.add(key)
                found.append(hit)

    return found


def extract_education_requirements(text):
    """Finds every education/degree mention in the text.

    Args:
        text (str): The job description text.

    Returns:
        list[str]: The education requirement mentions found.
    """
    lines = _clean_lines(text)
    found, seen = [], set()

    for line in lines:
        for match in re_c.EDUCATION_RE.finditer(line):
            hit = so.clean(match.group(0))
            key = hit.lower()
            # "degree in Computer Science, Applied Computing, ..." can be a
            # long field list - allow generous hits, only strip trailing noise.
            if hit and key not in seen and 2 <= len(hit) <= 160:
                seen.add(key)
                found.append(hit)

    return found


def extract_certificates(text):
    """Finds every certificate/certification mention in the text.

    Args:
        text (str): The job description text.

    Returns:
        list[str]: The certificate mentions found.
    """
    lines = _clean_lines(text)
    found, seen = [], set()

    for line in lines:
        # Named certificates first (AWS Certified, PMP, CISSP...).
        for match in re_c.CERTIFICATE_RE.finditer(line):
            hit = so.clean(match.group(0))
            key = hit.lower()
            if hit and key not in seen and len(hit) <= 80:
                seen.add(key)
                found.append(hit)

        # Generic "certification in X" mentions, if no named cert was matched
        # on this line (avoids double-reporting the same sentence twice).
        if not re_c.CERTIFICATE_RE.search(line):
            for match in re_c.GENERIC_CERTIFICATE_RE.finditer(line):
                hit = so.clean(match.group(0))
                key = hit.lower()
                if hit and key not in seen and 4 <= len(hit) <= 100 and \
                        not re.search(r"\b(certify|certifies)\b", hit, re.I):
                    seen.add(key)
                    found.append(hit)

    return found


def extract_skills(text):
    """Finds known skill keywords mentioned in the text.

    Args:
        text (str): The job description text.

    Returns:
        list[str]: The skill keywords found, lowercased and deduplicated.
    """
    lowered = text.lower()
    return sorted({skill for skill in constants.SKILL_WORDS
                   if re.search(rf"\b{re.escape(skill)}\b", lowered)})


def extract_requirement_sections(description):
    """Splits a description into the employer-requirements part and the rest.

    LinkedIn descriptions interleave "Qualifications", "Nice to have",
    "About us" and "Benefits" sections. This returns the lines belonging to
    requirement sections, which the field extractors then use as their most
    reliable input.

    Args:
        description (str): The full job description text.

    Returns:
        list[str]: Requirement-section lines (cleaned).
    """
    lines = _clean_lines(description)
    in_requirements = False
    requirement_lines = []

    for line in lines:
        lowered = line.strip().lower()
        words = set(so.split_name(line))

        if any(phrase in lowered for phrase in constants.REQUIREMENT_SECTION_WORDS):
            in_requirements = True
            requirement_lines.append(line)
            continue

        if in_requirements and any(phrase in lowered for phrase in constants.BOILERPLATE_SECTION_WORDS):
            in_requirements = False
            continue

        if in_requirements:
            requirement_lines.append(line)

    return requirement_lines or lines  # fall back to the whole description when no sections are found


# ---------------------------------------------------------------------------
# Language requirements
# ---------------------------------------------------------------------------

_LANG_PATTERN = re.compile(
    r"\b(?P<level>fluent(?:ly)?|fluency|proficient|proficiency|native|bilingual|"
    r"business[- ]level|conversational|basic|intermediate|advanced|working\s+proficiency)\s+"
    r"(?:in|with|speaker\s+of|level\s+of|of)?\s*(?P<lang>" +
    "|".join(sorted(job_vocabulary.LANGUAGES, key=len, reverse=True)) +
    r")\b", re.I)

_LANG_TAIL_PATTERN = re.compile(
    r"\b(?P<lang>" + "|".join(sorted(job_vocabulary.LANGUAGES, key=len, reverse=True)) +
    r")\s+(?:proficiency|fluency|language\s+skills|speaking\s+skills|speaker|native|skills)\b",
    re.I)

_LEVEL_NORMALIZATION = {
    "fluent": "fluent", "fluently": "fluent", "fluency": "fluent", "proficient": "fluent",
    "proficiency": "fluent", "business level": "fluent", "business-level": "fluent",
    "intermediate": "fluent", "advanced": "fluent", "working proficiency": "conversational",
    "conversational": "conversational", "basic": "basic", "native": "native",
    "bilingual": "native",
}


def extract_languages(text):
    """Finds language requirements in the description text.

    Detects phrasings like "fluent in English", "English proficiency",
    "native German speaker" and "business level French".

    Args:
        text (str): The job description text.

    Returns:
        list[dict]: One entry per language with keys language, level and
        is_preferred (always False here; preference tagging happens upstream).
    """
    if not text:
        return []

    found, seen = [], set()

    for match in _LANG_PATTERN.finditer(text):
        language = match.group("lang").lower()
        level = _LEVEL_NORMALIZATION.get(match.group("level").lower(), None)
        if language not in seen:
            seen.add(language)
            found.append({"language": language, "level": level})

    for match in _LANG_TAIL_PATTERN.finditer(text):
        language = match.group("lang").lower()
        if language not in seen:
            seen.add(language)
            found.append({"language": language, "level": None})

    # Lines that clearly talk about languages usually list several of them
    # ("Fluency in English and German"): sweep such lines for every language
    # name so none is missed.
    if found:
        for line in _clean_lines(text):
            if not re.search(r"\b(fluent|fluency|proficient|proficiency|speak|spoken|"
                             r"native|language|bilingual)\b", line, re.I):
                continue
            for language in job_vocabulary.LANGUAGES:
                if language in seen:
                    continue
                if re.search(r"(?<![a-z])" + re.escape(language) + r"(?![a-z])", line.lower()):
                    seen.add(language)
                    found.append({"language": language, "level": None})

    return found
