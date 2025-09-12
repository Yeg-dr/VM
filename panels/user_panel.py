from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel,
    QHBoxLayout, QDialog, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
import json
import os

from mock_card_reader import CardReader
from mock_relay_controller import RelayController


class ConfirmDialog(QDialog):
    """
    A modal dialog that displays the selected items and the total price.
    Provides 'Confirm' and 'Cancel' buttons to proceed or abort payment.
    """
    def __init__(self, items, total_price, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Payment")
        self.setModal(True)

        # Apply styling for dialog appearance
        self.setStyleSheet("""
            QDialog {
                background-color: #F9F9F9;
                border-radius: 15px;
            }
            QLabel {
                font-size: 30px;
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

        # Scroll area to show list of selected items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Add item labels to the scroll view
        for item in items:
            lbl = QLabel(f"{item['name']} - {item['price']} IRR")
            lbl.setAlignment(Qt.AlignLeft)
            scroll_layout.addWidget(lbl)

        # Display total price
        total_lbl = QLabel(f"\nTotal: {total_price} IRR")
        total_lbl.setAlignment(Qt.AlignLeft)
        scroll_layout.addWidget(total_lbl)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Confirm and cancel buttons
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


class PaymentWorker(QObject):
    """
    Worker class that runs card payment logic in a separate thread.
    Emits status messages during the process and a final result dict.
    """
    status = pyqtSignal(str)       # Signal for status messages
    finished = pyqtSignal(dict)    # Signal for the result of card_reader.charge

    def __init__(self, card_reader, amount):
        super().__init__()
        self.card_reader = card_reader
        self.amount = amount

    def run(self):
        """Execute the payment process."""
        self.status.emit("Processing payment...")
        result = self.card_reader.charge(self.amount)
        if isinstance(result, dict):
            self.finished.emit(result)
        else:
            # Wrap unexpected results into a failure dict
            self.finished.emit({"success": False, "message": str(result)})


class DispenseWorker(QObject):
    """
    Worker class for controlling the relay (dispensing mechanism).
    Runs in a separate thread to avoid blocking the UI.
    """
    status = pyqtSignal(str)    # Signal for relay status messages
    finished = pyqtSignal()     # Signal emitted when dispensing completes

    def __init__(self, relay_controller, selected_items):
        super().__init__()
        self.relay_controller = relay_controller
        # Make a copy to avoid race conditions with mutable data
        self.selected_items = [dict(i) for i in selected_items]

    def run(self):
        """Execute the dispensing process via relay controller."""

        def status_callback(msg):
            self.status.emit(msg)

        self.relay_controller.dispense(self.selected_items, status_callback)
        self.finished.emit()


class UserPanel(QWidget):
    """
    Main user interface panel for the vending machine.
    Handles keypad input, item selection, payment, and dispensing.
    """
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

        # Auto-reset after 30 seconds of inactivity
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(30_000)
        self.inactivity_timer.timeout.connect(self.reset_to_initial)
        self.inactivity_timer.start()

        # Thread/worker references (kept alive during execution)
        self._payment_thread = None
        self._payment_worker = None
        self._dispense_thread = None
        self._dispense_worker = None

    def setup_ui(self):
        """Build and configure the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Display label at the top (shows messages and instructions)
        self.display_label = QLabel()
        self.display_label.setObjectName("display_label")
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setWordWrap(True)
        layout.addWidget(self.display_label)

        # Numeric keypad for item entry
        self.keypad_layout = QGridLayout()
        self.keypad_layout.setSpacing(8)

        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('↵', 3, 0), ('0', 3, 1), ('+', 3, 2)
        ]

        # Create keypad buttons and bind events
        for text, row, col in buttons:
            button = QPushButton(text)
            button.setFixedHeight(60)
            if text == '↵':
                button.setStyleSheet("background-color: #FF5252; color: white; font-size: 28px; border-radius: 10px;")
            elif text == '+':
                button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 28px; border-radius: 10px;")
            button.clicked.connect(lambda _, t=text: self.on_keypad_clicked(t))
            self.keypad_layout.addWidget(button, row, col)

        layout.addLayout(self.keypad_layout)

        # Pay button
        button_group_layout = QVBoxLayout()
        button_group_layout.setSpacing(12)

        self.confirm_pay_btn = QPushButton("Pay")
        self.confirm_pay_btn.setObjectName("action_button")
        self.confirm_pay_btn.setFixedHeight(90)
        self.confirm_pay_btn.setStyleSheet(
            "background-color: #FFA726; color: white; border-radius: 10px; font-size: 22px;")
        self.confirm_pay_btn.clicked.connect(self.on_confirm_pay)
        button_group_layout.addWidget(self.confirm_pay_btn)

        layout.addLayout(button_group_layout)

        # Admin button row
        admin_row = QHBoxLayout()
        admin_row.addStretch()
        self.admin_btn = QPushButton("⚙️")
        self.admin_btn.setObjectName("admin_button")
        self.admin_btn.setFixedHeight(60)
        self.admin_btn.setFixedWidth(60)
        self.admin_btn.setStyleSheet(
            "background-color: #7ED6DF; color: #222; border-radius: 40px; font-size: 28px; margin: 50px;")
        self.admin_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.admin_login))
        admin_row.addWidget(self.admin_btn)
        layout.addLayout(admin_row)

        self.setLayout(layout)
        self.set_initial_display()

    def set_initial_display(self):
        """Reset display to the initial 'READY' state."""
        self.display_label.setText(
            '<div style="font-size:32px;">'
            'READY<br>'
            '<span style="font-size:24px;">Enter the desired item number.</span>'
            '</div>'
        )
        self.confirm_pay_btn.setText("Pay")

    def reset_to_initial(self):
        """Reset the state and display due to inactivity or user action."""
        self.selected_items = []
        self.total_price = 0
        self.current_input = ""
        self.set_initial_display()

    def load_items(self):
        """Load item database (JSON) from the file defined in parent."""
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
        """Return item information by item code."""
        return self.items.get(str(code), None)

    def on_keypad_clicked(self, text):
        """
        Handle keypad button presses.
        Supports item number entry, add (+), and remove (↵).
        """
        self.inactivity_timer.start()

        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return

        if text == '↵':
            # Handle 'enter' / remove functionality
            if self.current_input:
                self.current_input = ""
                if self.selected_items:
                    self.update_selection_display()
                else:
                    self.set_initial_display()
            elif self.selected_items:
                removed_item = self.selected_items.pop()
                self.total_price -= removed_item['price']
                if self.selected_items:
                    self.update_selection_display()
                else:
                    self.set_initial_display()
            else:
                self.set_initial_display()
            return

        if text == '+':
            # Handle item selection
            if not self.current_input:
                self.display_label.setText(
                    '<div style="font-size:32px;">'
                    'READY<br>'
                    '<span style="font-size:24px;">Enter the desired item number.</span>'
                    '</div>'
                )
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
            return

        if text.isdigit():
            # Append digit to current input
            self.current_input += text
            self.display_label.setText(f"Press the + button to select the item {self.current_input}.")

    def update_selection_display(self):
        """Update the display to show selected items and instructions."""
        if not self.selected_items:
            self.display_label.setText('<div style="font-size:20px;">No items available yet.</div>')
            self.set_initial_display()
            return

        selected_display = ""
        for i in self.selected_items:
            selected_display += (
                f"<div style='font-size:24px;'><b>{i['name']}</b> - {i['price']} IRR</div>"
            )

        instructions = (
            "<div style='font-size:20px; color:#555; margin-top:8px;'>"
            "To add another item, press <b>+</b>.<br>"
            "To remove an item, press <b>↵</b>.<br>"
            "Or complete the payment."
            "</div>"
        )
        self.display_label.setText(f"{selected_display}{instructions}")
        self.confirm_pay_btn.setText(f"Pay (Total: {self.total_price} IRR)")

    def on_confirm_pay(self):
        """Handle Pay button press and show confirmation dialog."""
        self.inactivity_timer.start()

        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return

        if not self.selected_items:
            self.display_label.setText(
                '<div style="font-size:24px;">'
                'Enter the item number you want and press the <b>+</b> button'
                '</div>'
            )
            return

        invalid_items = [
            item["code"] for item in self.selected_items
            if not self.item_lookup(item["code"]) or not self.item_lookup(item["code"]).get('name')
        ]
        if invalid_items:
            self.display_label.setText(f"Items {', '.join(invalid_items)} not available")
            return

        dlg = ConfirmDialog(self.selected_items, self.total_price, self)
        if dlg.exec_() == QDialog.Accepted:
            self.display_label.setText(f"Proceeding to payment\nTotal: {self.total_price} IRR")
            self.process_payment()
        else:
            self.selected_items = []
            self.total_price = 0
            self.current_input = ""
            self.set_initial_display()

    def process_payment(self):
        """Start payment in a worker thread and update UI via signals."""
        self.confirm_pay_btn.setEnabled(False)

        # Create worker and thread
        self._payment_worker = PaymentWorker(self.card_reader, self.total_price)
        self._payment_thread = QThread()
        self._payment_worker.moveToThread(self._payment_thread)

        # Connect signals
        self._payment_thread.started.connect(self._payment_worker.run)
        self._payment_worker.status.connect(lambda msg: self.display_label.setText(msg))
        self._payment_worker.finished.connect(self._on_payment_finished)

        # Ensure cleanup when done
        def _cleanup_payment():
            if self._payment_thread:
                self._payment_thread.quit()
                self._payment_thread.wait()
            self._payment_worker = None
            self._payment_thread = None

        self._payment_worker.finished.connect(_cleanup_payment)
        self._payment_thread.start()

    def _on_payment_finished(self, result):
        """Handle result from PaymentWorker."""
        msg = result.get("message", "")
        if msg:
            self.display_label.setText(msg)
        self.handle_payment_result(result)

    def handle_payment_result(self, result):
        """Process payment outcome and proceed accordingly."""
        if result.get("success"):
            self.display_label.setText("Payment successful\nPreparing to dispense items...")
            self.start_dispensing()
        else:
            self.display_label.setText("Payment failed\nPlease try again")
            self.confirm_pay_btn.setEnabled(True)

    def start_dispensing(self):
        """Start dispensing in a worker thread and stream status updates."""
        self.confirm_pay_btn.setEnabled(False)

        self._dispense_worker = DispenseWorker(self.relay_controller, self.selected_items)
        self._dispense_thread = QThread()
        self._dispense_worker.moveToThread(self._dispense_thread)

        self._dispense_thread.started.connect(self._dispense_worker.run)
        self._dispense_worker.status.connect(lambda msg: self.display_label.setText(msg))
        self._dispense_worker.finished.connect(self._on_dispense_finished)

        def _cleanup_dispense():
            if self._dispense_thread:
                self._dispense_thread.quit()
                self._dispense_thread.wait()
            self._dispense_worker = None
            self._dispense_thread = None

        self._dispense_worker.finished.connect(_cleanup_dispense)
        self._dispense_thread.start()

    def _on_dispense_finished(self):
        """Reset state after dispensing finishes successfully."""
        self.display_label.setText("All items were successfully dispensed")
        self.selected_items = []
        self.total_price = 0
        self.current_input = ""
        self.set_initial_display()
        self.confirm_pay_btn.setText("Pay")
        self.confirm_pay_btn.setEnabled(True)
