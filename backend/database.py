"""数据库连接和会话管理 — 支持 SQLite（本地）和 PostgreSQL（云端）"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库连接：优先使用环境变量 DATABASE_URL（例如 Railway 提供的 PostgreSQL）
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL（云端，如 Railway）
    # 兼容 postgres:// 和 postgresql:// 前缀
    engine = create_engine(DATABASE_URL)
else:
    # SQLite（本地开发）
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debate.db")
    SQLITE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """获取数据库会话（用于FastAPI依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
