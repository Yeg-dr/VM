from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
import json
import os

from card_reader import CardReader
from relay_controller import RelayController

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
        layout.addWidget(self.display_label)

        self.keypad_layout = QGridLayout()
        self.keypad_layout.setSpacing(10)

        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('C', 3, 0), ('0', 3, 1), ('↵', 3, 2)
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.setFixedHeight(80)
            if text == 'C':
                button.setStyleSheet("background-color: #FF5252;")
            elif text == '↵':
                button.setObjectName("action_button")
            button.clicked.connect(lambda _, t=text: self.on_keypad_clicked(t))
            self.keypad_layout.addWidget(button, row, col)

        layout.addLayout(self.keypad_layout)

        self.select_another_btn = QPushButton("Select Another Item")
        self.select_another_btn.setObjectName("action_button")
        self.select_another_btn.clicked.connect(self.on_select_another)
        layout.addWidget(self.select_another_btn)

        self.confirm_pay_btn = QPushButton("Confirm and Pay")
        self.confirm_pay_btn.setObjectName("action_button")
        self.confirm_pay_btn.clicked.connect(self.on_confirm_pay)
        layout.addWidget(self.confirm_pay_btn)

        self.admin_btn = QPushButton("Admin")
        self.admin_btn.setObjectName("admin_button")
        self.admin_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.admin_login))
        layout.addWidget(self.admin_btn)

    def load_items(self):
        try:
            with open(self.parent.items_file, 'r', encoding='utf-8') as f:
                self.items = json.load(f)
            self.json_error = False
        except Exception as e:
            self.items = {}
            self.json_error = True
            self.display_label.setText("Fatal error: Items DB missing/corrupt")
            self.setDisabled(True)

    def item_lookup(self, code):
        """ Returns the item dict for the given code, or None """
        return self.items.get(str(code), None)

    def on_keypad_clicked(self, text):
        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return
            
        if text == 'C':
            self.current_input = ""
            self.display_label.setText("Ready")
        elif text == '↵':
            self.process_item_selection()
        else:
            self.current_input += text
            self.display_label.setText(f"Entered: {self.current_input}")

    def process_item_selection(self):
        if not self.current_input:
            self.display_label.setText("Please enter an item code")
            QTimer.singleShot(2000, lambda: self.display_label.setText("Ready"))
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
            QTimer.singleShot(2000, lambda: self.display_label.setText("Ready"))

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

    def on_select_another(self):
        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return
        self.current_input = ""
        if self.selected_items:
            self.update_selection_display()
        else:
            self.display_label.setText("Ready")

    def on_confirm_pay(self):
        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return
            
        if not self.selected_items:
            self.display_label.setText("Please select an item first")
            QTimer.singleShot(2000, lambda: self.display_label.setText("Ready"))
            return

        # Check if all selected items are valid
        invalid_items = []
        for item in self.selected_items:
            if not self.item_lookup(item["code"]) or not self.item_lookup(item["code"]).get('name'):
                invalid_items.append(item["code"])
        
        if invalid_items:
            self.display_label.setText(f"Items {', '.join(invalid_items)} not available")
            QTimer.singleShot(3000, lambda: self.display_label.setText("Ready"))
            return

        self.display_label.setText(f"Total: ${self.total_price/100:.2f}\nPlease proceed with payment")
        QTimer.singleShot(1500, self.process_payment)

    def process_payment(self):
        result = self.card_reader.charge(self.total_price)
        self.handle_payment_result(result)

    def handle_payment_result(self, result):
        if result.get("success"):
            self.display_label.setText("Payment successful\nPreparing to dispense items...")
            QTimer.singleShot(1500, self.start_dispensing)
        else:
            self.display_label.setText("Payment failed\nPlease try again")
            QTimer.singleShot(3000, lambda: self.display_label.setText("Ready"))

    def start_dispensing(self):
        def status_callback(msg):
            self.display_label.setText(msg)
            
        def dispensing_complete():
            self.display_label.setText("All items were successfully dispensed")
            self.selected_items = []
            self.total_price = 0
            self.current_input = ""
            QTimer.singleShot(3000, lambda: self.display_label.setText("Ready"))

        self.relay_controller.dispense(self.selected_items, status_callback)
        QTimer.singleShot(3000, dispensing_complete)