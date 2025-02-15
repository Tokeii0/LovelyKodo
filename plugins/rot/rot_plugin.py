from plugins import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QLabel, QComboBox, QHBoxLayout, 
    QLineEdit, QSpinBox, QSizePolicy
)
from style import FONTS

class ROTCipher:
    """ROT加密实现类"""
    
    @staticmethod
    def rot_n(text: str, n: int, charset: str, charset_len: int) -> str:
        """通用ROT-N实现"""
        result = ""
        for char in text:
            if char in charset:
                idx = (charset.index(char) + n) % charset_len
                result += charset[idx]
            else:
                result += char
        return result

    @staticmethod
    def rot5(text: str) -> str:
        """ROT5: 仅对数字进行移位"""
        digits = "0123456789"
        return ROTCipher.rot_n(text, 5, digits, 10)

    @staticmethod
    def rot13(text: str) -> str:
        """ROT13: 对字母进行移位"""
        result = ""
        for char in text:
            if char.isalpha():
                # 分别处理大小写
                base = 'A' if char.isupper() else 'a'
                result += chr((ord(char) - ord(base) + 13) % 26 + ord(base))
            else:
                result += char
        return result

    @staticmethod
    def rot18(text: str) -> str:
        """ROT18: 数字ROT5 + 字母ROT13"""
        return ROTCipher.rot13(ROTCipher.rot5(text))

    @staticmethod
    def rot47(text: str) -> str:
        """ROT47: 对可见ASCII字符进行移位"""
        result = ""
        for char in text:
            ascii_val = ord(char)
            if 33 <= ascii_val <= 126:  # 可见ASCII字符范围
                result += chr(33 + ((ascii_val - 33) + 47) % 94)
            else:
                result += char
        return result

    @staticmethod
    def rot8000(text: str) -> str:
        """ROT8000: Unicode版本的ROT13
        在Unicode基本多文种平面内对字符进行0x8000(32768)位移
        这是一个自反函数，加密两次等于解密"""
        result = ""
        for char in text:
            code_point = ord(char)
            # 只处理基本多文种平面内的字符 (U+0000 到 U+FFFF)
            if code_point <= 0xFFFF:
                # 对字符进行0x8000位移
                new_point = code_point ^ 0x8000
                result += chr(new_point)
            else:
                # 超出范围的字符保持不变
                result += char
        return result

    @staticmethod
    def rot_custom(text: str, shift: int) -> str:
        """自定义ROT-N: 对字母进行指定位数移位"""
        result = ""
        for char in text:
            if char.isalpha():
                # 分别处理大小写
                base = 'A' if char.isupper() else 'a'
                result += chr((ord(char) - ord(base) + shift) % 26 + ord(base))
            else:
                result += char
        return result

class ROTPlugin(Plugin):
    # 使用水平布局
    layout_direction = 'horizontal'
    
    def __init__(self):
        super().__init__()
        self.cipher = ROTCipher()
        self.rot_combo = None
        self.shift_spin = None
        self.input_edit = None
        self.auto_run = True
        
        # ROT类型列表
        self.rot_types = [
            "ROT5 (仅数字)",
            "ROT13 (仅字母)",
            "ROT18 (数字+字母)",
            "ROT47 (ASCII)",
            "ROT8000 (Unicode)",
            "自定义ROT-N"
        ]

    @property
    def name(self) -> str:
        return "ROT加密"

    @property
    def category(self) -> str:
        return "加密解密"

    @property
    def description(self) -> str:
        return "支持ROT5/13/18/47和自定义ROT-N的加密解密工具"

    def create_input(self, parent: QWidget = None) -> Dict[str, Any]:
        """创建输入框"""
        self.input_edit = QLineEdit(parent)
        self.input_edit.setStyleSheet(f"font: {FONTS['mono']};")
        self.input_edit.setPlaceholderText("输入要加密/解密的文本")
        return {"widget": self.input_edit}

    def process(self, text: str) -> str:
        """处理输入文本"""
        if not text:
            return ""
            
        try:
            rot_type = self.rot_combo.currentText()
            
            if rot_type == "ROT5 (仅数字)":
                return self.cipher.rot5(text)
            elif rot_type == "ROT13 (仅字母)":
                return self.cipher.rot13(text)
            elif rot_type == "ROT18 (数字+字母)":
                return self.cipher.rot18(text)
            elif rot_type == "ROT47 (ASCII)":
                return self.cipher.rot47(text)
            elif rot_type == "ROT8000 (Unicode)":
                return self.cipher.rot8000(text)
            else:  # 自定义ROT-N
                shift = self.shift_spin.value()
                return self.cipher.rot_custom(text, shift)
                
        except Exception as e:
            return f"处理出错：{str(e)}"

    def create_custom_ui(self, parent: QWidget = None) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建容器widget
        container = QWidget(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 创建ROT类型选择
        type_label = QLabel("ROT类型:", parent)
        type_label.setFixedWidth(70)
        type_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.rot_combo = QComboBox(parent)
        self.rot_combo.addItems(self.rot_types)
        self.rot_combo.setFixedWidth(200)  
        self.rot_combo.setStyleSheet(f"""
            font: {FONTS['body']};
            QComboBox {{
                min-width: 200px;
                padding: 5px;
            }}
            QComboBox QAbstractItemView {{
                min-width: 200px;
                padding: 5px;
            }}
        """)
        
        # 创建自定义位移输入
        shift_label = QLabel("位移量:", parent)
        shift_label.setFixedWidth(70)
        shift_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.shift_spin = QSpinBox(parent)
        self.shift_spin.setRange(1, 25)
        self.shift_spin.setValue(13)
        self.shift_spin.setFixedWidth(80)
        self.shift_spin.setStyleSheet(f"font: {FONTS['body']};")

        # 添加弹性空间
        spacer = QWidget(parent)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 根据ROT类型显示/隐藏位移输入
        def update_shift_visibility():
            is_custom = self.rot_combo.currentText() == "自定义ROT-N"
            shift_label.setVisible(is_custom)
            self.shift_spin.setVisible(is_custom)
        
        self.rot_combo.currentTextChanged.connect(update_shift_visibility)
        update_shift_visibility()
        
        # 添加所有控件到布局
        widgets = [
            (type_label, None),
            (self.rot_combo, None),
            (shift_label, None),
            (self.shift_spin, None),
            (spacer, 1)
        ]
        
        for widget, stretch in widgets:
            layout.addWidget(widget)
            if stretch is not None:
                layout.setStretch(layout.count() - 1, stretch)
        
        container.setLayout(layout)
        return [{"widget": container}]
