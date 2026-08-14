"""得到大脑 OpenAPI 客户端 — 真实只读调用。

从环境变量读取鉴权，封装 recall 检索接口。
被测对象：真实第三方 RAG 知识库检索服务。
"""
import os
import requests

DDND_API_KEY = os.environ.get("DDND_API_KEY", "")
DDND_CLIENT_ID = os.environ.get("DDND_CLIENT_ID", "")
DDND_TOPIC_ID = os.environ.get("DDND_TOPIC_ID", "YM9DBm2Y")

RECALL_URL = "https://openapi.biji.com/open/api/v1/resource/recall/knowledge"


class DDNDClient:
    """得到大脑 OpenAPI 客户端。"""

    def __init__(self, topic_id: str = "", api_key: str = "", client_id: str = ""):
        self.topic_id = topic_id or DDND_TOPIC_ID
        self.api_key = api_key or DDND_API_KEY
        self.client_id = client_id or DDND_CLIENT_ID
        self._headers = {
            "Authorization": self.api_key,
            "X-Client-ID": self.client_id,
            "Content-Type": "application/json",
        }

    def recall(self, query: str, top_k: int = 5, timeout: int = 15) -> dict:
        """知识库语义检索（只读，不修改任何数据）。

        Args:
            query: 自然语言问题
            top_k: 返回条数（1-10）
            timeout: 请求超时秒数

        Returns:
            dict: 原始响应，含 data.results 列表

        Raises:
            requests.HTTPError: 4xx/5xx
            requests.Timeout: 超时
        """
        body = {"topic_id": self.topic_id, "query": query, "top_k": top_k}
        resp = requests.post(
            RECALL_URL, json=body, headers=self._headers, timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def recall_content(self, query: str, top_k: int = 5, timeout: int = 15) -> list:
        """检索并返回片段文本列表（供质量断言使用）。"""
        data = self.recall(query, top_k, timeout)
        results = data.get("data", {}).get("results", [])
        return [r.get("content", "") for r in results if r.get("content")]

    def recall_titles(self, query: str, top_k: int = 5, timeout: int = 15) -> list:
        """检索并返回片段标题列表。"""
        data = self.recall(query, top_k, timeout)
        results = data.get("data", {}).get("results", [])
        return [r.get("title", "") for r in results if r.get("title")]
