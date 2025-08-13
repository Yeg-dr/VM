from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLineEdit)
from PyQt5.QtCore import Qt

class Keyboard(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.target = None
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
        
        # Regular keys rows
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '.', '-', '@'],
            ['Backspace', 'Space']  # Only these two in the second last row
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
                
                if key == 'Space':
                    btn.setFixedWidth(int(screen_width - 20))  # Full width
                    btn.setStyleSheet(base_style)
                elif key == 'Backspace':
                    btn.setFixedWidth(int(screen_width - 20))  # Full width
                    btn.setStyleSheet(base_style)
                else:
                    btn.setFixedWidth(int(key_width))
                    btn.setStyleSheet(base_style)
                
                btn.clicked.connect(lambda _, k=key: self.on_key_pressed(k))
                h_layout.addWidget(btn)
            
            keyboard_layout.addLayout(h_layout)
        
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
    
    def on_key_pressed(self, key):
        current_text = self.display.text()
        
        if key == 'Space':
            new_text = current_text + " "
        elif key == 'Backspace':
            new_text = current_text[:-1]
        elif key == 'Done':
            if self.target:
                self.target.setText(current_text)
            self.display.clear()  # Clear the display after submission
            self.parent.switch_screen(self.parent.edit_panel)
            return
        else:
            new_text = current_text + key
        
        self.display.setText(new_text)
        if self.target:
            self.target.setText(new_text)