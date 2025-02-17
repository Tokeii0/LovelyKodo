from .. import Plugin
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QPushButton, QCheckBox, QLineEdit,
                              QFileDialog, QMessageBox, QTextEdit, QProgressBar,
                              QComboBox)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QThread, Signal
from PIL import Image
import numpy as np
import style
from style import FONTS
from io import StringIO

class PixelConvertThread(QThread):
    progress_signal = Signal(int)  # 进度信号
    finished_signal = Signal(str)  # 完成信号
    
    def __init__(self, image, include_alpha, separator):
        super().__init__()
        self.image = image
        self.include_alpha = include_alpha
        self.separator = separator
        
    def run(self):
        if self.image is None:
            self.finished_signal.emit("请先选择一张图片")
            return
            
        # 确保图片是RGBA模式
        if self.image.mode != 'RGBA':
            self.image = self.image.convert('RGBA')
            
        img_array = np.array(self.image)
        height, width = img_array.shape[:2]
        total_pixels = height * width
        processed_pixels = 0
        
        # 使用StringIO来优化字符串拼接
        output = StringIO()
        
        for y in range(height):
            row_pixels = []
            for x in range(width):
                if self.include_alpha:
                    # 包含alpha通道
                    p = img_array[y, x]
                    row_pixels.append(f"({p[0]},{p[1]},{p[2]},{p[3]})")
                else:
                    # 不包含alpha通道
                    p = img_array[y, x]
                    row_pixels.append(f"({p[0]},{p[1]},{p[2]})")
                
                processed_pixels += 1
                if processed_pixels % width == 0:
                    progress = int((processed_pixels / total_pixels) * 100)
                    self.progress_signal.emit(progress)
            
            # 使用选定的分隔符连接每行的像素
            output.write(self.separator.join(row_pixels))
            output.write("\n")  # 每行末尾添加换行符
            
            # 让出一些CPU时间
            if y % 10 == 0:
                self.msleep(1)
        
        result = output.getvalue().rstrip()  # 移除最后一个换行符
        output.close()
        self.finished_signal.emit(result)

