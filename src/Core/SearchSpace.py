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

The user's job search space.

Everything the user tells JobScout about themselves and what they are
looking for, in one structured object. The GUI builds one from the panel
inputs, the scraper uses the job title/location, and the matcher compares
the profile fields against every extracted job's requirements.

"""

from dataclasses import dataclass, field, asdict


@dataclass
class JobSearchSpace:
    """One job search: the target role plus the user's profile."""

    job_title: str
    experience_years: float | None = None          # total professional years
    experience_domains: list = field(default_factory=list)  # e.g. ["machine learning"]
    education_level: str | None = None             # high school | associate | bachelor | master | phd
    education_field: str | None = None             # e.g. "Computer Science"
    skills: list = field(default_factory=list)
    certificates: list = field(default_factory=list)
    languages: list = field(default_factory=list)  # list of (language, level)
    workplace: list = field(default_factory=list)  # ["Remote", "Hybrid", "On-site"]
    location: str | None = None                    # search location ("Worldwide" when empty)
    check_interval_hours: float = 1.0              # background re-search frequency

    @property
    def key(self):
        """Stable identifier used by the GUI to map sidebar items to searches."""
        return self.job_title.strip().casefold()

    @property
    def label(self):
        """Short human-readable name shown in the sidebar."""
        return self.job_title.strip()

    @property
    def has_profile_data(self):
        """True when the user filled any profile field (enables matching)."""
        return bool(self.experience_years or self.experience_domains or self.education_level
                    or self.skills or self.certificates or self.languages)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        known = {name for name in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in (data or {}).items() if key in known})
