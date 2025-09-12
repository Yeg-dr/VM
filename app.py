import json
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from panels.user_panel import UserPanel
from panels.admin_login import AdminLogin
from panels.admin_panel import AdminPanel
from panels.edit_panel import EditPanel
from panels.keyboard import Keyboard
from panels.change_password_panel import ChangePasswordPanel
from panels.items_list_panel import ItemsListPanel

class VendingMachineApp(QMainWindow):
    def __init__(self):
        """
        Main application class for the vending machine interface.
        Handles initialization of items, panels, and global application state.
        """
        super().__init__()
        self.items_file = "vending_items.json"
        self.load_items()
        self.current_input = ""
        self.selected_items = []
        self.total_price = 0

        # Initialize all panels after loading item data
        self.user_panel = UserPanel(self)
        self.admin_login = AdminLogin(self)
        self.admin_panel = AdminPanel(self)
        self.edit_panel = EditPanel(self)
        self.keyboard = Keyboard(self)
        self.change_password_panel = ChangePasswordPanel(self, items_file=self.items_file)
        self.items_list_panel = ItemsListPanel(self, items_file=self.items_file)

        self.setup_ui()
        
    def setup_ui(self):
        """
        Configure the main window and set up the stacked widget layout
        containing all panels.
        """
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setFixedSize(480, 770)
        
        # Configure central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Create stacked widget for panel navigation
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Add all panels to the stacked widget
        self.stacked_widget.addWidget(self.user_panel)
        self.stacked_widget.addWidget(self.admin_login)
        self.stacked_widget.addWidget(self.admin_panel)
        self.stacked_widget.addWidget(self.edit_panel)
        self.stacked_widget.addWidget(self.keyboard)
        self.stacked_widget.addWidget(self.change_password_panel)
        self.stacked_widget.addWidget(self.items_list_panel)
        
        # Set initial screen to user panel
        self.stacked_widget.setCurrentWidget(self.user_panel)
        
        # Apply global stylesheet
        self.apply_styles()
    
    def apply_styles(self):
        """
        Apply application-wide stylesheet for consistent UI appearance.
        """
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
        """
        Load vending machine items from a JSON file. If the file does not exist,
        create a default set of items including the admin password.
        """
        self.items_file = "vending_items.json"
        try:
            if os.path.exists(self.items_file):
                with open(self.items_file, 'r') as f:
                    self.items = json.load(f)
            else:
                # Initialize default items if file is missing
                self.items = {"admin_password": "1234"}
                rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
                for i in range(1, 33):
                    row = rows[(i-1)//4]
                    col = (i-1)%4 + 1
                    self.items[str(i)] = {
                        "name": "",
                        "price": 0,
                        "location": f"{row}{col}"
                    }
                self.save_items()
        except Exception as e:
            print(f"Error loading items: {str(e)}")
            self.items = {}
    
    def save_items(self):
        """
        Save vending machine items to the JSON file.
        """
        try:
            with open(self.items_file, 'w') as f:
                json.dump(self.items, f, indent=4)
        except Exception as e:
            print(f"Failed to save items: {str(e)}")
    
    def switch_screen(self, screen):
        """
        Switch the current displayed panel to the provided screen.
        """
        self.stacked_widget.setCurrentWidget(screen)
