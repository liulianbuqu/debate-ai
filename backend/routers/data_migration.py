"""数据导出/导入 API — 用于备份和迁移数据（SQLite ↔ PostgreSQL）"""

import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Material, DebaterProfile, GenerationLog

router = APIRouter(prefix="/api/data", tags=["数据迁移"])


class ExportData(BaseModel):
    exported_at: str
    version: str
    materials: list
    profiles: list
    generations: list


@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    """导出所有数据为 JSON"""
    try:
        # 查询所有素材
        materials = db.query(Material).all()
        materials_data = []
        for m in materials:
            materials_data.append({
                "id": m.id,
                "type": m.type,
                "title": m.title,
                "content": m.content,
                "tags": m.tags,
                "context": m.context,
                "extracted_features": m.extracted_features,
                "analysis_status": m.analysis_status,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            })

        # 查询所有画像
        profiles = db.query(DebaterProfile).all()
        profiles_data = []
        for p in profiles:
            profiles_data.append({
                "id": p.id,
                "name": p.name,
                "debate_understanding": p.debate_understanding,
                "style_profile": p.style_profile,
                "frequent_vocabulary": p.frequent_vocabulary,
                "update_count": p.update_count,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "last_updated": p.last_updated.isoformat() if p.last_updated else None,
            })

        # 查询所有生成记录
        generations = db.query(GenerationLog).all()
        gens_data = []
        for g in generations:
            gens_data.append({
                "id": g.id,
                "type": g.type,
                "request": g.request,
                "response": g.response,
                "feedback": g.feedback,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            })

        return ExportData(
            exported_at=datetime.now().isoformat(),
            version="1.0.0",
            materials=materials_data,
            profiles=profiles_data,
            generations=gens_data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


class ImportResponse(BaseModel):
    success: bool
    message: str
    imported: dict


@router.post("/import")
def import_data(data: ExportData, db: Session = Depends(get_db)):
    """导入 JSON 数据到数据库"""
    try:
        counts = {"materials": 0, "profiles": 0, "generations": 0}

        # 导入素材
        for m_data in data.materials:
            existing = db.query(Material).filter(Material.id == m_data["id"]).first()
            if not existing:
                material = Material(
                    id=m_data["id"],
                    type=m_data.get("type", "立论"),
                    title=m_data.get("title", ""),
                    content=m_data.get("content", ""),
                    tags=m_data.get("tags", "[]"),
                    context=m_data.get("context", "{}"),
                    extracted_features=m_data.get("extracted_features", "{}"),
                    analysis_status=m_data.get("analysis_status", "pending"),
                    created_at=datetime.fromisoformat(m_data["created_at"]) if m_data.get("created_at") else None,
                )
                db.add(material)
                counts["materials"] += 1

        # 导入画像
        for p_data in data.profiles:
            existing = db.query(DebaterProfile).filter(
                DebaterProfile.id == p_data["id"]
            ).first()
            if existing:
                existing.name = p_data.get("name", existing.name)
                existing.debate_understanding = p_data.get("debate_understanding", existing.debate_understanding)
                existing.style_profile = p_data.get("style_profile", existing.style_profile)
                existing.frequent_vocabulary = p_data.get("frequent_vocabulary", existing.frequent_vocabulary)
                existing.update_count = p_data.get("update_count", existing.update_count)
            else:
                profile = DebaterProfile(
                    id=p_data["id"],
                    name=p_data.get("name", "我的辩手画像"),
                    debate_understanding=p_data.get("debate_understanding", "{}"),
                    style_profile=p_data.get("style_profile", "{}"),
                    frequent_vocabulary=p_data.get("frequent_vocabulary", "[]"),
                    update_count=p_data.get("update_count", 0),
                    created_at=datetime.fromisoformat(p_data["created_at"]) if p_data.get("created_at") else None,
                    last_updated=datetime.fromisoformat(p_data["last_updated"]) if p_data.get("last_updated") else None,
                )
                db.add(profile)
            counts["profiles"] += 1

        # 导入生成记录
        for g_data in data.generations:
            existing = db.query(GenerationLog).filter(
                GenerationLog.id == g_data["id"]
            ).first()
            if not existing:
                gen = GenerationLog(
                    id=g_data["id"],
                    type=g_data.get("type", "立论"),
                    request=g_data.get("request", "{}"),
                    response=g_data.get("response", "{}"),
                    feedback=g_data.get("feedback", "{}"),
                    created_at=datetime.fromisoformat(g_data["created_at"]) if g_data.get("created_at") else None,
                )
                db.add(gen)
                counts["generations"] += 1

        db.commit()
        return ImportResponse(
            success=True,
            message=f"导入完成: {counts['materials']} 个素材, {counts['profiles']} 条画像, {counts['generations']} 条生成记录",
            imported=counts,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
