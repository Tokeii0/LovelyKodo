import hashlib
from plugins import Plugin

class MD5Plugin(Plugin):
    @property
    def name(self) -> str:
        return "MD5哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的MD5哈希值 (128位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.md5(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA1Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA1哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA1哈希值 (160位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha1(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA224Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA224哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA224哈希值 (224位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha224(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA256Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA256哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA256哈希值 (256位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha256(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA384Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA384哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA384哈希值 (384位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha384(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA512Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA512哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA512哈希值 (512位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha512(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA3_224Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA3-224哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA3-224哈希值 (224位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha3_224(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA3_256Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA3-256哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA3-256哈希值 (256位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha3_256(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA3_384Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA3-384哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA3-384哈希值 (384位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha3_384(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class SHA3_512Plugin(Plugin):
    @property
    def name(self) -> str:
        return "SHA3-512哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的SHA3-512哈希值 (512位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.sha3_512(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class Blake2bPlugin(Plugin):
    @property
    def name(self) -> str:
        return "BLAKE2b哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的BLAKE2b哈希值 (512位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.blake2b(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"


class Blake2sPlugin(Plugin):
    @property
    def name(self) -> str:
        return "BLAKE2s哈希"
    
    @property
    def category(self) -> str:
        return "哈希计算"
    
    @property
    def description(self) -> str:
        return "计算文本的BLAKE2s哈希值 (256位)"
    
    def process(self, input_data: str) -> str:
        try:
            return hashlib.blake2s(input_data.encode()).hexdigest()
        except Exception as e:
            return f"错误: {str(e)}"
