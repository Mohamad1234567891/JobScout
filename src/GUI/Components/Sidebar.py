from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configure the sidebar's width and identify it for custom styling.
        self.setFixedWidth(220)
        self.setObjectName("sidebar")

        # Create the main vertical layout that organizes the sidebar elements.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(12)

        # Create a horizontal header to position the title and plus button.
        header_layout = QHBoxLayout()

        # Display the application name in the sidebar header.
        title = QLabel("JobScout")
        title.setObjectName("sidebarTitle")

        # Create the plus button for future sidebar functionality.
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(32, 32)
        self.plus_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plus_button.setObjectName("plusButton")

        # Align the title to the left and the plus button to the right.
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.plus_button)

        layout.addLayout(header_layout)

        # Connect the button's click event to its handler method.
        self.plus_button.clicked.connect(self.on_plus_clicked)

        # Add a horizontal divider to separate the header from future content.
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("sidebarDivider")
        layout.addWidget(divider)

        # Keep the header at the top by occupying the remaining vertical space.
        layout.addStretch()

        # Apply custom styles to control the sidebar's appearance.
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

            /* Highlight the plus button when the user hovers over it. */
            QPushButton#plusButton:hover {
                background-color: #3b5272;
            }
        """)

    def on_plus_clicked(self):
        # Placeholder for the functionality that will be added later.
        pass