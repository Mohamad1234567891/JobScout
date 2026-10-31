from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal

from GUI.Components.Button import Button  # reused styled button


class Panel(QFrame):
    """Responsive dark translucent panel containing search tools and cards."""
    closed = Signal()
    start_search_clicked = Signal()  # emitted when the Start Search button is clicked

    def __init__(self, parent=None):
        super().__init__(parent)

        # Search bar that is currently docked inside the panel (None when it lives in the window)
        self._docked_bar = None
        self._saved_bar_state = None

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

        # Footer row with "Start Search" button at the bottom right
        self.footer_layout = QHBoxLayout()
        self.footer_layout.addStretch()

        # Reuse the Button component (same look as the rest of the app)
        self.start_search_btn = Button("Start Search", "")
        # This button doesn't open a URL, so remove Button's default click action
        self.start_search_btn.clicked.disconnect(self.start_search_btn.OnClicked)
        self.start_search_btn.setFixedSize(130, 34)  # a bit wider than the default 110px for the longer text
        self.start_search_btn.clicked.connect(self.start_search_clicked.emit)

        self.footer_layout.addWidget(self.start_search_btn)
        self.main_layout.addLayout(self.footer_layout)

    def dock_search_bar(self, bar):
        """Moves the window's existing SearchBar into the top of the panel and restyles it for the dark panel."""
        if self._docked_bar is bar:
            return

        # Remember the original look so it can be restored later
        self._saved_bar_state = {
            "bar_style": bar.styleSheet(),
            "input_style": bar.input_field.styleSheet(),
            "max_width": bar.maximumWidth(),
            "height": bar.minimumHeight(),
            "margins": bar.layout().contentsMargins(),
            "btn_visible": True,
        }

        # Hide the Search button (pressing Enter still submits)
        bar.search_btn.hide()

        # Dark look that matches the panel and dropdown
        bar.setFixedHeight(44)
        bar.setMaximumWidth(16777215)  # fill the panel width like the dropdown
        bar.layout().setContentsMargins(14, 4, 14, 4)
        bar.setStyleSheet("""
            SearchBar {
                background-color: #313135;
                border: 1px solid #3f3f46;
                border-radius: 8px;
            }
        """)
        bar.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #f4f4f5;
                selection-background-color: #1e3a8a;
            }
        """)

        # Put it above the dropdown row
        self.main_layout.insertWidget(0, bar)
        bar.show()
        self._docked_bar = bar

    def undock_search_bar(self):
        """Takes the SearchBar out of the panel, restores its original look, and returns it (or None)."""
        bar = self._docked_bar
        if bar is None:
            return None

        state = self._saved_bar_state
        self.main_layout.removeWidget(bar)

        bar.setStyleSheet(state["bar_style"])
        bar.input_field.setStyleSheet(state["input_style"])
        bar.setFixedHeight(state["height"])
        bar.setMaximumWidth(state["max_width"])
        bar.layout().setContentsMargins(state["margins"])
        bar.search_btn.setVisible(state["btn_visible"])

        self._docked_bar = None
        self._saved_bar_state = None
        return bar

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