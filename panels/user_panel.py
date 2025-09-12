from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel,
    QHBoxLayout, QDialog, QDialogButtonBox, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
import json
import os

from mock_card_reader import CardReader
from mock_relay_controller import RelayController


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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for item in items:
            lbl = QLabel(f"{item['name']} - {item['price']} IRR")
            lbl.setAlignment(Qt.AlignLeft)
            scroll_layout.addWidget(lbl)

        total_lbl = QLabel(f"\nTotal: {total_price} IRR")
        total_lbl.setAlignment(Qt.AlignLeft)
        scroll_layout.addWidget(total_lbl)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

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


# Worker for processing payment in a separate thread
class PaymentWorker(QObject):
    status = pyqtSignal(str)       # status messages to display
    finished = pyqtSignal(dict)    # emits the result dict from card_reader.charge

    def __init__(self, card_reader, amount):
        super().__init__()
        self.card_reader = card_reader
        self.amount = amount

    def run(self):
        # Notify UI that payment is being processed
        self.status.emit("Processing payment...")
        # Call synchronous charge() (kept as-is from your module)
        result = self.card_reader.charge(self.amount)
        # Emit final result
        if isinstance(result, dict):
            self.finished.emit(result)
        else:
            # safety: if module returns unexpected, wrap as failure
            self.finished.emit({"success": False, "message": str(result)})


