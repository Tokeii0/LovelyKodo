from .. import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QTextEdit, QPushButton
from style import FONTS
from urllib.parse import quote, quote_plus, unquote, unquote_plus

class UrlPlugin(Plugin):
    plugin_name = "URL编码转换"
    plugin_category = "编码转换"
    plugin_description = "URL编码和解码工具"
    
    # 使用水平布局
    layout_direction = 'horizontal'
    
    def __init__(self):
        super().__init__()
        self.mode_combo = None
        self.custom_widgets = []
        self.auto_run = True  # 自动运行
        
        # 操作模式列表
        self.modes = ["URL编码", "URL编码(全部字符)", "URL解码"]
        self.current_mode = 0
        
    @property
    def name(self) -> str:
        return self.plugin_name
    
    @property
    def category(self) -> str:
        return self.plugin_category
    
    @property
    def description(self) -> str:
        return self.plugin_description
        
    def create_custom_ui(self, parent: QWidget = None) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签和下拉框
        label = QLabel("操作模式:", parent)
        label.setFixedWidth(80)
        label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.mode_combo = QComboBox(parent)
        self.mode_combo.setFixedWidth(180)
        self.mode_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 添加模式选项
        for mode in self.modes:
            self.mode_combo.addItem(mode)
            
        # 设置默认选项
        self.mode_combo.setCurrentIndex(self.current_mode)
        
        # 连接下拉框变化信号
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        
        # 添加到布局，并添加弹性空间
        layout.addWidget(label)
        layout.addWidget(self.mode_combo)
        layout.addStretch()
        
        # 将布局添加到容器widget
        container = QWidget(parent)
        container.setLayout(layout)
        
        return [
            {
                'type': 'label',
                'widget': label
            },
            {
                'type': 'input',
                'key': 'mode',
                'widget': self.mode_combo
            }
        ]
    
    def on_mode_changed(self, index: int):
        """算法选择变化时触发"""
        self.current_mode = index
        if self.auto_run:
            self.run_process()
    
    def on_input_changed(self, _):
        """输入文本变化时触发"""
        if self.auto_run:
            self.run_process()
    
    def setup_ui(self, input_edit, output_edit):
        """设置UI组件"""
        super().setup_ui(input_edit, output_edit)
        # 连接输入框变化信号
        if input_edit and hasattr(input_edit, 'textChanged'):
            input_edit.textChanged.connect(self.on_input_changed)
    
    def run_process(self):
        """运行处理"""
        if not self.input_edit or not self.output_edit:
            return
            
        input_text = self.input_edit.toPlainText()
        if not input_text:
            self.output_edit.setPlainText("")
            return
            
        try:
            # 获取当前选择的模式
            mode = self.mode_combo.currentText()
            result = self.process(input_text, mode=mode)
            self.output_edit.setPlainText(result)
        except Exception as e:
            self.output_edit.setPlainText(f"错误: {str(e)}")
    
    def process(self, input_data: str, **kwargs) -> str:
        """处理输入数据"""
        mode = kwargs.get('mode', 'URL编码')
        try:
            if mode == "URL编码":
                # 普通URL编码，只编码特殊字符
                return quote(input_data)
            elif mode == "URL编码(全部字符)":
                # 对所有字符进行编码，不管是字母数字还是特殊字符
                # 先将字符串转换为UTF-8字节序列，然后对每个字节进行编码
                encoded = ""
                for b in input_data.encode('utf-8'):
                    encoded += f'%{b:02X}'
                return encoded
            else:  # URL解码
                # 检查是否是我们的全字符编码格式（每个字符都是%XX形式）
                if all(len(part) == 2 and all(c.isalnum() for c in part) 
                      for part in input_data.replace('%', ' ').split() if part):
                    try:
                        # 尝试按照全字符编码格式解码
                        parts = input_data.split('%')
                        # 收集所有字节
                        bytes_data = bytearray()
                        for part in parts:
                            if part:  # 跳过空字符串（开头的%会产生空字符串）
                                bytes_data.append(int(part, 16))
                        # 将字节序列解码为UTF-8字符串
                        return bytes_data.decode('utf-8')
                    except:
                        # 如果解码失败，使用标准URL解码
                        return unquote_plus(input_data)
                else:
                    # 使用标准URL解码
                    return unquote_plus(input_data)
        except Exception as e:
            return f"错误: {str(e)}"
