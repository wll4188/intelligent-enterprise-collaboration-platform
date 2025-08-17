# 智能企业协作平台 - 配置指南

## 概述

本文档详细说明了智能企业协作平台的环境配置方法，包括API密钥配置、数据库设置、服务端口配置等。

## 环境配置文件

### 主配置文件 `.env`

项目根目录下的 `.env` 文件包含了所有服务的配置信息。请根据以下说明进行配置：

#### 1. 基础配置

```bash
# 开发模式（生产环境请设置为false）
DEBUG=true

# Django密钥（生产环境请使用强密码）
SECRET_KEY=your-super-secret-key-change-in-production

# 允许的主机
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

#### 2. AI服务配置 ⭐ **重要**

```bash
# AI服务地址
AI_SERVICE_URL=http://127.0.0.1:8002

# OpenAI API配置（推荐）
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Google Gemini API配置（推荐）
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash

# Anthropic Claude API配置（可选）
ANTHROPIC_API_KEY=your-anthropic-api-key

# HuggingFace Token（可选）
HUGGINGFACE_TOKEN=your-huggingface-token
```

#### 3. 数据库配置

```bash
# PostgreSQL配置（可选，默认使用SQLite）
DATABASE_URL=postgresql://collab_user:collab_password@localhost:5432/collab_platform
DATABASE_NAME=collab_platform
DATABASE_USER=collab_user
DATABASE_PASSWORD=collab_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

#### 4. Redis配置（可选）

```bash
# Redis缓存配置
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### AI服务配置文件 `ai-service/.env`

AI服务目录下的 `.env` 文件已经配置了默认值，通常不需要修改。

## API密钥获取指南

### 1. OpenAI API密钥 🔑

**获取步骤：**
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账户
3. 进入 "API Keys" 页面
4. 点击 "Create new secret key"
5. 复制生成的密钥（格式：`sk-...`）
6. 将密钥填入 `OPENAI_API_KEY=sk-your-actual-key`

**注意事项：**
- 需要绑定信用卡并充值
- 建议设置使用限额
- 密钥具有完整权限，请妥善保管

### 2. Google Gemini API密钥 🔑

**获取步骤：**
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 使用Google账户登录
3. 点击 "Create API Key"
4. 选择或创建Google Cloud项目
5. 复制生成的密钥（格式：`AIza...`）
6. 将密钥填入 `GEMINI_API_KEY=AIza-your-actual-key`

**注意事项：**
- Gemini API有免费额度
- 某些地区可能需要VPN访问
- 支持多种模型（gemini-1.5-flash, gemini-1.5-pro等）

### 3. Anthropic Claude API密钥 🔑

**获取步骤：**
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账户
3. 进入 "API Keys" 页面
4. 点击 "Create Key"
5. 复制生成的密钥
6. 将密钥填入 `ANTHROPIC_API_KEY=your-actual-key`

## 快速配置步骤

### 方式一：最小配置（推荐新手）

1. **获取Gemini API密钥**（免费且易获取）
2. **编辑 `.env` 文件**：
   ```bash
   GEMINI_API_KEY=AIza-your-actual-gemini-key
   ```
3. **启动服务**（参考下方启动指南）

### 方式二：完整配置

1. **获取多个API密钥**（OpenAI + Gemini）
2. **编辑 `.env` 文件**：
   ```bash
   OPENAI_API_KEY=sk-your-actual-openai-key
   GEMINI_API_KEY=AIza-your-actual-gemini-key
   ```
3. **配置数据库**（可选，默认使用SQLite）
4. **启动服务**

## 服务启动指南

### 1. 环境准备

```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
# 或
source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务

**启动AI服务：**
```bash
cd ai-service
uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

**启动Django后端：**
```bash
cd backend
python manage.py migrate  # 首次运行
python manage.py runserver 127.0.0.1:8001
```

**启动前端：**
```bash
cd frontend
npm install  # 首次运行
npm run dev
```

### 3. 访问应用

- **前端界面**：http://localhost:5173
- **后端API**：http://127.0.0.1:8001
- **AI服务**：http://127.0.0.1:8002

## 故障排除

### 常见问题

#### 1. "离线兜底"回复

**原因**：API密钥无效或网络超时

**解决方案**：
1. 检查API密钥是否正确配置
2. 验证API密钥是否有效
3. 检查网络连接
4. 增加超时时间：在 `.env` 中添加 `STREAM_TIMEOUT_SECONDS=15`

#### 2. AI服务连接失败

**原因**：AI服务未启动或端口冲突

**解决方案**：
1. 确认AI服务正在运行（端口8002）
2. 检查 `AI_SERVICE_URL` 配置
3. 查看AI服务日志

#### 3. 数据库连接错误

**原因**：数据库配置错误或服务未启动

**解决方案**：
1. 使用默认SQLite（删除DATABASE_URL配置）
2. 或正确配置PostgreSQL连接信息

### 日志查看

**AI服务日志**：启动AI服务的终端窗口
**Django日志**：启动Django的终端窗口
**前端日志**：浏览器开发者工具Console

## 安全注意事项

1. **API密钥安全**：
   - 不要将真实API密钥提交到Git仓库
   - 使用 `.env` 文件管理敏感信息
   - 定期轮换API密钥

2. **生产环境配置**：
   - 设置 `DEBUG=false`
   - 使用强密码作为 `SECRET_KEY`
   - 配置适当的 `ALLOWED_HOSTS`
   - 使用HTTPS

3. **权限控制**：
   - 限制API密钥权限
   - 设置使用配额
   - 监控API使用情况

## 支持与帮助

如果遇到配置问题，请：

1. 检查本文档的故障排除部分
2. 查看服务日志获取详细错误信息
3. 确认所有依赖服务正常运行
4. 验证网络连接和API密钥有效性

---

**最后更新**：2025年1月
**版本**：v1.0