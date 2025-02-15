from plugins import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QComboBox, QCheckBox
from style import FONTS

class NumberSystemConverter:
    """进制转换器"""
    @staticmethod
    def convert(number: str, from_base: int, to_base: int) -> str:
        """在不同进制之间转换数字"""
        try:
            # 先将输入转换为10进制整数
            decimal = int(number, from_base)
            
            # 然后转换到目标进制
            if to_base == 2:
                return bin(decimal)[2:]  # 去掉'0b'前缀
            elif to_base == 8:
                return oct(decimal)[2:]  # 去掉'0o'前缀
            elif to_base == 10:
                return str(decimal)
            elif to_base == 16:
                return hex(decimal)[2:]  # 去掉'0x'前缀
            else:
                raise ValueError(f"不支持的目标进制: {to_base}")
        except ValueError as e:
            raise ValueError(f"无效的输入格式: {str(e)}")
    
    @staticmethod
    def convert_string(text: str, to_base: int) -> List[str]:
        """将字符串转换为指定进制"""
        try:
            # 将字符串中的每个字符转换为指定进制
            result = []
            for char in text:
                decimal = ord(char)  # 空格的ASCII码是32
                if to_base == 2:
                    result.append(bin(decimal)[2:].zfill(8))
                elif to_base == 8:
                    result.append(oct(decimal)[2:].zfill(3))
                elif to_base == 10:
                    result.append(str(decimal))
                elif to_base == 16:
                    result.append(hex(decimal)[2:].zfill(2))
                else:
                    raise ValueError(f"不支持的目标进制: {to_base}")
            return result
        except Exception as e:
            raise ValueError(f"字符串转换错误: {str(e)}")
    
    @staticmethod
    def convert_from_string(numbers: List[str], from_base: int) -> str:
        """将指定进制的数字列表转换回字符串"""
        try:
            result = []
            for num in numbers:
                if num:  # 处理空字符串
                    decimal = int(num, from_base)
                    if not (0 <= decimal <= 0x10FFFF):  # Unicode 字符范围检查
                        raise ValueError(f"无效的字符编码: {decimal}")
                    result.append(chr(decimal))
            return ''.join(result)
        except Exception as e:
            raise ValueError(f"数字转换为字符串错误: {str(e)}")

class NumberSystemPlugin(Plugin):
    # 设置水平布局
    layout_direction = 'horizontal'
    
    @property
    def name(self) -> str:
        return "进制转换"
    
    @property
    def category(self) -> str:
        return "数值转换"
    
    @property
    def description(self) -> str:
        return "在2进制、8进制、10进制、16进制之间转换数字，支持字符串转换"
    
    def create_custom_ui(self, parent: QWidget) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建源进制选择下拉框
        from_base_label = QLabel("源进制:", parent)
        from_base_label.setStyleSheet(f"font: {FONTS['body']};")
        from_base_combo = QComboBox(parent)
        from_base_combo.addItems(["字符串", "2进制", "8进制", "10进制", "16进制"])
        from_base_combo.setCurrentText("字符串")
        from_base_combo.setFixedWidth(100)  # 设置固定宽度
        from_base_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建目标进制选择下拉框
        to_base_label = QLabel("目标进制:", parent)
        to_base_label.setStyleSheet(f"font: {FONTS['body']};")
        to_base_combo = QComboBox(parent)
        to_base_combo.addItems(["字符串", "2进制", "8进制", "10进制", "16进制"])
        to_base_combo.setCurrentText("16进制")
        to_base_combo.setFixedWidth(100)  # 设置固定宽度
        to_base_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建分隔符选择下拉框
        separator_label = QLabel("分隔符:", parent)
        separator_label.setStyleSheet(f"font: {FONTS['body']};")
        separator_combo = QComboBox(parent)
        separator_combo.addItems(["空格", "逗号", "分号", "无"])
        separator_combo.setCurrentText("空格")
        separator_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建前导零选项
        padding_check = QCheckBox("使用前导零填充", parent)
        padding_check.setChecked(True)
        padding_check.setStyleSheet(f"font: {FONTS['body']};")
        
        return [
            {
                'type': 'label',
                'widget': from_base_label
            },
            {
                'type': 'input',
                'key': 'from_base',
                'widget': from_base_combo
            },
            {
                'type': 'label',
                'widget': to_base_label
            },
            {
                'type': 'input',
                'key': 'to_base',
                'widget': to_base_combo
            },
            {
                'type': 'label',
                'widget': separator_label
            },
            {
                'type': 'input',
                'key': 'separator',
                'widget': separator_combo
            },
            {
                'type': 'input',
                'key': 'padding',
                'widget': padding_check
            }
        ]
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """验证输入参数"""
        from_base = kwargs.get('from_base', '')
        to_base = kwargs.get('to_base', '')
        
        if not from_base or not to_base:
            return False, "请选择源进制和目标进制"
            
        return True, ""
    
    def process(self, input_data: str, **kwargs) -> str:
        try:
            # 不去除首尾空格，因为空格也是有效字符
            if not input_data and input_data != ' ':  # 允许单个空格作为输入
                return "请输入要转换的内容"
            
            # 获取参数
            from_base_str = kwargs.get('from_base', '字符串')
            to_base_str = kwargs.get('to_base', '16进制')
            separator_str = kwargs.get('separator', '空格')
            use_padding = kwargs.get('padding') == 'true'
            
            # 设置分隔符
            separator_map = {
                '空格': ' ',
                '逗号': ',',
                '分号': ';',
                '无': ''
            }
            separator = separator_map.get(separator_str, ' ')
            
            # 进制映射
            base_map = {
                '2进制': 2,
                '8进制': 8,
                '10进制': 10,
                '16进制': 16
            }
            
            # 获取目标进制
            to_base = base_map.get(to_base_str)
            
            # 字符串 -> 进制
            if from_base_str == '字符串':
                if to_base_str == '字符串':
                    return input_data
                result = NumberSystemConverter.convert_string(input_data, to_base)
                return separator.join(result)
            
            # 进制 -> 字符串
            elif to_base_str == '字符串':
                from_base = base_map.get(from_base_str)
                if not from_base:
                    return "不支持的源进制类型"
                # 分割输入数据，保留空字符串（它们可能是数字）
                numbers = input_data.split()
                if not numbers:
                    return "输入格式错误"
                return NumberSystemConverter.convert_from_string(numbers, from_base)
            
            # 进制 -> 进制
            else:
                from_base = base_map.get(from_base_str)
                if not from_base or not to_base:
                    return "不支持的进制类型"
                    
                # 分割输入数据，支持多个数字转换
                numbers = input_data.split()
                if not numbers:
                    return "输入格式错误"
                result = []
                for num in numbers:
                    if num.strip():  # 跳过空字符串
                        converted = NumberSystemConverter.convert(num, from_base, to_base)
                        # 添加前导零
                        if use_padding:
                            if to_base == 2:
                                converted = converted.zfill(8)
                            elif to_base == 8:
                                converted = converted.zfill(3)
                            elif to_base == 16:
                                converted = converted.zfill(2)
                        result.append(converted)
                return separator.join(result)
                
        except ValueError as e:
            return f"错误: {str(e)}"
        except Exception as e:
            return f"转换错误: {str(e)}"
