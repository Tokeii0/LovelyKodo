import json
import base64
from datetime import datetime
from plugins import Plugin
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QLabel, QComboBox, QHBoxLayout, 
    QVBoxLayout, QLineEdit, QPushButton, QPlainTextEdit
)
from PySide6.QtCore import Qt
from style import FONTS

try:
    import jwt
except ImportError:
    import pip
    pip.main(['install', 'PyJWT==1.7.1'])
    import jwt

class JWTPlugin(Plugin):
    # 使用垂直布局
    layout_direction = 'vertical'
    
    def __init__(self):
        super().__init__()
        self.mode_combo = None
        self.algo_combo = None
        self.secret_edit = None
        self.input_edit = None
        self.auto_run = True
        
        # JWT算法列表
        self.algorithms = [
            'HS256', 'HS384', 'HS512'  # 只使用HMAC算法
        ]

    @property
    def name(self) -> str:
        return "JWT工具"

    @property
    def category(self) -> str:
        return "加密解密"

    @property
    def description(self) -> str:
        return "JWT令牌的编码、解码和验证工具"

    def create_input(self, parent: QWidget = None) -> Dict[str, Any]:
        """创建输入框"""
        input_edit = QPlainTextEdit(parent)
        input_edit.setStyleSheet(f"font: {FONTS['mono']};")
        input_edit.setPlaceholderText("输入JWT令牌进行解码，或输入JSON数据进行编码")
        self.input_edit = input_edit
        return {"widget": input_edit}

    def decode_jwt_parts(self, token: str) -> str:
        """解码JWT的各个部分"""
        try:
            # 分割token
            parts = token.split('.')
            if len(parts) != 3:
                return "错误：无效的JWT格式（应该包含三个由点分隔的部分）"

            # 解码header
            header_b64 = parts[0]
            try:
                header_data = base64.b64decode(self._fix_base64_padding(header_b64))
                header = json.loads(header_data)
                header_str = json.dumps(header, ensure_ascii=False, indent=2)
            except Exception:
                header_str = "无法解析"

            # 解码payload
            payload_b64 = parts[1]
            try:
                payload_data = base64.b64decode(self._fix_base64_padding(payload_b64))
                payload = json.loads(payload_data)
                
                # 处理时间戳
                for key, value in payload.items():
                    if key in ['exp', 'iat', 'nbf'] and isinstance(value, (int, float)):
                        try:
                            payload[key] = {
                                'timestamp': value,
                                'datetime': datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
                            }
                        except Exception:
                            pass
                
                payload_str = json.dumps(payload, ensure_ascii=False, indent=2)
            except Exception:
                payload_str = "无法解析"

            # 返回格式化的结果
            return (
                "HEADER: ALGORITHM & TOKEN TYPE\n"
                "--------------------------------\n"
                f"{header_str}\n\n"
                "PAYLOAD: DATA\n"
                "--------------------------------\n"
                f"{payload_str}"
            )
        except Exception as e:
            return f"解析JWT结构时出错：{str(e)}"

    def _fix_base64_padding(self, data: str) -> str:
        """修复base64填充"""
        pad = len(data) % 4
        if pad:
            data += '=' * (4 - pad)
        return data.replace('-', '+').replace('_', '/')

    def process(self, text: str) -> str:
        """处理输入文本"""
        if not text:
            return ""
            
        try:
            mode = self.mode_combo.currentText()
            algorithm = self.algo_combo.currentText()
            secret = self.secret_edit.text()
            
            if mode == "编码":
                # 尝试解析JSON数据
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    return "错误：输入的不是有效的JSON数据"
                
                # 编码JWT
                try:
                    token = jwt.encode(payload, secret, algorithm=algorithm)
                    if isinstance(token, bytes):
                        token = token.decode('utf-8')
                    return token
                except Exception as e:
                    return f"JWT编码错误：{str(e)}"
                
            else:  # 解码
                try:
                    # 首先展示JWT的结构
                    structure = self.decode_jwt_parts(text)
                    
                    # 然后尝试验证签名
                    try:
                        jwt.decode(text, secret, algorithms=[algorithm])
                        return structure + "\n\nSignature: 验证成功 ✓"
                    except jwt.ExpiredSignatureError:
                        return structure + "\n\nSignature: 令牌已过期 ✗"
                    except jwt.InvalidTokenError:
                        return structure + "\n\nSignature: 签名验证失败 ✗"
                    except Exception as e:
                        return structure + f"\n\nSignature: 验证出错 - {str(e)} ✗"
                    
                except Exception as e:
                    return f"JWT解析错误：{str(e)}"
                
        except Exception as e:
            return f"处理出错：{str(e)}"

    def create_custom_ui(self, parent: QWidget = None) -> List[Dict[str, Any]]:
        """创建自定义UI元素"""
        # 创建顶部容器
        top_container = QWidget(parent)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)
        
        # 创建模式选择
        mode_label = QLabel("模式:", parent)
        mode_label.setFixedWidth(40)
        mode_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.mode_combo = QComboBox(parent)
        self.mode_combo.addItems(["编码", "解码"])
        self.mode_combo.setFixedWidth(80)
        self.mode_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建算法选择
        algo_label = QLabel("算法:", parent)
        algo_label.setFixedWidth(40)
        algo_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.algo_combo = QComboBox(parent)
        self.algo_combo.addItems(self.algorithms)
        self.algo_combo.setFixedWidth(80)
        self.algo_combo.setStyleSheet(f"font: {FONTS['body']};")
        
        # 创建密钥输入框
        secret_label = QLabel("密钥:", parent)
        secret_label.setFixedWidth(40)
        secret_label.setStyleSheet(f"font: {FONTS['body']};")
        
        self.secret_edit = QLineEdit(parent)
        self.secret_edit.setStyleSheet(f"font: {FONTS['mono']};")
        self.secret_edit.setPlaceholderText("输入密钥")
        
        # 添加所有控件到布局
        widgets = [
            (mode_label, None),
            (self.mode_combo, None),
            (algo_label, None),
            (self.algo_combo, None),
            (secret_label, None),
            (self.secret_edit, 1),  
        ]
        
        for widget, stretch in widgets:
            top_layout.addWidget(widget)
            if stretch is not None:
                top_layout.setStretch(top_layout.count() - 1, stretch)
        
        # 设置顶部容器的布局
        top_container.setLayout(top_layout)
        
        return [{"widget": top_container}]

    def format_json_input(self):
        """格式化输入的JSON数据"""
        if not self.input_edit:
            return
            
        try:
            # 获取当前文本
            text = self.input_edit.toPlainText()
            if not text:
                return
                
            # 尝试解析和格式化JSON
            data = json.loads(text)
            formatted = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 更新文本框
            self.input_edit.setPlainText(formatted)
        except json.JSONDecodeError:
            # 如果不是有效的JSON，保持原样
            pass
