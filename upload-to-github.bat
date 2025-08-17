@echo off
echo ========================================
echo GitHub 上传脚本
echo ========================================
echo.

echo 请确保您已经：
echo 1. 在GitHub上创建了新仓库
echo 2. 复制了仓库的HTTPS链接
echo.

set /p REPO_URL="请输入您的GitHub仓库链接 (例如: https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo 错误: 仓库链接不能为空！
    pause
    exit /b 1
)

echo.
echo [1/5] 初始化Git仓库...
git init

echo [2/5] 添加远程仓库...
git remote add origin %REPO_URL%

echo [3/5] 添加所有文件...
git add .

echo [4/5] 提交文件...
git commit -m "🎉 Initial commit: 智能企业协作平台

✨ Features:
- 🤖 AI智能对话助手
- 👥 用户认证与会话管理
- 💬 实时流式对话
- 🛡️ 离线兜底机制
- 🎨 现代化响应式UI
- 🔧 Docker容器化部署

🏗️ Tech Stack:
- Frontend: Vue 3 + TypeScript + Vite
- Backend: Django + Django REST Framework
- AI Service: FastAPI + OpenAI/Gemini/Claude
- Database: SQLite (可扩展至PostgreSQL)
- Deployment: Docker + Nginx"

echo [5/5] 推送到GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo 🎉 上传完成！
echo ========================================
echo.
echo 您的项目已成功上传到GitHub！
echo 仓库地址: %REPO_URL%
echo.
echo 接下来您可以：
echo 1. 访问GitHub仓库页面完善项目信息
echo 2. 添加项目描述和标签
echo 3. 创建Release发布版本
echo 4. 邀请其他开发者协作
echo.
echo 详细指南请查看: docs\GITHUB_UPLOAD_GUIDE.md
echo.
pause