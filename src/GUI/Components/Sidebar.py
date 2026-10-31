
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt

from GUI.Components.Action_item import ActionItem
from GUI.Components.Scroll import SidebarScrollContainer


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

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.plus_button)

        layout.addLayout(header_layout)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("sidebarDivider")
        layout.addWidget(divider)

        # Scrollable area for action items
        self.action_scroll = SidebarScrollContainer()
        layout.addWidget(self.action_scroll)

        # Add example action items
        self.action_scroll.add_item(ActionItem("Dashboard"))
        self.action_scroll.add_item(ActionItem("Job Search"))
        self.action_scroll.add_item(ActionItem("Saved Jobs"))
        self.action_scroll.add_item(ActionItem("Application Tracker"))

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
