import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFrame
)

from GUI.Components.Sidebar import Sidebar
from PySide6.QtCore import Qt

# Import the search bar component
from GUI.Components.SearchBar import SearchBar



class JobScoutWindow(QMainWindow):
    """Main JobScout window - featuring a flexible centered search bar."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JobScout")
        self.resize(900, 600)
        self.setMinimumSize(400, 300)

        
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
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1f1f1f;")

        self.layout = QVBoxLayout(content_widget)
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
        main_layout.addWidget(content_widget, 1)


        # Connect search signal to handler
        self.search_bar.search_submitted.connect(self.on_search)

    def on_search(self, query):
        """Triggered when search is submitted or Enter is pressed"""
        print(f"Search query submitted: {query}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JobScoutWindow()
    window.show()
    sys.exit(app.exec())