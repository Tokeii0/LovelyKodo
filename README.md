# PyDataChef

PyDataChef 是一个基于插件架构的数据处理工具，灵感来自于GCHQ的CyberChef项目。它提供了一个直观的图形界面，让用户可以方便地进行各种数据转换和编码操作。

## 特点

- 插件化架构设计
- 分类展示的插件树形结构
- 简洁的用户界面
- 实时数据处理
  - 自动执行功能
  - 保留输入数据
  - 实时结果显示
- 智能搜索功能
  - 实时过滤插件
  - 支持名称和描述搜索
  - 自动隐藏无关分类
- 易于扩展的插件系统
- 主题系统
  - 内置多种精美主题
  - 一键切换主题
  - 实时预览效果
  - 统一的样式管理

## 安装

1. 确保已安装Python 3.8或更高版本
2. 克隆本仓库
3. 安装依赖:
```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 开发新插件

1. 在 `plugins` 目录下创建新的Python文件，命名格式为 `*_plugin.py`
2. 创建新的插件类，继承自 `Plugin` 基类
3. 实现必要的属性和方法:
   - name: 插件名称
   - category: 插件分类
   - description: 插件描述
   - process: 数据处理方法

示例:
```python
from plugins import Plugin

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "我的插件"
    
    @property
    def category(self) -> str:
        return "我的分类"
    
    @property
    def description(self) -> str:
        return "这是一个示例插件"
    
    def process(self, input_data: str) -> str:
        # 处理数据
        return input_data.upper()
```

## 项目结构

```
PyDataChef/
├── main.py              # 主程序
├── plugin_manager.py    # 插件管理器
├── plugins/             # 插件目录
│   ├── __init__.py     # 插件基类
│   ├── encoding/       # 编码转换插件
│   │   └── base64_plugin.py
│   └── hash/           # 哈希计算插件
│       └── hash_plugin.py
├── style.py             # 样式管理
├── themes.json          # 主题配置
└── requirements.txt     # 项目依赖
```

## 开发环境

- Python 3.8+
- PySide6
- Windows/Linux/MacOS

## 许可证

MIT License
