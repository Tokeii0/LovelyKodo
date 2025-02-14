from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton,
                               QSplitter, QGroupBox, QLineEdit)
from PySide6.QtCore import Qt
import style
from .title_bar import TitleBar
import os
import importlib
import inspect
from plugins import Plugin

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LovelyKodo")
        self.setFixedSize(1200, 800)  # 设置固定窗口大小
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(style.dynamic_styles())

        # 主窗口部件
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        self.title_bar = TitleBar(self)
        self.title_bar.setObjectName("title_bar")
        main_layout.addWidget(self.title_bar)

        # 内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(style.DIMENS['padding'], style.DIMENS['padding'],
                                        style.DIMENS['padding'], style.DIMENS['padding'])
        content_layout.setSpacing(style.DIMENS['spacing'])

        # 左侧插件区域
        plugin_group = QGroupBox("插件列表")
        plugin_group.setStyleSheet(style.get_group_box_style())
        plugin_group.setObjectName("plugin_group")
        plugin_layout = QVBoxLayout(plugin_group)
        plugin_layout.setContentsMargins(10, 20, 10, 10)
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索插件...")
        self.search_edit.textChanged.connect(self.filter_plugins)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #3498db;
                border-radius: 3px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_edit.setObjectName("search_edit")
        plugin_layout.addWidget(self.search_edit)
        
        self.plugin_tree = QTreeWidget()
        self.plugin_tree.setHeaderHidden(True)
        self.plugin_tree.setStyleSheet(style.get_tree_widget_style())
        self.plugin_tree.itemDoubleClicked.connect(self.on_plugin_selected)
        self.plugin_tree.setObjectName("plugin_tree")
        plugin_layout.addWidget(self.plugin_tree)
        content_layout.addWidget(plugin_group)

        # 右侧区域
        right_widget = QWidget()
        self.right_layout = QVBoxLayout(right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(style.DIMENS['spacing'])

        # 插件参数区域
        self.param_group = QGroupBox("插件参数")
        self.param_group.setStyleSheet(style.get_group_box_style())
        self.param_group.setObjectName("param_group")
        self.param_layout = QVBoxLayout(self.param_group)
        self.param_layout.setContentsMargins(10, 20, 10, 10)
        self.right_layout.addWidget(self.param_group)
        self.param_group.hide()  # 默认隐藏参数区域

        # 输入区域
        input_group = QGroupBox("输入")
        input_group.setObjectName("input_group")
        input_group.setStyleSheet(style.get_group_box_style())
        input_layout = QVBoxLayout(input_group)
        
        self.input_edit = QTextEdit()
        self.input_edit.setObjectName("input_edit")
        self.input_edit.setPlaceholderText("在这里输入要处理的文本...")
        self.input_edit.textChanged.connect(self.on_input_changed)
        self.input_edit.setStyleSheet(style.get_text_edit_style())
        input_layout.addWidget(self.input_edit)
        self.right_layout.addWidget(input_group)

        # 运行按钮
        self.run_btn = QPushButton("编码/解码/加密/解密")
        self.run_btn.setStyleSheet(style.get_run_button_style())
        self.run_btn.clicked.connect(self.run_plugin)
        self.run_btn.setObjectName("run_btn")
        self.right_layout.addWidget(self.run_btn)

        # 输出区域
        output_group = QGroupBox("处理结果")
        output_group.setStyleSheet(style.get_group_box_style())
        output_group.setObjectName("output_group")
        output_layout = QVBoxLayout(output_group)
        output_layout.setContentsMargins(10, 20, 10, 10)
        
        self.output_edit = QTextEdit()
        self.output_edit.setPlaceholderText("处理结果将显示在这里...")
        self.output_edit.setStyleSheet(style.get_text_edit_style())
        self.output_edit.setObjectName("output_edit")
        output_layout.addWidget(self.output_edit)
        self.right_layout.addWidget(output_group)

        content_layout.addWidget(right_widget)
        content_layout.setStretch(0, 1)  # 左侧占比
        content_layout.setStretch(1, 3)  # 右侧占比

        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)
        
        # 当前选中的插件
        self.current_plugin = None
        self.custom_widgets = []
        
        # 加载插件
        self.load_plugins()

    def load_plugins(self):
        """加载所有插件"""
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
        categories = {}

        # 遍历插件目录
        for item in os.listdir(plugins_dir):
            if item.startswith('__'):
                continue
                
            plugin_dir = os.path.join(plugins_dir, item)
            if not os.path.isdir(plugin_dir):
                continue

            # 遍历插件目录中的Python文件
            for file in os.listdir(plugin_dir):
                if not file.endswith('_plugin.py'):
                    continue

                try:
                    # 导入插件模块
                    module_name = f"plugins.{item}.{file[:-3]}"
                    module = importlib.import_module(module_name)

                    # 查找插件类
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and issubclass(obj, Plugin) 
                            and obj != Plugin):
                            plugin = obj()
                            category = plugin.category

                            # 创建分类节点
                            if category not in categories:
                                category_item = QTreeWidgetItem(self.plugin_tree)
                                category_item.setText(0, category)
                                categories[category] = category_item

                            # 添加插件节点
                            plugin_item = QTreeWidgetItem(categories[category])
                            plugin_item.setText(0, plugin.name)
                            plugin_item.setToolTip(0, plugin.description)
                            plugin_item.setData(0, Qt.ItemDataRole.UserRole, plugin)

                except Exception as e:
                    print(f"加载插件失败: {module_name}, 错误: {str(e)}")

        # 展开所有节点
        self.plugin_tree.expandAll()

    def filter_plugins(self, text: str):
        """根据搜索文本筛选插件"""
        search_text = text.lower()
        
        # 遍历所有分类
        for i in range(self.plugin_tree.topLevelItemCount()):
            category_item = self.plugin_tree.topLevelItem(i)
            category_visible = False
            
            # 遍历分类下的所有插件
            for j in range(category_item.childCount()):
                plugin_item = category_item.child(j)
                plugin = plugin_item.data(0, Qt.ItemDataRole.UserRole)
                
                # 检查插件名称和描述是否包含搜索文本
                if (search_text in plugin.name.lower() or 
                    search_text in plugin.description.lower()):
                    plugin_item.setHidden(False)
                    category_visible = True
                else:
                    plugin_item.setHidden(True)
            
            # 如果分类下有可见的插件，则显示分类
            category_item.setHidden(not category_visible)

    def on_plugin_selected(self, item: QTreeWidgetItem, column: int):
        """处理插件选择事件"""
        plugin = item.data(0, Qt.ItemDataRole.UserRole)
        if not plugin:  # 如果是分类节点，直接返回
            return
            
        self.current_plugin = plugin
        # 更新窗口标题
        self.title_bar.set_title(f"LovelyKodo - {plugin.name}")
        
        # 不清除输入文本
        # self.input_edit.clear()
        self.output_edit.clear()
        
        # 清理旧的自定义控件
        for widget_info in self.custom_widgets:
            if 'widget' in widget_info:
                widget_info['widget'].setParent(None)
        self.custom_widgets.clear()
        
        # 创建新的自定义控件
        self.custom_widgets = plugin.create_custom_ui(self)
        
        # 如果有自定义控件，显示参数区域
        if self.custom_widgets:
            for widget_info in self.custom_widgets:
                if 'widget' in widget_info:
                    self.param_layout.insertWidget(
                        self.param_layout.count() - 1,
                        widget_info['widget']
                    )
            self.param_group.show()
        else:
            self.param_group.hide()
            
        # 自动执行插件
        self.run_plugin()
                
    def run_plugin(self):
        """执行当前选中的插件"""
        if not self.current_plugin:
            self.output_edit.setText("请先选择一个插件")
            return
            
        # 获取输入数据
        input_data = self.input_edit.toPlainText()
        if not input_data.strip():  # 如果输入为空，直接返回
            return
            
        # 收集自定义控件的值
        kwargs = {}
        for widget_info in self.custom_widgets:
            if 'key' in widget_info and 'widget' in widget_info:
                widget = widget_info['widget']
                if hasattr(widget, 'text'):
                    kwargs[widget_info['key']] = widget.text()
                elif hasattr(widget, 'currentText'):
                    kwargs[widget_info['key']] = widget.currentText()
                elif hasattr(widget, 'value'):
                    kwargs[widget_info['key']] = widget.value()
        
        try:
            # 验证输入
            is_valid, error_msg = self.current_plugin.validate_input(**kwargs)
            if not is_valid:
                self.output_edit.setText(f"输入验证失败: {error_msg}")
                return
                
            # 执行插件
            result = self.current_plugin.process(input_data, **kwargs)
            self.output_edit.setText(result)
        except Exception as e:
            self.output_edit.setText(f"执行失败: {str(e)}")

    def on_input_changed(self):
        """处理输入文本变化事件"""
        if self.current_plugin:
            self.run_plugin()
