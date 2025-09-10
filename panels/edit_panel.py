import json
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title and item number display
        self.edit_title = QLabel("Edit Item")
        self.edit_title.setAlignment(Qt.AlignCenter)
        self.edit_title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            font-family: Arial;
            color: #333333;
            margin-bottom: 10px;
        """)
        layout.addWidget(self.edit_title)
        
        self.item_code_display = QLabel("")
        self.item_code_display.setAlignment(Qt.AlignCenter)
        self.item_code_display.setStyleSheet("""
            font-size: 50px;
            font-weight: bold;
            color: #4A90E2;
            margin-bottom: 20px;
        """)
        layout.addWidget(self.item_code_display)
        
        # Name field
        self.name_label = QLabel("Item Name:")
        layout.addWidget(self.name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)  
        self.name_edit.mousePressEvent = lambda event: self.show_keyboard(self.name_edit)
        layout.addWidget(self.name_edit)
        
        # Price field
        self.price_label = QLabel("Price:")
        layout.addWidget(self.price_label)
        
        self.price_edit = QLineEdit()
        self.price_edit.setReadOnly(True)  
        self.price_edit.setValidator(QtGui.QIntValidator(0, 999999999))
        self.price_edit.mousePressEvent = lambda event: self.show_keyboard(self.price_edit)
        layout.addWidget(self.price_edit)
        
        # Simple location display (read-only)
        self.location_label = QLabel("Location:")
        layout.addWidget(self.location_label)
        
        self.location_display = QLabel("")
        self.location_display.setAlignment(Qt.AlignCenter)
        self.location_display.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #7ED6DF;
            margin-bottom: 15px;
        """)
        layout.addWidget(self.location_display)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.back_to_admin_btn = QPushButton("Back")
        self.back_to_admin_btn.setObjectName("admin_button")
        self.back_to_admin_btn.clicked.connect(
            lambda: self.parent.switch_screen(self.parent.admin_panel))
        btn_layout.addWidget(self.back_to_admin_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background-color: #FF5252;")
        self.delete_btn.clicked.connect(self.on_delete_item)
        btn_layout.addWidget(self.delete_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("action_button")
        self.save_btn.clicked.connect(self.on_save_item)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def update_location_display(self, location_code):
        if location_code and len(location_code) == 2:
            self.location_display.setText(location_code)
        else:
            self.location_display.setText("")

    def show_keyboard(self, target_field):
        self.parent.keyboard.target = target_field
        self.parent.switch_screen(self.parent.keyboard)
    
    def load_item_data(self, item_code):
        try:
            with open(self.parent.items_file, 'r', encoding='utf-8') as f:
                items = json.load(f)
            
            self.item_code_display.setText(item_code)  # مهم برای ذخیره‌سازی
            
            if item_code in items:
                item = items[item_code]
                self.name_edit.setText(item["name"])
                self.price_edit.setText(str(item["price"]))
                self.update_location_display(item["location"])
            else:
                self.name_edit.setText("")
                self.price_edit.setText("")
                self.update_location_display("")
        except Exception as e:
            print(f"Error loading item data: {e}")
            self.item_code_display.setText("")
            self.name_edit.setText("")
            self.price_edit.setText("")
            self.update_location_display("")
    
    def on_save_item(self):
        reply = QMessageBox.question(
            self, 'Confirm', 'Are you sure you want to save this item?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            item_code = self.item_code_display.text()
            try:
                with open(self.parent.items_file, 'r') as f:
                    items = json.load(f)
                
                if item_code not in items:
                    QMessageBox.warning(self, "Error", "Invalid item code")
                    return
                
                # فقط اسم و قیمت تغییر می‌کنند
                items[item_code]["name"] = self.name_edit.text()
                price_str = self.price_edit.text()
                try:
                    price = int(price_str)
                except ValueError:
                    price = 0
                items[item_code]["price"] = price
                
                with open(self.parent.items_file, 'w') as f:
                    json.dump(items, f, indent=4)

                self.parent.load_items()
                self.parent.switch_screen(self.parent.admin_panel)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save item: {str(e)}")
    
    def on_delete_item(self):
        reply = QMessageBox.question(
            self, 'Confirm', 'Are you sure you want to clear this item?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            item_code = self.item_code_display.text()
            try:
                with open(self.parent.items_file, 'r') as f:
                    items = json.load(f)
                
                if item_code in items:
                    # فقط name و price رو ریست کن، location رو نگه دار
                    items[item_code]["name"] = ""
                    items[item_code]["price"] = 0
                    
                    with open(self.parent.items_file, 'w') as f:
                        json.dump(items, f, indent=4)

                self.parent.load_items()
                self.parent.switch_screen(self.parent.admin_panel)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to clear item: {str(e)}")
