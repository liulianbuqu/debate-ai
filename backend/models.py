"""SQLAlchemy 数据模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON
from database import Base


def generate_uuid():
    return str(uuid.uuid4())


class DebaterProfile(Base):
    """辩手画像表 - 存储用户的辩论风格和理解"""
    __tablename__ = "debater_profile"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, default="我的辩手画像")
    debate_understanding = Column(Text, default="{}")  # JSON: 辩论观
    style_profile = Column(Text, default="{}")  # JSON: 风格画像详细数据
    frequent_vocabulary = Column(Text, default="[]")  # JSON: 常用词汇列表
    update_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now)


class Material(Base):
    """素材表 - 存储用户上传的各类稿件"""
    __tablename__ = "materials"

    id = Column(String, primary_key=True, default=generate_uuid)
    type = Column(String, nullable=False)  # 立论稿/质询稿/陈词稿/自由辩战场稿/辩论理解
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(Text, default="[]")  # JSON array
    context = Column(Text, default="{}")  # JSON
    extracted_features = Column(Text, default="{}")  # JSON
    analysis_status = Column(String, default="pending")  # pending / completed / failed
    created_at = Column(DateTime, default=datetime.now)


class GenerationLog(Base):
    """生成日志表 - 记录每次AI生成的内容和反馈"""
    __tablename__ = "generation_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    type = Column(String, nullable=False)
    request = Column(Text, nullable=False)  # JSON
    response = Column(Text, nullable=False)  # JSON
    feedback = Column(Text, default="{}")  # JSON
    created_at = Column(DateTime, default=datetime.now)
