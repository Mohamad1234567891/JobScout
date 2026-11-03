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
"""

import time

from PySide6.QtWidgets import (
    QComboBox, QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPoint, QSize, QEvent, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetrics


class CustomDropdown(QComboBox):
    """A clean, dark-themed Bootstrap-style dropdown component matching the panel range."""

    def __init__(self, placeholder="Option", items=None, parent=None):
        super().__init__(parent)

        self.setPlaceholderText(placeholder)
        self.setCurrentIndex(-1)

        if items:
            self.addItems(items)

        self.setFixedHeight(38)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QComboBox {
                background-color: #313135;
                border: 1px solid #3f3f46;
                border-radius: 8px;
                padding: 6px 14px;
                color: #f4f4f5;
                font-size: 13px;
                font-weight: 500;
            }
            QComboBox:hover {
                border-color: #52525b;
                background-color: #38383d;
            }
            QComboBox:on {
                border-color: #3b82f6;
                background-color: #313135;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                font-size: 12px;
                color: #a1a1aa;
                subcontrol-position: center right;
                margin-right: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #313135;
                color: #f4f4f5;
                border: 1px solid #3f3f46;
                border-radius: 8px;
                selection-background-color: #3b82f6;
                selection-color: #ffffff;
                padding: 4px;
                outline: none;
            }
        """)

    def add_option(self, option_text: str):
        """Adds a new option item to the dropdown list."""
        self.addItem(option_text)

    def current_value(self):
        """Returns the selected text, or None when nothing is selected."""
        return self.currentText() if self.currentIndex() >= 0 else None

    def set_value(self, text):
        """Selects the given option when it exists (no-op otherwise)."""
        index = self.findText(text)
        if index >= 0:
            self.setCurrentIndex(index)


