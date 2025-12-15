@echo off
if not exist venv (
    py -3.8 -m venv venv
    if errorlevel 1 (
        echo [错误] Python 或 py 启动器未找到
        pause
        exit /b
    )
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
start http://127.0.0.1:5000
python app.py
