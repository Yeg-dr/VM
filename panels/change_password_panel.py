from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import json

class ChangePasswordPanel(QWidget):
    def __init__(self, parent, items_file="vending_items.json"):
        super().__init__()
        self.parent = parent
        self.items_file = items_file
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter New Admin Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        btn = QPushButton("Set Password")
        btn.clicked.connect(self.on_set_password)
        layout.addWidget(btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.admin_panel))
        layout.addWidget(back_btn)

    def on_set_password(self):
        new_pass = self.password_input.text().strip()
        if not new_pass:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return
        try:
            with open(self.items_file, "r") as f:
                data = json.load(f)
            data["admin_password"] = new_pass
            with open(self.items_file, "w") as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Success", "Password changed successfully.")
            self.password_input.clear()
            self.parent.load_items()  # reload items so app stays up to date
            self.parent.switch_screen(self.parent.admin_panel)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))