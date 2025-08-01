from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui

class EditPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Title
        self.edit_title = QLabel("Edit Item")
        self.edit_title.setAlignment(Qt.AlignCenter)
        self.edit_title.setStyleSheet("font-size: 32px;")
        layout.addWidget(self.edit_title)
        
        # Item code display
        self.item_code_display = QLabel("")
        self.item_code_display.setObjectName("display_label")
        self.item_code_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.item_code_display)
        
        # Name field
        self.name_label = QLabel("Item Name:")
        layout.addWidget(self.name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        self.name_edit.mousePressEvent = self.show_keyboard
        layout.addWidget(self.name_edit)
        
        # Price field
        self.price_label = QLabel("Price:")
        layout.addWidget(self.price_label)
        
        self.price_edit = QLineEdit()
        self.price_edit.setValidator(QtGui.QIntValidator(0, 999999))
        layout.addWidget(self.price_edit)
        
        # Location field
        self.location_label = QLabel("Location:")
        layout.addWidget(self.location_label)
        
        self.location_edit = QLineEdit()
        layout.addWidget(self.location_edit)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("action_button")
        self.save_btn.clicked.connect(self.on_save_item)
        btn_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background-color: #FF5252;")
        self.delete_btn.clicked.connect(self.on_delete_item)
        btn_layout.addWidget(self.delete_btn)
        
        self.back_to_admin_btn = QPushButton("Back")
        self.back_to_admin_btn.setObjectName("admin_button")
        self.back_to_admin_btn.clicked.connect(
            lambda: self.parent.switch_screen(self.parent.admin_panel))
        btn_layout.addWidget(self.back_to_admin_btn)
        
        layout.addLayout(btn_layout)
    
    def show_keyboard(self, event):
        self.parent.keyboard.target = self.name_edit
        self.parent.switch_screen(self.parent.keyboard)
    
    def on_save_item(self):
        reply = QMessageBox.question(
            self, 'Confirm', 'Are you sure you want to save this item?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            item_code = self.item_code_display.text()
            self.parent.items[item_code] = {
                "name": self.name_edit.text(),
                "price": int(self.price_edit.text()),
                "location": self.location_edit.text()
            }
            self.parent.save_items()
            self.parent.switch_screen(self.parent.admin_panel)
    
    def on_delete_item(self):
        reply = QMessageBox.question(
            self, 'Confirm', 'Are you sure you want to delete this item?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            item_code = self.item_code_display.text()
            if item_code in self.parent.items:
                del self.parent.items[item_code]
                self.parent.save_items()
            self.parent.switch_screen(self.parent.admin_panel)