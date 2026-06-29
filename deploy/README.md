# 部署指南

## 方式一：Docker 部署（推荐）

### 前提
- 安装 Docker 和 Docker Compose

### 步骤

```bash
# 1. 克隆/上传项目到服务器
# 2. 进入项目目录
cd debate-ai-system

# 3. 配置 API Key（两种方式选一）

# 方式 A：通过 .env 文件
echo "DEEPSEEK_API_KEY=你的key" >> .env

# 方式 B：通过环境变量
export DEEPSEEK_API_KEY=你的key

# 4. 启动
docker compose up -d

# 5. 查看运行状态
docker compose ps
docker compose logs -f

# 6. 访问
curl http://localhost:8000/api/health
```

### 更新

```bash
git pull                    # 拉取最新代码
docker compose down
docker compose up -d --build  # 重新构建并启动
```

---

## 方式二：直接部署（无 Docker）

### 前提
- Python 3.10+
- pip

### 步骤

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
export DEEPSEEK_API_KEY=你的key

# 3. 启动（生产模式）
python run.py --prod

# 4. 后台运行（使用 nohup）
nohup python run.py --prod > app.log 2>&1 &
```

---

## 方式三：腾讯云/阿里云一键部署

### 使用 Cloud Shell

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 supervisor（进程管理）
apt install supervisor -y

# 3. 创建 supervisor 配置
cat > /etc/supervisor/conf.d/debate-ai.conf << 'EOF'
[program:debate-ai]
command=python /root/debate-ai-system/run.py --prod
directory=/root/debate-ai-system
autostart=true
autorestart=true
user=root
EOF

# 4. 重启 supervisor
supervisorctl reread
supervisorctl update
supervisorctl start debate-ai

# 5. 配置 Nginx 反向代理（参考 deploy/nginx.conf）
```

---

## 方式四：Railway / Render 等 PaaS 平台

### Railway
1. Fork 项目到 GitHub
2. 在 Railway 创建新项目 → Deploy from GitHub repo
3. 设置环境变量 `DEEPSEEK_API_KEY`
4. Start Command: `python run.py --prod --host 0.0.0.0 --port $PORT`

### Render
1. 创建 Web Service → 连接 GitHub
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python run.py --prod --host 0.0.0.0 --port $PORT`
4. 添加环境变量 `DEEPSEEK_API_KEY`

---

## 配置 HTTPS（使用自己的域名）

推荐使用 Caddy 自动处理 HTTPS，比 Nginx 简单：

```bash
# 安装 Caddy
apt install caddy

# 配置 Caddyfile
cat > /etc/caddy/Caddyfile << 'EOF'
your-domain.com {
    reverse_proxy localhost:8000
}
EOF

systemctl restart caddy
```

---

## 安全注意事项

1. **API Key 保护**：不要将 `.env` 文件提交到 Git
2. **端口放行**：云服务器需要在安全组放行 8000 端口
3. **防火墙**：建议只放行 443（HTTPS），通过 Nginx/Caddy 反向代理
4. **数据备份**：定期备份 `debate.db` 数据库文件

## 数据库迁移

如果更新后需要重置数据库：
```bash
# 删除旧数据库（会丢失所有素材和画像数据）
rm debate.db
# 重启后会自动创建新数据库
```
