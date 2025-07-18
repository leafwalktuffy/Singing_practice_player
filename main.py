import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QSlider, QLabel, QFileDialog, 
                             QProgressBar, QGroupBox, QGridLayout, QFrame, QTextEdit)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont, QTextCursor, QFontDatabase
import time

class ClickJumpSlider(QSlider):
    """支持精确点击跳转的进度条 - 安全简化版本"""
    
    def __init__(self, orientation, parent=None, slider_type="progress"):
        super().__init__(orientation, parent)
        self._parent_player = None
        self._slider_type = slider_type  # "progress" 或 "volume"
        
    def set_parent_player(self, parent_player):
        """设置父播放器引用，用于回调"""
        self._parent_player = parent_player
        
    def mousePressEvent(self, event):
        """安全的点击跳转实现"""
        if event.button() == Qt.LeftButton and self.orientation() == Qt.Horizontal:
            # 计算点击位置
            click_pos = event.x()
            slider_width = self.width()
            
            if slider_width > 0:
                # 简单的比例计算
                value_ratio = click_pos / slider_width
                new_value = int(value_ratio * (self.maximum() - self.minimum()) + self.minimum())
                new_value = max(self.minimum(), min(self.maximum(), new_value))
                
                # 设置新值
                self.setValue(new_value)
                
                # 通知父播放器，根据滑块类型调用不同方法
                if self._parent_player:
                    if self._slider_type == "progress":
                        self._parent_player.on_progress_clicked(new_value)
                    elif self._slider_type == "volume":
                        self._parent_player.on_volume_clicked(new_value)
                    
        # 调用父类方法保持正常拖动功能
        super().mousePressEvent(event)

