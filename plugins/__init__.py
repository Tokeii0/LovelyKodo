from abc import ABC, abstractmethod
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

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

    def create_ui(self, parent: QWidget, layout: QVBoxLayout) -> None:
        """创建插件的UI界面
        参数：
            parent: 父级窗口部件
            layout: 右侧区域的布局管理器
        
        默认实现会创建基本的输入输出界面，
        插件可以完全重写这个方法来创建自定义界面
        """
        from PySide6.QtWidgets import QGroupBox, QTextEdit, QPushButton
        import style
        
        # 插件参数区域
        self.param_group = QGroupBox("插件参数", parent)
        self.param_group.setStyleSheet(style.get_group_box_style())
        self.param_group.setObjectName("param_group")
        
        # 根据插件的layout_direction属性决定布局方向
        layout_direction = getattr(self, 'layout_direction', 'vertical')
        self.param_layout = QHBoxLayout(self.param_group) if layout_direction == 'horizontal' else QVBoxLayout(self.param_group)
        self.param_layout.setContentsMargins(10, 20, 10, 10)
        layout.addWidget(self.param_group)
        
        # 添加自定义控件
        self.custom_widgets = self.create_custom_ui(parent)
        if self.custom_widgets:
            current_layout = None
            
            for widget_info in self.custom_widgets:
                if 'widget' in widget_info:
                    if layout_direction == 'horizontal':
                        # 水平布局：标签和输入框放在一起
                        if widget_info.get('type') == 'label':
                            current_layout = QHBoxLayout()
                            current_layout.addWidget(widget_info['widget'])
                            # 如果下一个widget是输入框，将它们放在一起
                            next_index = self.custom_widgets.index(widget_info) + 1
                            if (next_index < len(self.custom_widgets) and 
                                self.custom_widgets[next_index].get('type') == 'input'):
                                current_layout.addWidget(self.custom_widgets[next_index]['widget'])
                                self.custom_widgets[next_index]['processed'] = True
                            self.param_layout.addLayout(current_layout)
                        elif not widget_info.get('processed'):
                            self.param_layout.addWidget(widget_info['widget'])
                    else:
                        # 垂直布局：每个控件独立一行
                        self.param_layout.addWidget(widget_info['widget'])
            
            self.param_group.show()
        else:
            self.param_group.hide()

        # 输入区域
        input_group = QGroupBox("输入", parent)
        input_group.setObjectName("input_group")
        input_group.setStyleSheet(style.get_group_box_style())
        input_layout = QVBoxLayout(input_group)
        
        self.input_edit = QTextEdit(parent)
        self.input_edit.setObjectName("input_edit")
        self.input_edit.setPlaceholderText("在这里输入要处理的文本...")
        self.input_edit.setStyleSheet(style.get_text_edit_style())
        self.input_edit.textChanged.connect(lambda: self._auto_run(parent))
        input_layout.addWidget(self.input_edit)
        layout.addWidget(input_group)

        # 运行按钮
        self.run_btn = QPushButton("执行", parent)
        self.run_btn.setStyleSheet(style.get_run_button_style())
        self.run_btn.setObjectName("run_btn")
        layout.addWidget(self.run_btn)

        # 输出区域
        output_group = QGroupBox("处理结果", parent)
        output_group.setStyleSheet(style.get_group_box_style())
        output_group.setObjectName("output_group")
        output_layout = QVBoxLayout(output_group)
        output_layout.setContentsMargins(10, 20, 10, 10)
        
        self.output_edit = QTextEdit(parent)
        self.output_edit.setPlaceholderText("处理结果将显示在这里...")
        self.output_edit.setStyleSheet(style.get_text_edit_style())
        self.output_edit.setObjectName("output_edit")
        output_layout.addWidget(self.output_edit)
        layout.addWidget(output_group)
        
    def _auto_run(self, parent):
        """当输入文本变化时自动执行插件"""
        if not hasattr(self, 'input_edit') or not hasattr(self, 'output_edit'):
            return
            
        # 获取输入文本
        input_data = self.input_edit.toPlainText()
            
        # 获取自定义参数
        kwargs = {}
        if hasattr(self, 'custom_widgets'):
            for widget_info in self.custom_widgets:
                if 'key' in widget_info and 'widget' in widget_info:
                    widget = widget_info['widget']
                    if hasattr(widget, 'text'):
                        kwargs[widget_info['key']] = widget.text()
                    elif hasattr(widget, 'currentText'):
                        kwargs[widget_info['key']] = widget.currentText()
                        
        # 验证输入
        valid, error = self.validate_input(**kwargs)
        if not valid:
            self.output_edit.setText(error)
            return
            
        # 执行插件
        try:
            result = self.process(input_data, **kwargs)
            self.output_edit.setText(result)
        except Exception as e:
            self.output_edit.setText(f"错误：{str(e)}")

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
