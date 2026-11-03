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

Adapts a user's search space and an extracted job to the matcher.

The extraction layer returns human-readable requirement strings
("6+ years of professional software development experience",
"Bachelor's degree in Computer Science") while the matcher expects clean
values (years as float, education level/field as strings). This module
bridges the two and applies the related-item maps so partial credit works
out of the box.

"""

import re

from src.Constants import job_vocabulary as vocab
from src.Constants import regex_constants as re_c
from src.Core.DataAnalysis import job_matcher

# Matcher education levels (the canonical keys used by job_matcher).
_MATCHER_LEVELS = {"high school", "associate", "bachelor", "master", "phd"}

# Extraction level keys -> matcher keys.
_LEVEL_ALIASES = {
    "high_school": "high school",
    "high-school": "high school",
    "undergraduate": "bachelor",
    "undergrad": "bachelor",
    "graduate": "master",
    "postgraduate": "master",
    "post-graduate": "master",
    "doctorate": "phd",
    "doctoral": "phd",
}

# Language level keys -> matcher keys.
_LANGUAGE_LEVELS = {"basic": "basic", "conversational": "conversational",
                    "fluent": "fluent", "native": "native"}

_RANK = {"high school": 0, "associate": 1, "bachelor": 2, "master": 3, "phd": 4}


def _required_years(statements):
    """Returns the highest minimum years of experience among the statements."""
    best = None
    for statement in statements or []:
        for match in re_c.YEARS_EXPERIENCE_RE.finditer(statement):
            numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", match.group("years"))]
            if not numbers:
                continue
            required = numbers[0]  # "2-5 years" requires at least 2; "6+ years" requires 6
            best = required if best is None else max(best, required)
        for match in re_c.EXPERIENCE_LEAD_RE.finditer(statement):
            numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", match.group("years"))]
            if numbers:
                best = numbers[0] if best is None else max(best, numbers[0])
        for match in re_c.MONTHS_EXPERIENCE_RE.finditer(statement):
            months = float(match.group("months") or match.group("months2"))
            years = round(months / 12, 2)
            best = years if best is None else max(best, years)
        if re_c.NO_EXPERIENCE_RE.search(statement) and best is None:
            best = 0.0
    return best


def _education_level_of(statements):
    """Detects the highest education level the employer asks for."""
    level = None
    for statement in statements or []:
        lowered = statement.lower()
        for token, bucket in vocab.DEGREE_LEVELS.items():
            if bucket not in _MATCHER_LEVELS and bucket not in _LEVEL_ALIASES:
                continue
            if token in ("bs", "ms", "as", "ma", "ba"):
                if not re.search(r"(?<![a-z])" + re.escape(token.upper()) + r"(?![a-z])", statement):
                    continue
            elif not re.search(r"(?<![a-z0-9])" + re.escape(token) + r"(?![a-z0-9])", lowered):
                continue
            normalized = _LEVEL_ALIASES.get(bucket, bucket)
            if normalized not in _MATCHER_LEVELS:
                continue
            if level is None or _RANK[normalized] > _RANK[level]:
                level = normalized
    return level


def _education_field_of(statements):
    """Detects the field of study the employer asks for."""
    for statement in statements or []:
        match = re.search(r"\bdegree\s+(?:in|of)\s+([A-Za-z][A-Za-z0-9 ,&/'-]{1,60}?)(?=\s*(?:,|\.|;|$|\bor\b))",
                          statement, re.I)
        if match:
            return match.group(1).strip()
        lowered = statement.lower()
        for field in sorted(vocab.FIELDS_OF_STUDY, key=len, reverse=True):
            if re.search(r"(?<![a-z])" + re.escape(field) + r"(?![a-z])", lowered):
                return field
    return None


def _language_tuples(entries):
    """Converts extraction language dicts to (language, level) tuples."""
    tuples = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        language = str(entry.get("language", "")).strip().casefold()
        if not language:
            continue
        level = _LANGUAGE_LEVELS.get(str(entry.get("level") or "").strip().casefold())
        tuples.append((language, level))
    return tuples


def match_search_space_job(search_space, job):
    """Scores one job against the user's search space.

    Args:
        search_space: A JobSearchSpace.
        job: The extracted job dict (from job_page.extract_job_page).

    Returns:
        dict: {"match_percentage": float | None, "breakdown": {...}}.
        The percentage is None when the user gave no profile data or the job
        has no requirements to compare against.
    """
    if search_space is None or not search_space.has_profile_data:
        return {"match_percentage": None, "breakdown": {}}

    required_experience = _required_years(job.get("experience_requirements"))
    required_level = _education_level_of(job.get("education_requirements"))
    required_field = _education_field_of(job.get("education_requirements"))

    result = job_matcher.match_job(
        user_experience=search_space.experience_years,
        required_experience=required_experience,
        user_skills=search_space.skills or None,
        required_skills=job.get("skills") or None,
        user_education_level=search_space.education_level,
        user_education_field=search_space.education_field,
        required_education_level=required_level,
        required_education_field=required_field,
        user_certificates=search_space.certificates or None,
        required_certificates=job.get("certificates") or None,
        user_languages=search_space.languages or None,
        required_languages=_language_tuples(job.get("languages")) or None,
        related_skills=vocab.RELATED_SKILLS,
        related_certificates=vocab.RELATED_CERTIFICATES,
    )
    return result
