@echo off
echo ========================================
echo 智能企业协作平台 - 启动脚本
echo ========================================
echo.

echo [1/4] 检查环境配置...
if not exist ".env" (
    echo 错误: .env 文件不存在！
    echo 请先复制 .env.example 为 .env 并配置API密钥
    echo 详细说明请查看: docs\CONFIGURATION.md
    pause
    exit /b 1
)

echo [2/4] 激活虚拟环境...
if not exist ".venv" (
    echo 错误: 虚拟环境不存在！
    echo 请先运行: python -m venv .venv
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo [3/4] 安装依赖...
echo 安装AI服务依赖...
pip install -r ai-service\requirements.txt

echo 安装后端依赖...
pip install -r backend\requirements.txt

echo 安装前端依赖...
cd frontend
npm install
cd ..

echo [4/4] 启动服务...
echo.
echo 正在启动服务，请稍候...
echo 前端地址: http://localhost:5173
echo 后端API: http://127.0.0.1:8001
echo AI服务: http://127.0.0.1:8002
echo.
echo 按 Ctrl+C 停止所有服务
echo.

REM 启动AI服务
start "AI服务" cmd /k "call .venv\Scripts\activate.bat && uvicorn main:app --host 127.0.0.1 --port 8002 --reload --app-dir ai-service"

REM 等待AI服务启动
timeout /t 3 /nobreak >nul

REM 启动Django后端
start "Django后端" cmd /k "call .venv\Scripts\activate.bat && cd backend && python manage.py migrate && python manage.py runserver 127.0.0.1:8001"

REM 等待后端启动
timeout /t 5 /nobreak >nul

REM 启动前端
start "前端" cmd /k "cd frontend && npm run dev"

echo 所有服务已启动！
echo 请在浏览器中访问: http://localhost:5173
echo.
echo 按任意键退出启动脚本（服务将继续运行）...
pause >nul