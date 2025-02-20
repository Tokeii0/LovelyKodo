"""
macOS风格主题配置
"""

import json
import os
from typing import Dict, Any

# 颜色定义
COLORS = {
    "color_primary": "#007AFF",
    "color_secondary": "#5856D6",
    "color_success": "#34C759",
    "color_warning": "#FF9500",
    "color_danger": "#FF3B30",
    "color_info": "#5AC8FA",
    "color_background": "#FFFFFF",
    "color_widget_bg": "#F5F5F5",
    "color_text": "#000000",
    "color_text_secondary": "#8E8E93",
    "color_border": "#C6C6C8",
    "color_hover": "#E5E5EA",
    "color_active": "#D1D1D6",
    # 窗口控制按钮颜色
    "color_close": "#ff6059",
    "color_minimize": "#ffbd2e",
    "color_maximize": "#28c940"
}

# 字体配置
FONTS = {
    'title': '12pt "汉仪文黑-85W"',
    'body': '10pt "汉仪文黑-85W"',
    'small': '9pt "汉仪文黑-85W"',
    'mono': '10pt "汉仪文黑-85W"'  # 等宽字体，适合代码和数据显示
}

# 尺寸配置
DIMENS = {
    'radius': 6,
    'padding': 10,
    'margin': 8,
    'spacing': 10
}

class ThemeManager:
    _instance = None
    _themes = {}
    _current_theme = "默认主题"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._load_themes()
            cls._instance._load_saved_theme()
        return cls._instance

    def _load_themes(self):
        """加载主题配置"""
        theme_file = os.path.join(os.path.dirname(__file__), 'themes.json')
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                self._themes = json.load(f)
        except Exception as e:
            print(f"加载主题配置失败: {str(e)}")
            # 使用默认主题作为备选
            self._themes = {"默认主题": {
                "color_primary": "#007AFF",
                "color_secondary": "#5856D6",
                "color_success": "#34C759",
                "color_warning": "#FF9500",
                "color_danger": "#FF3B30",
                "color_info": "#5AC8FA",
                "color_background": "#FFFFFF",
                "color_widget_bg": "#F5F5F5",
                "color_text": "#000000",
                "color_text_secondary": "#8E8E93",
                "color_border": "#C6C6C8",
                "color_hover": "#E5E5EA",
                "color_active": "#D1D1D6",
                "color_close": "#ff6059",
                "color_minimize": "#ffbd2e",
                "color_maximize": "#28c940"
            }}

    def _load_saved_theme(self):
        """加载保存的主题设置"""
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'theme' in config and config['theme'] in self._themes:
                        self._current_theme = config['theme']
                        # 更新全局颜色定义
                        global COLORS
                        COLORS.update(self._themes[config['theme']])
        except Exception as e:
            print(f"加载主题设置失败: {str(e)}")

    @property
    def current_colors(self) -> Dict[str, str]:
        """获取当前主题的颜色配置"""
        return self._themes.get(self._current_theme, self._themes["默认主题"])

    @property
    def available_themes(self) -> list[str]:
        """获取所有可用的主题名称"""
        return list(self._themes.keys())

    def set_theme(self, theme_name: str) -> bool:
        """设置当前主题"""
        if theme_name in self._themes:
            self._current_theme = theme_name
            # 更新全局颜色定义
            global COLORS
            COLORS.update(self._themes[theme_name])
            return True
        return False

    def get_theme_preview(self, theme_name: str) -> str:
        """获取主题预览的样式表"""
        if theme_name not in self._themes:
            return ""
        
        colors = self._themes[theme_name]
        return f"""
            /* 主预览容器 */
            QWidget#preview_container {{
                background: {colors['color_background']};
                color: {colors['color_text']};
                border: 1px solid {colors['color_border']};
                border-radius: {DIMENS['radius']}px;
                padding: 10px;
            }}
            
            /* 按钮预览 */
            QPushButton#preview_primary_btn {{
                background: {colors['color_primary']};
                color: white;
                border: none;
                border-radius: {DIMENS['radius']}px;
                padding: 5px 10px;
                font: {FONTS['body']};
            }}
            
            QPushButton#preview_success_btn {{
                background: {colors['color_success']};
                color: white;
                border: none;
                border-radius: {DIMENS['radius']}px;
                padding: 5px 10px;
                font: {FONTS['body']};
            }}
            
            /* 文本框预览 */
            QTextEdit#preview_text {{
                background: {colors['color_widget_bg']};
                color: {colors['color_text']};
                border: 1px solid {colors['color_border']};
                border-radius: {DIMENS['radius']}px;
                padding: 5px;
                font: {FONTS['mono']};
                min-height: 30px;
                max-height: 30px;
            }}
            
            /* 标签预览 */
            QLabel#preview_label {{
                color: {colors['color_text']};
                font: {FONTS['body']};
            }}
            
            QLabel#preview_secondary_label {{
                color: {colors['color_text_secondary']};
                font: {FONTS['small']};
            }}
        """

# 创建主题管理器实例
theme_manager = ThemeManager()

# 获取当前主题的颜色
COLORS = theme_manager.current_colors

# 窗口控制按钮样式
def get_window_button_style(color):
    return f"""
        QPushButton {{
            background: {color};
            border: none;
            border-radius: 6px;
        }}
        QPushButton:hover {{
            background: {color}99;
        }}
    """

# 标题样式
def get_title_style():
    return f"""
        QLabel {{
            color: {COLORS['color_text']};
            font: {FONTS['title']};
        }}
    """

