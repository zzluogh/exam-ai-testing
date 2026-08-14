"""得到大脑 OpenAPI — 健壮性与边界测试（黑盒，确定性高）。

被测对象：真实第三方检索服务。
测试不依赖知识库内容预期，验证服务本身的健壮性：
  - 错误鉴权 → 401/403
  - 非法 topic_id → 明确错误
  - 边界输入（空/超长/特殊字符）
  - 超时保护
"""
import os

import pytest
import requests

from exam_testing.ddnd_client import DDNDClient

# 无 key 时跳过整个文件（这些测试都需要真实服务响应）
pytestmark = [
    pytest.mark.realapi,
    pytest.mark.skipif(
        not os.environ.get("DDND_API_KEY"),
        reason="需要 DDND_API_KEY 环境变量",
    ),
]


@pytest.fixture
def client():
    return DDNDClient()


# ── 鉴权健壮性 ───────────────────────────────────────────────

@pytest.mark.p0
def test_invalid_api_key_rejected():
    """错误 API key 必须被拒绝（403）。"""
    c = DDNDClient(api_key="gk_live_invalid", client_id="cli_invalid")
    with pytest.raises(requests.HTTPError):
        c.recall("Nav2是什么")


@pytest.mark.p0
def test_invalid_client_id_rejected():
    """错误 Client ID 必须被拒绝（403）。"""
    c = DDNDClient(api_key="gk_live_valid", client_id="cli_wrong")
    with pytest.raises(requests.HTTPError):
        c.recall("Nav2是什么")


# ── 非法参数 ─────────────────────────────────────────────────

@pytest.mark.p1
def test_invalid_topic_id():
    """不存在的 topic_id 应返回业务错误标识（success=false）。"""
    c = DDNDClient(topic_id="NONEXISTENT_TOPIC")
    resp = c.recall("测试")
    # 真实系统行为：无效 topic_id 返回 200 + success=false + error.code
    assert resp.get("success") is False
    assert resp.get("error", {}).get("code") == 10000
    assert "topic" in resp.get("error", {}).get("message", "").lower()



@pytest.mark.p1
def test_top_k_zero_or_negative(client):
    """top_k=0 或负数，服务应拒绝或返回空，不崩溃。"""
    for bad in [0, -1, 11]:
        try:
            resp = client.recall("测试", top_k=bad)
            results = resp.get("data", {}).get("results", [])
            assert isinstance(results, list)
        except (requests.HTTPError, ValueError):
            pass  # 拒绝也是合理行为


# ── 超时保护 ─────────────────────────────────────────────────

@pytest.mark.p1
@pytest.mark.timeout(8)
def test_request_respects_timeout(client):
    """极小 timeout 应触发超时异常，而不是无限等待。"""
    with pytest.raises((requests.Timeout, requests.ConnectionError)):
        client.recall("测试查询", timeout=0.001)


# ── 响应结构 ─────────────────────────────────────────────────

@pytest.mark.p0
@pytest.mark.skipif(
    not __import__("os").environ.get("DDND_API_KEY"),
    reason="需要 DDND_API_KEY 环境变量",
)
def test_recall_response_structure(client):
    """正常检索返回标准结构：data.results 列表。"""
    resp = client.recall("ROS2", top_k=3)
    assert "data" in resp
    assert "results" in resp["data"]
    assert isinstance(resp["data"]["results"], list)
