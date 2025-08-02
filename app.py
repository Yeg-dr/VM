import json
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from panels.user_panel import UserPanel
from panels.admin_login import AdminLogin
from panels.admin_panel import AdminPanel
from panels.edit_panel import EditPanel
from panels.keyboard import Keyboard

class VendingMachineApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_items()
        self.current_input = ""
        self.selected_items = []
        self.total_price = 0
        
    def setup_ui(self):
        # Main window configuration
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setFixedSize(480, 800)
        
        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Create all panels
        self.user_panel = UserPanel(self)
        self.admin_login = AdminLogin(self)
        self.admin_panel = AdminPanel(self)
        self.edit_panel = EditPanel(self)
        self.keyboard = Keyboard(self)
        
        # Add panels to stacked widget
        self.stacked_widget.addWidget(self.user_panel)
        self.stacked_widget.addWidget(self.admin_login)
        self.stacked_widget.addWidget(self.admin_panel)
        self.stacked_widget.addWidget(self.edit_panel)
        self.stacked_widget.addWidget(self.keyboard)
        
        # Set initial screen
        self.stacked_widget.setCurrentWidget(self.user_panel)
        
        # Apply styles
        self.apply_styles()
    
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F7FA;
            }
            QLabel {
                color: #333333;
                font-size: 24px;
            }
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 10px;
                padding: 15px;
                font-size: 24px;
                border: 2px solid #4A90E2;
            }
            QPushButton:pressed {
                background-color: #3A70C2;
            }
            QPushButton#action_button {
                background-color: #FFA726;
            }
            QPushButton#action_button:pressed {
                background-color: #E09726;
            }
            QPushButton#admin_button {
                background-color: #7ED6DF;
            }
            QPushButton#admin_button:pressed {
                background-color: #6EC6CF;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #CCCCCC;
                border-radius: 10px;
                padding: 15px;
                font-size: 28px;
            }
            #display_label {
                background-color: white;
                border: 2px solid #CCCCCC;
                border-radius: 10px;
                padding: 20px;
                font-size: 32px;
                min-height: 80px;
            }
        """)
    
    def load_items(self):
        self.items_file = "vending_items.json"
        try:
            if os.path.exists(self.items_file):
                with open(self.items_file, 'r') as f:
                    self.items = json.load(f)
            else:
                # Create default items
                self.items = {
                    "11": {"name": "Water", "price": 10000, "location": "A1"},
                    "12": {"name": "Chips", "price": 15000, "location": "A3"},
                    "13": {"name": "Soda", "price": 18000, "location": "B1"},
                    "admin_password": "1234"
                }
                self.save_items()
        except Exception as e:
            print(f"Failed to load items: {str(e)}")
            self.items = {}
    
    def save_items(self):
        try:
            with open(self.items_file, 'w') as f:
                json.dump(self.items, f, indent=4)
        except Exception as e:
            print(f"Failed to save items: {str(e)}")
    
    def switch_screen(self, screen):
        self.stacked_widget.setCurrentWidget(screen)