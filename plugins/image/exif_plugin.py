from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QScrollArea
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
from plugins import Plugin
from style import FONTS

class EXIFViewer:
    """EXIF信息查看器"""
    
    @staticmethod
    def get_exif_data(image_path: str) -> Dict[str, Any]:
        """获取图片的EXIF信息"""
        try:
            image = Image.open(image_path)
            exif = {}
            
            # 基本图片信息
            exif['基本信息'] = {
                '文件名': os.path.basename(image_path),
                '图片大小': f"{image.size[0]}x{image.size[1]}",
                '文件大小': f"{os.path.getsize(image_path) / 1024:.2f} KB",
                '图片格式': image.format,
                '色彩模式': image.mode,
                '色彩深度': f"{image.bits} bits" if hasattr(image, 'bits') else "未知",
                '调色板': str(image.palette) if image.palette else "无"
            }
            
            # EXIF信息
            if hasattr(image, '_getexif'):
                exif_data = image._getexif()
                if exif_data:
                    # 相机信息
                    camera_info = {}
                    # 拍摄信息
                    shooting_info = {}
                    # GPS信息
                    gps_info = {}
                    # 其他信息
                    other_info = {}
                    
                    for tag_id in exif_data:
                        tag = TAGS.get(tag_id, tag_id)
                        data = exif_data.get(tag_id)
                        
                        # 处理bytes类型的数据
                        if isinstance(data, bytes):
                            try:
                                data = data.decode('utf-8')
                            except:
                                data = data.hex()
                                
                        # 分类信息
                        if tag in ['Make', 'Model', 'Software', 'LensMake', 'LensModel']:
                            camera_info[tag] = data
                        elif tag in ['ExposureTime', 'FNumber', 'ISOSpeedRatings', 'FocalLength', 
                                   'ExposureProgram', 'Flash', 'MeteringMode', 'WhiteBalance']:
                            shooting_info[tag] = data
                        elif tag == 'GPSInfo':
                            for gps_tag in GPSTAGS:
                                if gps_tag in data:
                                    gps_info[GPSTAGS[gps_tag]] = data[gps_tag]
                        else:
                            other_info[tag] = data
                    
                    if camera_info:
                        exif['相机信息'] = camera_info
                    if shooting_info:
                        exif['拍摄信息'] = shooting_info
                    if gps_info:
                        exif['GPS信息'] = gps_info
                    if other_info:
                        exif['其他EXIF信息'] = other_info
            
            return exif
        except Exception as e:
            return {'错误': str(e)}

class EXIFPlugin(Plugin):
    name = "EXIF查看器"
    description = "查看图片的EXIF信息和基本属性"
    category = "图片工具"
    
    def __init__(self):
        super().__init__()
        self.viewer = EXIFViewer()
        self.file_label = None
        self.table = None
        self.image_label = None
        self.current_file = None
        
    def create_ui(self, parent: QWidget, layout: QVBoxLayout) -> None:
        """创建自定义UI界面"""
        # 创建主容器
        container = QWidget(parent)
        main_layout = QHBoxLayout(container)  # 使用水平布局
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # 左侧：EXIF信息
        left_widget = QWidget(parent)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 文件选择区域
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel("未选择文件", parent)
        self.file_label.setStyleSheet(f"font: {FONTS['body']};")
        
        select_btn = QPushButton("选择图片", parent)
        select_btn.setStyleSheet(f"font: {FONTS['body']};")
        select_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_btn)
        
        # 创建表格
        self.table = QTableWidget(0, 2, parent)
        self.table.setHorizontalHeaderLabels(["属性", "值"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(f"font: {FONTS['body']};")
        
        # 添加到左侧布局
        left_layout.addLayout(file_layout)
        left_layout.addWidget(self.table)
        
        # 右侧：图片预览
        right_widget = QWidget(parent)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建图片预览区域（使用QScrollArea支持缩放）
        scroll_area = QScrollArea(parent)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.image_label = QLabel(parent)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setWidget(self.image_label)
        
        right_layout.addWidget(scroll_area)
        
        # 设置左右区域的比例为1:1
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)
        
        # 添加到插件布局
        layout.addWidget(container)
        
    def select_file(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.tiff *.bmp);;所有文件 (*.*)"
        )
        
        if file_path:
            self.current_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.update_exif_info(file_path)
            self.update_image_preview(file_path)
    
    def update_exif_info(self, file_path: str):
        """更新EXIF信息显示"""
        exif_data = self.viewer.get_exif_data(file_path)
        
        # 清空表格
        self.table.setRowCount(0)
        
        # 添加数据
        row = 0
        for category, items in exif_data.items():
            # 添加分类标题
            self.table.insertRow(row)
            title_item = QTableWidgetItem(category)
            title_item.setBackground(Qt.GlobalColor.lightGray)
            self.table.setItem(row, 0, title_item)
            self.table.setItem(row, 1, QTableWidgetItem(""))
            row += 1
            
            # 添加该分类下的所有项目
            if isinstance(items, dict):
                for key, value in items.items():
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(str(key)))
                    self.table.setItem(row, 1, QTableWidgetItem(str(value)))
                    row += 1
            else:
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem("值"))
                self.table.setItem(row, 1, QTableWidgetItem(str(items)))
                row += 1
    
    def update_image_preview(self, file_path: str):
        """更新图片预览"""
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # 调整图片大小以适应预览区域，保持宽高比
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
    
    def process(self, text: str) -> str:
        """处理输入文本 - 这个插件不处理文本"""
        return ""
