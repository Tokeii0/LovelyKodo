from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QPoint
import style
from .theme_dialog import ThemeDialog

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(32)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        # 左侧控制按钮容器
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)


        # 窗口控制按钮
        self.close_btn = QPushButton()
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()

                # 主题切换按钮
        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(12, 12)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #007AFF, stop:0.5 #5856D6, stop:1 #FF2D55);
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)
        self.theme_btn.clicked.connect(self.show_theme_dialog)
        left_layout.addWidget(self.theme_btn)

        
        for btn, tip in [
            (self.close_btn, "关闭"),
            (self.minimize_btn, "最小化"),
            (self.maximize_btn, "最大化")
        ]:
            btn.setFixedSize(12, 12)
            btn.setToolTip(tip)
            left_layout.addWidget(btn)

        # 设置窗口控制按钮样式
        self.close_btn.setStyleSheet(style.get_window_button_style(style.COLORS['color_close']))
        self.minimize_btn.setStyleSheet(style.get_window_button_style(style.COLORS['color_minimize']))
        self.maximize_btn.setStyleSheet(style.get_window_button_style(style.COLORS['color_maximize']))

        layout.addWidget(left_container)

        # 标题（居中）
        self.title_label = QLabel("LovelyKodo")
        self.title_label.setStyleSheet(style.get_title_style())
        layout.addWidget(self.title_label, 1, Qt.AlignmentFlag.AlignCenter)

        # 右侧占位（为了保持标题居中）
        right_container = QWidget()
        right_container.setFixedWidth(left_container.sizeHint().width())
        layout.addWidget(right_container)

        # 连接信号
        self.close_btn.clicked.connect(self.parent.close)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)

        self.start = QPoint(0, 0)
        self.pressing = False

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.position().toPoint())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            end = self.mapToGlobal(event.position().toPoint())
            movement = end - self.start
            self.parent.setGeometry(self.parent.x() + movement.x(),
                                  self.parent.y() + movement.y(),
                                  self.parent.width(),
                                  self.parent.height())
            self.start = end

    def mouseReleaseEvent(self, event):
        self.pressing = False

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def show_theme_dialog(self):
        dialog = ThemeDialog(self.window())
        dialog.exec_()

    def set_title(self, title: str):
        """设置标题文本"""
        self.title_label.setText(title)
