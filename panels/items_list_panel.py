from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
)
import json


class ItemsListPanel(QWidget):
    """
    Panel for displaying the list of items available in the vending machine.
    Reads item data from a JSON file and displays them in a QListWidget.
    Provides a back button to return to the admin panel.
    """

    def __init__(self, parent, items_file="vending_items.json"):
        """
        Initialize the ItemsListPanel.

        Args:
            parent: The parent widget (application main controller).
            items_file (str): Path to the items JSON file.
        """
        super().__init__()
        self.parent = parent
        self.items_file = items_file
        self.setup_ui()

    def setup_ui(self):
        """Build and configure the panel layout and UI components."""
        layout = QVBoxLayout(self)

        # Title label
        layout.addWidget(QLabel("Existing Items"))

        # List widget to display items
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Back button (returns to admin panel)
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.admin_panel))
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def load_items(self):
        """
        Load items from the JSON file and populate the list widget.
        Only items with a valid name and price > 0 are shown.
        If an error occurs, display the error in the list.
        """
        self.list_widget.clear()
        try:
            with open(self.parent.items_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Filter keys that represent item codes
            keys = [k for k in data.keys() if k.isdigit()]

            for key in sorted(keys, key=int):
                if key == "admin_password":
                    continue
                item = data[key]

                # Only display items with valid data
                if item.get("name") and item.get("price", 0) > 0:
                    display = (
                        f'#{key}: {item["name"]} - '
                        f'Price: {item["price"]} - '
                        f'Location: {item["location"]}'
                    )
                    QListWidgetItem(display, self.list_widget)

        except Exception as e:
            # Show error message in the list if loading fails
            QListWidgetItem(f"Error loading items: {e}", self.list_widget)
