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

Detects the user's location (city level) via IP geolocation.

Uses ipapi.co IP geolocation, extended to city
level: LinkedIn searches work best with a concrete city. The result is cached
so repeated searches only make one request.

"""

import threading

from curl_cffi import requests

_cache = None
_lock = threading.Lock()


def detect_user_location():
    """Returns {"city", "region", "country", "country_code"} or None.

    Uses ipapi.co (no key required); the city falls back to the region when
    the provider cannot resolve a city.
    """
    global _cache

    with _lock:
        if _cache is not None:
            return dict(_cache)

        try:
            response = requests.get("https://ipapi.co/json/", impersonate="chrome", timeout=10)
            if response.status_code == 200:
                data = response.json()
                _cache = {
                    "city": data.get("city") or data.get("region"),
                    "region": data.get("region"),
                    "country": data.get("country_name"),
                    "country_code": (data.get("country_code") or "").upper(),
                }
                return dict(_cache)
        except Exception:
            pass

        return None


def resolve_search_location(workplace, explicit_location):
    """Decides the LinkedIn search location for a search space.

    - explicit location wins when the user typed one;
    - "Remote" searches run Worldwide;
    - otherwise the user's city is auto-detected (Worldwide on failure).
    """
    if explicit_location:
        return explicit_location.strip()

    workplace_lower = {str(value).strip().lower() for value in (workplace or [])}
    if "remote" in workplace_lower:
        return None  # None = Worldwide in the scraper

    detected = detect_user_location()
    return detected["city"] if detected else None
