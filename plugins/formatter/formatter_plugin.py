import json
import xml.dom.minidom
import sqlparse
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QLabel, QComboBox, QHBoxLayout,
    QSpinBox, QSizePolicy, QCheckBox
)
from plugins import Plugin
from style import FONTS

class Formatter:
    """格式化工具类"""
    
    @staticmethod
    def format_json(text: str, indent: int = 4, sort_keys: bool = False) -> str:
        """JSON格式化"""
        try:
            # 首先尝试解析JSON
            obj = json.loads(text)
            # 返回格式化的JSON
            return json.dumps(obj, ensure_ascii=False, indent=indent, sort_keys=sort_keys)
        except json.JSONDecodeError as e:
            return f"JSON格式错误：{str(e)}"

    @staticmethod
    def format_xml(text: str, indent: str = '    ') -> str:
        """XML格式化"""
        try:
            # 解析XML
            dom = xml.dom.minidom.parseString(text)
            # 使用指定的缩进格式化
            formatted = dom.toprettyxml(indent=indent)
            # 移除空行
            lines = [line for line in formatted.split('\n') if line.strip()]
            return '\n'.join(lines)
        except Exception as e:
            return f"XML格式错误：{str(e)}"

    @staticmethod
    def format_sql(text: str, indent_width: int = 4) -> str:
        """SQL格式化"""
        try:
            # 使用sqlparse格式化SQL
            formatted = sqlparse.format(
                text,
                reindent=True,
                keyword_case='upper',
                indent_width=indent_width,
                indent_tabs=False
            )
            return formatted
        except Exception as e:
            return f"SQL格式错误：{str(e)}"

    @staticmethod
    def minify_json(text: str) -> str:
        """JSON压缩"""
        try:
            return json.dumps(json.loads(text), ensure_ascii=False, separators=(',', ':'))
        except json.JSONDecodeError as e:
            return f"JSON格式错误：{str(e)}"

    @staticmethod
    def minify_xml(text: str) -> str:
        """XML压缩"""
        try:
            dom = xml.dom.minidom.parseString(text)
            return dom.toxml()
        except Exception as e:
            return f"XML格式错误：{str(e)}"

    @staticmethod
    def minify_sql(text: str) -> str:
        """SQL压缩"""
        try:
            return sqlparse.format(text, strip_comments=True, strip_whitespace=True)
        except Exception as e:
            return f"SQL格式错误：{str(e)}"

class FormatterPlugin(Plugin):
    # 插件基本信息
    name = "格式美化"
    description = "支持JSON、XML、SQL等格式的美化和压缩"
    category = "格式化"
    
    # 使用水平布局
    layout_direction = 'horizontal'
    
    def __init__(self):
        super().__init__()
        self.formatter = Formatter()
        self.format_combo = None
        self.indent_spin = None
        self.sort_check = None
        self.minify_check = None
        self.auto_run = True
        
        # 格式类型列表
        self.format_types = [
            "JSON",
            "XML",
            "SQL"
        ]

    def create_custom_ui(self, parent: QWidget = None) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建容器widget
        container = QWidget(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 创建格式类型选择
        type_label = QLabel("格式类型:", parent)
        type_label.setFixedWidth(70)
        type_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.format_combo = QComboBox(parent)
        self.format_combo.addItems(self.format_types)
        self.format_combo.setFixedWidth(120)
        self.format_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建缩进设置
        indent_label = QLabel("缩进量:", parent)
        indent_label.setFixedWidth(70)
        indent_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.indent_spin = QSpinBox(parent)
        self.indent_spin.setRange(1, 8)
        self.indent_spin.setValue(4)
        self.indent_spin.setFixedWidth(60)
        self.indent_spin.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建排序选项（仅用于JSON）
        self.sort_check = QCheckBox("排序键", parent)
        self.sort_check.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建压缩选项
        self.minify_check = QCheckBox("压缩", parent)
        self.minify_check.setStyleSheet(f"font: {FONTS['body']};")

        # 添加弹性空间
        spacer = QWidget(parent)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 根据格式类型显示/隐藏选项
        def update_options_visibility():
            is_json = self.format_combo.currentText() == "JSON"
            self.sort_check.setVisible(is_json)
        
        self.format_combo.currentTextChanged.connect(update_options_visibility)
        update_options_visibility()
        
        # 添加所有控件到布局
        widgets = [
            (type_label, None),
            (self.format_combo, None),
            (indent_label, None),
            (self.indent_spin, None),
            (self.sort_check, None),
            (self.minify_check, None),
            (spacer, 1)
        ]
        
        for widget, stretch in widgets:
            layout.addWidget(widget)
            if stretch is not None:
                layout.setStretch(layout.count() - 1, stretch)
        
        container.setLayout(layout)
        return [{"widget": container}]

    def process(self, text: str) -> str:
        """处理输入文本"""
        if not text:
            return ""
            
        try:
            format_type = self.format_combo.currentText()
            indent = self.indent_spin.value()
            is_minify = self.minify_check.isChecked()
            
            if format_type == "JSON":
                if is_minify:
                    return self.formatter.minify_json(text)
                else:
                    sort_keys = self.sort_check.isChecked()
                    return self.formatter.format_json(text, indent, sort_keys)
                    
            elif format_type == "XML":
                if is_minify:
                    return self.formatter.minify_xml(text)
                else:
                    return self.formatter.format_xml(text, ' ' * indent)
                    
            elif format_type == "SQL":
                if is_minify:
                    return self.formatter.minify_sql(text)
                else:
                    return self.formatter.format_sql(text, indent)
                
        except Exception as e:
            return f"处理出错：{str(e)}"
            
        return text
