from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QListWidgetItem, QWidget, QTreeWidget, QTextEdit, QGroupBox)
from PySide6.QtCore import Qt
import style

class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("主题选择")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(style.DIMENS['spacing'])

        # 主题列表
        self.theme_list = QListWidget()
        self.theme_list.setStyleSheet(style.get_tree_widget_style())
        for theme_name in style.theme_manager.available_themes:
            item = QListWidgetItem(theme_name)
            self.theme_list.addItem(item)
            # 选中当前主题
            if theme_name == style.theme_manager._current_theme:
                self.theme_list.setCurrentItem(item)
        layout.addWidget(self.theme_list)

        # 预览区域
        preview_label = QLabel("预览效果")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preview_label)
        
        self.preview = QWidget()
        self.preview.setFixedHeight(100)
        self.update_preview()  # 初始化预览
        layout.addWidget(self.preview)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(style.DIMENS['spacing'])

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(style.get_button_style())
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("应用")
        apply_btn.setStyleSheet(style.get_button_style())
        apply_btn.clicked.connect(self.apply_theme)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

        # 连接信号
        self.theme_list.currentItemChanged.connect(self.on_theme_selected)

    def on_theme_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """当选择的主题改变时更新预览"""
        if current:
            self.update_preview(current.text())

    def update_preview(self, theme_name=None):
        """更新预览区域"""
        if theme_name is None:
            theme_name = style.theme_manager._current_theme
            
        preview_style = style.theme_manager.get_theme_preview(theme_name)
        self.preview.setStyleSheet(preview_style)

    def apply_theme(self):
        """应用选中的主题"""
        current_item = self.theme_list.currentItem()
        if current_item:
            theme_name = current_item.text()
            if style.theme_manager.set_theme(theme_name):
                # 更新主窗口及所有子控件的样式
                main_window = self.window()
                if main_window:
                    # 更新全局样式
                    main_window.setStyleSheet(style.dynamic_styles())
                    
                    # 更新标题栏样式
                    title_bar = main_window.findChild(QWidget, "title_bar")
                    if title_bar:
                        title_bar.theme_btn.setStyleSheet("""
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
                    
                    # 更新插件树样式
                    plugin_tree = main_window.findChild(QTreeWidget)
                    if plugin_tree:
                        plugin_tree.setStyleSheet(style.get_tree_widget_style())
                    
                    # 更新文本框样式
                    for text_edit in main_window.findChildren(QTextEdit):
                        text_edit.setStyleSheet(style.get_text_edit_style())
                    
                    # 更新按钮样式
                    run_btn = main_window.findChild(QPushButton, "run_btn")
                    if run_btn:
                        run_btn.setStyleSheet(style.get_run_button_style())
                    
                    # 更新分组框样式
                    for group_box in main_window.findChildren(QGroupBox):
                        group_box.setStyleSheet(style.get_group_box_style())
                        
                self.accept()
            else:
                self.reject()
