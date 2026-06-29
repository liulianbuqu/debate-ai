"""辩手画像 API 路由"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import ProfileResponse, ProfileUpdate, MessageResponse
from services.profile_manager import get_or_create_profile, update_profile, get_profile_dict

router = APIRouter(prefix="/api/profile", tags=["辩手画像"])


@router.get("/", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    """获取当前辩手画像"""
    profile = get_or_create_profile(db)
    return get_profile_dict(profile)


@router.put("/", response_model=ProfileResponse)
def update_profile_endpoint(data: ProfileUpdate, db: Session = Depends(get_db)):
    """更新辩手画像"""
    profile = get_or_create_profile(db)

    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.debate_understanding is not None:
        update_data["debate_understanding"] = data.debate_understanding
    if data.style_profile is not None:
        update_data["style_profile"] = data.style_profile

    updated = update_profile(db, profile.id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="更新失败")

    return get_profile_dict(updated)


@router.post("/understanding", response_model=ProfileResponse)
def update_understanding(data: dict, db: Session = Depends(get_db)):
    """更新辩论理解（部分更新）"""
    profile = get_or_create_profile(db)

    allowed_keys = ["辩论观", "胜负观", "对辩题的理解方法论",
                     "对质询的理解", "对陈词的理解", "对自由辩的理解"]

    update_data = {"debate_understanding": {}}
    for key in allowed_keys:
        if key in data:
            update_data["debate_understanding"][key] = data[key]

    updated = update_profile(db, profile.id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="更新失败")

    return get_profile_dict(updated)
