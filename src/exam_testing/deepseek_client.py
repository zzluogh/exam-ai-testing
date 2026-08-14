"""DeepSeek API 客户端 — 真实调用封装。

被测对象：真实 LLM 推理服务。
"""
import os
import requests

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
CHAT_URL = "https://api.deepseek.com/chat/completions"


class DeepSeekClient:
    """DeepSeek Chat API 客户端。"""

    def __init__(self, api_key: str = "", model: str = "deepseek-chat"):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.model = model

    def chat(self, user_prompt: str, system_prompt: str = "",
             temperature: float = 0.3, max_tokens: int = 256,
             timeout: int = 30) -> str:
        """调用对话接口，返回文本回复。

        Raises:
            requests.HTTPError: 4xx/5xx（如鉴权失败、限流）
            requests.Timeout: 超时
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = requests.post(CHAT_URL, json=body, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
