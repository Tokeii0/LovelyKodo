import base64
from plugins import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QComboBox
from style import FONTS

class RC4:
    """RC4加密解密工具"""
    @staticmethod
    def crypt(text: str, key: str, is_encrypt: bool = True, input_format: str = "text", output_format: str = "base64") -> str:
        """RC4加密/解密
        
        Args:
            text: 要处理的文本
            key: 密钥
            is_encrypt: True表示加密，False表示解密
            input_format: 输入格式，可选 'text'、'hex'、'base64'
            output_format: 输出格式，可选 'text'、'hex'、'base64'
        """
        try:
            if not text or not key:
                return ""
            
            # 处理输入格式
            if input_format == "hex":
                try:
                    text_bytes = bytes.fromhex(text)
                except:
                    raise ValueError("无效的十六进制格式")
            elif input_format == "base64":
                try:
                    text_bytes = base64.b64decode(text.encode())
                except:
                    raise ValueError("无效的base64编码")
            else:  # text
                text_bytes = text.encode()
            
            # 初始化S盒
            S = list(range(256))
            j = 0
            key_bytes = key.encode()
            key_length = len(key_bytes)
            
            # 初始置换
            for i in range(256):
                j = (j + S[i] + key_bytes[i % key_length]) % 256
                S[i], S[j] = S[j], S[i]
            
            # 生成密钥流
            i = j = 0
            result = []
            
            for byte in text_bytes:
                i = (i + 1) % 256
                j = (j + S[i]) % 256
                S[i], S[j] = S[j], S[i]
                k = S[(S[i] + S[j]) % 256]
                result.append(byte ^ k)
            
            # 处理输出格式
            result_bytes = bytes(result)
            if output_format == "hex":
                return result_bytes.hex()
            elif output_format == "base64":
                return base64.b64encode(result_bytes).decode()
            else:  # text
                try:
                    return result_bytes.decode()
                except:
                    raise ValueError("结果无法解码为文本，请尝试其他输出格式")
                
        except Exception as e:
            raise ValueError(f"{'加密' if is_encrypt else '解密'}错误: {str(e)}")

class RC4Plugin(Plugin):
    # 使用水平布局
    layout_direction = 'horizontal'
    
    def __init__(self):
        super().__init__()
        self.rc4 = RC4()
        self.key_edit = None
        self.operation_combo = None
        self.input_format_combo = None
        self.output_format_combo = None
        self.auto_run = True
    
    @property
    def name(self) -> str:
        return "RC4加密/解密"
    
    @property
    def category(self) -> str:
        return "加密/解密"
    
    @property
    def description(self) -> str:
        return "使用RC4算法加密/解密文本"
    
    def create_custom_ui(self, parent: QWidget = None) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建容器widget
        container = QWidget(parent)
        
        # 创建水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建操作选择下拉框
        op_label = QLabel("操作:", parent)
        op_label.setFixedWidth(40)
        op_label.setStyleSheet(f"font: {FONTS['body']};")
        self.operation_combo = QComboBox(parent)
        self.operation_combo.setFixedWidth(80)
        self.operation_combo.setStyleSheet(f"font: {FONTS['body']};")
        self.operation_combo.addItems(["加密", "解密"])
        self.operation_combo.currentTextChanged.connect(self.on_input_changed)
        
        # 创建输入格式选择下拉框
        input_format_label = QLabel("输入格式:", parent)
        input_format_label.setFixedWidth(60)
        input_format_label.setStyleSheet(f"font: {FONTS['body']};")
        self.input_format_combo = QComboBox(parent)
        self.input_format_combo.setFixedWidth(80)
        self.input_format_combo.setStyleSheet(f"font: {FONTS['body']};")
        self.input_format_combo.addItems(["文本", "十六进制", "Base64"])
        self.input_format_combo.currentTextChanged.connect(self.on_input_changed)
        
        # 创建输出格式选择下拉框
        output_format_label = QLabel("输出格式:", parent)
        output_format_label.setFixedWidth(60)
        output_format_label.setStyleSheet(f"font: {FONTS['body']};")
        self.output_format_combo = QComboBox(parent)
        self.output_format_combo.setFixedWidth(80)
        self.output_format_combo.setStyleSheet(f"font: {FONTS['body']};")
        self.output_format_combo.addItems(["文本", "十六进制", "Base64"])
        self.output_format_combo.setCurrentText("Base64")
        self.output_format_combo.currentTextChanged.connect(self.on_input_changed)
        
        # 创建密钥输入框
        key_label = QLabel("密钥:", parent)
        key_label.setFixedWidth(40)
        key_label.setStyleSheet(f"font: {FONTS['body']};")
        self.key_edit = QLineEdit(parent)
        self.key_edit.setFixedWidth(120)
        self.key_edit.setStyleSheet(f"font: {FONTS['body']};")
        self.key_edit.textChanged.connect(self.on_input_changed)
        
        # 添加所有控件到布局
        widgets = [
            (op_label, None),
            (self.operation_combo, None),
            (input_format_label, None),
            (self.input_format_combo, None),
            (output_format_label, None),
            (self.output_format_combo, None),
            (key_label, None),
            (self.key_edit, None)
        ]
        
        for widget, stretch in widgets:
            layout.addWidget(widget)
            if stretch is not None:
                layout.setStretch(layout.count() - 1, stretch)
        
        # 设置容器的布局
        container.setLayout(layout)
        
        return [{"widget": container}]
    
    def on_input_changed(self, _):
        """输入变化时触发"""
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
            is_encrypt = self.operation_combo.currentText() == "加密"
            key = self.key_edit.text()
            
            # 获取输入输出格式
            input_format = self.input_format_combo.currentText()
            output_format = self.output_format_combo.currentText()
            
            # 转换格式名称
            format_map = {
                "文本": "text",
                "十六进制": "hex",
                "Base64": "base64"
            }
            
            input_format = format_map[input_format]
            output_format = format_map[output_format]
            
            # 调用RC4加密/解密
            result = self.rc4.crypt(input_text, key, is_encrypt, input_format, output_format)
            self.output_edit.setPlainText(result)
        except Exception as e:
            self.output_edit.setPlainText(f"错误: {str(e)}")
    
    def process(self, input_data: str, **kwargs) -> str:
        try:
            if not input_data:
                return "请输入要处理的文本"
            
            key = self.key_edit.text()
            if not key:
                return "请输入密钥"
                
            is_encrypt = self.operation_combo.currentText() == "加密"
            input_format = self.input_format_combo.currentText()
            output_format = self.output_format_combo.currentText()
            
            # 转换格式名称
            format_map = {
                "文本": "text",
                "十六进制": "hex",
                "Base64": "base64"
            }
            
            input_format = format_map[input_format]
            output_format = format_map[output_format]
            
            return self.rc4.crypt(input_data, key, is_encrypt, input_format, output_format)
            
        except ValueError as e:
            return f"错误: {str(e)}"
