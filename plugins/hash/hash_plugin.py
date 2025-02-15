import hashlib
from plugins import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QTextEdit
from style import FONTS

class HashCalculator:
    """哈希计算器"""
    
    # 支持的哈希算法
    ALGORITHMS = {
        "MD5 (128位)": hashlib.md5,
        "SHA1 (160位)": hashlib.sha1,
        "SHA224 (224位)": hashlib.sha224,
        "SHA256 (256位)": hashlib.sha256,
        "SHA384 (384位)": hashlib.sha384,
        "SHA512 (512位)": hashlib.sha512,
        "SHA3-224 (224位)": hashlib.sha3_224,
        "SHA3-256 (256位)": hashlib.sha3_256,
        "SHA3-384 (384位)": hashlib.sha3_384,
        "SHA3-512 (512位)": hashlib.sha3_512,
        "BLAKE2s (256位)": hashlib.blake2s,
        "BLAKE2b (512位)": hashlib.blake2b,
        "SHAKE128 (128位)": hashlib.shake_128,
        "SHAKE256 (256位)": hashlib.shake_256,
        "RIPEMD160 (160位)": 'ripemd160',
        "Whirlpool (512位)": 'whirlpool'
    }
    
    @staticmethod
    def calculate(text: str, algorithm: str) -> str:
        """计算哈希值"""
        try:
            if not text:
                return ""
                
            if algorithm not in HashCalculator.ALGORITHMS:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
                
            hash_func = HashCalculator.ALGORITHMS[algorithm]
            
            # 处理特殊的哈希算法
            if algorithm in ["SHAKE128 (128位)", "SHAKE256 (256位)"]:
                length = 128 if "128" in algorithm else 256
                h = hash_func()
                h.update(text.encode())
                return h.hexdigest(length // 8)  # 转换为字节长度
            elif algorithm in ["RIPEMD160 (160位)", "Whirlpool (512位)"]:
                h = hashlib.new(hash_func)
                h.update(text.encode())
                return h.hexdigest()
            else:
                h = hash_func()
                h.update(text.encode())
                return h.hexdigest()
                
        except Exception as e:
            raise ValueError(f"哈希计算错误: {str(e)}")

class HashPlugin(Plugin):
    # 插件基本信息
    plugin_name = "哈希计算"
    plugin_category = "哈希计算"
    plugin_description = "使用多种算法计算文本的哈希值"
    
    # 使用水平布局
    layout_direction = 'horizontal'
    
    def __init__(self):
        super().__init__()
        self.calculator = HashCalculator()
        self.algorithm_combo = None
        self.custom_widgets = []
        self.auto_run = True  # 启用自动运行
    
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
        label = QLabel("算法:", parent)
        label.setFixedWidth(40)
        label.setStyleSheet(f"font: {FONTS['body']};")
        self.algorithm_combo = QComboBox(parent)
        self.algorithm_combo.setFixedWidth(180)
        self.algorithm_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 添加算法选项
        for algo in self.calculator.ALGORITHMS:
            self.algorithm_combo.addItem(algo)
            
        # 设置默认选项
        default_index = self.algorithm_combo.findText("SHA256 (256位)")
        if default_index >= 0:
            self.algorithm_combo.setCurrentIndex(default_index)
        
        # 连接下拉框变化信号
        self.algorithm_combo.currentTextChanged.connect(self.on_algorithm_changed)
            
        # 添加到布局，并添加弹性空间
        layout.addWidget(label)
        layout.addWidget(self.algorithm_combo)
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
                'key': 'algorithm',
                'widget': self.algorithm_combo
            }
        ]
    
    def on_algorithm_changed(self, _):
        """算法选择变化时触发"""
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
            algorithm = self.algorithm_combo.currentText()
            result = self.calculator.calculate(input_text, algorithm)
            self.output_edit.setPlainText(result)
        except Exception as e:
            self.output_edit.setPlainText(f"错误: {str(e)}")
    
    def process(self, input_data: str, **kwargs) -> str:
        try:
            if not input_data:
                return "请输入要计算哈希的文本"
            
            algorithm = self.algorithm_combo.currentText()
            return self.calculator.calculate(input_data, algorithm)
            
        except ValueError as e:
            return f"错误: {str(e)}"
