from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt

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