from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class Keyboard(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.target = None
        self.setup_ui()
    
    def setup_ui(self):
        # Assuming Waveshare with 800x480 resolution
        screen_width = 800
        screen_height = 480
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)  # Comfortable margins
        layout.setSpacing(8)  # Space between rows

        button_style = """
            QPushButton {
                font-size: 24px;
                font-weight: bold;
                min-width: 40px;
                min-height: 60px;
                padding: 5px;
                margin: 2px;
                border-radius: 5px;
            }
            QPushButton#action_button {
                background-color: #4CAF50;
                color: white;
            }
        """
        
        # Keyboard layout including numbers and letters
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '.', '-', '@'],
            ['Space', 'Backspace', 'Done']
        ]
        
        # Calculate row height with better proportions
        row_height = int((screen_height - 30 - (len(rows) * 8)) / len(rows))  # Account for margins and spacing
        
        for row in rows:
            h_layout = QHBoxLayout()
            h_layout.setSpacing(6)  # Space between buttons
            
            # Calculate available width accounting for spacing
            available_width = screen_width - 30 - (len(row) * 6)
            btn_width = available_width / len(row)
            
            for key in row:
                btn = QPushButton(key)
                btn.setStyleSheet(button_style)
                btn.setFixedHeight(row_height)
                
                if key == 'Space':
                    btn.setFixedWidth(int(btn_width * 3.5))
                elif key in ['Backspace', 'Done']:
                    btn.setFixedWidth(int(btn_width * 1.8))
                    if key == 'Done':
                        btn.setObjectName("action_button")
                    elif key == 'Backspace':
                        btn.setStyleSheet(button_style + "background-color: #FF5252; color: white;")
                else:
                    btn.setFixedWidth(int(btn_width * 0.95))  # Slightly less than full width for spacing
                
                btn.clicked.connect(lambda _, k=key: self.on_key_pressed(k))
                h_layout.addWidget(btn)
            
            layout.addLayout(h_layout)
    
    def on_key_pressed(self, key):
        if not self.target:
            return
            
        if key == 'Space':
            self.target.setText(self.target.text() + " ")
        elif key == 'Backspace':
            self.target.setText(self.target.text()[:-1])
        elif key == 'Done':
            self.parent.switch_screen(self.parent.edit_panel)
        else:
            self.target.setText(self.target.text() + key)