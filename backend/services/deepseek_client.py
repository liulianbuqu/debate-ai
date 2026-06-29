"""DeepSeek API 客户端封装"""

import os
import json
import httpx
from typing import Optional, Dict, Any

# 默认 API 配置
DEFAULT_API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY_ENV = "DEEPSEEK_API_KEY"


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        # 优先级：传入参数 > 环境变量
        self.api_key = api_key or os.getenv(API_KEY_ENV, "")
        self.api_url = api_url or os.getenv("DEEPSEEK_API_URL", DEFAULT_API_URL)

    def is_configured(self) -> bool:
        """检查 API 密钥是否已配置"""
        return bool(self.api_key)

    async def chat(
        self,
        messages: list,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """调用 DeepSeek 聊天补全 API

        Args:
            messages: 消息列表 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度参数 (0-2)
            max_tokens: 最大输出 token 数

        Returns:
            API 响应字典
        """
        if not self.is_configured():
            return {
                "error": "API_KEY_NOT_CONFIGURED",
                "message": "DeepSeek API 密钥未配置，请在页面右上角的设置中填写 API Key。"
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {
                    "error": "API_ERROR",
                    "message": f"API 返回错误: {e.response.status_code}",
                    "detail": str(e)
                }
            except httpx.TimeoutException:
                return {
                    "error": "TIMEOUT",
                    "message": "API 请求超时，请稍后重试"
                }
            except Exception as e:
                return {
                    "error": "UNKNOWN",
                    "message": f"请求失败: {str(e)}"
                }

    def extract_content(self, response: Dict) -> str:
        """从 API 响应中提取生成的文本内容"""
        if "error" in response:
            return f"[错误] {response['message']}"

        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return "[错误] 无法解析 API 返回结果"
