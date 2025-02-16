from .. import Plugin
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                              QSpinBox, QSlider, QPushButton, QFileDialog, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont
import numpy as np
from PIL import Image
import style
from style import FONTS
import io

class ArnoldCatMap:
    """Arnold's Cat Map 变换实现"""
    def __init__(self):
        pass
        
    def transform(self, image: np.ndarray, iterations: int = 1) -> np.ndarray:
        """
        使用Arnold's Cat Map进行图像变换
        
        Args:
            image: 输入图像（numpy数组）
            iterations: 迭代次数
            
        Returns:
            变换后的图像
        """
        N = image.shape[0]
        if N != image.shape[1]:
            raise ValueError("图像必须是正方形")
            
        # 创建结果图像和临时图像
        result = np.copy(image)
        temp = np.empty_like(image)
        
        # 迭代应用变换
        for _ in range(iterations):
            # 对每个像素计算新位置
            for y in range(N):
                for x in range(N):
                    # 计算新坐标
                    xNew = (2 * x + y) % N
                    yNew = (x + y) % N
                    # 复制像素到新位置
                    temp[yNew, xNew] = result[y, x]
            
            # 交换结果和临时图像
            result, temp = temp, result
        
        return result

class ArnoldCatMapPlugin(Plugin):
    name = "Arnold's Cat Map"
    category = "图像变换"
    description = "使用Arnold's Cat Map进行图像混沌变换"
    
    def __init__(self):
        super().__init__()
        self.image_label = None
        self.iteration_slider = None
        self.iteration_spinbox = None
        self.current_image = None
        self.transformer = ArnoldCatMap()
        
        # 动画相关
        self.current_iterations = 0  # 当前迭代次数
        self.target_iterations = 0   # 目标迭代次数
        self.original_image = None   # 原始图像
        self.temp_image = None       # 临时图像
        self.animation_timer = None  # 动画定时器
        
    def _setup_animation_timer(self):
        """设置动画定时器"""
        if self.animation_timer is None:
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._update_animation)
            self.animation_timer.setInterval(1)  # 1ms更新一次
        
    def _update_animation(self):
        """更新动画帧"""
        if self.current_image is None:
            return
            
        # 计算当前迭代次数与目标次数的差值
        diff = self.target_iterations - self.current_iterations
        
        if diff == 0:
            self.animation_timer.stop()
            return
            
        # 确定迭代方向
        step = 1 if diff > 0 else -1
        self.current_iterations += step
        
        try:
            # 对每个像素计算新位置
            N = self.current_image.shape[0]
            temp = np.empty_like(self.temp_image)
            
            for y in range(N):
                for x in range(N):
                    # 计算新坐标
                    xNew = (2 * x + y) % N
                    yNew = (x + y) % N
                    # 根据迭代方向复制像素
                    if step > 0:
                        temp[yNew, xNew] = self.current_image[y, x]
                    else:
                        temp[y, x] = self.current_image[yNew, xNew]
            
            # 交换图像
            self.current_image, self.temp_image = temp, self.current_image
            
            # 只在差值较小或是10的倍数时更新显示
            if abs(diff) < 10 or abs(diff) % 10 == 0:
                self._display_image(self.current_image)
                
        except Exception as e:
            self.animation_timer.stop()
            QMessageBox.warning(None, "错误", f"图像处理失败: {str(e)}")
    
    def _display_image(self, image):
        """显示图像"""
        try:
            # 转换为QImage并显示
            height, width, channel = image.shape
            bytes_per_line = width * channel
            
            # 使用Format_RGB888确保正确的颜色显示
            q_img = QImage(image.data, width, height, 
                         bytes_per_line, QImage.Format.Format_RGB888).copy()
            
            # 等比例缩放到标签大小
            label_size = self.image_label.size()
            scaled_pixmap = QPixmap.fromImage(q_img).scaled(
                label_size, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            QMessageBox.warning(None, "错误", f"显示图像失败: {str(e)}")
    
    def _on_slider_changed(self):
        """滑动条改变时的处理函数"""
        self.target_iterations = self.iteration_slider.value()
        self.iteration_spinbox.setValue(self.target_iterations)
        
        # 确保动画定时器已设置
        self._setup_animation_timer()
        
        # 如果定时器没有运行，启动它
        if not self.animation_timer.isActive():
            self.animation_timer.start()
    
    def _on_spinbox_changed(self):
        """输入框改变时的处理函数"""
        self.target_iterations = self.iteration_spinbox.value()
        self.iteration_slider.setValue(self.target_iterations)
        
        # 确保动画定时器已设置
        self._setup_animation_timer()
        
        # 如果定时器没有运行，启动它
        if not self.animation_timer.isActive():
            self.animation_timer.start()
            
    def _load_image(self):
        """加载图像文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            None, "选择图像", "", "图像文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # 使用PIL打开图像
                image = Image.open(file_path)
                
                # 确保图像是RGB模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 获取原始尺寸
                original_size = image.size
                
                # 如果图像太小，将其放大到标准尺寸
                MIN_SIZE = 128  # 降低最小标准尺寸
                if original_size[0] < MIN_SIZE or original_size[1] < MIN_SIZE:
                    # 计算缩放比例
                    ratio = MIN_SIZE / min(original_size)
                    new_size = tuple(int(dim * ratio) for dim in original_size)
                    # 使用LANCZOS重采样方法进行高质量放大
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # 确保图像是正方形
                width, height = image.size
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                image = image.crop((left, top, left + size, top + size))
                
                # 转换为numpy数组，确保是uint8类型
                self.current_image = np.array(image, dtype=np.uint8)
                self.temp_image = np.empty_like(self.current_image)
                
                # 重置迭代计数
                self.current_iterations = 0
                self.target_iterations = 0
                self.iteration_slider.setValue(0)
                self.iteration_spinbox.setValue(0)
                
                # 更新显示
                self._display_image(self.current_image)
                
            except Exception as e:
                QMessageBox.warning(None, "错误", f"加载图像失败: {str(e)}")
    
    def create_ui(self, parent: QWidget, layout: QVBoxLayout) -> None:
        """创建UI界面"""
        # 创建主容器
        container = QWidget(parent)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # 参数设置区域 (1/5的高度)
        param_group = QGroupBox("变换参数", parent)
        param_group.setStyleSheet(style.get_group_box_style())
        param_group.setMinimumWidth(600)  # 设置最小宽度
        param_layout = QHBoxLayout(param_group)
        param_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建一个水平布局来包含所有参数
        params_container = QHBoxLayout()
        params_container.setSpacing(20)  # 增加组件之间的间距
        
        # 迭代次数设置
        iteration_layout = QHBoxLayout()
        iteration_layout.setSpacing(5)
        
        iteration_label = QLabel("迭代:", parent)
        iteration_label.setFont(QFont(FONTS['body']))
        
        self.iteration_slider = QSlider(Qt.Orientation.Horizontal, parent)
        self.iteration_slider.setRange(0, 2000)
        self.iteration_slider.setValue(0)
        self.iteration_slider.setFixedWidth(400)  # 增加滑动条宽度
        self.iteration_slider.valueChanged.connect(self._on_slider_changed)
        
        self.iteration_spinbox = QSpinBox(parent)
        self.iteration_spinbox.setRange(0, 2000)
        self.iteration_spinbox.setValue(0)
        self.iteration_spinbox.setFixedWidth(80)  # 调整输入框宽度
        self.iteration_spinbox.valueChanged.connect(self._on_spinbox_changed)
        
        iteration_layout.addWidget(iteration_label)
        iteration_layout.addWidget(self.iteration_slider)
        iteration_layout.addWidget(self.iteration_spinbox)
        
        # 添加迭代控制到主容器
        params_container.addLayout(iteration_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        load_btn = QPushButton("加载", parent)
        load_btn.setFont(QFont(FONTS['body']))
        load_btn.setStyleSheet(style.get_button_style())
        load_btn.setFixedWidth(60)
        load_btn.clicked.connect(self._load_image)
        
        save_btn = QPushButton("保存", parent)
        save_btn.setFont(QFont(FONTS['body']))
        save_btn.setStyleSheet(style.get_button_style())
        save_btn.setFixedWidth(60)
        save_btn.clicked.connect(self._save_image)
        
        button_layout.addWidget(load_btn)
        button_layout.addWidget(save_btn)
        
        # 添加按钮到主容器
        params_container.addLayout(button_layout)
        
        # 将所有参数添加到参数组
        param_layout.addLayout(params_container)
        param_layout.addStretch()  # 添加弹性空间
        
        # 图像预览区域
        preview_group = QGroupBox("图像预览", parent)
        preview_group.setStyleSheet(style.get_group_box_style())
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        
        self.image_label = QLabel(parent)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #cccccc; }")
        preview_layout.addWidget(self.image_label)
        
        # 添加到主布局，设置比例1:5
        main_layout.addWidget(param_group, 1)
        main_layout.addWidget(preview_group, 5)
        
        # 添加到插件布局
        layout.addWidget(container)

    def _save_image(self):
        """保存图像"""
        if self.current_image is None:
            QMessageBox.warning(None, "警告", "没有可保存的图像")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "保存图像",
            "",
            "PNG图像 (*.png);;JPEG图像 (*.jpg *.jpeg);;BMP图像 (*.bmp)"
        )
        
        if file_path:
            try:
                # 获取当前显示的图像
                pixmap = self.image_label.pixmap()
                if pixmap:
                    # 保存为文件
                    pixmap.save(file_path)
            except Exception as e:
                QMessageBox.warning(None, "错误", f"保存图像失败: {str(e)}")

    def process(self, text: str) -> str:
        """处理输入文本 - 这个插件不处理文本"""
        return text
