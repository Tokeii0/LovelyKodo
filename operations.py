import base64
import hashlib
import urllib.parse
import qrcode
from io import BytesIO
from PIL import Image

class Operations:
    @staticmethod
    def base64_encode(data: str) -> str:
        try:
            return base64.b64encode(data.encode()).decode()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def base64_decode(data: str) -> str:
        try:
            return base64.b64decode(data.encode()).decode()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def hex_encode(data: str) -> str:
        try:
            return data.encode().hex()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def hex_decode(data: str) -> str:
        try:
            return bytes.fromhex(data).decode()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def url_encode(data: str) -> str:
        try:
            return urllib.parse.quote(data)
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def url_decode(data: str) -> str:
        try:
            return urllib.parse.unquote(data)
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def md5_hash(data: str) -> str:
        try:
            return hashlib.md5(data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def sha1_hash(data: str) -> str:
        try:
            return hashlib.sha1(data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def sha256_hash(data: str) -> str:
        try:
            return hashlib.sha256(data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def to_upper(data: str) -> str:
        try:
            return data.upper()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def to_lower(data: str) -> str:
        try:
            return data.lower()
        except Exception as e:
            return f"错误: {str(e)}"
    
    @staticmethod
    def generate_qr(data: str) -> Image:
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            return img
        except Exception as e:
            return f"错误: {str(e)}"
