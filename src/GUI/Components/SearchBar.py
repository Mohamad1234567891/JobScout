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
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QCompleter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor


class SearchBar(QWidget):
    """Search input with an autocomplete completer and a search button; emits text_changed while typing and search_submitted on Enter or click."""
    text_changed = Signal(str)
    search_submitted = Signal(str)

    def __init__(self, suggestions=None, parent=None):
        super().__init__(parent)

        self.setFixedHeight(50)
        self.setMinimumWidth(240)    # Shrinks smoothly on small screens
        self.setMaximumWidth(1100) # Removes the upper limit completely

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
            SearchBar {
                background-color: #ffffff;
                border: 1px solid #dcdfe4;
                border-radius: 25px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 6, 4)
        layout.setSpacing(10)

        # Search icon
        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("font-size: 14px; border: none; background: transparent;")
        layout.addWidget(icon_label)

        # Text input
        self.input_field = QLineEdit()
        self.input_field.setMinimumWidth(80)
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.input_field.setPlaceholderText("Search for a product (e.g. Samsung Galaxy S25)...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #0f172a;
            }
        """)
        layout.addWidget(self.input_field)

        if suggestions:
            self.set_suggestions(suggestions)

        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setFixedSize(90, 38)
        self.search_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e3a5f;
                color: #ffffff;
                font-size: 13px;
                font-weight: 600;
                border-radius: 19px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2b4f7a;
            }
            QPushButton:pressed {
                background-color: #152942;
            }
        """)
        layout.addWidget(self.search_btn)

        self.input_field.textChanged.connect(self._on_text_changed)
        self.input_field.returnPressed.connect(self._on_submit)
        self.search_btn.clicked.connect(self._on_submit)

    def set_suggestions(self, words: list):
        completer = QCompleter(words, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.input_field.setCompleter(completer)

    def _on_text_changed(self, text):
        self.text_changed.emit(text.strip().casefold())

    def _on_submit(self):
        self.search_submitted.emit(self.input_field.text().strip())

    def text(self):
        return self.input_field.text().strip()