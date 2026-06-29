"""Pydantic 数据模型 - API请求/响应结构"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ============ 素材相关 ============

class MaterialCreate(BaseModel):
    """创建素材请求"""
    type: str = Field(..., description="素材类型：立论/质询/陈词/结辩/自由辩")
    title: str = Field(..., description="素材标题")
    content: str = Field(..., description="素材全文内容")
    tags: List[str] = Field(default=[], description="标签列表")
    context: Dict = Field(default={}, description="上下文信息（辩题、持方、环节等）")


class MaterialUpdate(BaseModel):
    """更新素材请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    context: Optional[Dict] = None
    extracted_features: Optional[Dict] = None


class MaterialResponse(BaseModel):
    """素材响应"""
    id: str
    type: str
    title: str
    content: str
    tags: List[str]
    context: Dict
    extracted_features: Dict
    analysis_status: str = ""
    created_at: str

    class Config:
        from_attributes = True


# ============ 生成相关 ============

class GenerationRequest(BaseModel):
    """生成稿件请求"""
    type: str = Field(..., description="稿子类型：立论/质询/陈词/结辩/自由辩")
    topic: str = Field(..., description="辩题")
    position: str = Field(..., description="持方：正方/反方")
    reference_ids: List[str] = Field(default=[], description="参考素材ID列表")
    additional_instructions: str = Field(default="", description="额外要求")
    model: str = Field(default="deepseek-chat", description="模型名称")
    api_key: Optional[str] = Field(default=None, description="API Key（前端传入）")


class GenerationResponse(BaseModel):
    """生成稿件响应"""
    id: str
    type: str
    content: str
    request_summary: Dict
    created_at: str


# ============ 反馈相关 ============

class FeedbackCreate(BaseModel):
    """提交反馈请求"""
    generation_id: str = Field(..., description="生成记录ID")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5")
    comments: str = Field(default="", description="评论/修改意见")
    was_used: bool = Field(default=False, description="是否使用了生成的稿件")
    modified_content: str = Field(default="", description="修改后的内容（如有）")


# ============ 画像相关 ============

class ProfileResponse(BaseModel):
    """辩手画像响应"""
    id: str
    name: str
    debate_understanding: Dict
    style_profile: Dict
    frequent_vocabulary: List[str]
    update_count: int
    last_updated: str
    created_at: str

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """更新画像请求"""
    name: Optional[str] = None
    debate_understanding: Optional[Dict] = None
    style_profile: Optional[Dict] = None


# ============ 通用 ============

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True
