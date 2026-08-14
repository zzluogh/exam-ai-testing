"""DeepSeek API — 真实 LLM 服务质量测试。

被测对象：真实 LLM 推理服务。
验证：
  - 鉴权：无效 key 被拒绝
  - 生成：能返回非空回答、响应结构正确
  - 边界：空 prompt、超长 prompt、max_tokens 限制
  - 性能：响应时间
"""
import os
import time

import pytest
import requests

from exam_testing.deepseek_client import DeepSeekClient

pytestmark = pytest.mark.realapi

if not os.environ.get("DEEPSEEK_API_KEY"):
    pytest.skip("需要 DEEPSEEK_API_KEY 环境变量", allow_module_level=True)


@pytest.fixture(scope="module")
def client():
    return DeepSeekClient()


@pytest.mark.skipif(
    not os.environ.get("DEEPSEEK_API_KEY"),
    reason="需要 DEEPSEEK_API_KEY 环境变量",
)
class TestDeepSeekQuality:
    """真实调用组（需要 key）。"""

    def test_chat_returns_nonempty(self, client):
        """正常提问应返回非空回答。"""
        reply = client.chat("用一句话介绍 ROS2")
        assert reply
        assert len(reply) > 0

    def test_response_is_relevant(self, client):
        """回答应与问题相关（黑盒语义断言）。"""
        reply = client.chat("ROS2 是什么？", temperature=0.0)
        # 黑盒断言：回答应包含问题相关的核心关键词
        assert any(kw in reply for kw in ["ROS", "机器人", "系统", "Operating"])

    def test_system_prompt_honored(self, client):
        """system prompt 应影响输出格式。"""
        reply = client.chat(
            "写一句话",
            system_prompt="只输出 JSON，不要解释",
            temperature=0.0,
        )
        assert "{" in reply or "}" in reply

    def test_invalid_key_rejected(self):
        """无效 API key 应被拒绝。"""
        bad = DeepSeekClient(api_key="sk-invalid-key-123")
        with pytest.raises(requests.HTTPError):
            bad.chat("你好")

    def test_returns_within_timeout(self, client):
        """单次调用应在 30 秒内完成（性能保护）。"""
        start = time.time()
        client.chat("说一句你好", max_tokens=32)
        assert time.time() - start < 30


@pytest.mark.skipif(
    not os.environ.get("DEEPSEEK_API_KEY"),
    reason="需要 DEEPSEEK_API_KEY 环境变量",
)
class TestDeepSeekBoundary:
    """边界输入（真实调用，但用极端输入验证服务健壮性）。"""

    def test_empty_prompt(self, client):
        """空 prompt：服务应处理或拒绝，不崩溃。"""
        try:
            reply = client.chat("", max_tokens=32)
            assert isinstance(reply, str)
        except (requests.HTTPError, requests.Timeout):
            pass  # 拒绝也是合理行为

    def test_long_prompt_ok(self, client):
        """长 prompt（约 2000 字）应正常处理。"""
        long_text = "ROS2 机器人操作系统" * 200
        reply = client.chat(long_text, max_tokens=64)
        assert reply

    def test_small_max_tokens(self, client):
        """max_tokens 很小（如 8）时，回答被截断但请求成功。"""
        reply = client.chat("请写一篇 500 字的长文", max_tokens=8)
        # 服务端可能返回截断或错误，但不应该崩溃/挂死
        assert isinstance(reply, str)
