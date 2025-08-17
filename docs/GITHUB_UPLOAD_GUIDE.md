# GitHub 上传指南

本指南将详细说明如何将智能企业协作平台项目上传到GitHub，包括仓库创建、文件上传、标题设置和内容添加。

## 📋 上传前准备

### 1. 确认文件清理完成

以下文件已被清理，不会上传到GitHub：
- ✅ `.venv/` - Python虚拟环境
- ✅ `backend/.venv/` - 后端虚拟环境
- ✅ `__pycache__/` - Python缓存文件
- ✅ `backend/db.sqlite3` - 本地数据库文件
- ✅ `.trae/` - IDE配置文件

### 2. 敏感信息检查

确认以下文件中的敏感信息已替换为占位符：
- ✅ `.env` - API密钥已替换为占位符
- ✅ `ai-service/.env` - API密钥已替换为占位符
- ✅ `.gitignore` - 已配置忽略敏感文件

## 🚀 GitHub 上传步骤

### 步骤1：创建GitHub仓库

1. **登录GitHub**
   - 访问 [github.com](https://github.com)
   - 使用您的GitHub账号登录

2. **创建新仓库**
   - 点击右上角的 `+` 按钮
   - 选择 `New repository`

3. **仓库基本信息**
   ```
   Repository name: intelligent-enterprise-collaboration-platform
   Description: 🤖 智能企业协作平台 - 基于AI的现代化企业协作解决方案
   
   ✅ Public (推荐) 或 Private
   ❌ 不要勾选 "Add a README file"
   ❌ 不要添加 .gitignore
   ❌ 不要选择 license
   ```

4. **点击 "Create repository"**

### 步骤2：本地Git初始化

在项目根目录执行以下命令：

```bash
# 初始化Git仓库
git init

# 添加远程仓库（替换为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/intelligent-enterprise-collaboration-platform.git

# 添加所有文件
git add .

# 提交文件
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

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 步骤3：完善仓库信息

#### 3.1 设置仓库描述和标签

在GitHub仓库页面：

1. **编辑仓库描述**
   - 点击仓库名称下方的 ⚙️ 设置图标
   - 在Description中填入：
     ```
     🤖 智能企业协作平台 - 基于AI的现代化企业协作解决方案，支持多种LLM提供商，具备完整的用户管理和实时对话功能
     ```

2. **添加网站链接**（可选）
   ```
   Website: http://localhost:5173
   ```

3. **添加标签（Topics）**
   ```
   ai, chatbot, vue3, django, fastapi, typescript, openai, gemini, claude, 
   enterprise, collaboration, real-time, docker, rest-api, websocket
   ```

#### 3.2 创建Release（可选）

1. **点击 "Releases"**
2. **点击 "Create a new release"**
3. **填写Release信息**：
   ```
   Tag version: v1.0.0
   Release title: 🎉 智能企业协作平台 v1.0.0
   
   Description:
   ## 🚀 首个正式版本发布
   
   ### ✨ 核心功能
   - 🤖 **AI智能对话**：支持OpenAI GPT、Google Gemini、Anthropic Claude
   - 👥 **用户系统**：完整的注册、登录、会话管理
   - 💬 **实时对话**：流式响应，支持停止功能
   - 🛡️ **容错机制**：AI服务异常时的离线兜底
   - 🎨 **现代UI**：响应式设计，优秀的用户体验
   
   ### 🏗️ 技术架构
   - **前端**：Vue 3 + TypeScript + Vite
   - **后端**：Django + DRF
   - **AI服务**：FastAPI + 多LLM支持
   - **部署**：Docker + Nginx
   
   ### 📦 快速开始
   1. 克隆项目：`git clone https://github.com/YOUR_USERNAME/intelligent-enterprise-collaboration-platform.git`
   2. 配置API密钥：参考 `docs/CONFIGURATION.md`
   3. 启动服务：运行 `start.bat` 或 `./start.sh`
   4. 访问：http://localhost:5173
   
   ### 📚 文档
   - [配置指南](docs/CONFIGURATION.md)
   - [部署检查清单](docs/DEPLOYMENT_CHECKLIST.md)
   
   ### 🤝 贡献
   欢迎提交Issue和Pull Request！
   ```

### 步骤4：优化仓库展示

#### 4.1 添加仓库徽章（可选）

在README.md顶部添加徽章：

```markdown
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.0+-green.svg)
![Django](https://img.shields.io/badge/django-4.0+-green.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green.svg)
```

#### 4.2 设置仓库社交预览

1. 进入仓库设置页面
2. 滚动到 "Social preview" 部分
3. 上传一张项目截图作为社交媒体预览图

## 📝 提交信息规范

### 提交类型

- `🎉 feat`: 新功能
- `🐛 fix`: 修复bug
- `📚 docs`: 文档更新
- `💄 style`: 代码格式化
- `♻️ refactor`: 代码重构
- `⚡ perf`: 性能优化
- `✅ test`: 测试相关
- `🔧 chore`: 构建工具或辅助工具的变动

### 提交信息示例

```bash
# 功能开发
git commit -m "✨ feat: 添加用户头像上传功能"

# Bug修复
git commit -m "🐛 fix: 修复AI服务连接超时问题"

# 文档更新
git commit -m "📚 docs: 更新API文档和配置说明"

# 性能优化
git commit -m "⚡ perf: 优化前端组件渲染性能"
```

## 🔄 后续维护

### 定期更新

1. **功能开发**
   ```bash
   git add .
   git commit -m "✨ feat: 新功能描述"
   git push origin main
   ```

2. **Bug修复**
   ```bash
   git add .
   git commit -m "🐛 fix: 修复问题描述"
   git push origin main
   ```

3. **文档更新**
   ```bash
   git add docs/
   git commit -m "📚 docs: 更新文档内容"
   git push origin main
   ```

### 版本发布

当有重大更新时，创建新的Release：

1. 更新版本号
2. 创建新的Git标签
3. 在GitHub上创建Release
4. 编写详细的更新日志

## 🛡️ 安全注意事项

### 永远不要提交的文件

- ❌ `.env` 文件（包含真实API密钥）
- ❌ 数据库文件（`*.sqlite3`, `*.db`）
- ❌ 虚拟环境（`.venv/`, `venv/`）
- ❌ 缓存文件（`__pycache__/`, `node_modules/`）
- ❌ IDE配置文件（`.vscode/`, `.idea/`）
- ❌ 日志文件（`*.log`）
- ❌ 临时文件（`*.tmp`, `*.temp`）

### 如果意外提交了敏感信息

1. **立即行动**：
   ```bash
   # 从Git历史中移除敏感文件
   git rm --cached .env
   git commit -m "🔒 security: 移除敏感配置文件"
   git push --force
   ```

2. **更换密钥**：
   - 立即更换所有暴露的API密钥
   - 检查相关服务的访问日志
   - 监控异常使用情况

3. **清理历史**（如果必要）：
   ```bash
   # 使用git filter-branch清理历史
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all
   ```

## 📞 获取帮助

如果在上传过程中遇到问题：

1. **检查网络连接**
2. **确认Git配置**：
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```
3. **查看详细错误信息**
4. **参考GitHub官方文档**：[docs.github.com](https://docs.github.com)

## 🎯 推荐的仓库结构

上传完成后，您的GitHub仓库应该具有以下结构：

```
intelligent-enterprise-collaboration-platform/
├── 📁 ai-service/          # AI服务模块
├── 📁 backend/             # Django后端
├── 📁 frontend/            # Vue.js前端
├── 📁 docs/                # 项目文档
├── 📁 infrastructure/      # 基础设施配置
├── 📄 README.md           # 项目说明
├── 📄 LICENSE             # 开源许可证
├── 📄 .gitignore          # Git忽略规则
├── 📄 docker-compose.yml  # Docker编排
├── 📄 start.bat           # Windows启动脚本
└── 📄 start.sh            # Linux/Mac启动脚本
```

---

**🎉 恭喜！您的智能企业协作平台已成功上传到GitHub！**

现在您可以：
- 📢 分享您的项目链接
- 🤝 邀请其他开发者协作
- 📈 跟踪项目的使用情况
- 🔄 持续改进和更新功能