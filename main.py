import sys
from PyQt5.QtWidgets import QApplication
from app import VendingMachineApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set font for better readability
    font = app.font()
    font.setPointSize(12)
    app.setFont(font)
    
    window = VendingMachineApp()
    window.show()
    
    sys.exit(app.exec_())