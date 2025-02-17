from .. import Plugin
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QPushButton, QCheckBox, QLineEdit,
                              QFileDialog, QMessageBox, QTextEdit, QProgressBar,
                              QSpinBox, QComboBox)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QThread, Signal
from PIL import Image
import numpy as np
import re
import style
from style import FONTS
from io import StringIO
import math

class PixelParseThread(QThread):
    progress_signal = Signal(int)  # 进度信号
    finished_signal = Signal(object)  # 完成信号，传递生成的图片
    error_signal = Signal(str)  # 错误信号
    
    def __init__(self, pixels, width, height, has_alpha):
        super().__init__()
        self.pixels = pixels  # 直接传入像素列表
        self.width = width
        self.height = height
        self.has_alpha = has_alpha
        
    def run(self):
        try:
            # 创建numpy数组
            if self.has_alpha:
                img_array = np.zeros((self.height, self.width, 4), dtype=np.uint8)
            else:
                img_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            # 像素值正则表达式
            if self.has_alpha:
                pattern = r'^\((\d+),(\d+),(\d+),(\d+)\)$'
            else:
                pattern = r'^\((\d+),(\d+),(\d+)\)$'
            
            # 处理每个像素
            for i, pixel in enumerate(self.pixels):
                # 计算坐标
                y = i // self.width
                x = i % self.width
                
                pixel = pixel.strip()
                match = re.match(pattern, pixel)
                if not match:
                    self.error_signal.emit(f"第 {i+1} 个像素格式错误：{pixel}")
                    return
                
                # 提取RGB(A)值
                values = [int(v) for v in match.groups()]
                img_array[y, x] = values
                
                # 更新进度
                if i % self.width == 0:
                    progress = int((y + 1) / self.height * 100)
                    self.progress_signal.emit(progress)
                    
                    # 每处理一行让出一些CPU时间
                    self.msleep(1)
            
            # 创建PIL图片
            if self.has_alpha:
                img = Image.fromarray(img_array, 'RGBA')
            else:
                img = Image.fromarray(img_array, 'RGB')
            
            self.finished_signal.emit(img)
            
        except Exception as e:
            self.error_signal.emit(str(e))

class PixelToImagePlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.width = 100
        self.height = 100
        self.has_alpha = False
        self.width_spin = None
        self.height_spin = None
        self.alpha_checkbox = None
        self.input_text = None
        self.preview_label = None
        self.progress_bar = None
        self.parse_thread = None
        self.convert_btn = None
        self.save_btn = None

    @property
    def name(self) -> str:
        return "像素转图片"

    @property
    def category(self) -> str:
        return "图像"

    @property
    def description(self) -> str:
        return "将像素数据转换为图片，支持RGB和RGBA格式"

    def process(self, text: str) -> str:
        """处理输入文本（此方法为满足Plugin接口要求）"""
        return text

    def create_ui(self, parent: QWidget, layout: QVBoxLayout):
        """创建UI界面"""
        # 1. 设置区域
        settings_group = QGroupBox("设置", parent)
        settings_group.setFont(FONTS['title'])
        settings_group.setStyleSheet(style.get_group_box_style())
        settings_layout = QVBoxLayout(settings_group)

        # 尺寸设置
        size_layout = QHBoxLayout()
        
        width_label = QLabel("宽度：")
        width_label.setFont(FONTS['default'])
        self.width_spin = QSpinBox()
        self.width_spin.setFont(FONTS['default'])
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(self.width)
        self.width_spin.valueChanged.connect(self.update_width)
        
        height_label = QLabel("高度：")
        height_label.setFont(FONTS['default'])
        self.height_spin = QSpinBox()
        self.height_spin.setFont(FONTS['default'])
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(self.height)
        self.height_spin.valueChanged.connect(self.update_height)
        
        size_layout.addWidget(width_label)
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(height_label)
        size_layout.addWidget(self.height_spin)
        settings_layout.addLayout(size_layout)

        # Alpha通道选项
        self.alpha_checkbox = QCheckBox("包含Alpha通道")
        self.alpha_checkbox.setFont(FONTS['default'])
        self.alpha_checkbox.setChecked(self.has_alpha)
        self.alpha_checkbox.stateChanged.connect(lambda state: self.update_alpha(state))
        settings_layout.addWidget(self.alpha_checkbox)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        settings_layout.addWidget(self.progress_bar)

        # 2. 输入区域
        input_group = QGroupBox("像素数据", parent)
        input_group.setFont(FONTS['title'])
        input_group.setStyleSheet(style.get_group_box_style())
        input_layout = QVBoxLayout(input_group)

        self.input_text = QTextEdit()
        self.input_text.setFont(FONTS['default'])
        self.input_text.setMinimumHeight(100)
        self.input_text.setPlaceholderText("请输入像素数据，每行表示一个像素，像素格式为(R,G,B)或(R,G,B,A)")
        input_layout.addWidget(self.input_text)

        # 3. 预览和控制区域
        preview_group = QGroupBox("预览", parent)
        preview_group.setFont(FONTS['title'])
        preview_group.setStyleSheet(style.get_group_box_style())
        preview_layout = QVBoxLayout(preview_group)

        # 图片预览
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(300, 300)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(FONTS['default'])
        self.preview_label.setText("等待转换")
        preview_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.convert_btn = QPushButton("转换")
        self.convert_btn.setFont(FONTS['default'])
        self.convert_btn.setStyleSheet(style.get_button_style())
        self.convert_btn.clicked.connect(self.convert_pixels)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.setFont(FONTS['default'])
        self.save_btn.setStyleSheet(style.get_button_style())
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        
        button_layout.addWidget(self.convert_btn)
        button_layout.addWidget(self.save_btn)
        preview_layout.addLayout(button_layout)

        # 添加所有区域到主布局
        layout.addWidget(settings_group)
        layout.addWidget(input_group)
        layout.addWidget(preview_group)

    def update_width(self, value):
        """更新图片宽度"""
        if value > 0:  # 确保值大于0
            self.width = value

    def update_height(self, value):
        """更新图片高度"""
        if value > 0:  # 确保值大于0
            self.height = value

    def update_alpha(self, state: int):
        """更新alpha通道选项"""
        self.has_alpha = (state == 2)  # Qt.Checked 的值是 2

    def convert_pixels(self):
        """转换像素数据为图片"""
        pixel_text = self.input_text.toPlainText().strip()
        if not pixel_text:
            QMessageBox.warning(None, "警告", "请输入像素数据")
            return
            
        # 分割像素数据并移除空行
        all_pixels = []
        for p in pixel_text.split('\n'):
            p = p.strip()
            if p and p.startswith('(') and p.endswith(')'):
                all_pixels.append(p)
        
        if not all_pixels:
            QMessageBox.warning(None, "警告", "没有有效的像素数据")
            return
            
        # 检查像素总数是否匹配
        total_pixels = len(all_pixels)
        expected_pixels = self.width * self.height
        if total_pixels != expected_pixels:
            QMessageBox.warning(None, "警告", f"像素数量不匹配：期望 {expected_pixels} 个，实际 {total_pixels} 个")
            return
        
        # 禁用转换按钮，显示进度条
        self.convert_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 创建并启动解析线程
        self.parse_thread = PixelParseThread(
            all_pixels,
            self.width,
            self.height,
            self.has_alpha
        )
        self.parse_thread.progress_signal.connect(self.update_progress)
        self.parse_thread.finished_signal.connect(self.conversion_finished)
        self.parse_thread.error_signal.connect(self.conversion_error)
        self.parse_thread.start()
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def conversion_finished(self, image):
        """转换完成的处理"""
        # 显示预览
        qimage = self.pil_to_qimage(image)
        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = pixmap.scaled(
            300, 300,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
        
        # 更新UI状态
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.parse_thread = None
    
    def conversion_error(self, error_message):
        """转换错误的处理"""
        QMessageBox.warning(None, "错误", error_message)
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.parse_thread = None
    
    def save_image(self):
        """保存图片"""
        # TODO: 实现保存图片功能
        pass
    
    def pil_to_qimage(self, pil_image):
        """将PIL图片转换为QImage"""
        if pil_image.mode == 'RGBA':
            return QImage(
                pil_image.tobytes('raw', 'RGBA'),
                pil_image.size[0],
                pil_image.size[1],
                QImage.Format_RGBA8888
            )
        else:
            return QImage(
                pil_image.tobytes('raw', 'RGB'),
                pil_image.size[0],
                pil_image.size[1],
                QImage.Format_RGB888
            )
