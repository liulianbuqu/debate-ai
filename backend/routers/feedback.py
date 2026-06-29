"""反馈处理 API 路由"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import GenerationLog
from schemas import FeedbackCreate, MessageResponse

router = APIRouter(prefix="/api/feedback", tags=["反馈"])


@router.post("/", response_model=MessageResponse)
def submit_feedback(data: FeedbackCreate, db: Session = Depends(get_db)):
    """提交对生成稿件的反馈"""
    log = db.query(GenerationLog).filter(GenerationLog.id == data.generation_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="生成记录不存在")

    feedback = {
        "rating": data.rating,
        "comments": data.comments,
        "was_used": data.was_used,
        "modified_content": data.modified_content
    }
    log.feedback = json.dumps(feedback, ensure_ascii=False)
    db.commit()

    return MessageResponse(message=f"反馈已提交，评分：{data.rating}/5")
