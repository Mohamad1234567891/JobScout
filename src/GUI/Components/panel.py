from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal


class Panel(QFrame):
    """Responsive white translucent panel containing a close button."""
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # White translucent style
        self.setStyleSheet("""
            Panel {
                background-color: rgba(255, 255, 255, 230);
                border: 1px solid rgba(255, 255, 255, 255);
                border-radius: 14px;
            }
        """)

        self.setMinimumSize(300, 200)

        # Panel inner layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header layout to align the close button to the top-right
        header_layout = QHBoxLayout()
        header_layout.addStretch()

        # Close button (X)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #475569;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 200);
                color: white;
            }
        """)

        self.close_btn.clicked.connect(self.hide)
        self.close_btn.clicked.connect(self.closed.emit)

        header_layout.addWidget(self.close_btn)
        layout.addLayout(header_layout)
        layout.addStretch()


    def show_panel_action(self):
        """You can call this function whenever you want to show this panel later."""
        self.show()
        self.raise_()
