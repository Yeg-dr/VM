from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer

class AdminLogin(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """
        Initialize the user interface for the admin login panel.
        This includes title, password display, keypad, and navigation button.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Title label
        title = QLabel("Please enter password")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            font-family: Arial;
        """)
        layout.addWidget(title)
        
        # Label to display masked password input
        self.password_display = QLabel("")
        self.password_display.setObjectName("display_label")
        self.password_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.password_display)
        
        # Numeric keypad layout
        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(10)
        
        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('C', 3, 0), ('0', 3, 1), ('Enter', 3, 2)
        ]
        
        # Create keypad buttons dynamically
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
        
        # Back navigation button to user panel
        back_btn = QPushButton("Back to User Panel")
        back_btn.setObjectName("admin_button")
        back_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.user_panel))
        layout.addWidget(back_btn)
    
    def on_keypad_clicked(self, text):
        """
        Handle keypad button clicks:
        - 'C' clears the current input
        - 'Enter' triggers password validation
        - Digits are appended to the current password input
        """
        if text == 'C':
            self.parent.current_input = ""
            self.password_display.setText("")
        elif text == 'Enter':
            self.check_admin_password()
        else:
            self.parent.current_input += text
            self.password_display.setText("*" * len(self.parent.current_input))
    
    def check_admin_password(self):
        """
        Validate the entered password against the stored admin password.
        On success: switch to the admin panel.
        On failure: display error and reset input after 2 seconds.
        """
        try:
            password = self.parent.items.get("admin_password", "1234")
        except Exception as e:
            self.password_display.setText("Fatal error: Items DB missing/corrupt")
            self.setDisabled(True)
            return
        
        if self.parent.current_input == self.parent.items.get("admin_password", "1234"):
            self.parent.current_input = ""
            self.password_display.setText("")
            self.parent.switch_screen(self.parent.admin_panel)
        else:
            self.password_display.setText("Wrong password")
            self.parent.current_input = ""
            QTimer.singleShot(2000, lambda: self.password_display.setText(""))
