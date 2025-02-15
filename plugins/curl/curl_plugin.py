import re
import json
from plugins import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout
from style import FONTS

class CurlConverter:
    """Curl命令转换器"""
    
    @staticmethod
    def parse_curl(curl_command: str) -> Dict[str, Any]:
        """解析curl命令"""
        try:
            # 移除开头的curl和多余的空格
            curl_command = curl_command.strip()
            if curl_command.lower().startswith("curl "):
                curl_command = curl_command[5:]
            
            # 将多行命令合并为一行，处理续行符 \
            curl_command = re.sub(r'\\\s*\n\s*', ' ', curl_command)
            
            result = {
                "method": "GET",
                "url": "",
                "headers": {},
                "data": None,
                "json": None,
                "verify": True
            }
            
            # 使用正则表达式匹配参数
            url_pattern = r'(?:^|\s)(\'https?://[^\']+\'|"https?://[^"]+"|https?://[^\s]+)'
            header_pattern = r'--header\s+["\']([^"\']+)["\']|-H\s+["\']([^"\']+)["\']'
            data_pattern = r'(?:--data|-d)\s*\'([^\']*(?:\'[^\']*\'[^\']*)*)\''  # 处理可能包含引号的数据
            json_pattern = r'--json\s+["\']([^"\']+)["\']'
            method_pattern = r'-X\s+([A-Z]+)'
            insecure_pattern = r'-k|--insecure'
            location_pattern = r'--location|-L'
            
            # 提取URL
            url_match = re.search(url_pattern, curl_command)
            if url_match:
                url = url_match.group(1)
                # 移除可能存在的引号
                result["url"] = url.strip("'\"")
            
            # 提取请求方法
            method_match = re.search(method_pattern, curl_command)
            if method_match:
                result["method"] = method_match.group(1)
            
            # 提取请求头
            header_matches = re.finditer(header_pattern, curl_command)
            for match in header_matches:
                header = match.group(1) or match.group(2)
                if ":" in header:
                    key, value = header.split(":", 1)
                    result["headers"][key.strip()] = value.strip()
            
            # 提取data参数
            data_match = re.search(data_pattern, curl_command, re.DOTALL)  # 使用DOTALL模式匹配多行
            if data_match:
                data = data_match.group(1)
                # 检查是否是JSON格式
                try:
                    # 尝试解析JSON，同时处理可能的转义字符
                    data = data.replace('\\"', '"').replace("\\'", "'")
                    json_data = json.loads(data)
                    result["json"] = json_data
                    if not result.get("headers", {}).get("Content-Type"):
                        result["headers"]["Content-Type"] = "application/json"
                except json.JSONDecodeError:
                    result["data"] = data
                    if not result.get("headers", {}).get("Content-Type"):
                        result["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
                
                if "method" not in result or result["method"] == "GET":
                    result["method"] = "POST"
            
            # 提取json参数
            json_match = re.search(json_pattern, curl_command)
            if json_match:
                json_str = json_match.group(1)
                try:
                    result["json"] = json.loads(json_str)
                except json.JSONDecodeError:
                    result["json"] = json_str
                if "method" not in result or result["method"] == "GET":
                    result["method"] = "POST"
            
            # 检查是否有-k或--insecure参数
            if re.search(insecure_pattern, curl_command):
                result["verify"] = False
            
            # 检查是否有-L或--location参数
            if re.search(location_pattern, curl_command):
                result["allow_redirects"] = True
            
            return result
            
        except Exception as e:
            raise ValueError(f"解析curl命令失败: {str(e)}")
    
    @staticmethod
    def to_python_code(curl_data: Dict[str, Any], style: str = "requests") -> str:
        """将解析后的curl数据转换为Python代码"""
        try:
            if style == "requests":
                code_lines = ["import requests", "import json\n"]
                
                # 添加请求头
                if curl_data["headers"]:
                    code_lines.append("headers = {")
                    for key, value in curl_data["headers"].items():
                        code_lines.append(f"    '{key}': '{value}',")
                    code_lines.append("}\n")
                
                # 如果有JSON数据，添加json导入和数据定义
                if isinstance(curl_data.get("json"), (dict, list)):
                    code_lines.append(f"data = {json.dumps(curl_data['json'], ensure_ascii=False)}\n")
                
                # 构建请求代码
                code_lines.append("response = requests.{}(".format(curl_data["method"].lower()))
                code_lines.append(f"    '{curl_data['url']}',")
                
                if curl_data["headers"]:
                    code_lines.append("    headers=headers,")
                
                if curl_data.get("data"):
                    code_lines.append(f"    data='{curl_data['data']}',")
                
                if curl_data.get("json"):
                    if isinstance(curl_data["json"], (dict, list)):
                        code_lines.append("    json=data,")
                    else:
                        code_lines.append(f"    json={curl_data['json']},")
                
                if not curl_data.get("verify", True):
                    code_lines.append("    verify=False,")
                
                if curl_data.get("allow_redirects"):
                    code_lines.append("    allow_redirects=True,")
                
                # 移除最后一个逗号
                last_line = code_lines[-1]
                if last_line.endswith(","):
                    code_lines[-1] = last_line[:-1]
                
                code_lines.append(")\n")
                
                # 添加响应处理
                code_lines.extend([
                    "# 打印响应状态码",
                    "print(f'Status Code: {response.status_code}')",
                    "",
                    "# 打印响应头",
                    "print('\\nResponse Headers:')",
                    "for header, value in response.headers.items():",
                    "    print(f'{header}: {value}')",
                    "",
                    "# 打印响应内容",
                    "print('\\nResponse Body:')",
                    "try:",
                    "    print(json.dumps(response.json(), indent=4, ensure_ascii=False))",
                    "except ValueError:",
                    "    print(response.text)"
                ])
                
                return "\n".join(code_lines)
                
            else:
                raise ValueError(f"不支持的代码风格: {style}")
                
        except Exception as e:
            raise ValueError(f"生成Python代码失败: {str(e)}")

class CurlToPythonPlugin(Plugin):
    # 使用水平布局
    layout_direction = 'horizontal'
    
    def __init__(self):
        super().__init__()
        self.converter = CurlConverter()
        self.style_combo = None
        self.auto_run = True
    
    @property
    def name(self) -> str:
        return "Curl转Python"
    
    @property
    def category(self) -> str:
        return "代码转换"
    
    @property
    def description(self) -> str:
        return "将Curl命令转换为Python代码"
    
    def process(self, text: str) -> str:
        """处理输入文本"""
        try:
            # 解析curl命令
            curl_data = self.converter.parse_curl(text)
            
            # 转换为Python代码
            style = "requests"  # 使用默认的 requests 风格
            result = self.converter.to_python_code(curl_data, style)
            
            return result
            
        except Exception as e:
            return str(e)
    
    def create_custom_ui(self, parent: QWidget = None) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建代码风格选择下拉框
        style_label = QLabel("代码风格:", parent)
        style_label.setFixedWidth(60)
        style_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.style_combo = QComboBox(parent)
        self.style_combo.addItems(["requests"])  # 未来可以添加更多选项，如 urllib3, aiohttp 等
        self.style_combo.setCurrentText("requests")
        self.style_combo.setFixedWidth(100)
        self.style_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 添加到布局
        layout.addWidget(style_label)
        layout.addWidget(self.style_combo)
        
        # 创建容器widget
        container = QWidget(parent)
        container.setLayout(layout)
        
        return [{"widget": container}]
    
    def process_input(self, text: str) -> str:
        """处理输入文本"""
        try:
            # 解析curl命令
            curl_data = self.converter.parse_curl(text)
            
            # 转换为Python代码
            style = self.style_combo.currentText().lower()
            result = self.converter.to_python_code(curl_data, style)
            
            return result
            
        except Exception as e:
            return str(e)
