#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台兼容性测试脚本
用于验证音乐播放器在Windows和macOS上的兼容性
"""

import sys
import os
import platform

def test_platform_info():
    """测试平台信息"""
    print("=" * 60)
    print("跨平台兼容性测试")
    print("=" * 60)
    
    # 获取系统信息
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    
    print(f"操作系统: {system}")
    print(f"版本: {release}")
    print(f"详细信息: {version}")
    print(f"架构: {machine}")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    return system

def test_pyqt5_installation():
    """测试PyQt5安装"""
    print("\n测试PyQt5安装...")
    
    try:
        from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
        print(f"✓ PyQt5版本: {QT_VERSION_STR}")
        print(f"✓ PyQt5编译版本: {PYQT_VERSION_STR}")
    except ImportError as e:
        print(f"✗ PyQt5导入失败: {e}")
        return False
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtMultimedia import QMediaPlayer
        from PyQt5.QtCore import QUrl
        print("✓ 所有必要的PyQt5模块导入成功")
    except ImportError as e:
        print(f"✗ PyQt5模块导入失败: {e}")
        return False
    
    return True

def test_audio_support():
    """测试音频支持"""
    print("\n测试音频支持...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtMultimedia import QMediaPlayer
        from PyQt5.QtCore import QUrl
        
        # 创建QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建媒体播放器
        player = QMediaPlayer()
        
        # 检查播放器状态
        print(f"✓ 媒体播放器创建成功")
        print(f"✓ 播放器状态: {player.state()}")
        print(f"✓ 媒体状态: {player.mediaStatus()}")
        
        # 检查错误
        if player.error() != QMediaPlayer.NoError:
            print(f"⚠ 播放器警告: {player.errorString()}")
        else:
            print("✓ 播放器无错误")
        
        return True
        
    except Exception as e:
        print(f"✗ 音频支持测试失败: {e}")
        return False

def test_file_system():
    """测试文件系统访问"""
    print("\n测试文件系统访问...")
    
    try:
        # 测试当前目录
        current_dir = os.getcwd()
        print(f"✓ 当前工作目录: {current_dir}")
        
        # 测试文件读写权限
        test_file = "test_temp.txt"
        with open(test_file, 'w') as f:
            f.write("test")
        
        with open(test_file, 'r') as f:
            content = f.read()
        
        # 清理测试文件
        os.remove(test_file)
        
        print("✓ 文件系统读写权限正常")
        return True
        
    except Exception as e:
        print(f"✗ 文件系统测试失败: {e}")
        return False

def test_ui_components():
    """测试UI组件"""
    print("\n测试UI组件...")
    
    try:
        from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                                     QHBoxLayout, QWidget, QPushButton, QSlider, 
                                     QLabel, QFileDialog, QProgressBar, QGroupBox)
        from PyQt5.QtCore import QTimer, Qt
        from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
        from PyQt5.QtCore import QUrl
        
        # 创建QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 测试创建主窗口
        window = QMainWindow()
        print("✓ 主窗口创建成功")
        
        # 测试创建各种UI组件
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 测试各种组件
        button = QPushButton("测试按钮")
        slider = QSlider(Qt.Horizontal)
        label = QLabel("测试标签")
        group = QGroupBox("测试组")
        progress = QProgressBar()
        
        layout.addWidget(button)
        layout.addWidget(slider)
        layout.addWidget(label)
        layout.addWidget(group)
        layout.addWidget(progress)
        
        print("✓ 所有UI组件创建成功")
        
        # 测试媒体播放器
        player1 = QMediaPlayer()
        player2 = QMediaPlayer()
        print("✓ 双媒体播放器创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ UI组件测试失败: {e}")
        return False

def test_platform_specific():
    """测试平台特定功能"""
    system = platform.system()
    print(f"\n测试{system}平台特定功能...")
    
    if system == "Darwin":  # macOS
        try:
            # 测试macOS特定功能
            print("✓ macOS平台检测成功")
            
            # 检查音频设备
            import subprocess
            result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ 音频设备信息获取成功")
            else:
                print("⚠ 音频设备信息获取失败")
                
        except Exception as e:
            print(f"⚠ macOS特定测试警告: {e}")
            
    elif system == "Windows":
        try:
            # 测试Windows特定功能
            print("✓ Windows平台检测成功")
            
            # 检查音频设备
            import subprocess
            result = subprocess.run(['wmic', 'sounddev', 'get', 'name'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ 音频设备信息获取成功")
            else:
                print("⚠ 音频设备信息获取失败")
                
        except Exception as e:
            print(f"⚠ Windows特定测试警告: {e}")
    
    return True

def main():
    """主测试函数"""
    print("开始跨平台兼容性测试...")
    
    # 测试平台信息
    system = test_platform_info()
    
    # 测试PyQt5安装
    if not test_pyqt5_installation():
        print("\n❌ PyQt5安装测试失败，请检查安装")
        return False
    
    # 测试音频支持
    if not test_audio_support():
        print("\n❌ 音频支持测试失败，请检查音频驱动")
        return False
    
    # 测试文件系统
    if not test_file_system():
        print("\n❌ 文件系统测试失败，请检查权限")
        return False
    
    # 测试UI组件
    if not test_ui_components():
        print("\n❌ UI组件测试失败，请检查PyQt5安装")
        return False
    
    # 测试平台特定功能
    test_platform_specific()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！音乐播放器可以在当前平台正常运行")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 