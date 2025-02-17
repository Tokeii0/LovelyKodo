from plugins import Plugin
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QLabel
import style
from style import FONTS

# Base62字符集
CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def encode_base62(num):
    if num == 0:
        return CHARSET[0]
    
    arr = []
    base = len(CHARSET)
    while num:
        num, rem = divmod(num, base)
        arr.append(CHARSET[rem])
    arr.reverse()
    return ''.join(arr)

def decode_base62(string):
    num = 0
    base = len(CHARSET)
    for char in string:
        num = num * base + CHARSET.index(char)
    return num

class Base62Plugin(Plugin):
    def __init__(self):
        super().__init__()
        self.mode = "encode"  # 默认为编码模式
        
    @property
    def name(self) -> str:
        return "Base62编码/解码"
    
    @property
    def category(self) -> str:
        return "编码转换"
    
    @property
    def description(self) -> str:
        return "将文本转换为Base62编码或将Base62编码解码为文本"

    def process(self, input_data: str, **kwargs) -> str:
        """处理输入数据"""
        if not input_data:
            return ""
            
        try:
            if self.mode == "encode":
                # 将输入字符串转换为bytes，然后转换为整数
                num = int.from_bytes(input_data.encode('utf-8'), 'big')
                # 编码为base62
                return encode_base62(num)
            else:
                # 解码base62为整数
                num = decode_base62(input_data)
                # 转换回bytes，再转换为字符串
                # 计算所需的字节数
                byte_length = (num.bit_length() + 7) // 8
                return num.to_bytes(byte_length, 'big').decode('utf-8')
        except Exception as e:
            return f"错误: {str(e)}"

    def create_custom_ui(self, parent: QWidget) -> list:
        """创建自定义UI控件"""
        # 模式选择
        mode_label = QLabel("模式:", parent)
        mode_label.setFont(FONTS['body'])
        
        self.mode_combo = QComboBox(parent)
        self.mode_combo.setFont(FONTS['body'])
        self.mode_combo.addItems(["编码", "解码"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        
        return [
            {'widget': mode_label, 'type': 'label'},
            {'widget': self.mode_combo, 'type': 'input'}
        ]
    
    def _on_mode_changed(self, text: str):
        """处理模式改变事件"""
        self.mode = "encode" if text == "编码" else "decode"
        # 获取当前输入框的文本
        if hasattr(self, 'input_edit'):
            current_text = self.input_edit.toPlainText()
            if current_text:
                # 重新处理文本
                result = self.process(current_text)
                if hasattr(self, 'output_edit'):
                    self.output_edit.setPlainText(result)
