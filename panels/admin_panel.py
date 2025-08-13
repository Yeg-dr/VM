from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QGridLayout, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt

class AdminPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
        self.parent.current_input = ""
        self.admin_item_display.setText("")
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        title = QLabel("Admin Panel")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            font-family: Arial;
        """)
        layout.addWidget(title)
        
        instruction = QLabel("Enter the desired item number (1-32)")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("font-size: 20px; color: #666666;")
        layout.addWidget(instruction)
        
        self.admin_item_display = QLabel("")
        self.admin_item_display.setObjectName("display_label")
        self.admin_item_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.admin_item_display)
        
        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(10)
        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('C', 3, 0), ('0', 3, 1), ('Enter', 3, 2)
        ]
        for text, row, col in buttons:
            button = QPushButton(text)
            button.setFixedHeight(80)
            if text == 'C':
                button.setStyleSheet("background-color: #FF5252;")
            elif text == 'Enter':
                button.setObjectName("action_button")
            button.clicked.connect(lambda _, t=text: self.on_keypad_clicked(t))
            keypad_layout.addWidget(button, row, col)
        layout.addLayout(keypad_layout)
        
        btn_layout = QHBoxLayout()
        self.back_to_user_btn = QPushButton("User Panel")
        self.back_to_user_btn.setObjectName("admin_button")
        self.back_to_user_btn.clicked.connect(
            lambda: self.parent.switch_screen(self.parent.user_panel))
        btn_layout.addWidget(self.back_to_user_btn)
        
        self.exit_app_btn = QPushButton("Exit")
        self.exit_app_btn.setStyleSheet("background-color: #FF5252;")
        self.exit_app_btn.clicked.connect(self.parent.close)
        btn_layout.addWidget(self.exit_app_btn)

        self.change_password_btn = QPushButton("Change Password")
        self.change_password_btn.setObjectName("admin_button")
        self.change_password_btn.clicked.connect(self.on_change_password_clicked)
        btn_layout.addWidget(self.change_password_btn)

        self.show_items_btn = QPushButton("Show Items")
        self.show_items_btn.setObjectName("admin_button")
        self.show_items_btn.clicked.connect(self.on_show_items_clicked)
        btn_layout.addWidget(self.show_items_btn)

        layout.addLayout(btn_layout)
    
    def on_keypad_clicked(self, text):
        if text == 'C':
            self.parent.current_input = ""
            self.admin_item_display.setText("")
        elif text == 'Enter':
            if not self.parent.current_input:
                return
            try:
                item_code = int(self.parent.current_input)
                if item_code < 1 or item_code > 32:
                    QMessageBox.warning(self, "Invalid Input", "Please enter a number between 1 and 32.")
                    self.parent.current_input = ""
                    self.admin_item_display.setText("")
                    return
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
                self.parent.current_input = ""
                self.admin_item_display.setText("")
                return
            item_code_str = self.parent.current_input
            self.parent.current_edit_item = item_code_str
            self.parent.edit_panel.item_code_display.setText(item_code_str)
            self.parent.edit_panel.load_item_data(item_code_str)
            self.parent.switch_screen(self.parent.edit_panel)
            self.parent.current_input = ""
        else:
            if len(self.parent.current_input) >= 2:
                return
            self.parent.current_input += text
            self.admin_item_display.setText(self.parent.current_input)

    def on_change_password_clicked(self):
        self.parent.switch_screen(self.parent.change_password_panel)

    def on_show_items_clicked(self):
        self.parent.items_list_panel.load_items()
        self.parent.switch_screen(self.parent.items_list_panel)