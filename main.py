import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from style import dynamic_styles

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 应用全局样式
    app.setStyleSheet(dynamic_styles())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
