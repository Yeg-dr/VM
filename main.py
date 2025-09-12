"""
Main entry point for the Vending Machine application.

This script initializes the PyQt5 application, applies global font settings,
and launches the main window (`VendingMachineApp`).
"""

import sys
from PyQt5.QtWidgets import QApplication
from app import VendingMachineApp


if __name__ == "__main__":
    # Create the Qt application object
    app = QApplication(sys.argv)

    # Set a default application-wide font size
    font = app.font()
    font.setPointSize(12)
    app.setFont(font)
    
    # Initialize and show the main application window
    window = VendingMachineApp()
    window.show()
    
    # Start the Qt event loop and exit cleanly
    sys.exit(app.exec_())
