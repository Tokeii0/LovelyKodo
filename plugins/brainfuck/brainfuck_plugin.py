from .. import Plugin
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                              QTextEdit, QPushButton, QGroupBox, QSpinBox)
from PySide6.QtCore import Qt
import style
from style import FONTS

class BrainfuckInterpreter:
    """Brainfuck解释器"""
    def __init__(self, memory_size=30000):
        self.memory_size = memory_size
        self.reset()
    
    def reset(self):
        """重置解释器状态"""
        self.memory = [0] * self.memory_size
        self.data_pointer = 0
        self.output = []
        self.input_buffer = []
    
    def interpret(self, code: str, input_text: str = "") -> str:
        """解释执行Brainfuck代码"""
        try:
            # 重置状态
            self.reset()
            
            # 预处理输入
            self.input_buffer = list(input_text)
            
            # 移除无关字符
            code = ''.join(c for c in code if c in '><+-.,[]')
            
            # 匹配括号
            brackets = self._match_brackets(code)
            
            # 执行代码
            code_pointer = 0
            while code_pointer < len(code):
                command = code[code_pointer]
                
                if command == '>':
                    self.data_pointer = (self.data_pointer + 1) % self.memory_size
                elif command == '<':
                    self.data_pointer = (self.data_pointer - 1) % self.memory_size
                elif command == '+':
                    self.memory[self.data_pointer] = (self.memory[self.data_pointer] + 1) % 256
                elif command == '-':
                    self.memory[self.data_pointer] = (self.memory[self.data_pointer] - 1) % 256
                elif command == '.':
                    self.output.append(chr(self.memory[self.data_pointer]))
                elif command == ',':
                    if self.input_buffer:
                        self.memory[self.data_pointer] = ord(self.input_buffer.pop(0))
                    else:
                        self.memory[self.data_pointer] = 0
                elif command == '[':
                    if self.memory[self.data_pointer] == 0:
                        code_pointer = brackets[code_pointer]
                elif command == ']':
                    if self.memory[self.data_pointer] != 0:
                        code_pointer = brackets[code_pointer]
                
                code_pointer += 1
            
            return ''.join(self.output)
            
        except Exception as e:
            return f"执行错误: {str(e)}"
    
    def _match_brackets(self, code: str) -> dict:
        """匹配代码中的括号对"""
        stack = []
        brackets = {}
        
        for i, c in enumerate(code):
            if c == '[':
                stack.append(i)
            elif c == ']':
                if not stack:
                    raise ValueError("括号不匹配：']' 没有对应的 '['")
                j = stack.pop()
                brackets[j] = i
                brackets[i] = j
        
        if stack:
            raise ValueError("括号不匹配：'[' 没有对应的 ']'")
            
        return brackets

class BrainfuckPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.interpreter = BrainfuckInterpreter()
        self.input_text = ""
        self.result_text = ""
        
        # UI组件
        self.input_edit = None
        self.result_edit = None
        self.memory_size_spin = None
    
    @property
    def name(self) -> str:
        return "Brainfuck解释器"
    
    @property
    def category(self) -> str:
        return "代码解释器"
    
    @property
    def description(self) -> str:
        return "解释执行Brainfuck代码，支持自定义内存大小和输入"
    
    def process(self, text: str) -> str:
        """处理输入的Brainfuck代码"""
        return self.interpreter.interpret(text, self.input_text)
    
    def create_ui(self, parent: QWidget, layout: QVBoxLayout):
        """创建UI界面"""
        # 参数设置组
        param_group = QGroupBox("参数设置", parent)
        param_group.setFont(FONTS['title'])
        param_group.setStyleSheet(style.get_group_box_style())
        param_layout = QHBoxLayout(param_group)
        
        # 内存大小设置
        memory_label = QLabel("内存大小:", param_group)
        memory_label.setFont(FONTS['body'])
        self.memory_size_spin = QSpinBox(param_group)
        self.memory_size_spin.setFont(FONTS['body'])
        self.memory_size_spin.setRange(1000, 100000)
        self.memory_size_spin.setValue(30000)
        self.memory_size_spin.setSingleStep(1000)
        self.memory_size_spin.valueChanged.connect(self._on_memory_size_changed)
        
        # 执行和停止按钮
        run_button = QPushButton("执行", param_group)
        run_button.setFont(FONTS['body'])
        run_button.setStyleSheet(style.get_run_button_style())
        run_button.clicked.connect(self._on_run_clicked)
        
        stop_button = QPushButton("停止", param_group)
        stop_button.setFont(FONTS['body'])
        stop_button.setStyleSheet(style.get_button_style())
        stop_button.clicked.connect(self._on_stop_clicked)
        
        param_layout.addWidget(memory_label)
        param_layout.addWidget(self.memory_size_spin)
        param_layout.addStretch()
        param_layout.addWidget(run_button)
        param_layout.addWidget(stop_button)
        
        layout.addWidget(param_group)
        
        # 输入文本组
        input_group = QGroupBox("程序输入", parent)
        input_group.setFont(FONTS['title'])
        input_group.setStyleSheet(style.get_group_box_style())
        input_layout = QVBoxLayout(input_group)
        
        self.input_edit = QTextEdit(input_group)
        self.input_edit.setFont(FONTS['mono'])
        self.input_edit.setPlaceholderText("在此输入程序需要的输入文本...")
        self.input_edit.textChanged.connect(self._on_input_changed)
        
        input_layout.addWidget(self.input_edit)
        layout.addWidget(input_group)
        
        # 执行结果组
        result_group = QGroupBox("执行结果", parent)
        result_group.setFont(FONTS['title'])
        result_group.setStyleSheet(style.get_group_box_style())
        result_layout = QVBoxLayout(result_group)
        
        self.result_edit = QTextEdit(result_group)
        self.result_edit.setFont(FONTS['mono'])
        self.result_edit.setReadOnly(True)
        
        result_layout.addWidget(self.result_edit)
        layout.addWidget(result_group)
    
    def _on_memory_size_changed(self):
        """内存大小改变时的处理函数"""
        self.interpreter = BrainfuckInterpreter(self.memory_size_spin.value())
    
    def _on_input_changed(self):
        """输入文本改变时的处理函数"""
        self.input_text = self.input_edit.toPlainText()
    
    def _on_run_clicked(self):
        """执行按钮点击处理函数"""
        if self.input_edit and self.result_edit:
            result = self.process(self.input_edit.toPlainText())
            self.update_result(result)
    
    def _on_stop_clicked(self):
        """停止按钮点击处理函数"""
        # 重置解释器状态
        self.interpreter.reset()
        if self.result_edit:
            self.result_edit.setText("执行已停止")
    
    def update_result(self, text: str):
        """更新执行结果"""
        self.result_text = text
        if self.result_edit:
            self.result_edit.setText(text)
