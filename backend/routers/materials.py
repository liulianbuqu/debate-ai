"""素材管理 API 路由 — 规则分析同步，AI 分析异步"""

import json
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models import Material
from schemas import MaterialCreate, MaterialUpdate, MaterialResponse, MessageResponse
from services.style_analyzer import rule_based_analysis
from services.deepseek_client import DeepSeekClient
from services.profile_manager import get_or_create_profile, update_style_from_analysis

router = APIRouter(prefix="/api/materials", tags=["素材管理"])


async def _try_ai_enhancement(material_id: str):
    """后台尝试 AI 增强分析（失败不影響已有结果）"""
    try:
        from database import SessionLocal
        from services.style_analyzer import analyze_material
        db = SessionLocal()
        try:
            mat = db.query(Material).filter(Material.id == material_id).first()
            if not mat or mat.analysis_status == "ai_done":
                return

            client = DeepSeekClient()
            if not client.is_configured():
                return  # 无 API Key，跳过 AI 增强

            analysis = await analyze_material(
                content=mat.content, material_type=mat.type,
                title=mat.title, deepseek_client=client
            )

            mat.extracted_features = json.dumps(analysis, ensure_ascii=False)
            mat.analysis_status = "ai_done"
            profile = get_or_create_profile(db)
            if mat: update_style_from_analysis(db, profile.id, analysis, material_type=mat.type, material_id=mat.id)
            db.commit()
            print(f"[AI增强] {material_id} 完成")
        except Exception as e:
            print(f"[AI增强] {material_id} 跳过: {e}")
        finally:
            db.close()
    except Exception:
        pass  # 彻底静默


@router.get("/", response_model=List[MaterialResponse])
def list_materials(type_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Material).order_by(Material.created_at.desc())
    if type_filter:
        query = query.filter(Material.type == type_filter)
    return [_material_to_response(m) for m in query.all()]


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: str, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")
    return _material_to_response(material)


@router.post("/", response_model=MaterialResponse)
def create_material(data: MaterialCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """创建素材 — 规则分析同步完成，AI 分析后台尝试"""
    # 先跑规则分析（快，不依赖 API）
    rule_result = rule_based_analysis(data.content, data.type)

    material = Material(
        type=data.type,
        title=data.title,
        content=data.content,
        tags=json.dumps(data.tags, ensure_ascii=False),
        context=json.dumps(data.context, ensure_ascii=False),
        extracted_features=json.dumps(rule_result, ensure_ascii=False),
        analysis_status="completed"
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    # 更新画像（规则分析结果）
    profile = get_or_create_profile(db)
    update_style_from_analysis(db, profile.id, rule_result, material_type=data.type, material_id=material.id)

    # 后台尝试 AI 增强
    background_tasks.add_task(_try_ai_enhancement, material.id)

    return _material_to_response(material)


@router.delete("/{material_id}", response_model=MessageResponse)
def delete_material(material_id: str, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")
    db.delete(material)
    db.commit()
    return MessageResponse(message="素材已删除")


@router.post("/{material_id}/reanalyze", response_model=MessageResponse)
def reanalyze_material(material_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """重新分析"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")

    # 重新跑规则分析
    rule_result = rule_based_analysis(material.content, material.type)
    material.extracted_features = json.dumps(rule_result, ensure_ascii=False)
    material.analysis_status = "completed"
    db.commit()

    # 更新画像
    profile = get_or_create_profile(db)
    update_style_from_analysis(db, profile.id, rule_result, material_type=material.type, material_id=material.id)

    # 后台再尝试 AI 增强
    background_tasks.add_task(_try_ai_enhancement, material.id)

    return MessageResponse(message="分析已完成")


def _material_to_response(m: Material) -> MaterialResponse:
    return MaterialResponse(
        id=m.id,
        type=m.type,
        title=m.title,
        content=m.content,
        tags=json.loads(m.tags or "[]"),
        context=json.loads(m.context or "{}"),
        extracted_features=json.loads(m.extracted_features or "{}"),
        analysis_status=m.analysis_status or "completed",
        created_at=m.created_at.isoformat() if m.created_at else ""
    )