# 输入框样式
def get_text_edit_style():
    """获取文本框样式"""
    return f"""
        QTextEdit {{
            background: {COLORS['color_widget_bg']};
            color: {COLORS['color_text']};
            border: 1px solid {COLORS['color_border']};
            border-radius: {DIMENS['radius']}px;
            padding: 5px;
            font: {FONTS['mono']};
            selection-background-color: {COLORS['color_primary']};
            selection-color: white;
        }}
        QTextEdit:focus {{
            border: 2px solid {COLORS['color_primary']};
        }}
        QTextEdit::placeholder {{
            color: {COLORS['color_text_secondary']};
            font: {FONTS['body']};
        }}
    """

# 按钮样式
def get_button_style():
    return f"""
        QPushButton {{
            background: {COLORS['color_primary']};
            color: white;
            border: none;
            border-radius: {DIMENS['radius']}px;
            padding: 8px 16px;
            font: {FONTS['body']};
        }}
        QPushButton:hover {{
            background: {COLORS['color_hover']};
        }}
        QPushButton:pressed {{
            background: {COLORS['color_active']};
        }}
    """

# 运行按钮样式
def get_run_button_style():
    return f"""
        QPushButton {{
            background: {COLORS['color_success']};
            color: white;
            border: none;
            border-radius: {DIMENS['radius']}px;
            padding: 8px 16px;
            font: {FONTS['body']};
        }}
        QPushButton:hover {{
            background: {COLORS['color_success']}CC;
        }}
        QPushButton:pressed {{
            background: {COLORS['color_success']}99;
        }}
        QPushButton:disabled {{
            background: {COLORS['color_border']};
            color: {COLORS['color_text_secondary']};
        }}
    """

# 下拉框样式
def get_combobox_style():
    return f"""
        QComboBox {{
            background: {COLORS['color_widget_bg']};
            border: 1px solid {COLORS['color_border']};
            border-radius: {DIMENS['radius']}px;
            padding: 5px 10px;
            font: {FONTS['body']};
            min-width: 100px;
        }}
        QComboBox:hover {{
            border-color: {COLORS['color_primary']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            width: 0;
        }}
        QComboBox QAbstractItemView {{
            background: {COLORS['color_widget_bg']};
            border: 1px solid {COLORS['color_border']};
            border-radius: {DIMENS['radius']}px;
            selection-background-color: {COLORS['color_primary']};
            selection-color: white;
        }}
    """

# 树形控件样式
def get_tree_widget_style():
    return f"""
        QTreeWidget {{
            background: {COLORS['color_widget_bg']};
            border: 1px solid {COLORS['color_border']};
            border-radius: {DIMENS['radius']}px;
            padding: {DIMENS['padding']}px;
            font: {FONTS['body']};
        }}
        
        QTreeWidget::item {{
            padding: {DIMENS['padding']}px;
            margin: {DIMENS['margin']}px 0;
            border-radius: {DIMENS['radius']}px;
        }}
        
        QTreeWidget::item:hover {{
            background: {COLORS['color_hover']};
        }}
        
        QTreeWidget::item:selected {{
            background: {COLORS['color_primary']};
            color: white;
        }}
        
        QTreeWidget::branch {{
            background: transparent;
        }}
        
        QTreeWidget::branch:has-siblings:!adjoins-item {{
            border-image: url(./assets/vline.png) 0;
        }}
        
        QTreeWidget::branch:has-siblings:adjoins-item {{
            border-image: url(./assets/branch-more.png) 0;
        }}
        
        QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: url(./assets/branch-end.png) 0;
        }}
        
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(./assets/branch-closed.png);
        }}
        
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(./assets/branch-open.png);
        }}
    """

# 分组框样式
def get_group_box_style():
    """获取分组框样式"""
    return f"""
        QGroupBox {{
            border: 1px solid {COLORS['color_border']};
            border-radius: {DIMENS['radius']}px;
            margin-top: 1em;
            padding: {DIMENS['padding']}px;
            font: {FONTS['body']};
            color: {COLORS['color_text']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {DIMENS['padding']}px;
            padding: 0 3px 0 3px;
            color: {COLORS['color_primary']};
            font: {FONTS['body']};
        }}
        QGroupBox:hover {{
            border: 1px solid {COLORS['color_primary']};
        }}
    """

# 标签样式
def get_label_style():
    """获取标签样式"""
    return f"""
        QLabel {{
            color: {COLORS['color_text']};
            font: {FONTS['body']};
            border: none;
        }}
    """

# 全局样式
def dynamic_styles():
    """获取全局样式"""
    return f"""
        QWidget {{
            color: {COLORS['color_text']};
        }}
        
        QLabel {{
            color: {COLORS['color_text']};
            font: {FONTS['body']};
            border: none;
        }}
        
        QLabel[secondary="true"] {{
            color: {COLORS['color_text_secondary']};
            font: {FONTS['small']};
        }}
        
        QMainWindow {{
            background: {COLORS['color_background']};
        }}
        
        QTreeWidget {{
            background: {COLORS['color_widget_bg']};
            border: 1px solid {COLORS['color_border']};
            border-radius: {DIMENS['radius']}px;
        }}
        
        QTreeWidget::item {{
            padding: 4px;
        }}
        
        QTreeWidget::item:selected {{
            background: {COLORS['color_primary']};
            color: white;
        }}
        
        QTextEdit {{
            background: {COLORS['color_widget_bg']};
            border: 1px solid {COLORS['color_border']};
            border-radius: {DIMENS['radius']}px;
            padding: 8px;
        }}
        
        QSplitter::handle {{
            background: {COLORS['color_border']};
        }}
        
        QScrollBar:vertical {{
            border: none;
            background: {COLORS['color_widget_bg']};
            width: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {COLORS['color_border']};
            border-radius: 5px;
            min-height: 20px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: {COLORS['color_widget_bg']};
            height: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {COLORS['color_border']};
            border-radius: 5px;
            min-width: 20px;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        QDialog {{
            background: {COLORS['color_background']};
        }}
    """
