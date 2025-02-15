import base64
from plugins import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QLineEdit, QLabel

class CustomBase64:
    """自定义Base64编解码器"""
    def __init__(self, alphabet: str = None):
        # 默认使用标准Base64字母表
        self.standard_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        self.custom_alphabet = alphabet if alphabet and len(alphabet) == 64 else self.standard_alphabet
        self.padding = "="
        
        # 创建编码和解码映射
        self.encode_map = str.maketrans(self.standard_alphabet, self.custom_alphabet)
        self.decode_map = str.maketrans(self.custom_alphabet, self.standard_alphabet)
    
    def encode(self, data: str) -> str:
        # 使用标准base64进行编码
        standard_b64 = base64.b64encode(data.encode()).decode()
        # 使用自定义字母表替换字符
        return standard_b64.translate(self.encode_map)
    
    def decode(self, data: str) -> str:
        try:
            # 使用自定义字母表转换回标准字母表
            standard_b64 = data.translate(self.decode_map)
            # 使用标准base64进行解码
            return base64.b64decode(standard_b64.encode()).decode()
        except Exception as e:
            raise ValueError(f"解码错误: {str(e)}")

class Base64EncodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base64编码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将文本转换为Base64编码，支持自定义码表"
    
    def create_custom_ui(self, parent: QWidget) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建码表输入框
        alphabet_label = QLabel("自定义码表（64个字符）:", parent)
        alphabet_edit = QLineEdit(parent)
        alphabet_edit.setPlaceholderText("留空则使用标准Base64码表")
        alphabet_edit.setText("")
        
        return [
            {
                'type': 'label',
                'widget': alphabet_label
            },
            {
                'type': 'input',
                'key': 'alphabet',
                'widget': alphabet_edit
            }
        ]
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """验证输入参数"""
        alphabet = kwargs.get('alphabet', '')
        if alphabet and len(alphabet) != 64:
            return False, "自定义码表必须包含64个字符"
        if alphabet and len(set(alphabet)) != 64:
            return False, "自定义码表中的字符不能重复"
        return True, ""
    
    def process(self, input_data: str, **kwargs) -> str:
        try:
            alphabet = kwargs.get('alphabet', '')
            encoder = CustomBase64(alphabet)
            return encoder.encode(input_data)
        except Exception as e:
            return f"错误: {str(e)}"

class Base64DecodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base64解码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将Base64编码转换为文本，支持自定义码表"
    
    def create_custom_ui(self, parent: QWidget) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建码表输入框
        alphabet_label = QLabel("自定义码表（64个字符）:", parent)
        alphabet_edit = QLineEdit(parent)
        alphabet_edit.setPlaceholderText("留空则使用标准Base64码表")
        alphabet_edit.setText("")
        
        return [
            {
                'type': 'label',
                'widget': alphabet_label
            },
            {
                'type': 'input',
                'key': 'alphabet',
                'widget': alphabet_edit
            }
        ]
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """验证输入参数"""
        alphabet = kwargs.get('alphabet', '')
        if alphabet and len(alphabet) != 64:
            return False, "自定义码表必须包含64个字符"
        if alphabet and len(set(alphabet)) != 64:
            return False, "自定义码表中的字符不能重复"
        return True, ""
    
    def process(self, input_data: str, **kwargs) -> str:
        try:
            alphabet = kwargs.get('alphabet', '')
            decoder = CustomBase64(alphabet)
            return decoder.decode(input_data)
        except Exception as e:
            return f"错误: {str(e)}"
