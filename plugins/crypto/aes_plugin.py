from ..import Plugin
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from PySide6.QtWidgets import QLineEdit, QComboBox, QWidget, QSpinBox
import style

class AESPlugin(Plugin):
    # AES支持的模式
    MODES = {
        'CBC': AES.MODE_CBC,
        'ECB': AES.MODE_ECB,
        'CFB': AES.MODE_CFB,
        'OFB': AES.MODE_OFB,
        'CTR': AES.MODE_CTR,
        'GCM': AES.MODE_GCM
    }
    
    # 填充方式
    PADDINGS = ['PKCS7', 'ISO7816', 'X923']
    
    @property
    def name(self) -> str:
        return "AES加密/解密"

    @property
    def category(self) -> str:
        return "加密/解密"

    @property
    def description(self) -> str:
        return "使用AES算法进行加密和解密，支持多种模式和填充方式"

    def create_custom_ui(self, parent: QWidget) -> list[dict]:
        # 创建密钥输入框
        key_input = QLineEdit(parent)
        key_input.setPlaceholderText("请输入16/24/32字节的密钥")
        key_input.setEchoMode(QLineEdit.Password)
        key_input.setStyleSheet(style.get_text_edit_style())
        
        # 创建模式选择下拉框
        mode_select = QComboBox(parent)
        mode_select.addItems(self.MODES.keys())
        mode_select.setStyleSheet(style.get_combobox_style())
        
        # 创建填充方式下拉框
        padding_select = QComboBox(parent)
        padding_select.addItems(self.PADDINGS)
        padding_select.setStyleSheet(style.get_combobox_style())
        
        # 创建操作选择下拉框
        operation_select = QComboBox(parent)
        operation_select.addItems(["加密", "解密"])
        operation_select.setStyleSheet(style.get_combobox_style())
        
        # 创建密钥长度选择
        key_size_select = QComboBox(parent)
        key_size_select.addItems(["128位", "192位", "256位"])
        key_size_select.setStyleSheet(style.get_combobox_style())
        
        # 创建随机IV开关
        use_random_iv = QComboBox(parent)
        use_random_iv.addItems(["使用随机IV", "自定义IV"])
        use_random_iv.setStyleSheet(style.get_combobox_style())
        
        # 创建IV输入框
        iv_input = QLineEdit(parent)
        iv_input.setPlaceholderText("请输入16字节的IV（仅在自定义IV时需要）")
        iv_input.setStyleSheet(style.get_text_edit_style())

        return [
            {
                "type": "input",
                "label": "密钥",
                "widget": key_input,
                "key": "key"
            },
            {
                "type": "combobox",
                "label": "密钥长度",
                "widget": key_size_select,
                "key": "key_size"
            },
            {
                "type": "combobox",
                "label": "加密模式",
                "widget": mode_select,
                "key": "mode"
            },
            {
                "type": "combobox",
                "label": "填充方式",
                "widget": padding_select,
                "key": "padding"
            },
            {
                "type": "combobox",
                "label": "IV设置",
                "widget": use_random_iv,
                "key": "use_random_iv"
            },
            {
                "type": "input",
                "label": "IV值",
                "widget": iv_input,
                "key": "iv"
            },
            {
                "type": "combobox",
                "label": "操作",
                "widget": operation_select,
                "key": "operation"
            }
        ]

    def validate_input(self, **kwargs) -> tuple[bool, str]:
        key = kwargs.get("key", "")
        mode = kwargs.get("mode", "")
        use_random_iv = kwargs.get("use_random_iv", "")
        iv = kwargs.get("iv", "")
        key_size = kwargs.get("key_size", "")
        
        if not key:
            return False, "密钥不能为空"
        
        # 检查密钥长度
        key_length = len(key.encode())
        expected_length = {
            "128位": 16,
            "192位": 24,
            "256位": 32
        }.get(key_size)
        
        if key_length != expected_length:
            return False, f"密钥长度必须为{expected_length}字节"
            
        # 检查IV
        if mode != "ECB":
            if use_random_iv == "自定义IV":
                if not iv:
                    return False, "使用自定义IV时，IV不能为空"
                if len(iv.encode()) != 16:
                    return False, "IV长度必须为16字节"
            
        return True, ""

    def _pad_data(self, data: bytes, padding: str) -> bytes:
        if padding == "PKCS7":
            return pad(data, AES.block_size)
        elif padding == "ISO7816":
            # ISO7816填充：添加0x80后跟随必要数量的0x00
            pad_len = AES.block_size - (len(data) % AES.block_size)
            if pad_len == 0:
                pad_len = AES.block_size
            padding_bytes = bytes([0x80]) + bytes([0x00] * (pad_len - 1))
            return data + padding_bytes
        elif padding == "X923":
            # X923填充：用0x00填充，最后一个字节是填充长度
            pad_len = AES.block_size - (len(data) % AES.block_size)
            if pad_len == 0:
                pad_len = AES.block_size
            padding_bytes = bytes([0x00] * (pad_len - 1)) + bytes([pad_len])
            return data + padding_bytes
        return data

    def _unpad_data(self, data: bytes, padding: str) -> bytes:
        if padding == "PKCS7":
            return unpad(data, AES.block_size)
        elif padding == "ISO7816":
            # 移除ISO7816填充
            i = len(data) - 1
            while i > 0 and data[i] == 0x00:
                i -= 1
            if data[i] == 0x80:
                return data[:i]
            return data
        elif padding == "X923":
            # 移除X923填充
            pad_len = data[-1]
            if pad_len > AES.block_size:
                return data
            padding = data[-pad_len:-1]
            if all(p == 0x00 for p in padding):
                return data[:-pad_len]
            return data
        return data

    def process(self, input_data: str, **kwargs) -> str:
        try:
            key = kwargs.get("key", "").encode()
            mode = kwargs.get("mode", "CBC")
            padding = kwargs.get("padding", "PKCS7")
            operation = kwargs.get("operation", "加密")
            use_random_iv = kwargs.get("use_random_iv", "使用随机IV")
            iv = kwargs.get("iv", "").encode() if kwargs.get("iv") else None
            
            mode_value = self.MODES[mode]
            
            if operation == "加密":
                # 加密过程
                if mode != "ECB":
                    if use_random_iv == "使用随机IV":
                        iv = get_random_bytes(16)
                    cipher = AES.new(key, mode_value, iv)
                else:
                    cipher = AES.new(key, mode_value)
                
                data = self._pad_data(input_data.encode(), padding)
                ciphertext = cipher.encrypt(data)
                
                if mode != "ECB":
                    # 对于需要IV的模式，将IV附加到密文前
                    result = base64.b64encode(iv + ciphertext).decode()
                else:
                    result = base64.b64encode(ciphertext).decode()
                
                return result
            else:
                # 解密过程
                try:
                    encrypted = base64.b64decode(input_data)
                    
                    if mode != "ECB":
                        # 从密文中提取IV
                        iv = encrypted[:16]
                        ciphertext = encrypted[16:]
                        cipher = AES.new(key, mode_value, iv)
                    else:
                        ciphertext = encrypted
                        cipher = AES.new(key, mode_value)
                    
                    decrypted = cipher.decrypt(ciphertext)
                    return self._unpad_data(decrypted, padding).decode()
                    
                except Exception as e:
                    return f"解密失败: {str(e)}"
                    
        except Exception as e:
            return f"处理失败: {str(e)}"