class PixelExtractPlugin(Plugin):
    # 预定义的分隔符选项
    SEPARATORS = {
        "换行 (\\n)": "\n",
        "分号 (;)": ";",
        "空格 ( )": " ",
        "制表符 (\\t)": "\t",
        "竖线 (|)": "|",
        "斜杠 (/)": "/",
        "自定义...": ""
    }

    def __init__(self):
        super().__init__()
        self.image = None
        self.include_alpha = False
        self.separator = '\n'  # 默认使用换行
        self.image_label = None
        self.separator_input = None
        self.separator_combo = None
        self.alpha_checkbox = None
        self.output_text = None
        self.progress_bar = None
        self.convert_thread = None
        self.convert_btn = None

    @property
    def name(self) -> str:
        return "像素提取器"

    @property
    def category(self) -> str:
        return "图像"

    @property
    def description(self) -> str:
        return "提取图片的像素点数据，支持自定义分隔符和alpha通道"
        
    def process(self, text: str) -> str:
        """处理输入文本（此方法为满足Plugin接口要求）"""
        return text  # 我们不使用这个方法，而是使用异步处理

    def create_ui(self, parent: QWidget, layout: QVBoxLayout):
        """创建UI界面"""
        # 1. 设置区域
        settings_group = QGroupBox("设置", parent)
        settings_group.setFont(FONTS['title'])
        settings_group.setStyleSheet(style.get_group_box_style())
        settings_layout = QVBoxLayout(settings_group)

        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        # 选择图片按钮
        select_btn = QPushButton("选择图片")
        select_btn.setFont(FONTS['default'])
        select_btn.setStyleSheet(style.get_button_style())
        select_btn.clicked.connect(self.select_image)
        
        # 转换按钮
        self.convert_btn = QPushButton("转换")
        self.convert_btn.setFont(FONTS['default'])
        self.convert_btn.setStyleSheet(style.get_button_style())
        self.convert_btn.clicked.connect(self.convert_image)
        
        control_layout.addWidget(select_btn)
        control_layout.addWidget(self.convert_btn)
        settings_layout.addLayout(control_layout)

        # 分隔符选项
        separator_layout = QHBoxLayout()
        self.separator_combo = QComboBox()
        self.separator_combo.setFont(FONTS['default'])
        self.separator_combo.addItems(self.SEPARATORS.keys())
        self.separator_combo.currentTextChanged.connect(self.update_separator)
        separator_layout.addWidget(QLabel("分隔符："))
        separator_layout.addWidget(self.separator_combo)
        self.separator_input = QLineEdit()
        self.separator_input.setFont(FONTS['default'])
        self.separator_input.setPlaceholderText("自定义分隔符")
        self.separator_input.setVisible(False)
        separator_layout.addWidget(self.separator_input)
        settings_layout.addLayout(separator_layout)

        # Alpha通道选项
        self.alpha_checkbox = QCheckBox("包含Alpha通道")
        self.alpha_checkbox.setFont(FONTS['default'])
        self.alpha_checkbox.setChecked(self.include_alpha)
        # 直接连接到Qt.Checked状态
        self.alpha_checkbox.stateChanged.connect(lambda state: self.update_alpha(state))
        settings_layout.addWidget(self.alpha_checkbox)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        settings_layout.addWidget(self.progress_bar)

        # 2. 图片预览区域
        preview_group = QGroupBox("图片预览", parent)
        preview_group.setFont(FONTS['title'])
        preview_group.setStyleSheet(style.get_group_box_style())
        preview_layout = QVBoxLayout(preview_group)

        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 300)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFont(FONTS['default'])
        self.image_label.setText("请选择图片")
        preview_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # 3. 输出区域
        output_group = QGroupBox("像素数据", parent)
        output_group.setFont(FONTS['title'])
        output_group.setStyleSheet(style.get_group_box_style())
        output_layout = QVBoxLayout(output_group)

        self.output_text = QTextEdit()
        self.output_text.setFont(FONTS['default'])
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        output_layout.addWidget(self.output_text)

        # 添加所有区域到主布局
        layout.addWidget(settings_group)
        layout.addWidget(preview_group)
        layout.addWidget(output_group)

    def convert_image(self):
        """转换图片为像素数据"""
        if self.image is None:
            QMessageBox.warning(None, "警告", "请先选择一张图片")
            return
            
        print(f"开始转换，Alpha通道状态为: {self.include_alpha}")  # 调试信息
        
        # 禁用转换按钮，显示进度条
        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.output_text.clear()
        
        # 创建并启动转换线程
        self.convert_thread = PixelConvertThread(
            self.image, 
            self.include_alpha,  # 传递当前的alpha通道状态
            self.separator
        )
        self.convert_thread.progress_signal.connect(self.update_progress)
        self.convert_thread.finished_signal.connect(self.conversion_finished)
        self.convert_thread.start()
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def conversion_finished(self, result):
        """转换完成的处理"""
        self.output_text.setText(result)
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.convert_thread = None

    def select_image(self):
        """选择图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                # 打开图片并转换为RGBA模式
                img = Image.open(file_path)
                print(f"原始图片模式: {img.mode}")  # 调试信息
                
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                    print(f"转换后图片模式: {img.mode}")  # 调试信息
                
                self.image = img
                
                # 检查numpy数组的形状
                img_array = np.array(self.image)
                print(f"图片数组形状: {img_array.shape}")  # 调试信息
                if len(img_array.shape) == 3:
                    print(f"通道数: {img_array.shape[2]}")  # 调试信息
                
                # 显示预览
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(
                    300, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                
                # 如果已经勾选了alpha通道，自动转换
                if self.include_alpha:
                    self.convert_image()
            except Exception as e:
                QMessageBox.warning(None, "错误", f"无法打开图片：{str(e)}")

    def update_alpha(self, state: int):
        """更新alpha通道选项"""
        print(f"收到状态改变信号: {state}")  # 调试信息
        self.include_alpha = (state == 2)  # Qt.Checked 的值是 2
        print(f"Alpha通道状态更新为: {self.include_alpha}")  # 调试信息
        # 如果有图片且改变了alpha设置，自动重新转换
        if self.image is not None:
            self.convert_image()

    def update_separator(self, text: str):
        """更新分隔符选项"""
        if text == "自定义...":
            self.separator_input.setVisible(True)
        else:
            self.separator_input.setVisible(False)
            self.separator = self.SEPARATORS[text]
