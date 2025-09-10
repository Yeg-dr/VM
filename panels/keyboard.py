from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLineEdit)
from PyQt5.QtCore import Qt

class Keyboard(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.target = None
        self.caps_lock = False
        self.setup_ui()
    
    def setup_ui(self):
        screen_width = 480
        screen_height = 800
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Display box
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                padding: 10px;
                border: 1px solid #aaa;
                min-height: 60px;
                background: white;
            }
        """)
        main_layout.addWidget(self.display)
        
        # Keyboard layout
        keyboard_layout = QVBoxLayout()
        keyboard_layout.setContentsMargins(0, 0, 0, 0)
        keyboard_layout.setSpacing(8)
        
        # Blue button style like keypad
        base_style = """
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                min-width: 30px;
                min-height: 50px;
                padding: 0px;
                margin: 0;
                border: 1px solid #4A90E2;
                background: #4A90E2;
                color: white;
                border-radius: 6px;
            }
            QPushButton:pressed {
                background: #3A70C2;
            }
        """
        
        # Special button style
        special_style = base_style.replace("#4A90E2", "#357ABD")
        
        # Regular keys rows - now with lowercase
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ':'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '-', ','],  
        ]
        
        max_keys_per_row = max(len(row) for row in rows)
        key_width = (screen_width - 20 - ((max_keys_per_row - 1) * 5)) / max_keys_per_row
        row_height = 60
        
        for row in rows:
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(5)
            
            for key in row:
                btn = QPushButton(key)
                btn.setFixedHeight(row_height)
                btn.setFixedWidth(int(key_width))
                btn.setStyleSheet(base_style)
                
                btn.clicked.connect(lambda _, k=key: self.on_key_pressed(k))
                h_layout.addWidget(btn)
            
            keyboard_layout.addLayout(h_layout)
        
        # ردیف آخر با دکمه Caps، Space و ↵
        last_row_layout = QHBoxLayout()
        last_row_layout.setContentsMargins(0, 0, 0, 0)
        last_row_layout.setSpacing(5)
        
        # دکمه Caps (سمت چپ)
        caps_btn = QPushButton('Caps')
        caps_btn.setFixedHeight(row_height)
        caps_btn.setFixedWidth(int(key_width * 1.5))  # عرض کمی بیشتر از دکمه‌های معمولی
        caps_btn.setStyleSheet(special_style)
        caps_btn.clicked.connect(lambda: self.on_key_pressed('Caps'))
        last_row_layout.addWidget(caps_btn)
        
        # دکمه Space (کل عرض باقیمانده)
        space_btn = QPushButton('⎼⎼')
        space_btn.setFixedHeight(row_height)
        space_btn.setStyleSheet(base_style)
        space_btn.clicked.connect(lambda: self.on_key_pressed('⎼⎼'))
        last_row_layout.addWidget(space_btn, 1)  # ضریب انبساط 1 برای پر کردن فضای باقیمانده
        
        # دکمه ↵ (سمت راست - هم اندازه Caps)
        backspace_btn = QPushButton('↵')
        backspace_btn.setFixedHeight(row_height)
        backspace_btn.setFixedWidth(int(key_width * 1.5))  # هم اندازه Caps
        backspace_btn.setStyleSheet(special_style)
        backspace_btn.clicked.connect(lambda: self.on_key_pressed('↵'))
        last_row_layout.addWidget(backspace_btn)
        
        keyboard_layout.addLayout(last_row_layout)
        
        # Add Done button as a separate full-width row
        done_layout = QHBoxLayout()
        done_layout.setContentsMargins(0, 0, 0, 0)
        done_btn = QPushButton('Done')
        done_btn.setFixedHeight(row_height)
        done_btn.setFixedWidth(screen_width - 20)  # Full width
        done_btn.setStyleSheet(base_style.replace("#4A90E2", "#FFA726").replace("#3A70C2", "#E09726"))
        done_btn.clicked.connect(lambda: self.on_key_pressed('Done'))
        done_layout.addWidget(done_btn)
        
        keyboard_layout.addLayout(done_layout)
        main_layout.addLayout(keyboard_layout)
    
    def toggle_case(self):
        """Toggle between uppercase and lowercase"""
        self.caps_lock = not self.caps_lock
        self.update_keyboard_layout()
    
    def update_keyboard_layout(self):
        """Update the keyboard layout based on current case state"""
        for layout in self.findChildren(QHBoxLayout):
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    text = widget.text()
                    if text.isalpha() and len(text) == 1:
                        if self.caps_lock:
                            widget.setText(text.upper())
                        else:
                            widget.setText(text.lower())
    
    def on_key_pressed(self, key):
        current_text = self.display.text()
        
        if key == '⎼⎼':
            new_text = current_text + " "
        elif key == '↵':
            new_text = current_text[:-1]
        elif key == 'Done':
            if self.target:
                self.target.setText(current_text)
            self.display.clear()
            self.parent.switch_screen(self.parent.edit_panel)
            # Reset keyboard state
            self.caps_lock = False
            self.update_keyboard_layout()
            return
        elif key == 'Caps':
            self.toggle_case()
            return
        else:
            # Add the character (respecting case)
            new_text = current_text + key
        
        self.display.setText(new_text)
        if self.target:
            self.target.setText(new_text)