from datetime import datetime, timezone, timedelta
import time
import calendar
from plugins import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QLineEdit, QCheckBox, QPushButton
from PySide6.QtCore import Signal, Qt
from style import FONTS

class TimeConverter:
    """时间转换器"""
    
    # 支持的时间格式
    TIME_FORMATS = {
        "ISO8601": "%Y-%m-%dT%H:%M:%S%z",
        "ISO8601_WITH_MS": "%Y-%m-%dT%H:%M:%S.%f%z",
        "RFC3339": "%Y-%m-%dT%H:%M:%S%z",
        "RFC822": "%a, %d %b %y %H:%M:%S %z",
        "RFC850": "%A, %d-%b-%y %H:%M:%S %z",
        "RFC1036": "%a, %d %b %y %H:%M:%S %z",
        "RFC1123": "%a, %d %b %Y %H:%M:%S %z",
        "RFC2822": "%a, %d %b %Y %H:%M:%S %z",
        "RFC5322": "%a, %d %b %Y %H:%M:%S %z",
        "中文日期时间": "%Y年%m月%d日 %H时%M分%S秒",
        "中文日期": "%Y年%m月%d日",
        "标准日期时间": "%Y-%m-%d %H:%M:%S",
        "标准日期": "%Y-%m-%d",
        "MySQL日期时间": "%Y-%m-%d %H:%M:%S",
        "日期斜线": "%Y/%m/%d",
        "日期时间斜线": "%Y/%m/%d %H:%M:%S",
        "简单时间": "%H:%M:%S",
        "12小时制": "%Y-%m-%d %I:%M:%S %p",
        "Unix时间戳(秒)": "timestamp_s",
        "Unix时间戳(毫秒)": "timestamp_ms",
        "Unix时间戳(微秒)": "timestamp_us",
        "星期几": "weekday",
        "一年中的第几天": "yearday",
        "一年中的第几周": "weeknum",
        "农历": "lunar"
    }
    
    @staticmethod
    def parse_time(time_str: str, input_format: str) -> datetime:
        """解析时间字符串"""
        try:
            if input_format in ["timestamp_s", "timestamp_ms", "timestamp_us"]:
                timestamp = float(time_str)
                if input_format == "timestamp_ms":
                    timestamp /= 1000
                elif input_format == "timestamp_us":
                    timestamp /= 1000000
                return datetime.fromtimestamp(timestamp, timezone.utc)
            else:
                # 尝试自动添加时区信息
                if "%z" in TimeConverter.TIME_FORMATS[input_format] and not any(x in time_str for x in ['+', '-', 'Z']):
                    time_str += "+0000"
                return datetime.strptime(time_str, TimeConverter.TIME_FORMATS[input_format])
        except Exception as e:
            raise ValueError(f"时间解析错误: {str(e)}")
    
    @staticmethod
    def format_time(dt: datetime, output_format: str, use_local_time: bool = True) -> str:
        """格式化时间"""
        try:
            # 转换为本地时间
            if use_local_time and dt.tzinfo is not None:
                dt = dt.astimezone()
            elif dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc).astimezone()
            
            if output_format == "timestamp_s":
                return str(int(dt.timestamp()))
            elif output_format == "timestamp_ms":
                return str(int(dt.timestamp() * 1000))
            elif output_format == "timestamp_us":
                return str(int(dt.timestamp() * 1000000))
            elif output_format == "weekday":
                weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
                return weekdays[dt.weekday()]
            elif output_format == "yearday":
                return f"第 {dt.timetuple().tm_yday} 天"
            elif output_format == "weeknum":
                return f"第 {dt.isocalendar()[1]} 周"
            elif output_format == "lunar":
                try:
                    import lunar  # 需要安装lunar-python包
                    lunar_date = lunar.Lunar.from_date(dt.date())
                    return lunar_date.strftime('%Y年%M月%D日')
                except ImportError:
                    return "需要安装lunar-python包"
            else:
                return dt.strftime(TimeConverter.TIME_FORMATS[output_format])
        except Exception as e:
            raise ValueError(f"时间格式化错误: {str(e)}")

