from plugins import Plugin
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QFileDialog, QLabel, QSpinBox,
    QScrollArea, QGroupBox
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt
import os
import style
from style import FONTS

class HexDumpPlugin(Plugin):
    name = "十六进制查看器"
    description = "以十六进制格式查看文件内容"
    category = "文件工具"
    
    def __init__(self):
        super().__init__()
        self.file_data = None
        self.current_file = None
        self.hex_view = None
        self.file_label = None
        self.bytes_spin = None
        self.bytes_per_line = 16
        
    def create_ui(self, parent: QWidget, layout: QVBoxLayout) -> None:
        """创建自定义UI界面"""
        # 创建主容器
        container = QWidget(parent)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # 创建工具栏组
        toolbar_group = QGroupBox("工具栏", parent)
        toolbar_group.setStyleSheet(style.get_group_box_style())
        toolbar = QHBoxLayout(toolbar_group)
        
        # 文件选择区域
        file_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件", parent)
        self.file_label.setStyleSheet(f"font: {FONTS['body']};")
        
        select_btn = QPushButton("打开文件", parent)
        select_btn.setStyleSheet(f"font: {FONTS['body']};")
        select_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_btn)
        file_layout.addStretch()
        
        # 每行字节数选择
        bytes_layout = QHBoxLayout()
        bytes_label = QLabel("每行字节数:", parent)
        bytes_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.bytes_spin = QSpinBox(parent)
        self.bytes_spin.setRange(8, 32)
        self.bytes_spin.setValue(16)
        self.bytes_spin.setSingleStep(8)
        self.bytes_spin.valueChanged.connect(self.update_view)
        self.bytes_spin.setStyleSheet(f"font: {FONTS['body']};")
        self.bytes_spin.setFixedWidth(80)
        
        bytes_layout.addWidget(bytes_label)
        bytes_layout.addWidget(self.bytes_spin)
        bytes_layout.addStretch()
        
        # 添加到工具栏
        toolbar.addLayout(file_layout)
        toolbar.addLayout(bytes_layout)
        main_layout.addWidget(toolbar_group)
        
        # 创建十六进制显示组
        hex_group = QGroupBox("十六进制视图", parent)
        hex_group.setStyleSheet(style.get_group_box_style())
        hex_layout = QVBoxLayout(hex_group)
        
        # 创建十六进制显示区域
        scroll_area = QScrollArea(parent)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.hex_view = QTextEdit(parent)
        self.hex_view.setReadOnly(True)
        # 使用等宽字体
        font = QFont("Courier New", 12)
        font.setFixedPitch(True)
        self.hex_view.setFont(font)
        # 设置样式
        self.hex_view.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
        """)
        
        scroll_area.setWidget(self.hex_view)
        hex_layout.addWidget(scroll_area)
        main_layout.addWidget(hex_group)
        
        # 添加到插件布局
        layout.addWidget(container)
        
    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "选择文件",
            "",
            "所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    self.file_data = f.read()
                self.current_file = file_path
                self.file_label.setText(os.path.basename(file_path))
                self.update_view()
            except Exception as e:
                self.hex_view.setText(f"错误：{str(e)}")
    
    def update_view(self):
        """更新十六进制视图"""
        if not self.file_data:
            return
            
        self.bytes_per_line = self.bytes_spin.value()
        hex_dump = []
        
        # 添加列标题
        header = "Offset    "
        # 添加十六进制列标题
        for i in range(self.bytes_per_line):
            header += f"{i:02X} "
        # 补充空格使其与数据行对齐
        header = header.ljust(self.bytes_per_line * 3 + 10)
        header += "|ASCII字符|"
        hex_dump.append(header)
        hex_dump.append("-" * len(header))
        
        # 生成十六进制显示
        for i in range(0, len(self.file_data), self.bytes_per_line):
            # 获取当前行的字节
            chunk = self.file_data[i:i+self.bytes_per_line]
            
            # 十六进制部分
            hex_line = []
            for b in chunk:
                hex_line.append(f"{b:02X}")
            
            # ASCII部分
            ascii_line = []
            for b in chunk:
                if 32 <= b <= 126:  # 可打印字符
                    ascii_line.append(chr(b))
                else:
                    ascii_line.append('.')
                    
            # 格式化输出
            offset = f"{i:08X}"
            hex_part = " ".join(hex_line).ljust(self.bytes_per_line * 3 - 1)
            ascii_part = "".join(ascii_line)
            
            hex_dump.append(f"{offset}  {hex_part}  |{ascii_part}|")
            
        self.hex_view.setText("\n".join(hex_dump))
    
    def process(self, text: str) -> str:
        """处理输入文本"""
        if not text:
            return ""
            
        try:
            self.file_data = text.encode('utf-8')
            self.update_view()
            return ""
        except Exception as e:
            return f"错误: {str(e)}"
