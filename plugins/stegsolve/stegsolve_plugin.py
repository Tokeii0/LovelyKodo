from .. import Plugin
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QPushButton, QFileDialog, QScrollArea,
                              QMessageBox, QDialog, QTextEdit, QCheckBox, QGroupBox, QRadioButton)
from PySide6.QtGui import QImage, QPixmap, QKeyEvent
from PySide6.QtCore import Qt, Signal
import numpy as np
from PIL import Image
import io
import style
from style import FONTS
from .lsb_dialog import LSBExtractDialog

class LSBExtractDialog(QDialog):
    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据提取")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self._plugin = plugin  # 保存插件实例引用
        
        layout = QVBoxLayout(self)
        
        # 预览设置
        preview_group = QGroupBox("预览设置", self)
        preview_layout = QVBoxLayout(preview_group)
        self.preview_check = QCheckBox("在预览中包含十六进制转储", self)
        preview_layout.addWidget(self.preview_check)
        layout.addWidget(preview_group)
        
        # 位平面选择
        bit_group = QGroupBox("位平面选择", self)
        bit_layout = QVBoxLayout(bit_group)
        
        # 创建通道选择网格
        channels = [
            ("Red", range(8)),
            ("Green", range(8)),
            ("Blue", range(8)),
            ("Alpha", range(8))
        ]
        
        # 为每个通道创建选择框
        self.bit_checkboxes = {}
        for channel, bits in channels:
            channel_layout = QVBoxLayout()
            
            # 顶部布局：通道名称和全选
            top_layout = QHBoxLayout()
            top_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
            label = QLabel(channel)
            all_check = QCheckBox("全选", self)
            
            # 添加弹性空间使全选靠左
            top_layout.addWidget(label)
            top_layout.addWidget(all_check)
            top_layout.addStretch()  # 添加弹性空间
            channel_layout.addLayout(top_layout)
            
            # 位平面复选框水平布局
            bits_layout = QHBoxLayout()
            bits_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
            bits_layout.setSpacing(5)  # 减小间距
            bit_boxes = []
            for bit in bits:
                check = QCheckBox(str(bit), self)
                check.setFixedWidth(40)  # 设置固定宽度使复选框更紧凑
                bits_layout.addWidget(check)
                bit_boxes.append(check)
                self.bit_checkboxes[f"{channel}_{bit}"] = check
            
            bits_layout.addStretch()  # 添加弹性空间，使复选框靠左对齐
            channel_layout.addLayout(bits_layout)
            
            # 连接全选复选框
            def update_checkboxes(state, boxes=bit_boxes):
                for box in boxes:
                    box.setChecked(bool(state))
            
            all_check.stateChanged.connect(lambda state, b=bit_boxes: update_checkboxes(state, b))
            
            # 连接单个复选框的变化到全选框
            def update_all_check(boxes=bit_boxes, all_check=all_check):
                all_check.setChecked(all(box.isChecked() for box in boxes))
            
            for box in bit_boxes:
                box.stateChanged.connect(lambda state, b=bit_boxes, a=all_check: update_all_check(b, a))
            
            bit_layout.addLayout(channel_layout)
        
        layout.addWidget(bit_group)
        
        # 提取选项
        options_group = QGroupBox("提取选项", self)
        options_layout = QHBoxLayout(options_group)
        
        # 提取方向
        direction_layout = QVBoxLayout()
        direction_label = QLabel("提取方向:")
        self.direction_msb = QRadioButton("MSB优先", self)
        self.direction_lsb = QRadioButton("LSB优先", self)
        self.direction_lsb.setChecked(True)
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.direction_msb)
        direction_layout.addWidget(self.direction_lsb)
        options_layout.addLayout(direction_layout)
        
        # 位顺序
        order_layout = QVBoxLayout()
        order_label = QLabel("位顺序:")
        self.order_column = QRadioButton("按列", self)
        self.order_row = QRadioButton("按行", self)
        self.order_row.setChecked(True)
        order_layout.addWidget(order_label)
        order_layout.addWidget(self.order_column)
        order_layout.addWidget(self.order_row)
        options_layout.addLayout(order_layout)
        
        # RGB顺序
        rgb_layout = QVBoxLayout()
        rgb_label = QLabel("RGB顺序:")
        self.rgb_orders = QComboBox(self)
        rgb_orders = ["RGB", "RBG", "GRB", "GBR", "BRG", "BGR"]
        self.rgb_orders.addItems(rgb_orders)
        rgb_layout.addWidget(rgb_label)
        rgb_layout.addWidget(self.rgb_orders)
        options_layout.addLayout(rgb_layout)
        
        layout.addWidget(options_group)
        
        # 预览区域
        preview_label = QLabel("预览", self)
        layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit(self)
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        self.preview_btn = QPushButton("预览", self)
        self.save_text_btn = QPushButton("保存文本", self)
        self.save_bin_btn = QPushButton("保存二进制", self)
        self.extract_btn = QPushButton("提取", self)
        self.close_btn = QPushButton("关闭", self)
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.save_text_btn)
        button_layout.addWidget(self.save_bin_btn)
        button_layout.addWidget(self.extract_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.preview_btn.clicked.connect(self._preview_data)
        self.save_text_btn.clicked.connect(self._save_text)
        self.save_bin_btn.clicked.connect(self._save_binary)
        self.close_btn.clicked.connect(self.close)
        # 提取按钮现在也执行预览
        self.extract_btn.clicked.connect(self._preview_data)

    def closeEvent(self, event):
        # 保存当前设置等清理工作
        event.accept()

    def _extract_data(self):
        """提取二进制数据，返回bytes对象"""
        if not hasattr(self, '_last_extracted_data'):
            return None
        return self._last_extracted_data

    def _save_text(self):
        """保存为文本文件"""
        data = self._extract_data()
        if not data:
            QMessageBox.warning(self, "警告", "请先预览数据")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存文本文件",
            "",
            "文本文件 (*.txt)"
        )
        if file_path:
            try:
                # 尝试将二进制数据解码为文本
                text = data.decode('utf-8', errors='ignore')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "成功", "文本文件保存成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件时发生错误：{str(e)}")

    def _save_binary(self):
        """保存为二进制文件"""
        data = self._extract_data()
        if not data:
            QMessageBox.warning(self, "警告", "请先预览数据")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存二进制文件",
            "",
            "二进制文件 (*.bin)"
        )
        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(data)
                QMessageBox.information(self, "成功", "二进制文件保存成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件时发生错误：{str(e)}")

    def _preview_data(self):
        """预览提取的数据"""
        selected_bits = []
        for key, checkbox in self.bit_checkboxes.items():
            if checkbox.isChecked():
                channel, bit = key.split('_')
                selected_bits.append((channel, int(bit)))
        
        if not selected_bits:
            QMessageBox.warning(self, "警告", "请至少选择一个位平面")
            return
        
        # 获取设置
        settings = self.get_extract_settings()
        
        try:
            # 使用插件实例提取二进制数据
            self._last_extracted_data = self._plugin._extract_lsb(self)
            
            if self._last_extracted_data:
                # 尝试解码为文本
                text = self._last_extracted_data.decode('utf-8', errors='ignore')
                result = ["=== LSB Extraction ===\n"]
                result.append(text)
                
                if self.preview_check.isChecked():
                    result.append("\nHexdump:")
                    # 生成hexdump格式输出
                    hex_bytes = self._last_extracted_data
                    for i in range(0, len(hex_bytes), 16):
                        chunk = hex_bytes[i:i+16]
                        result.append(f"{i:08x}  ")
                        
                        hex_line = ""
                        ascii_line = ""
                        
                        for j, byte in enumerate(chunk):
                            if j == 8:
                                hex_line += " "
                            hex_line += f"{byte:02x} "
                            if 32 <= byte <= 126:
                                ascii_line += chr(byte)
                            else:
                                ascii_line += "."
                        
                        hex_line = hex_line.ljust(49)
                        ascii_line = ascii_line.ljust(16)
                        
                        result.append(f"{hex_line} |{ascii_line}|")
                
                self.preview_text.setText("\n".join(result))
            else:
                self.preview_text.setText("无数据")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"提取数据时发生错误：{str(e)}")

    def get_extract_settings(self):
        """获取当前的提取设置"""
        settings = {
            'selected_bits': [],
            'msb_first': self.direction_msb.isChecked(),
            'by_column': self.order_column.isChecked(),
            'rgb_order': self.rgb_orders.currentText(),
            'include_hex': self.preview_check.isChecked()
        }
        
        for key, checkbox in self.bit_checkboxes.items():
            if checkbox.isChecked():
                channel, bit = key.split('_')
                settings['selected_bits'].append((channel, int(bit)))
                
        return settings

class StegSolvePlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.current_mode = None
        self.image_label = None
        self.mode_combo = None
        self.layout_direction = 'horizontal'
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
        return ""

    def create_ui(self, parent: QWidget, layout: QVBoxLayout) -> None:
        # 创建主布局
        main_widget = QWidget(parent)
        main_widget.setFocusPolicy(Qt.StrongFocus)  # 使widget可以接收键盘事件
        main_widget.keyPressEvent = self._handle_key_press  # 添加键盘事件处理
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 创建控制区域
        control_widget = QWidget(parent)
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加文件选择按钮
        self.file_btn = QPushButton("选择图片", parent)
        self.file_btn.clicked.connect(lambda: self._load_image(parent))
        control_layout.addWidget(self.file_btn)

        # 添加LSB提取按钮
        self.lsb_btn = QPushButton("LSB提取", parent)
        self.lsb_btn.clicked.connect(self._show_lsb_dialog)
        self.lsb_btn.setEnabled(False)  # 初始禁用
        control_layout.addWidget(self.lsb_btn)

        # 添加模式选择下拉框
        mode_label = QLabel("分析模式：", parent)
        mode_label.setFont(FONTS.get("default"))
        control_layout.addWidget(mode_label)

        self.mode_combo = QComboBox(parent)
        self.mode_combo.addItems(self.modes)
        self.mode_combo.currentTextChanged.connect(self._update_image)
        control_layout.addWidget(self.mode_combo)
        
        control_layout.addStretch()
        main_layout.addWidget(control_widget)

        # 创建图片显示区域
        scroll_area = QScrollArea(parent)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { background-color: #2b2b2b; border: none; }")
        
        self.image_label = QLabel(parent)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("QLabel { background-color: #2b2b2b; }")
        scroll_area.setWidget(self.image_label)
        
        main_layout.addWidget(scroll_area)
        layout.addWidget(main_widget)

    def _handle_key_press(self, event: QKeyEvent):
        if not self.current_image:
            return
            
        current_index = self.mode_combo.currentIndex()
        if event.key() == Qt.Key_Left:
            new_index = (current_index - 1) % len(self.modes)
            self.mode_combo.setCurrentIndex(new_index)
        elif event.key() == Qt.Key_Right:
            new_index = (current_index + 1) % len(self.modes)
            self.mode_combo.setCurrentIndex(new_index)

    def _show_lsb_dialog(self):
        if not self.current_image:
            return
            
        dialog = LSBExtractDialog(self, self.image_label.window())  # 传入插件实例和父窗口
        # 连接提取信号
        dialog.preview_btn.clicked.connect(lambda: self._extract_lsb(dialog))
        dialog.extract_btn.clicked.connect(lambda: self._extract_lsb(dialog))
        dialog.exec_()

    def _extract_lsb(self, dialog: LSBExtractDialog):
        """提取LSB数据，返回bytes对象"""
        if not self.current_image:
            return None
            
        try:
            img_array = np.array(self.current_image)
            if len(img_array.shape) == 2:  # 灰度图
                img_array = np.stack((img_array,) * 3, axis=-1)
                
            settings = dialog.get_extract_settings()
            selected_bits = settings['selected_bits']
            msb_first = settings['msb_first']
            by_column = settings['by_column']
            rgb_order = settings['rgb_order']
            include_hex = settings['include_hex']
            
            if not selected_bits:
                QMessageBox.warning(dialog, "警告", "请至少选择一个位平面")
                return None
            
            # 根据RGB顺序重新排列通道
            channel_map = {'R': 0, 'G': 1, 'B': 2}
            channel_indices = [channel_map[c] for c in rgb_order]
            if img_array.shape[2] >= 3:
                img_array = img_array[:, :, channel_indices]
            
            # 创建一个位数组来存储所有提取的位
            height, width = img_array.shape[:2]
            total_bits = []
            
            # 按照行或列的顺序遍历像素
            if by_column:
                pixel_coords = [(x, y) for x in range(width) for y in range(height)]
            else:
                pixel_coords = [(x, y) for y in range(height) for x in range(width)]
            
            # 对每个像素，按RGB顺序提取所选通道的位
            for x, y in pixel_coords:
                for channel, bit in selected_bits:
                    if channel == 'Red':
                        channel_idx = 0
                    elif channel == 'Green':
                        channel_idx = 1
                    elif channel == 'Blue':
                        channel_idx = 2
                    elif channel == 'Alpha':
                        if img_array.shape[2] <= 3:
                            continue
                        channel_idx = 3
                    
                    # 提取位值
                    bit_value = (img_array[y, x, channel_idx] >> bit) & 1
                    total_bits.append(bit_value)
            
            # 如果是MSB优先，反转位顺序
            if msb_first:
                total_bits = total_bits[::-1]
            
            # 将位转换为字节
            total_bits = np.array(total_bits, dtype=np.uint8)
            bytes_data = np.packbits(total_bits)
            
            # 返回原始字节数据
            return bytes_data.tobytes()
            
        except Exception as e:
            QMessageBox.critical(dialog, "错误", f"提取数据时发生错误：{str(e)}")
            return None

    def _load_image(self, parent):
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                self.lsb_btn.setEnabled(True)  # 启用LSB提取按钮
                self._update_image()
            except Exception as e:
                QMessageBox.critical(parent, "错误", f"无法加载图片：{str(e)}")

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
        
        # 确保数据是连续的
        result = np.ascontiguousarray(result)
        qimg = QImage(result.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        # 根据窗口大小缩放图片
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
