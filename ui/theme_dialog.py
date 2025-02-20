from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QListWidgetItem, QWidget, QTreeWidget, QTextEdit, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
import style
import os
import json

class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("主题选择")
        self.setFixedSize(400, 350)
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
        self.preview.setObjectName("preview_container")
        self.preview.setFixedHeight(150)
        
        preview_layout = QVBoxLayout(self.preview)
        preview_layout.setSpacing(8)
        
        # 添加预览元素
        label = QLabel("标准文本")
        label.setObjectName("preview_label")
        preview_layout.addWidget(label)
        
        secondary_label = QLabel("次要文本")
        secondary_label.setObjectName("preview_secondary_label")
        preview_layout.addWidget(secondary_label)
        
        text_edit = QTextEdit()
        text_edit.setObjectName("preview_text")
        text_edit.setPlaceholderText("输入框预览")
        preview_layout.addWidget(text_edit)
        
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        primary_btn = QPushButton("主按钮")
        primary_btn.setObjectName("preview_primary_btn")
        btn_layout.addWidget(primary_btn)
        
        success_btn = QPushButton("成功按钮")
        success_btn.setObjectName("preview_success_btn")
        btn_layout.addWidget(success_btn)
        
        preview_layout.addWidget(btn_container)
        
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
                # 保存主题设置
                self.save_theme_setting(theme_name)
                
                # 显示重启提示对话框
                msg = QMessageBox(self)
                msg.setWindowTitle("主题切换")
                msg.setText("主题已更改,需要重启应用后才能完全生效。\n是否立即重启?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg.setDefaultButton(QMessageBox.StandardButton.Yes)
                
                if msg.exec() == QMessageBox.StandardButton.Yes:
                    # 重启应用
                    import sys
                    from PySide6.QtCore import QProcess
                    
                    # 启动新实例
                    program = sys.executable
                    args = sys.argv
                    QProcess.startDetached(program, args)
                    
                    # 退出当前实例
                    from PySide6.QtWidgets import QApplication
                    QApplication.quit()
                else:
                    self.accept()

    def save_theme_setting(self, theme_name: str):
        """保存主题设置到配置文件"""
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        config = {}
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
        except Exception:
            pass
            
        config['theme'] = theme_name
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存主题设置失败: {str(e)}")
