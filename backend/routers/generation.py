"""稿件生成 API 路由"""

import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import GenerationLog, Material, DebaterProfile
from schemas import GenerationRequest, GenerationResponse, MessageResponse
from services.deepseek_client import DeepSeekClient
from services.prompt_builder import build_generation_prompt
from services.profile_manager import get_or_create_profile, get_profile_dict

router = APIRouter(prefix="/api/generation", tags=["稿件生成"])


@router.post("/", response_model=GenerationResponse)
async def generate_script(data: GenerationRequest, db: Session = Depends(get_db)):
    """生成辩论稿件"""
    # 获取辩手画像
    profile = get_or_create_profile(db)
    profile_dict = get_profile_dict(profile)

    # 获取参考素材
    reference_materials = []
    for ref_id in data.reference_ids:
        mat = db.query(Material).filter(Material.id == ref_id).first()
        if mat:
            reference_materials.append({
                "title": mat.title,
                "content": mat.content,
                "type": mat.type
            })

    # 如果没有指定参考素材，自动选取同类型的最新素材
    if not reference_materials:
        auto_refs = (
            db.query(Material)
            .filter(Material.type == data.type)
            .order_by(Material.created_at.desc())
            .limit(2)
            .all()
        )
        for mat in auto_refs:
            reference_materials.append({
                "title": mat.title,
                "content": mat.content,
                "type": mat.type
            })

    # 构建 Prompt
    messages = build_generation_prompt(
        script_type=data.type,
        topic=data.topic,
        position=data.position,
        style_profile=profile_dict.get("style_profile"),
        debate_understanding=profile_dict.get("debate_understanding"),
        reference_materials=reference_materials,
        additional_instructions=data.additional_instructions
    )

    # 调用 DeepSeek API（使用前端传入的 API Key）
    client = DeepSeekClient(api_key=data.api_key)
    response = await client.chat(
        messages=messages,
        model=data.model,
        temperature=0.7,
        max_tokens=4096
    )

    if "error" in response:
        raise HTTPException(status_code=500, detail=response["message"])

    content = client.extract_content(response)

    # 保存生成记录
    log = GenerationLog(
        type=data.type,
        request=json.dumps({
            "topic": data.topic,
            "position": data.position,
            "reference_ids": data.reference_ids,
            "additional_instructions": data.additional_instructions,
            "model": data.model
        }, ensure_ascii=False),
        response=json.dumps({
            "content": content,
            "model_used": data.model,
            "prompt_version": "1.0"
        }, ensure_ascii=False),
        feedback=json.dumps({}, ensure_ascii=False)
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return GenerationResponse(
        id=log.id,
        type=data.type,
        content=content,
        request_summary={
            "topic": data.topic,
            "position": data.position,
            "reference_count": len(reference_materials)
        },
        created_at=log.created_at.isoformat() if log.created_at else ""
    )


@router.get("/history", response_model=list)
def get_generation_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取生成历史"""
    logs = (
        db.query(GenerationLog)
        .order_by(GenerationLog.created_at.desc())
        .limit(limit)
        .all()
    )
    results = []
    for log in logs:
        req = json.loads(log.request or "{}")
        resp = json.loads(log.response or "{}")
        fb = json.loads(log.feedback or "{}")
        results.append({
            "id": log.id,
            "type": log.type,
            "topic": req.get("topic", ""),
            "position": req.get("position", ""),
            "content_preview": resp.get("content", "")[:200] + "..." if len(resp.get("content", "")) > 200 else resp.get("content", ""),
            "rating": fb.get("rating"),
            "created_at": log.created_at.isoformat() if log.created_at else ""
        })
    return results
