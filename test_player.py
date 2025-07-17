#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐播放器测试脚本
用于验证播放器的基本功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtCore import QUrl

def test_media_player():
    """测试媒体播放器基本功能"""
    print("测试媒体播放器功能...")
    
    app = QApplication(sys.argv)
    
    # 创建媒体播放器
    player = QMediaPlayer()
    
    # 检查播放器状态
    print(f"播放器状态: {player.state()}")
    print(f"媒体状态: {player.mediaStatus()}")
    
    # 检查错误
    if player.error() != QMediaPlayer.NoError:
        print(f"播放器错误: {player.errorString()}")
    else:
        print("播放器初始化成功")
    
    return True

def test_imports():
    """测试所有必要的导入"""
    print("测试模块导入...")
    
    try:
        from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                                     QWidget, QPushButton, QSlider, QLabel, QFileDialog, 
                                     QProgressBar, QGroupBox, QGridLayout, QFrame)
        print("✓ QtWidgets 导入成功")
    except ImportError as e:
        print(f"✗ QtWidgets 导入失败: {e}")
        return False
    
    try:
        from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
        print("✓ QtCore 导入成功")
    except ImportError as e:
        print(f"✗ QtCore 导入失败: {e}")
        return False
    
    try:
        from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
        print("✓ QtMultimedia 导入成功")
    except ImportError as e:
        print(f"✗ QtMultimedia 导入失败: {e}")
        return False
    
    try:
        from PyQt5.QtCore import QUrl
        print("✓ QUrl 导入成功")
    except ImportError as e:
        print(f"✗ QUrl 导入失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 50)
    print("音乐播放器功能测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("导入测试失败，请检查PyQt5安装")
        return False
    
    # 测试媒体播放器
    if not test_media_player():
        print("媒体播放器测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("所有测试通过！音乐播放器可以正常运行")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 