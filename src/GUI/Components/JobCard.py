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

Job result card shown next to the sidebar.

Displays the important fields of one found job (title, company, location,
posted date, match percentage and a requirement snippet) plus a button that
opens the full posting in the default browser.

"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from src.GUI.Components.Button import Button


def _match_color(percentage):
    if percentage is None:
        return "#6b7280"
    if percentage >= 70:
        return "#22c55e"
    if percentage >= 45:
        return "#eab308"
    return "#ef4444"


class JobCard(QFrame):
    """One extracted job with its match percentage and a View Job button."""

    def __init__(self, job, parent=None):
        super().__init__(parent)
        self.job = job

        self.setFixedWidth(280)
        self.setObjectName("jobCard")
        self.setStyleSheet("""
            #jobCard {
                background-color: #313135;
                border: 1px solid #3f3f46;
                border-radius: 10px;
            }
            #jobCard:hover {
                border: 1px solid #52525b;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        # Top row: title + match badge (or NEW badge)
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        title = QLabel(job.get("job_title") or "N/A")
        title.setWordWrap(True)
        title.setStyleSheet(
            "font-weight: bold; color: #f4f4f5; font-size: 14px; border: none; background: transparent;")
        top_row.addWidget(title, 1)

        badge_text = "NEW" if job.get("is_new") else self._match_text()
        badge = QLabel(badge_text)
        badge_color = "#3b82f6" if job.get("is_new") else _match_color(job.get("match_percentage"))
        badge.setStyleSheet(f"""
            background-color: {badge_color};
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            border: none;
        """)
        top_row.addWidget(badge)
        layout.addLayout(top_row)

        # Company • location
        company = job.get("company_name") or ""
        location = job.get("location") or ""
        sub = " • ".join(part for part in (company, location) if part) or "N/A"
        sub_label = QLabel(sub)
        sub_label.setWordWrap(True)
        sub_label.setStyleSheet("color: #a1a1aa; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(sub_label)

        # Posted date
        posted = job.get("posted_date") or job.get("posted_time_ago") or ""
        if posted:
            posted_label = QLabel(f"Posted: {posted}")
            posted_label.setStyleSheet("color: #71717a; font-size: 11px; border: none; background: transparent;")
            layout.addWidget(posted_label)

        # Requirement snippet (first experience/education line, trimmed)
        snippet = self._snippet()
        if snippet:
            snippet_label = QLabel(snippet)
            snippet_label.setWordWrap(True)
            snippet_label.setStyleSheet("color: #d4d4d8; font-size: 11px; border: none; background: transparent;")
            layout.addWidget(snippet_label)

        # Footer: View Job button
        footer = QHBoxLayout()
        footer.addStretch()
        view_button = Button("View Job", job.get("job_url") or "")
        footer.addWidget(view_button)
        layout.addLayout(footer)

    def _match_text(self):
        percentage = self.job.get("match_percentage")
        if percentage is None:
            return "—"
        return f"{percentage:.0f}%"

    def _snippet(self):
        """Builds a one-line summary of what the employer requires."""
        parts = []
        experience = self.job.get("experience_requirements") or []
        if experience:
            parts.append(f"Requires: {experience[0]}")
        education = self.job.get("education_requirements") or []
        if education:
            parts.append(education[0])
        text = " | ".join(parts)
        return (text[:110] + "…") if len(text) > 110 else text
