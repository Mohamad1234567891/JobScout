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

Scrollable containers for cards (results grid) and sidebar items.
"""

from PySide6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout, QHBoxLayout,
    QFrame, QVBoxLayout
)
from PySide6.QtCore import Qt


class ScrollContainer(QScrollArea):
    """Scrollable results area that arranges cards in a responsive centered
    grid and cleans up its widgets when cleared."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.card_width = 280
        self.spacing = 20
        self.items = []

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        # Outer wrapper that expands to the full viewport width
        self.outer_widget = QWidget()
        self.outer_widget.setStyleSheet("background: transparent;")

        # Horizontal layout with flanking spacers to keep cards centered
        self.outer_layout = QHBoxLayout(self.outer_widget)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)

        # Inner container that strictly wraps the grid of cards
        self.cards_holder = QWidget()
        self.cards_holder.setStyleSheet("background: transparent;")

        self.grid_layout = QGridLayout(self.cards_holder)
        self.grid_layout.setSpacing(self.spacing)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Stretch spacers on both sides balance the remaining whitespace
        self.outer_layout.addStretch(1)
        self.outer_layout.addWidget(self.cards_holder)
        self.outer_layout.addStretch(1)

        self.setWidget(self.outer_widget)

    def add_item(self, widget):
        self.items.append(widget)
        self._rebuild_grid()

    def rebuild(self):
        """Re-lays-out the cards (call after re-sorting self.items)."""
        self._rebuild_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rebuild_grid()

    def _rebuild_grid(self):
        if not self.items:
            return

        # Available width inside the scroll area
        viewport_w = self.viewport().width() - 30
        if viewport_w <= 0:
            return

        slot_width = self.card_width + self.spacing
        columns = max(1, (viewport_w + self.spacing) // slot_width)

        while self.grid_layout.count() > 0:
            self.grid_layout.takeAt(0)

        for index, widget in enumerate(self.items):
            row = index // columns
            col = index % columns
            self.grid_layout.addWidget(widget, row, col)

    def clear(self):
        """Removes and destroys every card widget."""
        while self.grid_layout.count() > 0:
            self.grid_layout.takeAt(0)

        for widget in self.items:
            # Cards may optionally clean up pending downloads before dying.
            cancel = getattr(widget, "cancel_image", None)
            if callable(cancel):
                cancel()
            widget.hide()
            widget.deleteLater()
        self.items.clear()

        self.verticalScrollBar().setValue(0)


class SidebarScrollContainer(QScrollArea):
    """Scrollable vertical list used by the sidebar for its action items."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self.container)

    def add_item(self, item):
        self.layout.addWidget(item)
