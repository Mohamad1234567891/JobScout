import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout
)

from GUI.Components.Sidebar import Sidebar
from PySide6.QtCore import Qt, QTimer

# Import components
from GUI.Components.SearchBar import SearchBar
from GUI.Components.panel import Panel
from GUI.Components.Drop_down import CustomDropdown


class JobScoutWindow(QMainWindow):
    """Main JobScout window - the search bar lives in the window until the panel opens, then moves into the panel."""

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

        # Left sidebar and connecting its plus_button to toggle the panel
        self.sidebar = Sidebar()
        self.sidebar.plus_button.clicked.connect(self.toggle_panel)
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

        # Search row (kept as an attribute so the search bar can be put back here later)
        self.search_row = QHBoxLayout()
        self.search_row.setContentsMargins(0, 0, 0, 0)
        self.search_row.setSpacing(10)

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

        self.search_row.addStretch()
        self.search_row.addWidget(self.search_bar)
        self.search_row.addStretch()
        self.layout.addLayout(self.search_row)

        # Keep the search bar area vertically centered
        self.layout.addStretch()

        # Let the content fill the remaining width
        main_layout.addWidget(self.content_widget, 1)

        # Connect search signal to handler (still works after the bar moves into the panel)
        self.search_bar.search_submitted.connect(self.on_search)

        # Initialize the panel
        self.panel = Panel(self.content_widget)

        # When the panel is closed with its X button, put the search bar back in the window
        self.panel.closed.connect(self.restore_search_bar)
        self.panel.start_search_clicked.connect(self.on_start_search)

        # Creat the Drop down and add it to panel
        self.education_dropdown = CustomDropdown(
            placeholder="Education Level",
            items=["Bachelor", "Master", "PhD",]
        )
        self.panel.add_header_widget(self.education_dropdown)

        # Show it automatically on startup using QTimer for precise centering
        QTimer.singleShot(0, self.toggle_panel)

    def move_search_bar_to_panel(self):
        """Takes the search bar out of the window layout and docks it at the top of the panel."""
        self.search_row.removeWidget(self.search_bar)
        self.panel.dock_search_bar(self.search_bar)

    def restore_search_bar(self):
        """Gives the search bar back to the window (between the two stretches of the search row)."""
        bar = self.panel.undock_search_bar()
        if bar is not None:
            self.search_row.insertWidget(1, bar)
            bar.show()

    def update_panel_geometry(self):
        """Dynamically resize and center the panel based on the content window size."""
        if hasattr(self, 'panel') and self.panel.isVisible():
            target_width = max(450, min(int(self.content_widget.width() * 0.85), 1000))
            target_height = max(350, min(int(self.content_widget.height() * 0.80), 700))

            self.panel.resize(target_width, target_height)

            # Center it horizontally, with a slight downward offset so it doesn't overlap the search bar
            x = (self.content_widget.width() - self.panel.width()) // 2
            y = ((self.content_widget.height() - self.panel.height()) // 2) + 60

            self.panel.move(x, y)

    def toggle_panel(self):
        """Toggles the panel visibility and ensures precise centering immediately."""
        if self.panel.isVisible():
            self.panel.hide()
            self.restore_search_bar()
        else:
            self.move_search_bar_to_panel()
            self.panel.show()
            self.panel.raise_()

            QTimer.singleShot(0, self.update_panel_geometry)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_panel_geometry()

    def on_search(self, query):
        """Triggered when search is submitted or Enter is pressed"""
        print(f"Search query submitted: {query}")

    def on_start_search(self):
        """Triggered when the Start Search button in the panel is clicked"""
        print("Start search clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JobScoutWindow()
    window.show()
    sys.exit(app.exec())