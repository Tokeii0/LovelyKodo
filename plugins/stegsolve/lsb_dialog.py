from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QPushButton, QFileDialog, QMessageBox,
                              QTextEdit, QCheckBox, QGroupBox, QRadioButton)
from PySide6.QtCore import Qt

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
        self.extract_btn.clicked.connect(self._preview_data)

    def closeEvent(self, event):
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
        selected_bits = []
        for key, checkbox in self.bit_checkboxes.items():
            if checkbox.isChecked():
                channel, bit = key.split('_')
                selected_bits.append((channel, int(bit)))
                
        return {
            'selected_bits': selected_bits,
            'msb_first': self.direction_msb.isChecked(),
            'by_column': self.order_column.isChecked(),
            'rgb_order': self.rgb_orders.currentText(),
            'include_hex': self.preview_check.isChecked()
        }
