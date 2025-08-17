# 部署前检查清单

在将项目上传到GitHub或部署到生产环境之前，请确保完成以下检查项目。

## 🔒 安全检查

### API密钥和敏感信息
- [ ] 确认 `.env` 文件中的API密钥已替换为占位符
- [ ] 确认 `ai-service/.env` 文件中的API密钥已替换为占位符
- [ ] 检查代码中是否有硬编码的API密钥或密码
- [ ] 确认 `.gitignore` 文件包含 `.env` 和其他敏感文件

### 数据库和配置
- [ ] 确认数据库密码使用占位符
- [ ] 确认 `SECRET_KEY` 使用占位符
- [ ] 检查是否有测试数据或个人信息

## 📁 文件检查

### 必需文件
- [ ] `README.md` - 项目说明和快速开始指南
- [ ] `docs/CONFIGURATION.md` - 详细配置指南
- [ ] `LICENSE` - 开源许可证
- [ ] `.gitignore` - Git忽略规则
- [ ] `start.bat` / `start.sh` - 启动脚本

### 配置文件
- [ ] `.env.example` - 环境配置模板（如果存在）
- [ ] `requirements.txt` - Python依赖列表
- [ ] `package.json` - Node.js依赖列表

