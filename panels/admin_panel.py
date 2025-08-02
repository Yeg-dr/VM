from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QGridLayout, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QTimer

class AdminPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Admin Panel")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px;")
        layout.addWidget(title)
        
        # Item input display
        self.admin_item_display = QLabel("")
        self.admin_item_display.setObjectName("display_label")
        self.admin_item_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.admin_item_display)
        
        # Keypad
        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(10)
        
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
            keypad_layout.addWidget(button, row, col)
        
        layout.addLayout(keypad_layout)
        
        # Admin action buttons
        btn_layout = QHBoxLayout()
        
        self.edit_item_btn = QPushButton("Edit Item")
        self.edit_item_btn.setObjectName("action_button")
        self.edit_item_btn.clicked.connect(self.on_edit_item)
        btn_layout.addWidget(self.edit_item_btn)
        
        self.back_to_user_btn = QPushButton("User Panel")
        self.back_to_user_btn.setObjectName("admin_button")
        self.back_to_user_btn.clicked.connect(
            lambda: self.parent.switch_screen(self.parent.user_panel))
        btn_layout.addWidget(self.back_to_user_btn)
        
        self.exit_app_btn = QPushButton("Exit")
        self.exit_app_btn.setStyleSheet("background-color: #FF5252;")
        self.exit_app_btn.clicked.connect(self.parent.close)
        btn_layout.addWidget(self.exit_app_btn)
        
        layout.addLayout(btn_layout)
    
    def on_keypad_clicked(self, text):
        if text == 'C':
            self.parent.current_input = ""
            self.admin_item_display.setText("")
        elif text == '↵':
            self.admin_item_display.setText(self.parent.current_input)
            self.parent.current_input = ""
        else:
            self.parent.current_input += text
            self.admin_item_display.setText(self.parent.current_input)
    
    def on_edit_item(self):
        item_code = self.admin_item_display.text()
        if item_code in self.parent.items and item_code != "admin_password":
            self.parent.current_edit_item = item_code
            self.parent.edit_panel.item_code_display.setText(item_code)
            self.parent.edit_panel.name_edit.setText(self.parent.items[item_code]["name"])
            self.parent.edit_panel.price_edit.setText(str(self.parent.items[item_code]["price"]))
            self.parent.edit_panel.location_edit.setText(self.parent.items[item_code]["location"])
            self.parent.switch_screen(self.parent.edit_panel)
        else:
            self.admin_item_display.setText("Invalid item")
            QTimer.singleShot(2000, lambda: self.admin_item_display.setText(""))