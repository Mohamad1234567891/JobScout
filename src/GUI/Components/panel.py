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

The search panel: a dark translucent overlay that collects everything
about a job search (title, experience, education, skills, certificates,
languages, workplace, location, re-check interval) and emits
start_search_clicked when the user presses Start Search.

The panel is a dumb container - the window owns the input widgets, adds them
with add_field(...) and reads them back when the signal fires.

"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, Signal


class Panel(QFrame):
    """Responsive dark panel containing the search-space inputs."""

    closed = Signal()
    start_search_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._docked_bar = None
        self._saved_bar_state = None

        self.setObjectName("panel")
        self.setStyleSheet("""
            #panel {
                background-color: #2a2a2a;
                border: 1px solid #3f3f46;
                border-radius: 12px;
            }
            QLabel[fieldLabel="true"] {
                color: #a1a1aa;
                font-size: 12px;
                font-weight: 600;
                border: none;
                background: transparent;
            }
        """)

        self.setMinimumSize(480, 420)

        # Panel inner layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Top row: close button at the top right, above the search bar
        self.top_row_layout = QHBoxLayout()
        self.top_row_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a1a1aa;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.15);
                color: #ef4444;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        self.close_btn.clicked.connect(self.closed.emit)

        self.top_row_layout.addWidget(self.close_btn)
        self.main_layout.addLayout(self.top_row_layout)

        # Scrollable area for the input fields (search bar gets docked above it)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.fields_widget = QWidget()
        self.fields_widget.setStyleSheet("background: transparent;")
        self.fields_layout = QVBoxLayout(self.fields_widget)
        self.fields_layout.setContentsMargins(0, 8, 0, 8)
        self.fields_layout.setSpacing(10)

        self.scroll_area.setWidget(self.fields_widget)
        self.main_layout.addWidget(self.scroll_area, 1)

        # Footer row with the "Start Search" button at the bottom right
        self.footer_layout = QHBoxLayout()
        self.footer_layout.addStretch()

        self.start_search_btn = QPushButton("Start Search")
        self.start_search_btn.setFixedSize(130, 34)
        self.start_search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e3a8a;
                color: #ffffff;
                font-size: 13px;
                font-weight: 600;
                border-radius: 17px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.start_search_btn.clicked.connect(self.start_search_clicked.emit)

        self.footer_layout.addWidget(self.start_search_btn)
        self.main_layout.addLayout(self.footer_layout)

    # ------------------------------------------------------------- field API

    def add_field(self, label_text, widget):
        """Adds one labeled input row to the panel's scrollable area."""
        row = QHBoxLayout()
        row.setSpacing(10)
        if label_text:
            label = QLabel(label_text)
            label.setProperty("fieldLabel", True)
            label.setFixedWidth(110)
            row.addWidget(label)
        row.addWidget(widget, 1)
        self.fields_layout.addLayout(row)
        return widget

    def add_header_widget(self, widget):
        """Adds a widget without a label (kept for compatibility)."""
        return self.add_field(None, widget)

    def clear_fields(self):
        """Removes every field row (except the docked search bar)."""
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            while item.count():
                child = item.takeAt(0)
                widget = child.widget()
                if widget is not None:
                    widget.hide()
                    widget.deleteLater()
            del item

    # ---------------------------------------------------------- search bar

    def dock_search_bar(self, bar):
        """Moves the window's SearchBar into the panel and restyles it dark."""
        if self._docked_bar is bar:
            return

        self._saved_bar_state = {
            "bar_style": bar.styleSheet(),
            "input_style": bar.input_field.styleSheet(),
            "max_width": bar.maximumWidth(),
            "height": bar.minimumHeight(),
            "margins": bar.layout().contentsMargins(),
            "btn_visible": True,
        }

        bar.search_btn.hide()  # pressing Enter still submits

        bar.setFixedHeight(44)
        bar.setMaximumWidth(16777215)  # fill the panel width
        bar.layout().setContentsMargins(14, 4, 14, 4)
        bar.setStyleSheet("""
            SearchBar {
                background-color: #313135;
                border: 1px solid #3f3f46;
                border-radius: 8px;
            }
        """)
        bar.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #f4f4f5;
                selection-background-color: #1e3a8a;
            }
        """)

        self.main_layout.insertWidget(1, bar)
        bar.show()
        self._docked_bar = bar

    def undock_search_bar(self):
        """Takes the SearchBar out of the panel and restores its look."""
        bar = self._docked_bar
        if bar is None:
            return None

        state = self._saved_bar_state
        self.main_layout.removeWidget(bar)

        bar.setStyleSheet(state["bar_style"])
        bar.input_field.setStyleSheet(state["input_style"])
        bar.setFixedHeight(state["height"])
        bar.setMaximumWidth(state["max_width"])
        bar.layout().setContentsMargins(state["margins"])
        bar.search_btn.setVisible(state["btn_visible"])

        self._docked_bar = None
        self._saved_bar_state = None
        return bar

    def show_panel_action(self):
        """Shows the panel (used when the '+' button is clicked)."""
        self.show()
        self.raise_()