class SelectionDropdown(QFrame):
    """Multi-select dropdown. Choose as many items as you want; chosen items show as small chips
    in the box. Clicking anywhere outside the list closes it and keeps the selection."""
    selection_changed = Signal(list)

    ROW_HEIGHT = 36
    MAX_VISIBLE_ROWS = 5

    def __init__(self, placeholder="Select...", items=None, parent=None):
        super().__init__(parent)
        self.placeholder = placeholder
        self._selected = []
        self._updating = False
        self._last_close = 0.0

        self.setFixedHeight(38)
        self.setMinimumWidth(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("open", False)
        self.setStyleSheet("""
            SelectionDropdown {
                background-color: #313135;
                border: 1px solid #3f3f46;
                border-radius: 8px;
            }
            SelectionDropdown:hover {
                border: 1px solid #52525b;
                background-color: #38383d;
            }
            SelectionDropdown[open="true"] {
                border: 1px solid #3b82f6;
                background-color: #313135;
            }
        """)

        # Header: chips on the left, arrow on the right
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(8)

        self._chips = QHBoxLayout()
        self._chips.setContentsMargins(0, 0, 0, 0)
        self._chips.setSpacing(6)
        layout.addLayout(self._chips, 1)

        self._arrow = QLabel("▾")
        self._arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._arrow.setStyleSheet("color: #a1a1aa; font-size: 14px; background: transparent; border: none;")
        layout.addWidget(self._arrow)

        self._build_popup()
        self.set_items(items or [])

    # ---------- popup (the floating list) ----------
    def _build_popup(self):
        self._popup = QWidget(
            self,
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint,
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        outer = QVBoxLayout(self._popup)
        outer.setContentsMargins(0, 0, 0, 0)

        box = QFrame()
        box.setObjectName("SelectionPopupBox")
        box.setStyleSheet("""
            #SelectionPopupBox {
                background-color: #313135;
                border: 1px solid #3f3f46;
                border-radius: 8px;
            }
        """)
        outer.addWidget(box)

        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(6, 6, 6, 6)
        box_layout.setSpacing(4)

        # Search box: typing filters the options (useful for long lists).
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search options...")
        self._search_input.setClearButtonEnabled(True)
        self._search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 6px 8px;
                color: #f4f4f5;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }
        """)
        self._search_input.textChanged.connect(self._filter_items)
        box_layout.addWidget(self._search_input)

        self._list = QListWidget()
        self._list.setFrameShape(QFrame.Shape.NoFrame)
        self._list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self._list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setSpacing(2)
        self._list.setMouseTracking(True)
        self._list.viewport().installEventFilter(self)   # click anywhere on a row to toggle it
        self._list.itemChanged.connect(self._on_item_changed)
        self._list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
                color: #e4e4e7;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.06);
            }
            QListWidget::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid #52525b;
                background-color: #2a2a2a;
            }
            QListWidget::indicator:checked {
                background-color: #3b82f6;
                border: 1px solid #3b82f6;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #52525b;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        box_layout.addWidget(self._list)

        # Footer: "2 selected" on the left, "Clear" on the right
        footer = QHBoxLayout()
        footer.setContentsMargins(8, 0, 4, 0)
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("color: #a1a1aa; font-size: 12px; background: transparent; border: none;")
        clear_btn = QPushButton("Clear")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setFlat(True)
        clear_btn.setStyleSheet("""
            QPushButton {
                color: #93c5fd;
                font-size: 12px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 4px 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(147, 197, 253, 0.12);
            }
        """)
        clear_btn.clicked.connect(self.clear_selection)
        footer.addWidget(self._count_label)
        footer.addStretch()
        footer.addWidget(clear_btn)
        box_layout.addLayout(footer)

        self._popup.installEventFilter(self)   # to know when it closes

    def eventFilter(self, obj, event):
        # Clicking a row toggles its check box (the whole row is clickable)
        if obj is self._list.viewport():
            kind = event.type()
            if kind in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonDblClick):
                item = self._list.itemAt(event.position().toPoint())
                if item is not None:
                    if item.checkState() == Qt.CheckState.Checked:
                        item.setCheckState(Qt.CheckState.Unchecked)
                    else:
                        item.setCheckState(Qt.CheckState.Checked)
                return True
            if kind == QEvent.Type.MouseButtonRelease:
                return True
        # The popup closed (click outside, Esc, ...)
        elif obj is self._popup and event.type() == QEvent.Type.Hide:
            self._last_close = time.monotonic()
            self._set_open(False)
        return super().eventFilter(obj, event)

    # ---------- public API ----------
    def set_items(self, items):
        self._updating = True
        self._list.clear()
        for text in items:
            item = QListWidgetItem(text)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setSizeHint(QSize(0, self.ROW_HEIGHT))
            self._list.addItem(item)
        self._updating = False
        self._filter_items(self._search_input.text())
        self._sync_from_list()

    def _filter_items(self, text):
        """Shows only the options that contain the search text."""
        query = (text or "").strip().casefold()
        for index in range(self._list.count()):
            item = self._list.item(index)
            item.setHidden(bool(query) and query not in item.text().casefold())

    def selected_items(self):
        return list(self._selected)

    def set_selected(self, texts):
        wanted = set(texts)
        self._updating = True
        for i in range(self._list.count()):
            item = self._list.item(i)
            state = Qt.CheckState.Checked if item.text() in wanted else Qt.CheckState.Unchecked
            item.setCheckState(state)
        self._updating = False
        self._sync_from_list()
        self.selection_changed.emit(list(self._selected))

    def clear_selection(self):
        self.set_selected([])

    # ---------- internals ----------
    def _sync_from_list(self):
        """Reads the checked rows, recolors them, and refreshes the header chips."""
        self._updating = True
        self._selected = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            checked = item.checkState() == Qt.CheckState.Checked
            item.setForeground(QColor("#93c5fd" if checked else "#e4e4e7"))
            if checked:
                self._selected.append(item.text())
        self._updating = False
        count = len(self._selected)
        self._count_label.setText(f"{count} selected" if count else "Nothing selected")
        self._refresh_header()

    def _on_item_changed(self, item):
        if self._updating:
            return
        self._sync_from_list()
        self.selection_changed.emit(list(self._selected))

    def _make_chip(self, text, extra=False):
        chip = QLabel(text)
        chip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        colors = "background-color: #3f3f46; color: #d4d4d8;" if extra else "background-color: #1e3a8a; color: #93c5fd;"
        chip.setStyleSheet(
            colors + " padding: 3px 10px; border-radius: 10px; font-size: 12px; font-weight: 600; border: none;"
        )
        return chip

    def _refresh_header(self):
        # Remove everything currently in the header
        while self._chips.count():
            child = self._chips.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

        if not self._selected:
            label = QLabel(self.placeholder)
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            label.setStyleSheet("color: #f4f4f5; font-size: 13px; font-weight: 500; background: transparent; border: none;")
            self._chips.addWidget(label)
            self._chips.addStretch()
            return

        font = QFont(self.font())
        font.setPixelSize(12)
        font.setBold(True)
        metrics = QFontMetrics(font)

        available = self.width() - 14 - 14 - 8 - 14   # paddings, spacing and the arrow
        used = 0
        shown = 0
        for i, text in enumerate(self._selected):
            chip_width = metrics.horizontalAdvance(text) + 26
            remaining = len(self._selected) - (i + 1)
            reserve = 44 if remaining > 0 else 0       # room for the "+N" chip
            if shown > 0 and used + chip_width + reserve > available:
                break
            self._chips.addWidget(self._make_chip(text))
            used += chip_width + 6
            shown += 1

        hidden = len(self._selected) - shown
        if hidden > 0:
            self._chips.addWidget(self._make_chip(f"+{hidden}", extra=True))
        self._chips.addStretch()

    def _set_open(self, is_open):
        self.setProperty("open", is_open)
        self.style().unpolish(self)
        self.style().polish(self)
        self._arrow.setText("▴" if is_open else "▾")

    def _show_popup(self):
        if self._list.count() == 0:
            return
        rows = max(1, min(self._list.count(), self.MAX_VISIBLE_ROWS))
        self._list.setFixedHeight(rows * (self.ROW_HEIGHT + 2) + 4)
        self._popup.setFixedWidth(self.width())
        self._popup.adjustSize()

        pos = self.mapToGlobal(QPoint(0, self.height() + 4))
        # If there isn't enough room under the dropdown, open it upwards instead
        screen = self.screen().availableGeometry()
        if pos.y() + self._popup.height() > screen.bottom():
            pos = self.mapToGlobal(QPoint(0, -self._popup.height() - 4))
        self._popup.move(pos)
        self._popup.show()
        self._set_open(True)

        # Fresh search each time the dropdown opens, ready for typing.
        self._search_input.clear()
        QTimer.singleShot(0, self._search_input.setFocus)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # If the popup was just closed by this same click, don't reopen it right away
            if time.monotonic() - self._last_close > 0.2:
                self._show_popup()
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_header()