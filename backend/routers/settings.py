"""设置管理 API 路由 — 极简版"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/settings", tags=["设置"])


class TestKeyRequest(BaseModel):
    api_key: str
    api_url: Optional[str] = None


class TestKeyResponse(BaseModel):
    success: bool
    message: str


@router.post("/test-key", response_model=TestKeyResponse)
async def test_api_key(data: TestKeyRequest):
    """测试 DeepSeek API Key 是否可用"""
    from services.deepseek_client import DeepSeekClient

    client = DeepSeekClient(api_key=data.api_key, api_url=data.api_url or None)
    if not client.is_configured():
        return TestKeyResponse(success=False, message="API Key 为空")

    response = await client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5
    )

    if "error" in response:
        return TestKeyResponse(success=False, message=response["message"])

    return TestKeyResponse(success=True, message="API Key 可用 ✓")
