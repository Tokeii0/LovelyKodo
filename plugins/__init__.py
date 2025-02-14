from abc import ABC, abstractmethod
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget

class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """插件分类"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass

    @abstractmethod
    def process(self, input_data: str, **kwargs) -> str:
        """处理数据"""
        pass
        
    def create_custom_ui(self, parent: QWidget) -> List[Dict[str, Any]]:
        """创建自定义UI元素
        返回一个列表，每个元素是一个字典，包含：
        - type: 控件类型 (如 'input', 'combobox')
        - label: 控件标签
        - widget: 控件实例
        - key: 在process方法中使用的参数键名
        """
        return []

    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """验证输入参数
        返回: (是否有效, 错误信息)
        """
        return True, ""
