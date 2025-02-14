import base64
from plugins import Plugin

class Base64EncodePlugin(Plugin):
    @property
    def name(self) -> str:
        return "Base64编码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将文本转换为Base64编码"
    
    def process(self, input_data: str) -> str:
        try:
            return base64.b64encode(input_data.encode()).decode()
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
        return "将Base64编码转换为文本"
    
    def process(self, input_data: str) -> str:
        try:
            return base64.b64decode(input_data.encode()).decode()
        except Exception as e:
            return f"错误: {str(e)}"
