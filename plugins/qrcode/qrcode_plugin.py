from .. import Plugin
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, 
                              QHBoxLayout, QGroupBox, QSpinBox, QComboBox,
                              QFileDialog, QMessageBox, QTextEdit)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
import numpy as np
import style
from style import FONTS

class QRCodePlugin(Plugin):
    def __init__(self):
        super().__init__()
        # 初始化参数
        self.qr_version = 1
        self.error_correction = 'M'
        self.box_size = 10
        self.border = 4
        self.fill_color = (0, 0, 0)
        self.back_color = (255, 255, 255)
        self.qr_image = None

    @property
    def name(self) -> str:
        return "二维码生成器"

    @property
    def category(self) -> str:
        return "二维码"

    @property
    def description(self) -> str:
        return "生成、保存和识别二维码"

    def process(self, text: str) -> str:
        """处理输入文本"""
        return text

    def create_ui(self, parent: QWidget, layout: QVBoxLayout):
        """创建UI界面"""
        # 上部分：参数设置和预览
        top_group = QGroupBox("二维码生成", parent)
        top_group.setFont(FONTS['title'])
        top_group.setStyleSheet(style.get_group_box_style())
        top_layout = QHBoxLayout(top_group)
        top_layout.setSpacing(20)  # 增加左右两侧的间距
        
        # 左侧参数面板
        param_group = QGroupBox("参数设置", top_group)
        param_group.setFont(FONTS['title'])
        param_group.setStyleSheet(style.get_group_box_style())
        param_layout = QVBoxLayout(param_group)
        param_layout.setSpacing(10)
        param_layout.setContentsMargins(20, 20, 20, 20)

        # 版本选择
        version_layout = QHBoxLayout()
        version_label = QLabel("版本:", param_group)
        version_label.setFont(FONTS['body'])
        version_label.setMinimumWidth(80)
        self.version_combo = QComboBox(param_group)
        self.version_combo.setFont(FONTS['body'])
        self.version_combo.setMinimumWidth(100)
        self.version_combo.addItems([str(i) for i in range(1, 41)])
        self.version_combo.setCurrentText(str(self.qr_version))
        self.version_combo.currentTextChanged.connect(self.update_preview)
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch()
        param_layout.addLayout(version_layout)

        # 纠错级别
        level_layout = QHBoxLayout()
        level_label = QLabel("纠错级别:", param_group)
        level_label.setFont(FONTS['body'])
        level_label.setMinimumWidth(80)
        self.level_combo = QComboBox(param_group)
        self.level_combo.setFont(FONTS['body'])
        self.level_combo.setMinimumWidth(100)
        self.level_combo.addItems(['L', 'M', 'Q', 'H'])
        self.level_combo.setCurrentText(self.error_correction)
        self.level_combo.currentTextChanged.connect(self.update_preview)
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_combo)
        level_layout.addStretch()
        param_layout.addLayout(level_layout)

        # 颜色选择
        color_layout = QHBoxLayout()
        color_label = QLabel("颜色:", param_group)
        color_label.setFont(FONTS['body'])
        color_label.setMinimumWidth(80)

        self.fg_btn = QPushButton("前景色", param_group)
        self.fg_btn.setFont(FONTS['body'])
        self.fg_btn.setMinimumWidth(100)
        self.fg_btn.clicked.connect(self.choose_fg_color)
        
        self.bg_btn = QPushButton("背景色", param_group)
        self.bg_btn.setFont(FONTS['body'])
        self.bg_btn.setMinimumWidth(100)
        self.bg_btn.clicked.connect(self.choose_bg_color)

        color_layout.addWidget(color_label)
        color_layout.addWidget(self.fg_btn)
        color_layout.addWidget(self.bg_btn)
        color_layout.addStretch()
        param_layout.addLayout(color_layout)
        
        # 模块大小
        size_layout = QVBoxLayout()
        size_label = QLabel("模块大小:", param_group)
        size_label.setFont(FONTS['body'])
        size_label.setMinimumWidth(80)
        self.size_spin = QSpinBox(param_group)
        self.size_spin.setFont(FONTS['body'])
        self.size_spin.setMinimumWidth(100)
        self.size_spin.setRange(1, 50)
        self.size_spin.setValue(self.box_size)
        self.size_spin.valueChanged.connect(self.update_preview)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        param_layout.addLayout(size_layout)
        
        # 边框
        border_layout = QVBoxLayout()
        border_label = QLabel("边框:", param_group)
        border_label.setFont(FONTS['body'])
        border_label.setMinimumWidth(80)
        self.border_spin = QSpinBox(param_group)
        self.border_spin.setFont(FONTS['body'])
        self.border_spin.setMinimumWidth(100)
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(self.border)
        self.border_spin.valueChanged.connect(self.update_preview)
        border_layout.addWidget(border_label)
        border_layout.addWidget(self.border_spin)
        border_layout.addStretch()
        param_layout.addLayout(border_layout)
        
        param_layout.addStretch()
        
        # 右侧预览区域
        preview_group = QGroupBox("预览", top_group)
        preview_group.setFont(FONTS['title'])
        preview_group.setStyleSheet(style.get_group_box_style())
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        preview_layout.setSpacing(10)
        
        self.preview_label = QLabel(preview_group)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        
        preview_layout.addWidget(self.preview_label)
        preview_layout.addStretch()

        # 添加左右两个面板到主布局
        top_layout.addWidget(param_group)
        top_layout.addWidget(preview_group)
        
        # 添加到主布局
        layout.addWidget(top_group)
        
        # 输入区域
        input_group = QGroupBox("输入", parent)
        input_group.setFont(FONTS['title'])
        input_group.setStyleSheet(style.get_group_box_style())
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(20, 20, 20, 20)  # 增加内边距
        
        self.input_text = QTextEdit(input_group)
        self.input_text.setFont(FONTS['body'])
        self.input_text.setPlaceholderText("请输入要生成二维码的内容")
        self.input_text.setMinimumHeight(100)
        self.input_text.textChanged.connect(self.update_preview)
        input_layout.addWidget(self.input_text)
        
        layout.addWidget(input_group)
        
        # 底部按钮区域
        button_group = QGroupBox("操作", parent)
        button_group.setFont(FONTS['title'])
        button_group.setStyleSheet(style.get_group_box_style())
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(20, 20, 20, 20)  # 增加内边距
        
        save_btn = QPushButton("保存二维码", button_group)
        save_btn.setFont(FONTS['body'])
        save_btn.setMinimumWidth(120)
        save_btn.setMinimumHeight(32)  # 增加按钮高度
        save_btn.clicked.connect(self.save_qr)
        
        decode_btn = QPushButton("识别二维码", button_group)
        decode_btn.setFont(FONTS['body'])
        decode_btn.setMinimumWidth(120)
        decode_btn.setMinimumHeight(32)  # 增加按钮高度
        decode_btn.clicked.connect(self.decode_qr)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(decode_btn)
        button_layout.addStretch()
        
        layout.addWidget(button_group)

    def update_preview(self):
        """更新二维码预览"""
        text = self.input_text.toPlainText()
        if not text:
            self.preview_label.clear()
            self.qr_image = None
            return
            
        try:
            # 获取参数
            self.qr_version = int(self.version_combo.currentText())
            self.error_correction = self.level_combo.currentText()
            self.box_size = self.size_spin.value()
            self.border = self.border_spin.value()
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=self.qr_version,
                error_correction=self.error_correction,
                box_size=self.box_size,
                border=self.border
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # 生成图片
            self.qr_image = qr.make_image(
                fill_color=self.fill_color,
                back_color=self.back_color
            )
            
            # 转换为QPixmap显示
            img_array = np.array(self.qr_image.convert('RGB'))
            height, width, channel = img_array.shape
            bytes_per_line = 3 * width
            
            q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # 缩放到预览区域大小
            preview_size = min(self.preview_label.width(), self.preview_label.height())
            if preview_size > 0:
                pixmap = pixmap.scaled(preview_size, preview_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.preview_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"生成二维码出错: {str(e)}")
            self.preview_label.clear()
            self.qr_image = None

    def choose_fg_color(self):
        """选择前景色"""
        from PySide6.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor()
        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())
            self.fill_color = rgb
            self.fg_btn.setStyleSheet(f"background-color: rgb{rgb}")
            self.update_preview()

    def choose_bg_color(self):
        """选择背景色"""
        from PySide6.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor()
        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())
            self.back_color = rgb
            self.bg_btn.setStyleSheet(f"background-color: rgb{rgb}")
            self.update_preview()

    def save_qr(self):
        """保存二维码图片"""
        if not self.qr_image:
            QMessageBox.warning(None, "错误", "请先生成二维码")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "保存二维码",
            "",
            "PNG图片 (*.png);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                self.qr_image.save(file_path)
                QMessageBox.information(None, "成功", "二维码已保存")
            except Exception as e:
                QMessageBox.warning(None, "错误", f"保存失败：{str(e)}")

    def decode_qr(self):
        """识别二维码图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择二维码图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                image = Image.open(file_path)
                results = decode(image)
                if results:
                    text = results[0].data.decode('utf-8')
                    self.input_text.setText(text)
                    QMessageBox.information(None, "成功", "二维码识别成功")
                else:
                    QMessageBox.warning(None, "错误", "未能识别二维码")
            except Exception as e:
                QMessageBox.warning(None, "错误", f"识别二维码时出错：{str(e)}")
