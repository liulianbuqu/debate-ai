# ============================================
# 辩论AI辅助写作系统 — Docker 部署
# 支持 Railway / Render / Zeabur / 自建服务器
# ============================================

FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口（云平台会通过 $PORT 环境变量覆盖）
EXPOSE 8000

# 启动（生产模式，固定端口 8000 以匹配 Railway 域名配置）
CMD ["python", "run.py", "--prod", "--port", "8000"]
