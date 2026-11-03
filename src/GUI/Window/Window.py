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

The main JobScout window.

Left: sidebar with one item per job search and the '+' button that opens the
search panel. Right: job result cards (sorted by acceptance estimate) with a
button that opens each posting in the browser.

Searches live in a shared state file used by the GUI, the CLI and the
detached daemon, so everything survives restarts and the background
re-checking continues after the window closes. A poller picks up the
daemon's updates while the window is open.

"""

import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QMenu
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor

from src.Constants import job_vocabulary as vocab
from src.Core import SharedState
from src.Core.SearchSpace import JobSearchSpace
from src.GUI.Components.Drop_down import CustomDropdown, SelectionDropdown
from src.GUI.Components.emoji_icon import emoji_icon
from src.GUI.Components.JobCard import JobCard
from src.GUI.Components.Loading import SmallLoader
from src.GUI.Components.panel import Panel
from src.GUI.Components.Scroll import ScrollContainer
from src.GUI.Components.SearchBar import SearchBar
from src.GUI.Components.Sidebar import Sidebar
from src.GUI.Core.SearchManager import SearchManager

DARK_BACKGROUND = "background-color: #1f1f1f;"
STORE_POLL_MS = 15_000


class JobScoutWindow(QMainWindow):
    """Main JobScout window - the search bar lives only inside the panel."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JobScout")
        self.setWindowIcon(emoji_icon("💼"))
        self.resize(1000, 700)
        self.setMinimumSize(800, 560)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar
        self.sidebar = Sidebar()
        self.sidebar.plus_button.clicked.connect(self.show_panel)
        main_layout.addWidget(self.sidebar)

        # Main content area
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(DARK_BACKGROUND)

        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setContentsMargins(20, 24, 20, 20)
        self.layout.setSpacing(14)

        # Header row: title, status message and the loading spinner
        header_layout = QHBoxLayout()
        self.results_title = QLabel("Job Results")
        self.results_title.setStyleSheet(
            "color: #f4f4f5; font-size: 18px; font-weight: bold; border: none; background: transparent;")
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #a1a1aa; font-size: 12px; border: none; background: transparent;")
        self.loader = SmallLoader()
        header_layout.addWidget(self.results_title)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        header_layout.addWidget(self.loader)
        self.layout.addLayout(header_layout)

        # Scrollable job cards
        self.results_scroll = ScrollContainer()
        self.layout.addWidget(self.results_scroll, 1)
        self.results_scroll.hide()

        # Empty state
        self.empty_label = QLabel("No job search yet.\nClick the + button to add one.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color: #71717a; font-size: 14px; border: none; background: transparent;")
        self.layout.addWidget(self.empty_label, 1)

        main_layout.addWidget(self.content_widget, 1)

        # The search panel (hidden by default - only the '+' button opens it)
        self.panel = Panel(self.content_widget)
        self.panel.hide()
        self.panel.start_search_clicked.connect(self.on_start_search)

        self._build_panel_inputs()

        # One manager + sidebar item per search space
        self.searches = {}   # key -> {"item", "manager", "jobs", "new_count"}
        self.active_key = None
        self._last_store_mtime = None

        # Load the searches recorded by the GUI/CLI in previous sessions
        self._load_stored_searches()

        # Poll the shared store so the daemon's updates appear while open
        self._store_poller = QTimer(self)
        self._store_poller.timeout.connect(self._poll_store)
        self._store_poller.start(STORE_POLL_MS)

    # ------------------------------------------------------------ panel setup

    def _build_panel_inputs(self):
        suggestions = [
            "AI Engineer", "Machine Learning Engineer", "Python Developer",
            "Backend Engineer", "Data Scientist", "Software Engineer",
        ]
        self.search_bar = SearchBar(suggestions=suggestions)
        self.search_bar.input_field.setPlaceholderText("Search for a job (e.g. AI Engineer)...")
        self.search_bar.search_submitted.connect(lambda _query: self.on_start_search())
        self.panel.dock_search_bar(self.search_bar)

        # Education level
        self.education_dropdown = CustomDropdown(placeholder="Education Level", items=vocab.EDUCATION_LEVELS)
        self.panel.add_field("Education", self.education_dropdown)

        # Experience: years + domain
        experience_widget = QWidget()
        experience_row = QHBoxLayout(experience_widget)
        experience_row.setContentsMargins(0, 0, 0, 0)
        experience_row.setSpacing(8)
        self.experience_years = QSpinBox()
        self.experience_years.setRange(0, 50)
        self.experience_years.setSpecialValueText("None")
        self.experience_years.setSuffix(" yrs")
        self.experience_years.setFixedWidth(90)
        self.experience_domain = QLineEdit()
        self.experience_domain.setPlaceholderText("domain (e.g. machine learning)")
        experience_row.addWidget(self.experience_years)
        experience_row.addWidget(self.experience_domain, 1)
        self.panel.add_field("Experience", experience_widget)

        # Skills (the full alphabetical vocabulary, searchable in the dropdown)
        skills_items = sorted({vocab.display_name(skill) for skill in vocab.SKILLS})
        self.skills_dropdown = SelectionDropdown(placeholder="Skills", items=skills_items)
        self.panel.add_field("Skills", self.skills_dropdown)

        # Certificates (the full alphabetical vocabulary, searchable)
        cert_items = sorted({vocab.display_name(cert)
                             for cert in vocab.CERTIFICATES | set(vocab.POPULAR_CERTIFICATES)})
        self.certificates_dropdown = SelectionDropdown(placeholder="Certificates", items=cert_items)
        self.panel.add_field("Certificates", self.certificates_dropdown)

        # Languages + level
        language_widget = QWidget()
        language_row = QHBoxLayout(language_widget)
        language_row.setContentsMargins(0, 0, 0, 0)
        language_row.setSpacing(8)
        language_items = sorted(vocab.display_name(language) for language in vocab.LANGUAGES)
        self.languages_dropdown = SelectionDropdown(placeholder="Languages", items=language_items)
        self.language_level = CustomDropdown(placeholder="Level", items=vocab.LANGUAGE_LEVELS)
        self.language_level.setFixedWidth(130)
        language_row.addWidget(self.languages_dropdown, 1)
        language_row.addWidget(self.language_level)
        self.panel.add_field("Languages", language_widget)

        # Location (auto-detected from the user's IP when the search is not remote)
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("auto-detected unless Remote is chosen")
        self.panel.add_field("Location", self.location_input)

        # Workplace preference
        self.workplace_dropdown = SelectionDropdown(placeholder="Workplace", items=vocab.WORKPLACE_OPTIONS)
        self.panel.add_field("Workplace", self.workplace_dropdown)

        # Background re-check interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 24)
        self.interval_spin.setValue(1)
        self.interval_spin.setSuffix(" hour(s)")
        self.interval_spin.setFixedWidth(110)
        self.panel.add_field("Re-check every", self.interval_spin)

    # ------------------------------------------------------------ panel logic

    def update_panel_geometry(self):
        """Dynamically resize and center the panel based on the content size."""
        if hasattr(self, 'panel') and self.panel.isVisible():
            target_width = max(480, min(int(self.content_widget.width() * 0.9), 1000))
            target_height = max(440, min(int(self.content_widget.height() * 0.92), 720))

            self.panel.resize(target_width, target_height)

            x = (self.content_widget.width() - self.panel.width()) // 2
            y = (self.content_widget.height() - self.panel.height()) // 2

            self.panel.move(x, y)

    def show_panel(self):
        """Shows the panel (used by the '+' button) with precise centering."""
        self.panel.show()
        self.panel.raise_()
        QTimer.singleShot(0, self.update_panel_geometry)

    def toggle_panel(self):
        if self.panel.isVisible():
            self.panel.hide()
        else:
            self.show_panel()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_panel_geometry()

    def closeEvent(self, event):
        """Waits (bounded) for running scrapes so no worker thread is killed
        while still running. The daemon keeps monitoring after we close."""
        for entry in self.searches.values():
            entry["manager"].shutdown()
        super().closeEvent(event)

    # ---------------------------------------------------------- search logic

    def _collect_search_space(self):
        """Builds a JobSearchSpace from the panel inputs (None on error)."""
        title = self.search_bar.text()
        if not title:
            self.status_label.setText("Enter a job title first.")
            return None

        level = self.language_level.current_value() or "Fluent"
        languages = [(language.lower(), level.lower())
                     for language in self.languages_dropdown.selected_items()]

        domains = [part.strip() for part in self.experience_domain.text().split(",") if part.strip()]

        return JobSearchSpace(
            job_title=title,
            experience_years=float(self.experience_years.value()) or None,
            experience_domains=domains,
            education_level=(self.education_dropdown.current_value() or "").lower() or None,
            skills=self.skills_dropdown.selected_items(),
            certificates=self.certificates_dropdown.selected_items(),
            languages=languages,
            workplace=self.workplace_dropdown.selected_items(),
            location=self.location_input.text().strip() or None,
            check_interval_hours=float(self.interval_spin.value() or 1),
        )

    def _reset_panel(self):
        """Clears every panel input so the next search starts fresh."""
        self.search_bar.input_field.clear()
        self.education_dropdown.setCurrentIndex(-1)
        self.experience_years.setValue(0)
        self.experience_domain.clear()
        self.skills_dropdown.clear_selection()
        self.certificates_dropdown.clear_selection()
        self.languages_dropdown.clear_selection()
        self.language_level.setCurrentIndex(-1)
        self.location_input.clear()
        self.workplace_dropdown.clear_selection()
        self.interval_spin.setValue(1)

    def on_start_search(self):
        """Runs when Start Search is pressed: records the search, resets the
        panel, selects the new sidebar item and starts scraping."""
        space = self._collect_search_space()
        if space is None:
            return

        key = space.key
        if key in self.searches:
            self.show_search(key)
            self.panel.hide()
            self._reset_panel()
            return

        item = self.sidebar.add_item(space.label)
        item.clicked.connect(lambda: self.show_search(key))
        item.options_clicked.connect(lambda: self._show_item_menu(key))

        manager = SearchManager(space, self)
        manager.job_found.connect(self.on_job_found)
        manager.search_finished.connect(self.on_search_finished)
        manager.status_changed.connect(self.on_status_changed)
        manager.set_interval_hours(space.check_interval_hours)

        self.searches[key] = {"item": item, "manager": manager, "jobs": [], "new_count": 0}

        # Switch to the new search right away: its card area stays empty
        # until the results arrive.
        self.active_key = key
        self._set_active_item(key)
        self.panel.hide()
        self._reset_panel()
        self._show_searching_state(space.label)
        manager.run_search()

    def on_job_found(self, space, job):
        """Adds a card the moment a job is extracted (results stream in)."""
        entry = self.searches.get(space.key)
        if entry:
            entry["jobs"].append(job)

        if self.active_key != space.key:
            return

        self.results_scroll.add_item(JobCard(job))
        self._sort_cards()
        self.empty_label.setText("")
        self._show_empty_state(False)
        label = self.searches.get(space.key, {}).get("item")
        title = label.title_button.text() if label else ""
        self.results_title.setText(f"Jobs for '{title}' ({len(self.results_scroll.items)})")

    def _sort_cards(self):
        """Keeps the cards ordered by the acceptance estimate."""
        self.results_scroll.items.sort(
            key=lambda card: (card.job.get("match_percentage") is None,
                              -(card.job.get("match_percentage") or 0.0)))
        self.results_scroll.rebuild()

    def on_search_finished(self, space, jobs):
        """Rebuilds the card area from the final, complete job list."""
        entry = self.searches.get(space.key)
        if entry:
            entry["jobs"] = jobs
        self.loader.stop()

        if self.active_key == space.key:
            self._populate_cards(jobs)

    def on_status_changed(self, space, message):
        if self.active_key == space.key:
            self.status_label.setText(message)
        if message.startswith("Searching"):
            self.loader.start()

    # ------------------------------------------------------------ display

    def _show_searching_state(self, title):
        """Clears the card area while a search runs."""
        self.results_scroll.clear()
        self.results_title.setText(f"Jobs for '{title}' (searching...)")
        self.empty_label.setText("Searching LinkedIn...")
        self._show_empty_state(True)
        self.loader.start()

    def _populate_cards(self, jobs):
        self.results_scroll.clear()
        for job in jobs:
            self.results_scroll.add_item(JobCard(job))

        label = self.searches.get(self.active_key, {}).get("item")
        title = label.title_button.text() if label else ""
        self.results_title.setText(f"Jobs for '{title}' ({len(jobs)})")

        if jobs:
            self._show_empty_state(False)
        else:
            self.empty_label.setText("No jobs found for this search yet.")
            self._show_empty_state(True)

    def _show_empty_state(self, empty):
        self.empty_label.setVisible(empty)
        self.results_scroll.setVisible(not empty)

    def _set_active_item(self, key):
        for search_key, entry in self.searches.items():
            entry["item"].set_active(search_key == key)
            if search_key == key:
                entry["new_count"] = 0
                entry["item"].set_badge_count(0)

    def show_search(self, key):
        """Switches the card area to the results of the given search."""
        entry = self.searches.get(key)
        if entry is None:
            return
        self.active_key = key
        self._set_active_item(key)
        self.status_label.setText(f"Showing results for '{entry['item'].title_button.text()}'.")
        self._populate_cards(entry["jobs"])

    def _show_item_menu(self, key):
        entry = self.searches.get(key)
        if entry is None:
            return
        manager = entry["manager"]

        menu = QMenu(self)
        if manager.is_monitoring():
            menu.addAction("Pause background search", lambda: manager.set_monitoring(False))
        else:
            menu.addAction("Resume background search", lambda: manager.set_monitoring(True))
        menu.addAction("Search now", manager.run_search)
        menu.addSeparator()
        menu.addAction("Remove", lambda: self._remove_search(key))
        menu.exec(QCursor.pos())

    def _remove_search(self, key):
        entry = self.searches.pop(key, None)
        if entry is None:
            return
        entry["manager"].shutdown()
        self.sidebar.remove_item(entry["item"])
        from src.Core import SharedState as _state
        _state.remove_search(key)

        if self.active_key == key:
            self.active_key = None
            self.results_scroll.clear()
            self.results_title.setText("Job Results")
            self.status_label.setText("")
            self.empty_label.setText("No job search yet.\nClick the + button to add one.")
            self._show_empty_state(True)

    # ----------------------------------------------------- shared store sync

    def _load_stored_searches(self):
        """Restores the searches recorded in previous GUI/CLI sessions."""
        stored = SharedState.load_searches()
        if not stored:
            return

        for key, saved in stored.items():
            try:
                space = JobSearchSpace.from_dict(saved.get("space"))
            except Exception:
                continue
            if not space.job_title or key in self.searches:
                continue

            item = self.sidebar.add_item(space.label)
            item.clicked.connect(lambda k=key: self.show_search(k))
            item.options_clicked.connect(lambda k=key: self._show_item_menu(k))

            manager = SearchManager(space, self)
            manager.job_found.connect(self.on_job_found)
            manager.search_finished.connect(self.on_search_finished)
            manager.status_changed.connect(self.on_status_changed)

            jobs = saved.get("results") or []
            new_count = len(saved.get("new") or [])
            self.searches[key] = {"item": item, "manager": manager,
                                  "jobs": jobs, "new_count": new_count}
            item.set_badge_count(new_count)

        self._last_store_mtime = SharedState.mtime()

    def _poll_store(self):
        """Reloads the active search when the daemon updated the shared file."""
        mtime = SharedState.mtime()
        if mtime is None or mtime == self._last_store_mtime:
            return
        self._last_store_mtime = mtime

        stored = SharedState.load_searches()
        for key, saved in stored.items():
            entry = self.searches.get(key)
            if entry is None:
                continue
            entry["jobs"] = saved.get("results") or []
            entry["new_count"] = len(saved.get("new") or [])
            entry["item"].set_badge_count(entry["new_count"])

        if self.active_key in self.searches:
            entry = self.searches[self.active_key]
            self._populate_cards(entry["jobs"])
            if entry["new_count"]:
                self.status_label.setText(
                    f"{entry['new_count']} new job(s) for '{entry['item'].title_button.text()}'.")


def start_gui():
    """Starts the JobScout GUI (call this from the CLI entry point)."""
    app = QApplication(sys.argv)
    window = JobScoutWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start_gui()
