"""辩论AI辅助写作系统 - FastAPI 主入口"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# 确保能找到 backend 包
_root = Path(__file__).resolve().parent.parent
_backend = Path(__file__).resolve().parent
for p in [str(_root), str(_backend)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 加载 .env 文件（从项目根目录）
load_dotenv(_root / ".env")

from database import init_db
from routers import materials, generation, profile, feedback, settings, data_migration

app = FastAPI(
    title="辩论AI辅助写作系统",
    description="用于华语辩论的AI辅助写作工具，支持风格学习和迭代优化",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(materials.router)
app.include_router(generation.router)
app.include_router(profile.router)
app.include_router(feedback.router)
app.include_router(settings.router)
app.include_router(data_migration.router)


@app.on_event("startup")
def startup():
    """应用启动时初始化数据库"""
    init_db()
    print(f"✓ 辩论AI辅助写作系统已启动")
    print(f"  访问地址: http://localhost:8000")
    print(f"  数据目录: {_root / 'debate.db'}")


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "message": "辩论AI辅助写作系统运行中"}


# 挂载前端静态文件
frontend_path = _root / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

