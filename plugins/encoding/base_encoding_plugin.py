from plugins import Plugin
import base64
import base58
import base45
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout
from style import FONTS


class Base16EncodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base16编码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将文本转换为Base16编码"
    
    def process(self, text: str) -> str:
        try:
            return base64.b16encode(text.encode()).decode()
        except Exception as e:
            return f"编码失败: {str(e)}"


class Base16DecodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base16解码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将Base16编码转换为原文"
    
    def process(self, text: str) -> str:
        try:
            return base64.b16decode(text.encode()).decode()
        except Exception as e:
            return f"解码失败: {str(e)}"


class Base32EncodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base32编码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将文本转换为Base32编码"
    
    def process(self, text: str) -> str:
        try:
            return base64.b32encode(text.encode()).decode()
        except Exception as e:
            return f"编码失败: {str(e)}"


class Base32DecodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base32解码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将Base32编码转换为原文"
    
    def process(self, text: str) -> str:
        try:
            return base64.b32decode(text.encode()).decode()
        except Exception as e:
            return f"解码失败: {str(e)}"


class Base45EncodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base45编码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将文本转换为Base45编码"
    
    def process(self, text: str) -> str:
        try:
            return base45.b45encode(text.encode()).decode()
        except Exception as e:
            return f"编码失败: {str(e)}"


class Base45DecodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base45解码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将Base45编码转换为原文"
    
    def process(self, text: str) -> str:
        try:
            return base45.b45decode(text.encode()).decode()
        except Exception as e:
            return f"解码失败: {str(e)}"


class Base58EncodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base58编码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将文本转换为Base58编码"
    
    def process(self, text: str) -> str:
        try:
            return base58.b58encode(text.encode()).decode()
        except Exception as e:
            return f"编码失败: {str(e)}"


class Base58DecodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base58解码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将Base58编码转换为原文"
    
    def process(self, text: str) -> str:
        try:
            return base58.b58decode(text.encode()).decode()
        except Exception as e:
            return f"解码失败: {str(e)}"
