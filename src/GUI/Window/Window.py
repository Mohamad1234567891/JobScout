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
from GUI.Components.Drop_down import CustomDropdown, SelectionDropdown


class JobScoutWindow(QMainWindow):
    """Main JobScout window - the search bar lives only inside the panel."""

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

        # Keep the content area stretched
        self.layout.addStretch()

        # Let the content fill the remaining width
        main_layout.addWidget(self.content_widget, 1)

        # Initialize the panel
        self.panel = Panel(self.content_widget)
        self.panel.start_search_clicked.connect(self.on_start_search)

        # The search bar is created here but goes straight into the panel (never into the window layout)
        suggestions = [
            "Python Developer",
            "Backend Engineer",
            "PySide6",
            "Software Engineer",
        ]

        self.search_bar = SearchBar(suggestions=suggestions)
        self.search_bar.input_field.setPlaceholderText(
            "Search for a job (e.g. Python Developer)..."
        )
        self.search_bar.search_submitted.connect(self.on_search)
        self.panel.dock_search_bar(self.search_bar)

        # Creat the Drop down and add it to panel
        self.education_dropdown = CustomDropdown(
            placeholder="Education Level",
            items=["Bachelor", "Master", "PhD",]
        )
        self.panel.add_header_widget(self.education_dropdown)

        # Multi-select drop down (can choose more than one item) and add it to panel
        self.skills_dropdown = SelectionDropdown(
            placeholder="Skills",
            items=["Python", "Java", "C++", "JavaScript", "SQL"]
        )
        self.skills_dropdown.selection_changed.connect(self.on_skills_changed)
        self.panel.add_header_widget(self.skills_dropdown)

        # Show it automatically on startup using QTimer for precise centering
        QTimer.singleShot(0, self.toggle_panel)

    def update_panel_geometry(self):
        """Dynamically resize and center the panel based on the content window size."""
        if hasattr(self, 'panel') and self.panel.isVisible():
            target_width = max(450, min(int(self.content_widget.width() * 0.85), 1000))
            target_height = max(350, min(int(self.content_widget.height() * 0.80), 700))

            self.panel.resize(target_width, target_height)

            # Center the panel in the content area
            x = (self.content_widget.width() - self.panel.width()) // 2
            y = (self.content_widget.height() - self.panel.height()) // 2

            self.panel.move(x, y)

    def toggle_panel(self):
        """Toggles the panel visibility and ensures precise centering immediately."""
        if self.panel.isVisible():
            self.panel.hide()
        else:
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
        # Collect everything the user chose in the panel (ready for the real search later)
        filters = {
            "query": self.search_bar.text(),
            "education": self.education_dropdown.currentText(),
            "skills": self.skills_dropdown.selected_items(),
        }
        print(f"Start search clicked: {filters}")

        # Close the panel
        self.panel.hide()

        # TODO: add the next steps here (run the search, show the results, ...)

    def on_skills_changed(self, selected):
        """Triggered when the chosen items in the Skills drop down change"""
        print(f"Skills selected: {selected}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JobScoutWindow()
    window.show()
    sys.exit(app.exec())