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
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(style.DIMENS['spacing'])
        content_layout.addWidget(self.right_widget)

        content_layout.setStretch(0, 1)  # 左侧占比
        content_layout.setStretch(1, 3)  # 右侧占比

        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)
        
        # 当前选中的插件
        self.current_plugin = None
        # 保存当前输入文本
        self.current_input_text = ""
        
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
            
        # 如果当前有插件，保存其输入文本并清理
        if self.current_plugin:
            if hasattr(self.current_plugin, 'input_edit'):
                self.current_input_text = self.current_plugin.input_edit.toPlainText()
            if hasattr(self.current_plugin, 'cleanup'):
                self.current_plugin.cleanup()
            
        self.current_plugin = plugin
        
        # 更新窗口标题
        self.title_bar.set_title(f"LovelyKodo - {plugin.name}")
        
        # 清理右侧区域
        for i in reversed(range(self.right_layout.count())): 
            widget = self.right_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        
        # 让插件创建UI
        plugin.create_ui(self.right_widget, self.right_layout)
        
        # 恢复输入文本
        if hasattr(plugin, 'input_edit'):
            plugin.input_edit.setText(self.current_input_text)
        
        # 绑定运行按钮事件（如果插件使用默认UI）
        if hasattr(plugin, 'run_btn'):
            plugin.run_btn.clicked.connect(self.run_plugin)

    def run_plugin(self):
        """执行当前选中的插件"""
        if not self.current_plugin:
            return
            
        # 获取输入文本（如果插件使用默认UI）
        input_data = ""
        if hasattr(self.current_plugin, 'input_edit'):
            input_data = self.current_plugin.input_edit.toPlainText()
            
        # 获取自定义参数
        kwargs = {}
        if hasattr(self.current_plugin, 'custom_widgets'):
            for widget_info in self.current_plugin.custom_widgets:
                if 'key' in widget_info and 'widget' in widget_info:
                    widget = widget_info['widget']
                    if hasattr(widget, 'text'):
                        kwargs[widget_info['key']] = widget.text()
                    elif hasattr(widget, 'currentText'):
                        kwargs[widget_info['key']] = widget.currentText()
                        
        # 验证输入
        valid, error = self.current_plugin.validate_input(**kwargs)
        if not valid:
            if hasattr(self.current_plugin, 'output_edit'):
                self.current_plugin.output_edit.setText(error)
            return
            
        # 执行插件
        try:
            result = self.current_plugin.process(input_data, **kwargs)
            if hasattr(self.current_plugin, 'output_edit'):
                self.current_plugin.output_edit.setText(result)
        except Exception as e:
            if hasattr(self.current_plugin, 'output_edit'):
                self.current_plugin.output_edit.setText(f"错误：{str(e)}")
