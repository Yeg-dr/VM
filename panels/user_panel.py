from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel,
    QHBoxLayout, QDialog, QDialogButtonBox, QScrollArea
)
from PyQt5.QtCore import Qt
import json
import os

from card_reader import CardReader
from relay_controller import RelayController


class ConfirmDialog(QDialog):
    def __init__(self, items, total_price, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Payment")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #F9F9F9;
                border-radius: 15px;
            }
            QLabel {
                font-size: 20px;
                color: #333;
            }
            QPushButton {
                min-height: 50px;
                border-radius: 10px;
                font-size: 20px;
                padding: 6px;
            }
            QPushButton#confirm {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#cancel {
                background-color: #B0BEC5;
                color: #333;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Scrollable area in case many items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for item in items:
            lbl = QLabel(f"{item['name']} - ${item['price']/100:.2f}")
            lbl.setAlignment(Qt.AlignLeft)
            scroll_layout.addWidget(lbl)

        total_lbl = QLabel(f"\nTotal: ${total_price/100:.2f}")
        total_lbl.setAlignment(Qt.AlignLeft)
        scroll_layout.addWidget(total_lbl)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        btn_box = QHBoxLayout()
        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setObjectName("confirm")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel")

        self.confirm_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(self.cancel_btn)
        btn_box.addWidget(self.confirm_btn)
        layout.addLayout(btn_box)


class UserPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.card_reader = CardReader()
        self.items = {}
        self.selected_items = []
        self.total_price = 0
        self.current_input = ""
        self.json_error = False
        self.setup_ui()
        self.load_items()
        self.relay_controller = RelayController(self.item_lookup)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.display_label = QLabel("Ready")
        self.display_label.setObjectName("display_label")
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setWordWrap(True)
        layout.addWidget(self.display_label)

        self.keypad_layout = QGridLayout()
        self.keypad_layout.setSpacing(8)

        # Keypad buttons
        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('C', 3, 0), ('0', 3, 1)
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.setFixedHeight(60)  # reduced height
            if text == 'C':
                button.setStyleSheet("background-color: #FF5252;")
            button.clicked.connect(lambda _, t=text: self.on_keypad_clicked(t))
            self.keypad_layout.addWidget(button, row, col)

        layout.addLayout(self.keypad_layout)

        # Vertical button group
        button_group_layout = QVBoxLayout()
        button_group_layout.setSpacing(12)

        self.confirm_btn = QPushButton("Enter")
        self.confirm_btn.setObjectName("action_button")
        self.confirm_btn.setFixedHeight(60)
        self.confirm_btn.clicked.connect(self.on_confirm_item)
        button_group_layout.addWidget(self.confirm_btn)

        self.confirm_pay_btn = QPushButton("Pay")
        self.confirm_pay_btn.setObjectName("action_button")
        self.confirm_pay_btn.setFixedHeight(60)
        self.confirm_pay_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; border-radius: 10px; font-size: 22px;")
        self.confirm_pay_btn.clicked.connect(self.on_confirm_pay)
        button_group_layout.addWidget(self.confirm_pay_btn)

        # Admin and Cancel row
        admin_cancel_row = QHBoxLayout()
        admin_cancel_row.setSpacing(8)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(60)
        self.cancel_btn.setMinimumWidth(160)
        self.cancel_btn.setStyleSheet(
            "background-color: #B0BEC5; color: #333; border-radius: 10px; font-size: 22px;")
        self.cancel_btn.clicked.connect(self.on_cancel)
        admin_cancel_row.addWidget(self.cancel_btn, stretch=2)

        self.admin_btn = QPushButton("Admin")
        self.admin_btn.setObjectName("admin_button")
        self.admin_btn.setFixedHeight(60)
        self.admin_btn.setFixedWidth(100)
        self.admin_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.admin_login))
        admin_cancel_row.addWidget(self.admin_btn, stretch=1)

        button_group_layout.addLayout(admin_cancel_row)
        layout.addLayout(button_group_layout)

    def load_items(self):
        try:
            with open(self.parent.items_file, 'r', encoding='utf-8') as f:
                self.items = json.load(f)
            self.json_error = False
        except Exception:
            self.items = {}
            self.json_error = True
            self.display_label.setText("Fatal error: Items DB missing/corrupt")
            self.setDisabled(True)

    def item_lookup(self, code):
        return self.items.get(str(code), None)

    def on_keypad_clicked(self, text):
        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return

        if text == 'C':
            self.current_input = ""
            self.display_label.setText("Ready")
        else:
            self.current_input += text
            self.display_label.setText(f"Entered: {self.current_input}")

    def on_confirm_item(self):
        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return

        if not self.current_input:
            self.display_label.setText("Please enter an item code")
            return

        item = self.item_lookup(self.current_input)
        if item and item.get('name') and item.get('price', 0) > 0:
            self.selected_items.append({
                "code": self.current_input,
                "name": item["name"],
                "price": item["price"],
                "location": item["location"]
            })
            self.total_price += item["price"]
            self.update_selection_display()
            self.current_input = ""
        else:
            self.display_label.setText(f"Item {self.current_input} not available")
            self.current_input = ""

    def update_selection_display(self):
        if not self.selected_items:
            self.display_label.setText("Ready")
            return

        selected_display = "\n".join([
            f"{i['name']} - ${i['price']/100:.2f}"
            for i in self.selected_items
        ])
        self.display_label.setText(
            f"Selected Items:\n{selected_display}\n\n"
            f"Total: ${self.total_price/100:.2f}"
        )

    def on_confirm_pay(self):
        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return

        if not self.selected_items:
            self.display_label.setText("Please select an item first")
            return

        invalid_items = [
            item["code"] for item in self.selected_items
            if not self.item_lookup(item["code"]) or not self.item_lookup(item["code"]).get('name')
        ]
        if invalid_items:
            self.display_label.setText(f"Items {', '.join(invalid_items)} not available")
            return

        # Show custom popup
        dlg = ConfirmDialog(self.selected_items, self.total_price, self)
        if dlg.exec_() == QDialog.Accepted:
            self.display_label.setText(
                f"Proceeding to payment\nTotal: ${self.total_price/100:.2f}"
            )
            self.process_payment()
        else:
            self.display_label.setText("Payment cancelled. Select more items or press Pay.")

    def process_payment(self):
        result = self.card_reader.charge(self.total_price)
        self.handle_payment_result(result)

    def handle_payment_result(self, result):
        if result.get("success"):
            self.display_label.setText("Payment successful\nPreparing to dispense items...")
            self.start_dispensing()
        else:
            self.display_label.setText("Payment failed\nPlease try again")
            self.confirm_pay_btn.setEnabled(True)

    def start_dispensing(self):
        def status_callback(msg):
            self.display_label.setText(msg)

        def dispensing_complete():
            self.display_label.setText("All items were successfully dispensed")
            self.selected_items = []
            self.total_price = 0
            self.current_input = ""
            self.update_selection_display()

        self.relay_controller.dispense(self.selected_items, status_callback)
        dispensing_complete()

    def on_cancel(self):
        self.selected_items = []
        self.total_price = 0
        self.current_input = ""
        self.display_label.setText("Process cancelled. Ready.")
