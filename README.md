# 🎯 辩论AI辅助写作系统

让 AI 学会你的辩论风格，生成高质量辩论稿件。

## 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动
python run.py

# 3. 打开浏览器访问
#    http://localhost:8000
```

### 配置 API Key

**方式一**：在页面右上角点击「设置」→ 填入 DeepSeek API Key →自动测试→ 保存

**方式二**：创建 `.env` 文件（复制 `.env.example`），填入：
```
DEEPSEEK_API_KEY=你的key
```

---

## 部署到服务器

### 🐳 方式一：Docker 部署（推荐）

```bash
# 1. 将项目上传到服务器
# 2. 配置 API Key
echo "DEEPSEEK_API_KEY=你的key" >> .env

# 3. 一键启动
docker compose up -d

# 4. 访问
curl http://你的服务器IP:8000
```

### ☁️ 方式二：云服务器直接部署

```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY=你的key
nohup python run.py --prod > app.log 2>&1 &
```

配置 Nginx 反向代理 + HTTPS 参考 `deploy/nginx.conf`。

### 🚀 方式三：Railway / Render 云端部署

| 平台 | 设置 |
|------|------|
| Railway | 连 GitHub → 设 `DEEPSEEK_API_KEY` → 启动: `python run.py --prod` |
| Render | 连 GitHub → Build: `pip install -r requirements.txt` → Start: `python run.py --prod` |

详细部署说明见 `deploy/README.md`。

---

## 项目结构

```
debate-ai-system/
├── run.py              # 启动入口
├── start.bat           # Windows 启动
├── Dockerfile          # Docker 构建
├── docker-compose.yml  # Docker 编排
├── .env                # API Key 配置
├── deploy/             # 部署配置
├── backend/            # 后端 API
└── frontend/           # 前端页面
```

## 技术栈

- 前端：HTML + CSS + JavaScript
- 后端：Python FastAPI
- 数据库：SQLite
- AI：DeepSeek API