class LyricDisplay(QTextEdit):
    """歌词展示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        """设置歌词展示界面"""
        # 设置只读
        self.setReadOnly(True)
        
        # 加载思源黑体字体文件
        font_path = "SourceHanSansSC-Regular-2.otf"
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    font_family = font_families[0]
                    font = QFont(font_family, 18)
                else:
                    # 回退到系统字体
                    font = QFont("Microsoft YaHei", 18)
            else:
                # 回退到系统字体
                font = QFont("Microsoft YaHei", 18)
        else:
            # 回退到系统字体
            font = QFont("Microsoft YaHei", 18)
        
        self.setFont(font)
        
        # 设置样式，支持垂直居中
        self.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                color: #495057;
                selection-background-color: #007bff;
            }
        """)
        
        # 设置最小高度，允许随窗口调整
        self.setMinimumHeight(150)
        
        # 设置垂直滚动条策略
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 初始化显示 - 先设置为空，后续会通过refresh_lyrics_display更新
        self.setPlainText("")
        
    def get_dynamic_font_sizes(self):
        """根据窗口大小计算动态字体大小"""
        if self.parent_window:
            window_width = self.parent_window.width()
            window_height = self.parent_window.height()
            # 基础字体大小根据窗口宽度和高度调整
            width_factor = max(14, min(32, int(window_width / 35)))
            height_factor = max(14, min(32, int(window_height / 25)))
            base_size = min(width_factor, height_factor)
            current_size = base_size + 10
            side_size = base_size - 2
        else:
            current_size = 26
            side_size = 18
        
        return current_size, side_size
    
    def update_lyrics(self, current_line, prev_line="", next_line=""):
        """更新歌词显示"""
        # 获取动态字体大小
        current_size, side_size = self.get_dynamic_font_sizes()
        
        # 获取控件高度，估算每行的高度
        widget_height = self.height()
        font_height = current_size + 8  # 估算每行高度（包括行间距）
        
        # 计算可显示的行数和需要的空行数
        total_lines = max(1, (widget_height - 60) // font_height)  # 减去padding
        content_lines = 3  # 歌词占3行
        empty_lines_top = max(0, (total_lines - content_lines) // 2)
        
        # 构建垂直居中的HTML文本
        lyrics_text = "<div style='text-align: center; line-height: 1.4;'>"
        
        # 添加顶部空行实现垂直居中
        for _ in range(empty_lines_top):
            lyrics_text += f"<p style='font-size: {font_height}px; margin: 0; height: {font_height}px;'>&nbsp;</p>"
        
        # 上一行歌词（较小字体，灰色）
        if prev_line:
            lyrics_text += f"<p style='color: #6c757d; font-size: {side_size}px; margin: 2px 0; font-weight: normal;'>{prev_line}</p>"
        else:
            lyrics_text += f"<p style='color: #6c757d; font-size: {side_size}px; margin: 2px 0; font-weight: normal;'>&nbsp;</p>"
            
        # 当前行歌词（大字体，蓝色加粗）
        if current_line:
            lyrics_text += f"<p style='color: #007bff; font-size: {current_size}px; font-weight: bold; margin: 4px 0;'>{current_line}</p>"
        else:
            lyrics_text += f"<p style='color: #007bff; font-size: {current_size}px; font-weight: bold; margin: 4px 0;'>&nbsp;</p>"
            
        # 下一行歌词（较小字体，灰色）
        if next_line:
            lyrics_text += f"<p style='color: #6c757d; font-size: {side_size}px; margin: 2px 0; font-weight: normal;'>{next_line}</p>"
        else:
            lyrics_text += f"<p style='color: #6c757d; font-size: {side_size}px; margin: 2px 0; font-weight: normal;'>&nbsp;</p>"
        
        lyrics_text += "</div>"
        
        # 设置HTML文本
        self.setHtml(lyrics_text)

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("伴唱播放器")
        self.setGeometry(100, 100, 900, 700)
        
        # 初始化两个媒体播放器
        self.player1 = QMediaPlayer()
        self.player2 = QMediaPlayer()
        
        # 播放器状态
        self.player1_playing = False
        self.player2_playing = False
        self.player1_file = ""
        self.player2_file = ""
        self.lyric_file = ""
        self.is_playing = False  # 全局播放状态
        
        # 音量控制状态
        self.volume_balance = 50  # 默认在中间位置
        
        # 歌词相关
        self.lyrics = []  # 存储歌词数据
        self.current_lyric_index = 0  # 当前歌词索引
        
        # 配置文件路径
        self.config_file = "player_config.json"
        
        # 暂停状态下的更新计数器
        self.pause_update_counter = 0
        
        # 进度条更新定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # 每100ms更新一次
        
        # 歌词更新定时器
        self.lyric_timer = QTimer()
        self.lyric_timer.timeout.connect(self.update_lyrics)
        self.lyric_timer.start(100)  # 每100ms更新一次歌词
        
        self.init_ui()
        self.setup_connections()
        
        # 在UI初始化后加载配置
        self.load_config()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # 歌词展示区域
        lyric_group = QGroupBox("歌词展示")
        lyric_layout = QVBoxLayout(lyric_group)
        
        self.lyric_display = LyricDisplay(self)
        lyric_layout.addWidget(self.lyric_display)
        main_layout.addWidget(lyric_group)
        
        # 延迟初始化歌词显示，确保控件已经完全渲染
        QTimer.singleShot(100, self.init_lyric_display)
        
        # 共享进度条区域
        progress_group = QGroupBox("播放进度控制")
        progress_layout = QVBoxLayout(progress_group)
        
        # 进度条
        self.progress_bar = ClickJumpSlider(Qt.Horizontal)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        self.progress_bar.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #5c6bc0;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border-radius: 4px;
            }
        """)
        
        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.time_label)
        main_layout.addWidget(progress_group)
        
        # 音量平衡控制区域
        volume_group = QGroupBox("音量平衡控制")
        volume_layout = QVBoxLayout(volume_group)
        
        # 音量平衡说明
        volume_info = QLabel("左滑减少人声音量 | 右滑减少伴奏音量")
        volume_info.setAlignment(Qt.AlignCenter)
        volume_info.setStyleSheet("color: #666666; font-style: italic; margin: 5px;")
        volume_layout.addWidget(volume_info)
        
        # 音量平衡滑块
        self.volume_balance_slider = ClickJumpSlider(Qt.Horizontal, slider_type="volume")
        self.volume_balance_slider.setMinimum(0)
        self.volume_balance_slider.setMaximum(100)
        self.volume_balance_slider.setValue(50)  # 默认在中间
        self.volume_balance_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b6b, stop:0.5 #4CAF50, stop:1 #4ecdc4);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #1976D2;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
        # 音量平衡标签
        self.volume_balance_label = QLabel("平衡: 人声 50% | 伴奏 50%")
        self.volume_balance_label.setAlignment(Qt.AlignCenter)
        
        volume_layout.addWidget(self.volume_balance_slider)
        volume_layout.addWidget(self.volume_balance_label)
        main_layout.addWidget(volume_group)
        
        # 文件选择区域 - 三个并列
        files_group = QGroupBox("文件选择")
        files_layout = QHBoxLayout(files_group)
        
        # 伴奏播放器
        accompaniment_group = self.create_player_group("伴奏", 1)
        files_layout.addWidget(accompaniment_group)
        
        # 人声播放器
        vocal_group = self.create_player_group("人声", 2)
        files_layout.addWidget(vocal_group)
        
        # 歌词文件选择
        lyric_group = self.create_lyric_group()
        files_layout.addWidget(lyric_group)
        
        main_layout.addWidget(files_group)
        
        # 全局控制按钮
        global_controls = QHBoxLayout()
        
        self.play_pause_btn = QPushButton("▶ 播放")
        self.stop_all_btn = QPushButton("⏹ 停止")
        
        # 设置播放/暂停按钮样式
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 12px 24px;
                text-align: center;
                font-size: 16px;
                font-weight: bold;
                margin: 4px 2px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        global_controls.addWidget(self.play_pause_btn)
        global_controls.addWidget(self.stop_all_btn)
        
        main_layout.addLayout(global_controls)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLabel {
                color: #333333;
            }
        """)
        
    def create_player_group(self, title, player_num):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        
        # 文件选择按钮
        select_btn = QPushButton(f"选择{title}文件")
        layout.addWidget(select_btn)
        
        # 文件路径标签
        file_label = QLabel("未选择文件")
        file_label.setWordWrap(True)
        file_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        layout.addWidget(file_label)
        
        # 状态标签
        status_label = QLabel("就绪")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(status_label)
        
        # 保存引用
        if player_num == 1:
            self.player1_select_btn = select_btn
            self.player1_file_label = file_label
            self.player1_status_label = status_label
        else:
            self.player2_select_btn = select_btn
            self.player2_file_label = file_label
            self.player2_status_label = status_label
            
        return group
    
    def create_lyric_group(self):
        """创建歌词文件选择组"""
        group = QGroupBox("歌词")
        layout = QVBoxLayout(group)
        
        # 文件选择按钮
        self.lyric_select_btn = QPushButton("选择歌词文件")
        layout.addWidget(self.lyric_select_btn)
        
        # 文件路径标签
        self.lyric_file_label = QLabel("未选择文件")
        self.lyric_file_label.setWordWrap(True)
        self.lyric_file_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        layout.addWidget(self.lyric_file_label)
        
        # 状态标签
        self.lyric_status_label = QLabel("就绪")
        self.lyric_status_label.setAlignment(Qt.AlignCenter)
        self.lyric_status_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.lyric_status_label)
        
        return group
        
    def setup_connections(self):
        # 播放器1连接
        self.player1_select_btn.clicked.connect(lambda: self.select_file(1))
        
        # 播放器2连接
        self.player2_select_btn.clicked.connect(lambda: self.select_file(2))
        
        # 歌词文件连接
        self.lyric_select_btn.clicked.connect(self.select_lyric_file)
        
        # 全局控制连接
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.stop_all_btn.clicked.connect(self.stop_all)
        
        # 进度条连接
        self.progress_bar.sliderPressed.connect(self.progress_pressed)
        self.progress_bar.sliderReleased.connect(self.progress_released)
        self.progress_bar.sliderMoved.connect(self.progress_moved)
        
        # 音量平衡连接
        self.volume_balance_slider.valueChanged.connect(self.update_volume_balance)
        
        # 设置进度条点击回调
        self.progress_bar.set_parent_player(self)
        
        # 设置音量平衡滑块点击回调
        self.volume_balance_slider.set_parent_player(self)
        
    def select_file(self, player_num):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f"选择音乐文件 - {'伴奏' if player_num == 1 else '人声'}",
            "",
            "音频文件 (*.mp3 *.wav *.flac *.m4a *.ogg);;所有文件 (*)"
        )
        
        if file_path:
            if player_num == 1:
                self.player1_file = file_path
                self.player1_file_label.setText(os.path.basename(file_path))
                self.player1_status_label.setText("文件已加载")
                self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            else:
                self.player2_file = file_path
                self.player2_file_label.setText(os.path.basename(file_path))
                self.player2_status_label.setText("文件已加载")
                self.player2.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            
            # 保存配置
            self.save_config()
    
    def select_lyric_file(self):
        """选择歌词文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择歌词文件",
            "",
            "歌词文件 (*.lrc *.txt);;所有文件 (*)"
        )
        
        if file_path:
            self.lyric_file = file_path
            self.lyric_file_label.setText(os.path.basename(file_path))
            self.lyric_status_label.setText("文件已加载")
            
            # 加载歌词
            self.load_lyrics(file_path)
            
            # 保存配置
            self.save_config()
    
    def load_lyrics(self, file_path):
        """加载歌词文件"""
        try:
            self.lyrics = []
            self.current_lyric_index = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and line.startswith('['):
                    # 解析LRC格式的时间标签
                    try:
                        time_str = line[1:line.find(']')]
                        text = line[line.find(']')+1:].strip()
                        
                        if text and ':' in time_str:
                            # 解析时间
                            time_parts = time_str.split(':')
                            if len(time_parts) == 2:
                                minutes = int(time_parts[0])
                                seconds = float(time_parts[1])
                                time_ms = int((minutes * 60 + seconds) * 1000)
                                
                                self.lyrics.append({
                                    'time': time_ms,
                                    'text': text
                                })
                    except:
                        continue
                elif line and not line.startswith('['):
                    # 普通文本行
                    self.lyrics.append({
                        'time': len(self.lyrics) * 3000,  # 每行3秒
                        'text': line
                    })
            
            # 按时间排序
            self.lyrics.sort(key=lambda x: x['time'])
            
            print(f"加载了 {len(self.lyrics)} 行歌词")
            
            # 歌词加载后立即显示第一行
            if self.lyrics:
                first_line = self.lyrics[0]['text']
                second_line = self.lyrics[1]['text'] if len(self.lyrics) > 1 else ""
                self.lyric_display.update_lyrics(first_line, "", second_line)
            else:
                self.lyric_display.setPlainText("歌词文件无有效内容")
            
        except Exception as e:
            print(f"加载歌词文件失败: {e}")
            self.lyrics = []
            self.lyric_display.setPlainText("歌词文件加载失败")
    
    def update_lyrics(self):
        """更新歌词显示"""
        if not self.lyrics:
            return
        
        # 获取当前播放时间
        current_time = 0
        if self.player1_file:
            current_time = self.player1.position()
        elif self.player2_file:
            current_time = self.player2.position()
        
        # 查找当前应该显示的歌词
        current_lyric = ""
        prev_lyric = ""
        next_lyric = ""
        
        for i, lyric in enumerate(self.lyrics):
            if lyric['time'] <= current_time:
                current_lyric = lyric['text']
                self.current_lyric_index = i
                
                # 获取上一行歌词
                if i > 0:
                    prev_lyric = self.lyrics[i-1]['text']
                
                # 获取下一行歌词
                if i < len(self.lyrics) - 1:
                    next_lyric = self.lyrics[i+1]['text']
        
        # 更新歌词显示
        self.lyric_display.update_lyrics(current_lyric, prev_lyric, next_lyric)
                
    def update_volume_balance(self, value):
        """更新音量平衡"""
        self.volume_balance = value
        
        # 计算人声和伴奏的音量
        if value <= 50:
            # 左半部分：减少人声音量
            vocal_volume = int((value / 50.0) * 100)
            accompaniment_volume = 100
        else:
            # 右半部分：减少伴奏音量
            vocal_volume = 100
            accompaniment_volume = int(((100 - value) / 50.0) * 100)
        
        # 设置音量
        self.player1.setVolume(accompaniment_volume)
        self.player2.setVolume(vocal_volume)
        
        # 更新标签
        self.volume_balance_label.setText(f"平衡: 人声 {vocal_volume}% | 伴奏 {accompaniment_volume}%")
        
    def play_all(self):
        """播放所有音乐"""
        if self.player1_file:
            self.player1.play()
            self.player1_playing = True
            self.player1_status_label.setText("播放中")
            
        if self.player2_file:
            self.player2.play()
            self.player2_playing = True
            self.player2_status_label.setText("播放中")
        
        # 更新全局播放状态
        if self.player1_file or self.player2_file:
            self.is_playing = True
            self.update_play_pause_button()
            
            # 立即更新一次歌词显示
            self.update_lyrics()
        
    def pause_all(self):
        """暂停所有音乐"""
        if self.player1_file:
            self.player1.pause()
            self.player1_playing = False
            self.player1_status_label.setText("已暂停")
            
        if self.player2_file:
            self.player2.pause()
            self.player2_playing = False
            self.player2_status_label.setText("已暂停")
        
        # 更新全局播放状态
        self.is_playing = False
        self.update_play_pause_button()
        
    def stop_all(self):
        """停止所有音乐"""
        if self.player1_file:
            self.player1.stop()
            self.player1_playing = False
            self.player1_status_label.setText("已停止")
            
        if self.player2_file:
            self.player2.stop()
            self.player2_playing = False
            self.player2_status_label.setText("已停止")
        
        # 更新全局播放状态
        self.is_playing = False
        self.update_play_pause_button()
        
    def progress_pressed(self):
        # 暂停进度条更新
        self.timer.stop()
        
    def progress_moved(self, position):
        # 拖动过程中实时更新时间显示
        self.update_time_display_from_position(position)
        
    def progress_released(self):
        # 恢复进度条更新
        self.timer.start(100)
        
        # 获取进度条位置
        position = self.progress_bar.value()
        
        # 计算实际时间位置并设置到播放器（无论是否正在播放）
        if self.player1_file:
            duration = self.player1.duration()
            if duration > 0:
                new_position = int((position / 100.0) * duration)
                self.player1.setPosition(new_position)
                
        if self.player2_file:
            duration = self.player2.duration()
            if duration > 0:
                new_position = int((position / 100.0) * duration)
                self.player2.setPosition(new_position)
        
        # 立即更新歌词显示
        self.update_lyrics()
        
    def on_progress_clicked(self, value):
        """处理进度条点击跳转"""
        # 计算新的播放位置
        if self.player1_file:
            duration = self.player1.duration()
            if duration > 0:
                new_position = int((value / 100.0) * duration)
                self.player1.setPosition(new_position)
                
        if self.player2_file:
            duration = self.player2.duration()
            if duration > 0:
                new_position = int((value / 100.0) * duration)
                self.player2.setPosition(new_position)
                
        # 立即更新时间显示
        self.update_time_display_from_position(value)
        
        # 立即更新歌词显示
        self.update_lyrics()
        
    def on_volume_clicked(self, value):
        """处理音量平衡滑块点击"""
        # 直接调用音量平衡更新方法
        self.update_volume_balance(value)

    def update_progress(self):
        # 判断是否有任何播放器在播放
        is_any_playing = self.player1_playing or self.player2_playing
        
        if is_any_playing:
            # 播放状态：正常获取位置信息
            player1_pos = self.player1.position() if self.player1_playing else 0
            player2_pos = self.player2.position() if self.player2_playing else 0
            self.pause_update_counter = 0  # 重置暂停计数器
        else:
            # 暂停状态：减少position()调用频率
            self.pause_update_counter += 1
            if self.pause_update_counter >= 10:  # 每1秒更新一次（100ms * 10）
                player1_pos = self.player1.position() if self.player1_file else 0
                player2_pos = self.player2.position() if self.player2_file else 0
                self.pause_update_counter = 0
            else:
                # 跳过这次更新，保持当前显示
                return
        
        # 获取时长信息（这个调用开销较小）
        player1_duration = self.player1.duration() if self.player1_file else 0
        player2_duration = self.player2.duration() if self.player2_file else 0
        
        # 计算平均进度
        if player1_duration > 0 or player2_duration > 0:
            if player1_duration > 0 and player2_duration > 0:
                # 两个播放器都有内容，计算平均进度
                progress1 = (player1_pos / player1_duration) * 100 if player1_duration > 0 else 0
                progress2 = (player2_pos / player2_duration) * 100 if player2_duration > 0 else 0
                avg_progress = (progress1 + progress2) / 2
            elif player1_duration > 0:
                avg_progress = (player1_pos / player1_duration) * 100
            else:
                avg_progress = (player2_pos / player2_duration) * 100
                
            self.progress_bar.setValue(int(avg_progress))
            
            # 更新时间标签
            max_duration = max(player1_duration, player2_duration)
            current_pos = max(player1_pos, player2_pos)
            
            if max_duration > 0:
                current_time = self.format_time(current_pos)
                total_time = self.format_time(max_duration)
                self.time_label.setText(f"{current_time} / {total_time}")
    

    def update_time_display_from_position(self, position):
        """根据进度条位置更新时间显示"""
        # 获取最长的音频文件时长
        player1_duration = self.player1.duration() if self.player1_file else 0
        player2_duration = self.player2.duration() if self.player2_file else 0
        max_duration = max(player1_duration, player2_duration)
        
        if max_duration > 0:
            # 根据进度条位置计算当前时间
            current_pos = int((position / 100.0) * max_duration)
            current_time = self.format_time(current_pos)
            total_time = self.format_time(max_duration)
            self.time_label.setText(f"{current_time} / {total_time}")
                
    def format_time(self, milliseconds):
        seconds = int(milliseconds / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # 加载上次的文件路径
                if 'player1_file' in config and config['player1_file']:
                    if os.path.exists(config['player1_file']):
                        self.player1_file = config['player1_file']
                        self.player1_file_label.setText(os.path.basename(self.player1_file))
                        self.player1_status_label.setText("文件已加载")
                        self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(self.player1_file)))
                        
                if 'player2_file' in config and config['player2_file']:
                    if os.path.exists(config['player2_file']):
                        self.player2_file = config['player2_file']
                        self.player2_file_label.setText(os.path.basename(self.player2_file))
                        self.player2_status_label.setText("文件已加载")
                        self.player2.setMedia(QMediaContent(QUrl.fromLocalFile(self.player2_file)))
                
                # 加载歌词文件
                if 'lyric_file' in config and config['lyric_file']:
                    if os.path.exists(config['lyric_file']):
                        self.lyric_file = config['lyric_file']
                        self.lyric_file_label.setText(os.path.basename(self.lyric_file))
                        self.lyric_status_label.setText("文件已加载")
                        self.load_lyrics(self.lyric_file)
                        
                # 加载音量平衡设置
                if 'volume_balance' in config:
                    self.volume_balance = config['volume_balance']
                    self.volume_balance_slider.setValue(self.volume_balance)
                    self.update_volume_balance(self.volume_balance)
                    
        except Exception as e:
            print(f"加载配置文件出错: {e}")
    

    def save_config(self):
        """保存配置文件"""
        try:
            config = {
                'player1_file': self.player1_file,
                'player2_file': self.player2_file,
                'lyric_file': self.lyric_file,
                'volume_balance': self.volume_balance
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件出错: {e}")
    
    def resizeEvent(self, event):
        """窗口大小改变时更新歌词字体"""
        super().resizeEvent(event)
        # 如果有歌词显示，触发一次更新以调整字体大小
        if hasattr(self, 'lyric_display'):
            # 使用QTimer延迟更新，避免频繁刷新
            QTimer.singleShot(50, self.refresh_lyrics_display)
    
    def init_lyric_display(self):
        """初始化歌词显示"""
        self.refresh_lyrics_display()
    
    def refresh_lyrics_display(self):
        """刷新歌词显示"""
        if self.lyrics:
            self.update_lyrics()
        else:
            # 即使没有歌词，也要更新初始显示的字体大小和居中
            current_size, _ = self.lyric_display.get_dynamic_font_sizes()
            widget_height = self.lyric_display.height()
            font_height = current_size + 8
            
            # 计算垂直居中需要的空行数
            total_lines = max(1, (widget_height - 60) // font_height)
            content_lines = 1  # 提示文本占1行
            empty_lines_top = max(0, (total_lines - content_lines) // 2)
            
            # 使用空行实现垂直居中
            centered_text = "<div style='text-align: center; line-height: 1.4;'>"
            
            # 添加顶部空行
            for _ in range(empty_lines_top):
                centered_text += f"<p style='font-size: {font_height}px; margin: 0; height: {font_height}px;'>&nbsp;</p>"
            
            # 添加提示文本
            centered_text += f"<p style='color: #495057; font-size: {current_size - 4}px; margin: 0; font-weight: normal;'>请选择歌词文件开始伴唱...</p>"
            
            centered_text += "</div>"
            
            self.lyric_display.setHtml(centered_text)
    
    def closeEvent(self, event):
        """程序关闭时保存配置"""
        self.save_config()
        event.accept()
    
    def toggle_play_pause(self):
        """切换播放/暂停状态"""
        if self.is_playing:
            self.pause_all()
        else:
            self.play_all()
    
    def update_play_pause_button(self):
        """更新播放/暂停按钮显示"""
        if self.is_playing:
            self.play_pause_btn.setText("⏸ 暂停")
            self.play_pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    border: none;
                    color: white;
                    padding: 12px 24px;
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                    margin: 4px 2px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
        else:
            self.play_pause_btn.setText("▶ 播放")
            self.play_pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 12px 24px;
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                    margin: 4px 2px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)

def main():
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
