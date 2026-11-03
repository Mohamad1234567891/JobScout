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

Sidebar action item: a clickable row with an options button.

Used for every search space added to the sidebar. Emits clicked when the
title is pressed and options_clicked when the three-dot button is pressed
(the window opens a small context menu there).

"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QToolButton, QLabel
from PySide6.QtCore import Qt, Signal


class ActionItem(QWidget):
    clicked = Signal()
    options_clicked = Signal()

    def __init__(self, title, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # Title button
        self.title_button = QPushButton(title)
        self.title_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_button.setObjectName("actionTitleButton")
        self.title_button.clicked.connect(self.clicked.emit)

        # Badge with the number of new jobs found by the background search
        self.badge = QLabel("")
        self.badge.setObjectName("actionBadge")
        self.badge.hide()

        # Three-dot options button
        self.options_button = QToolButton()
        self.options_button.setText("⋯")
        self.options_button.setFixedSize(28, 28)
        self.options_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.options_button.setObjectName("optionsButton")
        self.options_button.clicked.connect(self.options_clicked.emit)

        layout.addWidget(self.title_button, 1)
        layout.addWidget(self.badge)
        layout.addWidget(self.options_button)

        self.setStyleSheet("""
            QPushButton#actionTitleButton {
                background-color: transparent;
                color: #d1d5db;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 8px;
                font-size: 13px;
            }

            QPushButton#actionTitleButton:hover {
                background-color: #29303a;
                color: white;
            }

            QPushButton#actionTitleButton[active="true"] {
                background-color: #1e3a8a;
                color: #93c5fd;
            }

            QLabel#actionBadge {
                background-color: #3b82f6;
                color: white;
                border-radius: 9px;
                padding: 0px 7px;
                font-size: 11px;
                font-weight: bold;
            }

            QToolButton#optionsButton {
                background-color: transparent;
                color: #9ca3af;
                border: none;
                border-radius: 6px;
                font-size: 20px;
            }

            QToolButton#optionsButton:hover {
                background-color: #29303a;
                color: white;
            }
        """)

    def set_badge_count(self, count):
        """Shows (or hides) the new-jobs badge with the given count."""
        if count > 0:
            self.badge.setText(str(count))
            self.badge.show()
        else:
            self.badge.setText("")
            self.badge.hide()

    def set_active(self, active):
        """Highlights the item when its search is the one being shown."""
        self.title_button.setProperty("active", active)
        self.title_button.style().unpolish(self.title_button)
        self.title_button.style().polish(self.title_button)

    def set_title(self, title):
        self.title_button.setText(title)
