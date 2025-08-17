#!/bin/bash

echo "========================================"
echo "智能企业协作平台 - 启动脚本"
echo "========================================"
echo

echo "[1/4] 检查环境配置..."
if [ ! -f ".env" ]; then
    echo "错误: .env 文件不存在！"
    echo "请先复制 .env.example 为 .env 并配置API密钥"
    echo "详细说明请查看: docs/CONFIGURATION.md"
    exit 1
fi

echo "[2/4] 激活虚拟环境..."
if [ ! -d ".venv" ]; then
    echo "错误: 虚拟环境不存在！"
    echo "请先运行: python -m venv .venv"
    exit 1
fi

source .venv/bin/activate

echo "[3/4] 安装依赖..."
echo "安装AI服务依赖..."
pip install -r ai-service/requirements.txt

echo "安装后端依赖..."
pip install -r backend/requirements.txt

echo "安装前端依赖..."
cd frontend
npm install
cd ..

echo "[4/4] 启动服务..."
echo
echo "正在启动服务，请稍候..."
echo "前端地址: http://localhost:5173"
echo "后端API: http://127.0.0.1:8001"
echo "AI服务: http://127.0.0.1:8002"
echo
echo "按 Ctrl+C 停止所有服务"
echo

# 创建日志目录
mkdir -p logs

# 启动AI服务
echo "启动AI服务..."
uvicorn main:app --host 127.0.0.1 --port 8002 --reload --app-dir ai-service > logs/ai-service.log 2>&1 &
AI_PID=$!

# 等待AI服务启动
sleep 3

# 启动Django后端
echo "启动Django后端..."
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8001 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 5

# 启动前端
echo "启动前端..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "所有服务已启动！"
echo "请在浏览器中访问: http://localhost:5173"
echo
echo "服务进程ID:"
echo "AI服务: $AI_PID"
echo "后端: $BACKEND_PID"
echo "前端: $FRONTEND_PID"
echo
echo "查看日志: tail -f logs/[service].log"
echo "停止服务: kill $AI_PID $BACKEND_PID $FRONTEND_PID"
echo
echo "按 Ctrl+C 停止所有服务..."

# 捕获Ctrl+C信号
trap 'echo "\n正在停止服务..."; kill $AI_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "所有服务已停止"; exit 0' INT

# 等待用户中断
while true; do
    sleep 1
done