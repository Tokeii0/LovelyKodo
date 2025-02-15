from ..import Plugin
from PySide6.QtWidgets import (QWidget, QLabel, QFileDialog, QPushButton, 
                              QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit,
                              QComboBox)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from PIL import Image
import numpy as np
import os
import style

class LSBStego(Plugin):
    @property
    def name(self) -> str:
        return "LSB隐写"

    @property
    def category(self) -> str:
        return "图片隐写"

    @property
    def description(self) -> str:
        return "使用最低有效位(LSB)方法在图片中隐藏或提取文本信息"

    def create_ui(self, parent: QWidget, layout: QVBoxLayout) -> None:
        self.image_path = ""
        
        # 上半部分：图片选择和预览
        top_group = QGroupBox("图片", parent)
        top_group.setStyleSheet(style.get_group_box_style())
        top_layout = QVBoxLayout(top_group)
        
        # 文件选择区域
        file_layout = QHBoxLayout()
        self.file_label = QLabel("未选择图片", parent)
        self.file_btn = QPushButton("选择图片", parent)
        self.file_btn.setStyleSheet(style.get_run_button_style())
        self.file_btn.clicked.connect(self._select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_btn)
        top_layout.addLayout(file_layout)
        
        # 图片预览
        self.preview_label = QLabel(parent)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")
        top_layout.addWidget(self.preview_label)
        
        layout.addWidget(top_group)
        
        # 中间部分：模式选择
        mode_group = QGroupBox("处理模式", parent)
        mode_group.setStyleSheet(style.get_group_box_style())
        mode_layout = QVBoxLayout(mode_group)
        
        mode_label = QLabel("选择模式:", parent)
        self.mode_combo = QComboBox(parent)
        self.mode_combo.addItems(["encode - 隐写文本", "decode - 提取文本"])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #3498db;
                border-radius: 3px;
                background: white;
            }
            QComboBox:hover {
                border: 1px solid #2980b9;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        
        layout.addWidget(mode_group)
        
        # 下半部分：文本输入输出
        # 输入区域
        input_group = QGroupBox("要隐写的文本", parent)
        input_group.setObjectName("input_group")
        input_group.setStyleSheet(style.get_group_box_style())
        input_layout = QVBoxLayout(input_group)
        
        self.input_edit = QTextEdit(parent)
        self.input_edit.setObjectName("input_edit")
        self.input_edit.setPlaceholderText("在这里输入要隐藏的文本...")
        self.input_edit.setStyleSheet(style.get_text_edit_style())
        input_layout.addWidget(self.input_edit)
        layout.addWidget(input_group)

        # 运行按钮
        self.run_btn = QPushButton("执行", parent)
        self.run_btn.setStyleSheet(style.get_run_button_style())
        self.run_btn.setObjectName("run_btn")
        layout.addWidget(self.run_btn)

        # 输出区域
        output_group = QGroupBox("处理结果", parent)
        output_group.setStyleSheet(style.get_group_box_style())
        output_layout = QVBoxLayout(output_group)
        
        self.output_edit = QTextEdit(parent)
        self.output_edit.setPlaceholderText("处理结果将显示在这里...")
        self.output_edit.setStyleSheet(style.get_text_edit_style())
        self.output_edit.setObjectName("output_edit")
        output_layout.addWidget(self.output_edit)
        layout.addWidget(output_group)

        # 根据模式更新UI
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self._on_mode_changed()

    def _on_mode_changed(self):
        """处理模式改变事件"""
        is_encode = self.mode_combo.currentText().startswith("encode")
        self.input_edit.setPlaceholderText(
            "在这里输入要隐藏的文本..." if is_encode else "解码模式下无需输入文本"
        )
        self.input_edit.setEnabled(is_encode)

    def _select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            
            # 更新预览图
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 保持宽高比例缩放到预览区域
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)

    def validate_input(self, **kwargs) -> tuple[bool, str]:
        if not self.image_path:
            return False, "请选择图片文件"
        
        mode = self.mode_combo.currentText().split(" - ")[0]
        if mode == "encode" and not self.input_edit.toPlainText():
            return False, "请输入要隐写的文本"
            
        return True, ""

    def process(self, input_data: str, **kwargs) -> str:
        mode = self.mode_combo.currentText().split(" - ")[0]
        
        if mode == "encode":
            return self._encode(self.input_edit.toPlainText())
        else:
            return self._decode()

    def _encode(self, text: str) -> str:
        try:
            # 打开图片并进行预处理
            img = Image.open(self.image_path)
            
            # 确保图片是RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # 获取图片尺寸
            width, height = img.size
            
            # 将图片转换为numpy数组
            pixels = np.asarray(img)
            if pixels.dtype != np.uint8:
                return "错误：图片格式不支持，请使用8位RGB图片"
                
            # 检查图片是否是3通道
            if len(pixels.shape) != 3 or pixels.shape[2] != 3:
                return "错误：请使用RGB格式的图片"
            
            # 将文本转换为二进制
            binary = ''.join([format(ord(c), '08b') for c in text])
            binary += '00000000'  # 添加结束标记
            
            # 检查容量
            max_bytes = pixels.size // 8
            if len(binary) > pixels.size:
                return f"错误：文本太长，图片容量不足。\n最大可存储{max_bytes}字节，当前文本需要{len(binary)//8}字节"
            
            # 创建副本进行修改
            pixels_copy = pixels.copy()
            
            # 修改像素的最低位
            idx = 0
            for h in range(height):
                for w in range(width):
                    for c in range(3):  # RGB三个通道
                        if idx < len(binary):
                            # 使用位运算修改最低位，使用 254 (0xFE) 代替 ~1
                            pixels_copy[h, w, c] = (pixels_copy[h, w, c] & 0xFE) | int(binary[idx])
                            idx += 1
            
            # 让用户选择保存位置
            output_path, _ = QFileDialog.getSaveFileName(
                None,
                "保存隐写后的图片",
                os.path.splitext(self.image_path)[0] + "_encoded.png",
                "PNG图片 (*.png)"
            )
            
            if not output_path:
                return "已取消保存"
            
            # 保存图片
            output_img = Image.fromarray(pixels_copy)
            output_img.save(output_path, format='PNG')
            
            # 更新预览
            pixmap = QPixmap(output_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
            
            return f"隐写成功！文件已保存为：{output_path}"
            
        except Exception as e:
            import traceback
            return f"错误：{str(e)}\n{traceback.format_exc()}"

    def _decode(self) -> str:
        try:
            # 打开图片并进行预处理
            img = Image.open(self.image_path)
            
            # 确保图片是RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 将图片转换为numpy数组
            pixels = np.asarray(img)
            if pixels.dtype != np.uint8:
                return "错误：图片格式不支持，请使用8位RGB图片"
                
            # 检查图片是否是3通道
            if len(pixels.shape) != 3 or pixels.shape[2] != 3:
                return "错误：请使用RGB格式的图片"
            
            # 提取最低位
            binary = ""
            text = ""
            for h in range(img.height):
                for w in range(img.width):
                    for c in range(3):  # RGB三个通道
                        binary += str(pixels[h, w, c] & 1)
                        
                        # 每8位转换为一个字符
                        if len(binary) >= 8:
                            try:
                                char = chr(int(binary[:8], 2))
                                if char == '\0':  # 检查结束标记
                                    return text
                                text += char
                                binary = binary[8:]
                            except ValueError:
                                continue  # 跳过无效的字符
            
            return "未找到隐写信息"
            
        except Exception as e:
            import traceback
            return f"错误：{str(e)}\n{traceback.format_exc()}"
