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

The left sidebar: app header, the '+' button that opens the search panel,
and the scrollable list of search spaces (one item per job search).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt

from src.GUI.Components.Action_item import ActionItem
from src.GUI.Components.Scroll import SidebarScrollContainer


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(220)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("JobScout")
        title.setObjectName("sidebarTitle")

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(32, 32)
        self.plus_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plus_button.setObjectName("plusButton")
        self.plus_button.setToolTip("Add a job search")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.plus_button)

        layout.addLayout(header_layout)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("sidebarDivider")
        layout.addWidget(divider)

        # Scrollable area for the search-space items
        self.action_scroll = SidebarScrollContainer()
        layout.addWidget(self.action_scroll)

        self._items = []  # (item, layout index bookkeeping is not needed)

        # Styling
        self.setStyleSheet("""
            QWidget#sidebar {
                background-color: #17191f;
                border-right: 1px solid #30343d;
            }

            QLabel#sidebarTitle {
                color: white;
                font-size: 22px;
                font-weight: bold;
                padding: 8px 4px;
            }

            QFrame#sidebarDivider {
                color: #30343d;
                margin-bottom: 12px;
            }

            QPushButton#plusButton {
                background-color: #29364a;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 22px;
                font-weight: bold;
            }

            QPushButton#plusButton:hover {
                background-color: #3b5272;
            }
        """)

    def add_item(self, title):
        """Adds a search-space item and returns it."""
        item = ActionItem(title)
        self.action_scroll.add_item(item)
        self._items.append(item)
        return item

    def remove_item(self, item):
        """Removes a search-space item from the sidebar."""
        if item in self._items:
            self._items.remove(item)
        self.action_scroll.layout.removeWidget(item)
        item.hide()
        item.deleteLater()

    def items(self):
        return list(self._items)
