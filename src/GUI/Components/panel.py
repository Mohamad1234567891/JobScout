from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal


class Panel(QFrame):
    """Responsive dark translucent panel containing search tools and cards."""
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Sleek dark Bootstrap-inspired surface styling
        self.setStyleSheet("""
            Panel {
                background-color: #2a2a2a;
                border: 1px solid #3f3f46;
                border-radius: 12px;
            }
        """)

        self.setMinimumSize(450,350)

        # Panel inner layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Header layout (Top row: Dropdowns + Close Button)
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(10)

        # Close button (X)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a1a1aa;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.15);
                color: #ef4444;
            }
        """)

        self.close_btn.clicked.connect(self.hide)
        self.close_btn.clicked.connect(self.closed.emit)

        self.header_layout.addStretch()
        self.header_layout.addWidget(self.close_btn)
        self.main_layout.addLayout(self.header_layout)

        # Container for content / dynamic cards
        self.content_container_layout = QVBoxLayout()
        self.content_container_layout.setSpacing(10)
        self.main_layout.addLayout(self.content_container_layout)

        self.main_layout.addStretch()

    def add_header_widget(self, widget):
        """Allows adding any widget (like a Dropdown) from the main window to the panel header."""
        # Insert the widget right before the close button stretch/item
        self.header_layout.insertWidget(self.header_layout.count() - 2, widget, 1)

    def add_job_card(self, title, company, location, badge_text="New"):
        """Adds a Bootstrap-styled job card dynamically inside the panel."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #313135;
                border: 1px solid #3f3f46;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(4)

        top_row = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-weight: bold; color: #f4f4f5; font-size: 14px; border: none; background: transparent;")

        badge = QLabel(badge_text)
        badge.setStyleSheet("""
            background-color: #1e3a8a;
            color: #93c5fd;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            border: none;
        """)

        top_row.addWidget(title_lbl)
        top_row.addStretch()
        top_row.addWidget(badge)
        card_layout.addLayout(top_row)

        sub_lbl = QLabel(f"{company} • {location}")
        sub_lbl.setStyleSheet("color: #a1a1aa; font-size: 12px; border: none; background: transparent;")
        card_layout.addWidget(sub_lbl)

        self.content_container_layout.addWidget(card)

    def show_panel_action(self):
        """You can call this function whenever you want to show this panel later."""
        self.show()
        self.raise_()