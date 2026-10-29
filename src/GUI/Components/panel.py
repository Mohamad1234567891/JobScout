from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from GUI.Components.Drop_down import CustomDropdown


class Panel(QFrame):
    """Responsive white translucent panel containing search tools and cards."""
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Bootstrap-inspired clean surface styling
        self.setStyleSheet("""
            Panel {
                background-color: rgba(255, 255, 255, 240);
                border: 1px solid rgba(226, 232, 240, 255);
                border-radius: 12px;
            }
        """)

        self.setMinimumSize(350, 280)

        # Panel inner layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Header layout (Top row: Dropdown filter + Close Button)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Initialize the modular CustomDropdown
        initial_locations = ["JAVA","PYTHON","C++"]
        self.filter_dropdown = CustomDropdown(placeholder="Option",items=initial_locations)

        header_layout.addWidget(self.filter_dropdown, 1)

        # Close button (X)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748b;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.1);
                color: #ef4444;
            }
        """)

        self.close_btn.clicked.connect(self.hide)
        self.close_btn.clicked.connect(self.closed.emit)

        header_layout.addWidget(self.close_btn)
        self.main_layout.addLayout(header_layout)

        # Container for content / dynamic cards
        self.content_container_layout = QVBoxLayout()
        self.content_container_layout.setSpacing(10)
        self.main_layout.addLayout(self.content_container_layout)

        self.main_layout.addStretch()

    def add_job_card(self, title, company, location, badge_text="New"):
        """Adds a Bootstrap-styled job card dynamically inside the panel."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(4)

        top_row = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-weight: bold; color: #0f172a; font-size: 14px; border: none; background: transparent;")

        badge = QLabel(badge_text)
        badge.setStyleSheet("""
            background-color: #e0f2fe;
            color: #0369a1;
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
        sub_lbl.setStyleSheet("color: #64748b; font-size: 12px; border: none; background: transparent;")
        card_layout.addWidget(sub_lbl)

        self.content_container_layout.addWidget(card)

    def show_panel_action(self):
        """You can call this function whenever you want to show this panel later."""
        self.show()
        self.raise_()