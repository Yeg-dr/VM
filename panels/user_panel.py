from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer

class UserPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Display label
        self.display_label = QLabel("Ready")
        self.display_label.setObjectName("display_label")
        self.display_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.display_label)
        
        # Keypad
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
        
        # Action buttons
        self.select_another_btn = QPushButton("Select Another Item")
        self.select_another_btn.setObjectName("action_button")
        self.select_another_btn.clicked.connect(self.on_select_another)
        layout.addWidget(self.select_another_btn)
        
        self.confirm_pay_btn = QPushButton("Confirm and Pay")
        self.confirm_pay_btn.setObjectName("action_button")
        self.confirm_pay_btn.clicked.connect(self.on_confirm_pay)
        layout.addWidget(self.confirm_pay_btn)
        
        # Admin button
        self.admin_btn = QPushButton("Admin")
        self.admin_btn.setObjectName("admin_button")
        self.admin_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.admin_login))
        layout.addWidget(self.admin_btn)
    
    def on_keypad_clicked(self, text):
        if text == 'C':
            self.parent.current_input = ""
            self.display_label.setText("Ready")
        elif text == '↵':
            self.process_item_selection()
        else:
            self.parent.current_input += text
            self.display_label.setText(self.parent.current_input)
    
    def process_item_selection(self):
        if not self.parent.current_input:
            return
            
        if self.parent.current_input in self.parent.items:
            item = self.parent.items[self.parent.current_input]
            self.display_label.setText(f"{item['name']} - {item['price']}")
            self.parent.selected_items.append({
                "code": self.parent.current_input,
                "name": item["name"],
                "price": item["price"]
            })
            self.parent.total_price += item["price"]
            self.parent.current_input = ""
        else:
            self.display_label.setText("Invalid item")
            self.parent.current_input = ""
            QTimer.singleShot(2000, lambda: self.display_label.setText("Ready"))
    
    def on_select_another(self):
        self.parent.current_input = ""
        self.display_label.setText("Ready")
    
    def on_confirm_pay(self):
        if not self.parent.selected_items:
            self.display_label.setText("No items selected")
            QTimer.singleShot(2000, lambda: self.display_label.setText("Ready"))
            return
            
        # Show summary
        items_list = "\n".join([f"{item['name']} - {item['price']}" for item in self.parent.selected_items])
        self.display_label.setText(f"Total: {self.parent.total_price}\nPlease pay")
        
        # Simulate card payment
        QTimer.singleShot(2000, self.process_payment)
    
    def process_payment(self):
        self.display_label.setText("Processing payment...")
        QTimer.singleShot(2000, self.payment_successful)
    
    def payment_successful(self):
        self.display_label.setText("Payment successful.\nDispensing item(s)...")
        
        # Simulate relay control
        locations = [self.parent.items[item["code"]]["location"] for item in self.parent.selected_items]
        print(f"Sending to relay module: {locations}")
        
        QTimer.singleShot(1500, self.dispense_complete)
    
    def dispense_complete(self):
        self.display_label.setText("Item(s) delivered successfully.")
        self.parent.selected_items = []
        self.parent.total_price = 0
        self.parent.current_input = ""
        QTimer.singleShot(3000, lambda: self.display_label.setText("Ready"))