# 智能企业协作平台

一个基于AI的现代化企业协作平台，集成了智能对话、文档管理、任务协作等功能。

##  功能特性

- 🤖 **智能对话**：支持OpenAI GPT、Google Gemini、Anthropic Claude等多种AI模型
- 💬 **实时聊天**：流式对话体验，支持上下文记忆
- 📱 **现代化UI**：基于Vue 3 + Element Plus的响应式界面
- 🔒 **用户认证**：完整的注册/登录/权限管理系统
- 🚀 **高性能**：Django + FastAPI双后端架构

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Docker & docker-compose
- Redis 7+
- PostgreSQL 15+

### 一键启动
```bash
# 克隆项目
git clone <repository-url>
cd intelligent-collaboration-platform

# 复制环境配置
cp .env.example .env

# 启动所有服务
make dev

# 或使用docker-compose
docker-compose up -d
```

### 开发模式
```bash
# 后端开发
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 前端开发
cd frontend
npm install
npm run dev

# AI服务
cd ai-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## 项目结构

```
intelligent-collaboration-platform/
├── backend/                 # Django后端服务
│   ├── apps/               # 业务应用模块
│   ├── config/             # 项目配置
│   ├── core/               # 核心组件
│   └── requirements.txt    # Python依赖
├── ai-service/             # FastAPI AI服务
│   ├── app/               # AI应用代码
│   ├── models/            # AI模型文件
│   └── requirements.txt   # AI服务依赖
├── frontend/              # Vue3前端
│   ├── src/              # 前端源码
│   ├── public/           # 静态资源
│   └── package.json      # 前端依赖
├── infrastructure/        # 基础设施配置
│   ├── docker/           # Docker配置
│   ├── k8s/             # Kubernetes配置
│   └── monitoring/      # 监控配置
├── docs/                 # 项目文档
├── scripts/              # 工具脚本
├── docker-compose.yml    # 本地开发环境
├── docker-compose.prod.yml # 生产环境
└── Makefile             # 常用命令
```

## 配置说明

### 环境变量
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/collab_platform
REDIS_URL=redis://localhost:6379/0

# AI服务配置
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_TOKEN=your-hf-token

# 文件存储
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# 其他配置
SECRET_KEY=your-secret-key
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
```

## API文档

- **后端API**: http://localhost:8000/api/docs/
- **AI服务API**: http://localhost:8001/docs/
- **前端访问**: http://localhost:3000/

## 测试

```bash
# 后端测试
cd backend
python -m pytest

# 前端测试
cd frontend
npm run test

# E2E测试
npm run test:e2e
```

## 监控面板

- **Grafana仪表板**: http://localhost:3001/
- **Prometheus监控**: http://localhost:9090/
- **Jaeger链路追踪**: http://localhost:16686/



如果这个项目对你有帮助，请给我一个 Star！
