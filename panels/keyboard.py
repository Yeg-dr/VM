from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class Keyboard(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.target = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Keyboard rows
        rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '.', '-', '@'],
            ['Space', 'Backspace', 'Done']
        ]
        
        for row in rows:
            h_layout = QHBoxLayout()
            h_layout.setSpacing(5)
            for key in row:
                btn = QPushButton(key)
                btn.setFixedHeight(60)
                if key in ['Space', 'Backspace', 'Done']:
                    if key == 'Done':
                        btn.setObjectName("action_button")
                    elif key == 'Backspace':
                        btn.setStyleSheet("background-color: #FF5252;")
                else:
                    btn.setFixedWidth(40)
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