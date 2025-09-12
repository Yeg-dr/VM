from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
import json


class ChangePasswordPanel(QWidget):
    """
    Panel for changing the admin password.
    Provides a numeric keypad, masked input display,
    and logic for verifying the old password before setting a new one.
    """

    def __init__(self, parent, items_file="vending_items.json"):
        """
        Initialize the ChangePasswordPanel.

        Args:
            parent: The parent widget or main controller.
            items_file (str): Path to the JSON file containing items and admin password.
        """
        super().__init__()
        self.parent = parent
        self.items_file = items_file
        self.state = "enter_old"  # State can be "enter_old" or "enter_new"
        self.current_input = ""   # Stores keypad input
        self.setup_ui()

    def setup_ui(self):
        """Build and configure the UI components for the password change process."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Instruction message
        self.message_label = QLabel("Enter current admin password")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 25px; color: #666;")
        self.layout.addWidget(self.message_label)

        # Masked password display
        self.input_display = QLabel("")
        self.input_display.setObjectName("display_label")
        self.input_display.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.input_display)

        # Numeric keypad
        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(10)
        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('C', 3, 0), ('0', 3, 1)
        ]
        for text, row, col in buttons:
            button = QPushButton(text)
            button.setFixedHeight(60)
            button.setFixedWidth(100)
            if text == 'C':
                button.setStyleSheet("background-color: #FF5252;")
            button.clicked.connect(lambda _, t=text: self.on_keypad_clicked(t))
            keypad_layout.addWidget(button, row, col)
        self.layout.addLayout(keypad_layout)

        # Enter button (orange, confirms input)
        self.enter_btn = QPushButton("Enter")
        self.enter_btn.setStyleSheet(
            "background-color: #FFA726; color: white; font-size: 22px; "
            "font-weight: bold; border-radius: 10px;"
        )
        self.enter_btn.setFixedHeight(60)
        self.enter_btn.clicked.connect(self.on_enter_clicked)
        self.layout.addWidget(self.enter_btn)

        # Back button (returns to admin panel)
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.admin_panel))
        self.back_btn.setFixedHeight(50)
        self.layout.addWidget(self.back_btn)

    def showEvent(self, event):
        """Reset panel state and clear input whenever the panel is shown."""
        self.state = "enter_old"
        self.message_label.setText("Enter current admin password")
        self.input_display.setText("")
        self.current_input = ""

    def on_keypad_clicked(self, text):
        """
        Handle keypad button clicks.

        Args:
            text (str): The key pressed ('0'-'9' or 'C').
        """
        if text == 'C':
            self.current_input = ""
            self.input_display.setText("")
        else:
            if len(self.current_input) >= 8:
                return  # Limit password length to 8 digits
            self.current_input += text
            # Display masked password as asterisks
            self.input_display.setText('*' * len(self.current_input))

    def on_enter_clicked(self):
        """Handle Enter button click based on current state."""
        if self.state == "enter_old":
            self.check_old_password()
        elif self.state == "enter_new":
            self.change_password()

    def check_old_password(self):
        """Verify that the entered password matches the stored admin password."""
        try:
            with open(self.parent.items_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            current_pass = str(data.get("admin_password", ""))
            if self.current_input == current_pass:
                # Switch to new password entry mode
                self.state = "enter_new"
                self.message_label.setText("Enter new admin password")
                self.input_display.setText("")
                self.current_input = ""
            else:
                QMessageBox.warning(self, "Error", "Incorrect password. Try again.")
                self.input_display.setText("")
                self.current_input = ""
        except Exception:
            QMessageBox.critical(self, "Error", "Unable to read password file.")

    def change_password(self):
        """Validate and update the admin password in the JSON file."""
        new_pass = self.current_input.strip()

        if not new_pass or not new_pass.isdigit():
            QMessageBox.warning(self, "Error", "Password must be numbers only.")
            return

        try:
            with open(self.parent.items_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data["admin_password"] = new_pass
            with open(self.items_file, "w") as f:
                json.dump(data, f, indent=4)

            QMessageBox.information(self, "Success", "Password changed successfully.")
            self.parent.load_items()
            self.parent.switch_screen(self.parent.admin_panel)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
