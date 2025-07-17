@echo off
cd /d "%~dp0"
echo 启动音乐播放器...
python main.py
if errorlevel 1 pause 