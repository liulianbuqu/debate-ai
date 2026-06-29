"""辩手画像管理器 - 管理风格画像的增删改查和自动更新"""

import json
from typing import Dict, Optional
from sqlalchemy.orm import Session
from models import DebaterProfile


def get_or_create_profile(db: Session) -> DebaterProfile:
    """获取当前辩手画像，如果不存在则创建一个默认的"""
    profile = db.query(DebaterProfile).first()
    if not profile:
        profile = DebaterProfile(
            name="我的辩手画像",
            debate_understanding=json.dumps({
                "辩论观": "",
                "胜负观": "",
                "对辩题的理解方法论": "",
                "对质询的理解": "",
                "对陈词的理解": ""
            }, ensure_ascii=False),
            style_profile=json.dumps({
                "语言风格": {"当前偏好": "", "强度": 0, "偏好历史": []},
                "论证方式": {"当前偏好": "", "强度": 0, "偏好历史": []},
                "结构偏好": {"当前偏好": "", "强度": 0, "偏好历史": []},
                "修辞特色": {"常用手法": []},
                "关键论点": [],
                "金句摘录": [],
                "论证模式": ""
            }, ensure_ascii=False),
            frequent_vocabulary=json.dumps([], ensure_ascii=False),
            update_count=0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_profile_dict(profile: DebaterProfile) -> Dict:
    """将画像对象转换为字典"""
    return {
        "id": profile.id,
        "name": profile.name,
        "debate_understanding": json.loads(profile.debate_understanding or "{}"),
        "style_profile": json.loads(profile.style_profile or "{}"),
        "frequent_vocabulary": json.loads(profile.frequent_vocabulary or "[]"),
        "update_count": profile.update_count,
        "last_updated": profile.last_updated.isoformat() if profile.last_updated else "",
        "created_at": profile.created_at.isoformat() if profile.created_at else ""
    }


def update_profile(db: Session, profile_id: str,
                   update_data: Dict) -> Optional[DebaterProfile]:
    """更新画像信息"""
    profile = db.query(DebaterProfile).filter(DebaterProfile.id == profile_id).first()
    if not profile:
        return None

    if "name" in update_data and update_data["name"]:
        profile.name = update_data["name"]

    if "debate_understanding" in update_data:
        current = json.loads(profile.debate_understanding or "{}")
        current.update(update_data["debate_understanding"])
        profile.debate_understanding = json.dumps(current, ensure_ascii=False)

    if "style_profile" in update_data:
        current = json.loads(profile.style_profile or "{}")
        current.update(update_data["style_profile"])
        profile.style_profile = json.dumps(current, ensure_ascii=False)

    profile.update_count = (profile.update_count or 0) + 1
    from datetime import datetime
    profile.last_updated = datetime.now()

    db.commit()
    db.refresh(profile)
    return profile


def update_style_from_analysis(db: Session, profile_id: str,
                                analysis_result: Dict,
                                material_type: str = None,
                                material_id: str = None) -> Optional[DebaterProfile]:
    """根据新的分析结果更新风格画像（含去重 + 按类型聚合）"""
    profile = db.query(DebaterProfile).filter(DebaterProfile.id == profile_id).first()
    if not profile:
        return None

    from services.style_analyzer import merge_analysis_into_profile

    current_style = json.loads(profile.style_profile or "{}")

    # 去重
    analyzed_ids = set(current_style.get("analyzed_material_ids", []))
    if material_id and material_id in analyzed_ids:
        return profile
    if material_id:
        analyzed_ids.add(material_id)

    merged_style = merge_analysis_into_profile(current_style, analysis_result, material_type)
    merged_style["analyzed_material_ids"] = list(analyzed_ids)

    profile.style_profile = json.dumps(merged_style, ensure_ascii=False)
    profile.update_count = (profile.update_count or 0) + 1

    from datetime import datetime
    profile.last_updated = datetime.now()

    db.commit()
    db.refresh(profile)
    return profile
