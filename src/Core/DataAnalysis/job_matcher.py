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
"""

from typing import Any


WEIGHTS = {
    "experience": 0.30,
    "skills": 0.28,
    "education": 0.18,
    "certificates": 0.08,
    "languages": 0.08,
}


def score_experience(user_years: float | None, required_years: float | None) -> float | None:
    """Score experience years from 0.0 to 1.0; None means insufficient data."""
    if required_years is None:
        return None
    if required_years < 0:
        raise ValueError("Required experience cannot be negative.")
    if user_years is not None and user_years < 0:
        raise ValueError("User experience cannot be negative.")
    if required_years == 0:
        return 1.0
    if user_years is None:
        return None

    ratio = user_years / required_years
    if ratio >= 1.0:
        return 1.0
    if ratio < 0.5:
        return 0.1 + (ratio / 0.5) * 0.2
    if ratio < 0.75:
        return 0.3 + ((ratio - 0.5) / 0.25) * 0.4
    return 0.7 + ((ratio - 0.75) / 0.25) * 0.3


def _score_named_requirements(
    user_items: list[str] | None,
    required_items: list[str] | None,
    related_items: dict[str, list[str]] | None = None,
) -> float | None:
    """Shared exact/related matching logic for skills and certificates."""
    if user_items is None or required_items is None:
        return None

    required = list(dict.fromkeys(
        item.strip().casefold()
        for item in required_items
        if isinstance(item, str) and item.strip()
    ))
    if not required:
        return None

    owned = {
        item.strip().casefold()
        for item in user_items
        if isinstance(item, str) and item.strip()
    }
    related = {
        key.strip().casefold(): {
            value.strip().casefold()
            for value in values
            if isinstance(value, str) and value.strip()
        }
        for key, values in (related_items or {}).items()
        if isinstance(key, str) and isinstance(values, list)
    }

    total = 0.0
    for requirement in required:
        if requirement in owned:
            total += 1.0
        elif owned.intersection(related.get(requirement, set())):
            total += 0.5
    return total / len(required)


def score_skills(
    user_skills: list[str] | None,
    required_skills: list[str] | None,
    related_skills: dict[str, list[str]] | None = None,
) -> float | None:
    """Score exact and explicitly related skills."""
    return _score_named_requirements(user_skills, required_skills, related_skills)


def score_education(
    user_education_level: str | None,
    user_education_field: str | None,
    required_education_level: str | None,
    required_education_field: str | None,
) -> float | None:
    """Score education level and field using the current prototype rules."""
    levels = {
        "high school": 1,
        "associate": 2,
        "bachelor": 3,
        "master": 4,
        "phd": 5,
    }
    if user_education_level is None or required_education_level is None:
        return None
    user_level = user_education_level.strip().casefold()
    required_level = required_education_level.strip().casefold()
    if user_level not in levels:
        raise ValueError(f"Unknown education level: {user_education_level}")
    if required_level not in levels:
        raise ValueError(f"Unknown education level: {required_education_level}")

    difference = levels[required_level] - levels[user_level]
    level_score = 1.0 if difference <= 0 else 0.5 if difference == 1 else 0.0
    if not user_education_field or not required_education_field:
        return level_score
    field_score = (
        1.0 if user_education_field.strip().casefold() == required_education_field.strip().casefold()
        else 0.5
    )
    return (level_score + field_score) / 2


def score_certificates(
    user_certificates: list[str] | None,
    required_certificates: list[str] | None,
    related_certificates: dict[str, list[str]] | None = None,
) -> float | None:
    """Score exact and explicitly related certificates."""
    return _score_named_requirements(user_certificates, required_certificates, related_certificates)


def score_languages(
    user_languages: list[tuple[str, str]] | None,
    required_languages: list[tuple[str, str | None]] | None,
) -> float | None:
    """Score language proficiency, including languages not listed by the user."""
    if user_languages is None or required_languages is None:
        return None
    levels = {"basic": 1, "conversational": 2, "fluent": 3, "native": 4}
    users = {
        language.strip().casefold(): level.strip().casefold()
        for language, level in user_languages
        if isinstance(language, str) and language.strip()
        and isinstance(level, str) and level.strip()
    }
    requirements = [
        (language.strip().casefold(), level)
        for language, level in required_languages
        if isinstance(language, str) and language.strip()
    ]
    if not requirements:
        return None

    total = 0.0
    for language, required_level in requirements:
        if required_level is not None:
            if not isinstance(required_level, str) or required_level.strip().casefold() not in levels:
                raise ValueError(f"Unknown required language level: {required_level}")
        if language not in users:
            continue
        user_level = users[language]
        if user_level not in levels:
            raise ValueError(f"Unknown user language level: {user_level}")
        if required_level is None:
            total += 1.0
        else:
            difference = levels[required_level.strip().casefold()] - levels[user_level]
            total += 1.0 if difference <= 0 else 0.5 if difference == 1 else 0.0
    return total / len(requirements)


def match_job(
    user_experience: float | None,
    required_experience: float | None,
    user_skills: list[str] | None,
    required_skills: list[str] | None,
    user_education_level: str | None,
    user_education_field: str | None,
    required_education_level: str | None,
    required_education_field: str | None,
    user_certificates: list[str] | None,
    required_certificates: list[str] | None,
    user_languages: list[tuple[str, str]] | None,
    required_languages: list[tuple[str, str | None]] | None,
    related_skills: dict[str, list[str]] | None = None,
    related_certificates: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Return a job-fit percentage and per-criterion breakdown, not hiring probability."""
    scores = {
        "experience": score_experience(user_experience, required_experience),
        "skills": score_skills(user_skills, required_skills, related_skills),
        "education": score_education(
            user_education_level, user_education_field,
            required_education_level, required_education_field,
        ),
        "certificates": score_certificates(
            user_certificates, required_certificates, related_certificates,
        ),
        "languages": score_languages(user_languages, required_languages),
    }
    active = {name: score for name, score in scores.items() if score is not None}
    total_weight = sum(WEIGHTS[name] for name in active)
    percentage = (
        round(100 * sum(score * WEIGHTS[name] for name, score in active.items()) / total_weight, 2)
        if total_weight else None
    )
    return {
        "match_percentage": percentage,
        "breakdown": {
            name: round(score * 100, 2) if score is not None else None
            for name, score in scores.items()
        },
    }

