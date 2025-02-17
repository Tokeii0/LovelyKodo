from .stegsolve_plugin import StegSolvePlugin
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QComboBox, QPushButton, QFileDialog, QScrollArea)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from plugins import Plugin
import numpy as np
from PIL import Image
import io

class StegSolvePlugin(Plugin):
    def __init__(self):
        self.current_image = None
        self.current_mode = None
        self.image_label = None
        self.mode_combo = None
        self.modes = [
            "Normal", 
            "Red plane", "Green plane", "Blue plane",
            "Alpha plane",
            "Red bit plane 0", "Red bit plane 1", "Red bit plane 2", "Red bit plane 3",
            "Red bit plane 4", "Red bit plane 5", "Red bit plane 6", "Red bit plane 7",
            "Green bit plane 0", "Green bit plane 1", "Green bit plane 2", "Green bit plane 3",
            "Green bit plane 4", "Green bit plane 5", "Green bit plane 6", "Green bit plane 7",
            "Blue bit plane 0", "Blue bit plane 1", "Blue bit plane 2", "Blue bit plane 3",
            "Blue bit plane 4", "Blue bit plane 5", "Blue bit plane 6", "Blue bit plane 7",
        ]

    @property
    def name(self) -> str:
        return "StegSolve"

    @property
    def category(self) -> str:
        return "图片分析"

    @property
    def description(self) -> str:
        return "类似于StegSolve的图片隐写分析工具，可以查看图片的不同通道和位平面"

    def process(self, input_data: str, **kwargs) -> str:
        return "请使用界面上的按钮选择图片进行分析"

    def create_ui(self, parent: QWidget, layout: QVBoxLayout) -> None:
        # 创建主布局
        main_widget = QWidget(parent)
        main_layout = QVBoxLayout(main_widget)

        # 创建控制区域
        control_layout = QHBoxLayout()
        
        # 添加文件选择按钮
        self.file_btn = QPushButton("选择图片", parent)
        self.file_btn.clicked.connect(lambda: self._load_image(parent))
        control_layout.addWidget(self.file_btn)

        # 添加模式选择下拉框
        self.mode_combo = QComboBox(parent)
        self.mode_combo.addItems(self.modes)
        self.mode_combo.currentTextChanged.connect(self._update_image)
        control_layout.addWidget(self.mode_combo)

        main_layout.addLayout(control_layout)

        # 创建图片显示区域
        scroll_area = QScrollArea(parent)
        scroll_area.setWidgetResizable(True)
        
        self.image_label = QLabel(parent)
        self.image_label.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(self.image_label)
        
        main_layout.addWidget(scroll_area)
        layout.addWidget(main_widget)

    def _load_image(self, parent):
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.current_image = Image.open(file_path)
            self._update_image()

    def _update_image(self):
        if self.current_image is None:
            return

        mode = self.mode_combo.currentText()
        img_array = np.array(self.current_image)

        if len(img_array.shape) == 2:  # 灰度图
            img_array = np.stack((img_array,) * 3, axis=-1)
        elif img_array.shape[2] == 3:  # RGB图
            img_array = np.pad(img_array, ((0,0), (0,0), (0,1)), mode='constant')

        if mode == "Normal":
            result = img_array[:,:,:3]
        elif mode == "Red plane":
            result = np.zeros_like(img_array[:,:,:3])
            result[:,:,0] = img_array[:,:,0]
        elif mode == "Green plane":
            result = np.zeros_like(img_array[:,:,:3])
            result[:,:,1] = img_array[:,:,1]
        elif mode == "Blue plane":
            result = np.zeros_like(img_array[:,:,:3])
            result[:,:,2] = img_array[:,:,2]
        elif mode == "Alpha plane":
            result = np.full_like(img_array[:,:,:3], img_array[:,:,3:4])
        else:
            # 处理位平面
            color = mode.split()[0].lower()
            bit = int(mode.split()[-1])
            color_idx = {'red': 0, 'green': 1, 'blue': 2}[color]
            
            result = np.zeros_like(img_array[:,:,:3])
            bit_plane = (img_array[:,:,color_idx] >> bit) & 1
            result[:,:,:] = bit_plane[:,:,np.newaxis] * 255

        # 转换为QImage显示
        height, width = result.shape[:2]
        bytes_per_line = 3 * width
        
        qimg = QImage(result.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        # 根据窗口大小缩放图片
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