class TimeConverterPlugin(Plugin):
    # 使用水平布局
    layout_direction = 'horizontal'
    
    def __init__(self):
        super().__init__()
        self.converter = TimeConverter()
        self.input_format_combo = None
        self.output_format_combo = None
        self.local_time_check = None
        self.input_edit = None
        self.auto_run = True

    def create_input(self, parent: QWidget = None) -> Dict[str, Any]:
        """创建输入框"""
        self.input_edit = QLineEdit(parent)
        self.input_edit.setStyleSheet(f"font: {FONTS['mono']};")
        return {"widget": self.input_edit}

    @property
    def name(self) -> str:
        return "时间转换"
    
    @property
    def category(self) -> str:
        return "时间工具"
    
    @property
    def description(self) -> str:
        return "在不同时间格式之间转换，支持时间戳、ISO8601、RFC标准等多种格式"
    
    def process(self, text: str) -> str:
        """处理输入文本"""
        try:
            if not text:
                return ""
            
            input_format = self.input_format_combo.currentText()
            output_format = self.output_format_combo.currentText()
            use_local_time = self.local_time_check.isChecked()
            
            # 如果输入是时间戳格式，直接转换为datetime对象
            if input_format in ["Unix时间戳(秒)", "Unix时间戳(毫秒)", "Unix时间戳(微秒)"]:
                try:
                    timestamp = float(text)
                    if input_format == "Unix时间戳(毫秒)":
                        timestamp /= 1000
                    elif input_format == "Unix时间戳(微秒)":
                        timestamp /= 1000000
                    dt = datetime.fromtimestamp(timestamp, timezone.utc)
                except ValueError:
                    return f"无效的时间戳: {text}"
            else:
                # 其他格式使用strptime解析
                try:
                    dt = datetime.strptime(text, self.converter.TIME_FORMATS[input_format])
                except ValueError:
                    return f"时间格式错误: {text} 不符合格式 {input_format}"
            
            # 格式化输出
            if output_format == "Unix时间戳(秒)":
                return str(int(dt.timestamp()))
            elif output_format == "Unix时间戳(毫秒)":
                return str(int(dt.timestamp() * 1000))
            elif output_format == "Unix时间戳(微秒)":
                return str(int(dt.timestamp() * 1000000))
            elif output_format == "weekday":
                weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
                return weekdays[dt.weekday()]
            elif output_format == "yearday":
                return f"第 {dt.timetuple().tm_yday} 天"
            elif output_format == "weeknum":
                return f"第 {dt.isocalendar()[1]} 周"
            elif output_format == "lunar":
                try:
                    import lunar
                    lunar_date = lunar.Lunar.from_date(dt.date())
                    return lunar_date.strftime('%Y年%M月%D日')
                except ImportError:
                    return "需要安装lunar-python包"
            else:
                if use_local_time and dt.tzinfo is not None:
                    dt = dt.astimezone()
                return dt.strftime(self.converter.TIME_FORMATS[output_format])
            
        except Exception as e:
            return str(e)

    def create_custom_ui(self, parent: QWidget = None) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建容器widget
        container = QWidget(parent)
        container.setContentsMargins(0, 0, 0, 0)
        
        # 创建水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 创建输入格式选择下拉框
        input_format_label = QLabel("输入格式:", parent)
        input_format_label.setFixedWidth(60)
        input_format_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.input_format_combo = QComboBox(parent)
        self.input_format_combo.addItems(list(self.converter.TIME_FORMATS.keys()))
        self.input_format_combo.setCurrentText("标准日期时间")
        self.input_format_combo.setFixedWidth(150)
        self.input_format_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建输出格式选择下拉框
        output_format_label = QLabel("输出格式:", parent)
        output_format_label.setFixedWidth(60)
        output_format_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.output_format_combo = QComboBox(parent)
        self.output_format_combo.addItems(list(self.converter.TIME_FORMATS.keys()))
        self.output_format_combo.setCurrentText("Unix时间戳(秒)")
        self.output_format_combo.setFixedWidth(150)
        self.output_format_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建本地时间选项
        self.local_time_check = QCheckBox("使用本地时间", parent)
        self.local_time_check.setChecked(True)
        self.local_time_check.setStyleSheet(f"font: {FONTS['body']};")

        # 创建获取当前时间按钮
        now_button = QPushButton("获取当前时间", parent)
        now_button.setStyleSheet(f"font: {FONTS['body']};")
        now_button.setFixedWidth(100)
        now_button.clicked.connect(self._set_current_time)
        
        # 添加所有控件到布局
        widgets = [
            (input_format_label, None),
            (self.input_format_combo, None),
            (output_format_label, None),
            (self.output_format_combo, None),
            (self.local_time_check, None),
            (now_button, None)
        ]
        
        for widget, stretch in widgets:
            layout.addWidget(widget)
            if stretch is not None:
                layout.setStretch(layout.count() - 1, stretch)
        
        # 设置容器的布局
        container.setLayout(layout)
        
        return [{"widget": container}]

    def _set_current_time(self):
        """设置当前时间到输入框"""
        if not hasattr(self, 'input_edit') or not self.input_edit:
            print("Debug: input_edit is None")
            return
            
        current_format = self.input_format_combo.currentText()
        now = datetime.now().replace(microsecond=0)
        
        try:
            if current_format == "Unix时间戳(秒)":
                current_time = str(int(now.timestamp()))
            elif current_format == "Unix时间戳(毫秒)":
                current_time = str(int(now.timestamp() * 1000))
            elif current_format == "Unix时间戳(微秒)":
                current_time = str(int(now.timestamp() * 1000000))
            else:
                current_time = now.strftime(self.converter.TIME_FORMATS[current_format])
            
            print(f"Debug: Setting text to: {current_time}")
            self.input_edit.setText(current_time)
        except Exception as e:
            print(f"Debug: Error occurred: {str(e)}")
            self.input_edit.setText(str(e))