# Worker for dispensing (relay) in a separate thread
class DispenseWorker(QObject):
    status = pyqtSignal(str)    # messages from relay_controller.dispense
    finished = pyqtSignal()     # emitted when dispensing complete

    def __init__(self, relay_controller, selected_items):
        super().__init__()
        self.relay_controller = relay_controller
        # copy list to avoid race conditions if original mutated
        self.selected_items = [dict(i) for i in selected_items]

    def run(self):
        # relay_controller.dispense expects a status_callback; we pass one that emits our signal
        def status_callback(msg):
            # emit status message to main thread
            self.status.emit(msg)

        # This call will run in this worker's thread; relay_controller will call status_callback
        self.relay_controller.dispense(self.selected_items, status_callback)
        # once dispense returns, notify finished
        self.finished.emit()


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

        # Inactivity timer (30 seconds)
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(30_000)
        self.inactivity_timer.timeout.connect(self.reset_to_initial)
        self.inactivity_timer.start()

        # Keep references to threads/workers so they are not GC'd while running
        self._payment_thread = None
        self._payment_worker = None
        self._dispense_thread = None
        self._dispense_worker = None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.display_label = QLabel()
        self.display_label.setObjectName("display_label")
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setWordWrap(True)
        layout.addWidget(self.display_label)

        self.keypad_layout = QGridLayout()
        self.keypad_layout.setSpacing(8)

        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('↵', 3, 0), ('0', 3, 1), ('+', 3, 2)
        ]

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
        self.display_label.setText(
            '<div style="font-size:32px;">'
            'READY<br>'
            '<span style="font-size:24px;">Enter the desired item number.</span>'
            '</div>'
            )

        self.confirm_pay_btn.setText("Pay")

    def reset_to_initial(self):
        self.selected_items = []
        self.total_price = 0
        self.current_input = ""
        self.set_initial_display()

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
        self.inactivity_timer.start()

        if self.json_error:
            self.display_label.setText("Cannot operate: Items DB error")
            return

        if text == '↵':
            if self.current_input:  # اگه کاربر در حال تایپ شماره آیتمه
                self.current_input = ""
                if self.selected_items:
                    self.update_selection_display()
                else:
                    self.set_initial_display()
            elif self.selected_items:  # اگه ورودی خالیه ولی آیتم انتخاب‌شده داریم
                removed_item = self.selected_items.pop()
                self.total_price -= removed_item['price']
                if self.selected_items:
                    self.update_selection_display()
                else:
                    self.set_initial_display()
            else:  # نه ورودی هست نه آیتم
                self.set_initial_display()
            return

        if text == '+':
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
            self.current_input += text
            self.display_label.setText(f"Press the + button to select the item {self.current_input}.")

    def update_selection_display(self):
        if not self.selected_items:
            self.display_label.setText(
                '<div style="font-size:20px;">No items available yet.</div>'
            )
            self.set_initial_display()
            return

        selected_display = ""
        for i in self.selected_items:
            selected_display += (
                f"<div style='font-size:24px;'><b>{i['name']}</b> - {i['price']} IRR</div>"
            )

        instructions = (
            "<div style='font-size:20px; color:#555; margin-top:8px;'>"
            "To add another item, press <b>+</b>.<br>To remove an item, press <b>↵</b>.<br>Or complete the payment."
            "</div>"
        )
        self.display_label.setText(f"{selected_display}{instructions}")

        self.confirm_pay_btn.setText(f"Pay (Total: {self.total_price} IRR)")

    def on_confirm_pay(self):
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
            self.display_label.setText(
                f"Proceeding to payment\nTotal: {self.total_price} IRR"
            )
            self.process_payment()
        else:
            self.selected_items = []
            self.total_price = 0
            self.current_input = ""
            self.set_initial_display()

    def process_payment(self):
        """
        Start payment in a worker thread, update UI via signals.
        """
        # disable the pay button to avoid double clicks
        self.confirm_pay_btn.setEnabled(False)

        # create worker and thread
        self._payment_worker = PaymentWorker(self.card_reader, self.total_price)
        self._payment_thread = QThread()
        self._payment_worker.moveToThread(self._payment_thread)

        # connect signals
        self._payment_thread.started.connect(self._payment_worker.run)
        self._payment_worker.status.connect(lambda msg: self.display_label.setText(msg))
        self._payment_worker.finished.connect(self._on_payment_finished)

        # cleanup when done
        def _cleanup_payment():
            if self._payment_thread:
                self._payment_thread.quit()
                self._payment_thread.wait()
            self._payment_worker = None
            self._payment_thread = None

        self._payment_worker.finished.connect(_cleanup_payment)

        # start thread
        self._payment_thread.start()

    def _on_payment_finished(self, result):
        """
        Handle the result emitted by PaymentWorker (runs in main thread).
        """
        # show the message from result if exists
        msg = result.get("message", "")
        if msg:
            self.display_label.setText(msg)

        self.handle_payment_result(result)

    def handle_payment_result(self, result):
        if result.get("success"):
            # proceed to dispensing phase — show preparing message then start dispensing
            self.display_label.setText("Payment successful\nPreparing to dispense items...")
            self.start_dispensing()
        else:
            # payment failed — enable button and notify user
            self.display_label.setText("Payment failed\nPlease try again")
            self.confirm_pay_btn.setEnabled(True)

    def start_dispensing(self):
        """
        Start dispensing in a worker thread; relay_controller.dispense will call
        the status_callback which we route through the worker.status signal.
        """
        # disable button during dispensing
        self.confirm_pay_btn.setEnabled(False)

        # create worker and thread for dispensing
        self._dispense_worker = DispenseWorker(self.relay_controller, self.selected_items)
        self._dispense_thread = QThread()
        self._dispense_worker.moveToThread(self._dispense_thread)

        # connect lifecycle
        self._dispense_thread.started.connect(self._dispense_worker.run)
        # route status messages to UI
        self._dispense_worker.status.connect(lambda msg: self.display_label.setText(msg))
        # when finished, call dispensing_complete in main thread
        self._dispense_worker.finished.connect(self._on_dispense_finished)

        # cleanup function
        def _cleanup_dispense():
            if self._dispense_thread:
                self._dispense_thread.quit()
                self._dispense_thread.wait()
            self._dispense_worker = None
            self._dispense_thread = None

        self._dispense_worker.finished.connect(_cleanup_dispense)

        # start thread
        self._dispense_thread.start()

    def _on_dispense_finished(self):
        """
        Called when DispenseWorker finishes (in main thread).
        Reset UI and show final message.
        """
        self.display_label.setText("All items were successfully dispensed")
        self.selected_items = []
        self.total_price = 0
        self.current_input = ""
        self.set_initial_display()
        self.confirm_pay_btn.setText("Pay")
        self.confirm_pay_btn.setEnabled(True)