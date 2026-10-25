"""
This file is part of ShopWise, an open-source multi-region, multi-store
price-comparison and product-search engine.

Copyright (c) 2026 Muhammed Bekiroğlu and the ShopWise contributors.

Original ShopWise repository: https://github.com/Mohamad1234567891/ShopWise

Muhammed Bekiroğlu (ShopWise team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
"""

from PySide6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt


class ScrollContainer(QScrollArea):
    """Scrollable results area that arranges product cards in a responsive centered grid and cleans up cards (and their pending image downloads) when cleared."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.card_width = 280
        self.spacing = 20
        self.items = []

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)

        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        # Outer wrapper that expands to the full viewport width
        self.outer_widget = QWidget()
        self.outer_widget.setStyleSheet("background: transparent;")

        # Horizontal layout with flanking spacers to ensure cards stay centered
        self.outer_layout = QHBoxLayout(self.outer_widget)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)

        # Inner container that strictly wraps the grid of cards
        self.cards_holder = QWidget()
        self.cards_holder.setStyleSheet("background: transparent;")

        self.grid_layout = QGridLayout(self.cards_holder)
        self.grid_layout.setSpacing(self.spacing)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setAlignment(Qt.AlignTop)

        # Place stretch spacers on both sides to balance remaining whitespace
        self.outer_layout.addStretch(1)
        self.outer_layout.addWidget(self.cards_holder)
        self.outer_layout.addStretch(1)

        self.setWidget(self.outer_widget)

    def add_item(self, widget):
        self.items.append(widget)
        self._rebuild_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rebuild_grid()

    def _rebuild_grid(self):
        if not self.items:
            return

        # Calculate actual available width inside the scroll area
        viewport_w = self.viewport().width() - 30
        if viewport_w <= 0:
            return

        slot_width = self.card_width + self.spacing
        columns = max(1, (viewport_w + self.spacing) // slot_width)

        # Clear existing items from the layout
        while self.grid_layout.count() > 0:
            self.grid_layout.takeAt(0)

        # Re-populate the cards across calculated rows and columns
        for index, widget in enumerate(self.items):
            row = index // columns
            col = index % columns
            self.grid_layout.addWidget(widget, row, col)

    def clear(self):
        while self.grid_layout.count() > 0:
            self.grid_layout.takeAt(0)

        for widget in self.items:
            widget.cancel_image()
            widget.hide()
            widget.deleteLater()
        self.items.clear()

        self.verticalScrollBar().setValue(0)