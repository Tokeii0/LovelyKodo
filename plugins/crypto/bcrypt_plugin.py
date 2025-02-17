# -*- coding: utf-8 -*-
"""
@ Author: b3nguang
@ Date: 2025-02-16 23:08:33
"""

import bcrypt
from PySide6.QtWidgets import QComboBox, QLineEdit, QSpinBox, QWidget

import style

from .. import Plugin


class BcryptPlugin(Plugin):
    # bcrypt支持的版本
    VERSIONS = ["2a", "2b"]

    @property
    def name(self) -> str:
        return "Bcrypt加密/解密"

    @property
    def category(self) -> str:
        return "加密/解密"

    @property
    def description(self) -> str:
        return "使用Bcrypt算法进行密码加密和验证，支持2a/2b版本和自定义加密轮数"

    def create_custom_ui(self, parent: QWidget) -> list[dict]:
        # 创建密码输入框
        password_input = QLineEdit(parent)
        password_input.setPlaceholderText("请输入要加密的密码")
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet(style.get_text_edit_style())

        # 创建版本选择下拉框
        version_select = QComboBox(parent)
        version_select.addItems(self.VERSIONS)
        version_select.setStyleSheet(style.get_combobox_style())

        # 创建加密轮数选择框
        rounds_input = QSpinBox(parent)
        rounds_input.setRange(4, 31)
        rounds_input.setValue(12)
        rounds_input.setStyleSheet(style.get_combobox_style())

        # 创建哈希值输入框（用于验证）
        hash_input = QLineEdit(parent)
        hash_input.setPlaceholderText("请输入bcrypt哈希值（仅验证时需要）")
        hash_input.setStyleSheet(style.get_text_edit_style())

        return [
            {"type": "combobox", "label": "Bcrypt版本", "widget": version_select, "key": "version"},
            {"type": "spinbox", "label": "加密轮数", "widget": rounds_input, "key": "rounds"},
            {"type": "input", "label": "哈希值", "widget": hash_input, "key": "hash"},
        ]

    def process(self, text: str, **kwargs) -> str:
        try:
            version = kwargs.get("version", "2a")
            rounds = int(kwargs.get("rounds", 12))
            hash_value = kwargs.get("hash", "")

            if not text:
                return "请输入密码"

            # 如果提供了哈希值，进行验证
            if hash_value:
                try:
                    is_valid = bcrypt.checkpw(text.encode("utf-8"), hash_value.encode("utf-8"))
                    return "密码验证成功" if is_valid else "密码验证失败"
                except ValueError:
                    return "无效的哈希值格式"

            # 否则进行加密
            else:
                if rounds < 4 or rounds > 31:
                    return "加密轮数必须在4-31之间"

                if version not in self.VERSIONS:
                    return "不支持的Bcrypt版本"

                prefix = f"2{version[1]}".encode("utf-8")  # 只使用2a或2b作为前缀
                salt = bcrypt.gensalt(rounds=rounds, prefix=prefix)
                hashed = bcrypt.hashpw(text.encode("utf-8"), salt)
                return hashed.decode("utf-8")

        except Exception as e:
            return f"处理失败: {str(e)}"
