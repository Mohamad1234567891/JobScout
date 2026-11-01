
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QToolButton
)
from PySide6.QtCore import Qt


class ActionItem(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        # Main horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # Action title button
        self.title_button = QPushButton(title)
        self.title_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_button.setObjectName("actionTitleButton")
        self.title_button.clicked.connect(self.on_clicked)

        # Three-dot button (no functionality for now)
        self.options_button = QToolButton()
        self.options_button.setText("⋯")
        self.options_button.setFixedSize(28, 28)
        self.options_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.options_button.setObjectName("optionsButton")

        # Add buttons to the layout
        layout.addWidget(self.title_button, 1)
        layout.addWidget(self.options_button)

        # Styling
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

    def on_clicked(self):
        pass
