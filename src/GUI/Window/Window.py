import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFrame
)

from GUI.Components.Sidebar import Sidebar
from PySide6.QtCore import Qt, QTimer

# Import components
from GUI.Components.SearchBar import SearchBar
from GUI.Components.panel import Panel


class JobScoutWindow(QMainWindow):
    """Main JobScout window - featuring a flexible centered search bar."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JobScout")
        self.resize(900, 600)

        # Set a safe minimum size limit so the window can't shrink and cause overlaps
        self.setMinimumSize(750, 500)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout: sidebar on the left, content on the right
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Main content area
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #1f1f1f;")

        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setContentsMargins(20, 40, 20, 20)
        self.layout.setSpacing(20)

        # Top spacer
        self.logo_space = QWidget()
        self.logo_space.setFixedHeight(40)
        self.layout.addWidget(self.logo_space)

        # Search row
        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(10)

        suggestions = [
            "Python Developer",
            "Backend Engineer",
            "PySide6",
            "Software Engineer",
        ]

        self.search_bar = SearchBar(suggestions=suggestions)
        self.search_bar.setMaximumWidth(700)
        self.search_bar.input_field.setPlaceholderText(
            "Search for a job (e.g. Python Developer)..."
        )

        search_row.addStretch()
        search_row.addWidget(self.search_bar)
        search_row.addStretch()
        self.layout.addLayout(search_row)

        # Keep the search bar area vertically centered
        self.layout.addStretch()

        # Let the content fill the remaining width
        main_layout.addWidget(self.content_widget, 1)

        # Connect search signal to handler
        self.search_bar.search_submitted.connect(self.on_search)

        # Initialize the panel
        self.panel = Panel(self.content_widget)

        # Show it automatically on startup using QTimer for precise centering
        QTimer.singleShot(0, self.toggle_panel)


    def update_panel_geometry(self):
        """Dynamically resize and center the panel based on the content window size."""
        if hasattr(self, 'panel') and self.panel.isVisible():
            target_width = max(350, min(int(self.content_widget.width() * 0.55), 700))
            target_height = max(220, min(int(self.content_widget.height() * 0.55), 500))

            self.panel.resize(target_width, target_height)

            # Center it inside content_widget
            x = (self.content_widget.width() - self.panel.width()) // 2
            y = (self.content_widget.height() - self.panel.height()) // 2
            self.panel.move(x, y)

    def toggle_panel(self):
        """
        Connect this function to your future button later like this:
        self.your_button.clicked.connect(self.toggle_panel)
        """
        self.update_panel_geometry()
        self.panel.show()
        self.panel.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_panel_geometry()

    def on_search(self, query):
        """Triggered when search is submitted or Enter is pressed"""
        print(f"Search query submitted: {query}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JobScoutWindow()
    window.show()
    sys.exit(app.exec())