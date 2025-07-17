@echo off
echo 正在启动音乐播放器...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python解释器！
    echo 请确保已安装Python并添加到系统PATH环境变量中。
    echo.
    pause
    exit /b 1
)

REM 检查main.py是否存在
if not exist "main.py" (
    echo 错误：未找到main.py文件！
    echo 请确保脚本与main.py在同一目录下。
    echo.
    pause
    exit /b 1
)

REM 检查是否安装了依赖
echo 检查依赖包...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo 警告：未检测到PyQt5，正在尝试安装依赖包...
    if exist "requirements.txt" (
        pip install -r requirements.txt
        if errorlevel 1 (
            echo 依赖安装失败，请手动执行: pip install -r requirements.txt
            pause
            exit /b 1
        )
    ) else (
        echo 请手动安装PyQt5: pip install PyQt5
        pause
        exit /b 1
    )
)

echo 启动程序...
echo.

REM 启动主程序
python main.py

REM 如果程序异常退出，显示错误信息
if errorlevel 1 (
    echo.
    echo 程序异常退出，错误代码：%errorlevel%
    echo 请检查控制台输出的错误信息。
    echo.
    pause
) 