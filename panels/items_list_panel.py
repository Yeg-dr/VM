from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
import json

class ItemsListPanel(QWidget):
    def __init__(self, parent, items_file="vending_items.json"):
        super().__init__()
        self.parent = parent
        self.items_file = items_file
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Existing Items"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.admin_panel))
        layout.addWidget(back_btn)
        self.setLayout(layout)

    def load_items(self):
        self.list_widget.clear()
        try:
            with open(self.parent.items_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            keys = [k for k in data.keys() if k.isdigit()]
            for key in sorted(keys, key=int):
                if key == "admin_password":
                    continue
                item = data[key]
                if item.get("name") and item.get("price", 0) > 0:
                    display = f'#{key}: {item["name"]} - Price: {item["price"]} - Location: {item["location"]}'
                    QListWidgetItem(display, self.list_widget)
        except Exception as e:
            QListWidgetItem(f"Error loading items: {e}", self.list_widget)