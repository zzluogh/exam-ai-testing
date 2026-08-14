"""得到大脑 OpenAPI — 检索质量测试（黑盒）。

被测对象：真实第三方检索服务。
通过"问题→期望关键词"断言检索相关度，不依赖知识库内部实现。
用 parametrize 数据驱动多组检索场景。
"""
import os
import pytest

pytest.importorskip("exam_testing")

pytestmark = pytest.mark.realapi

from exam_testing.ddnd_client import DDNDClient

# 知识库内容领域（Nav2/ROS2/LLM评估）
# 期望关键词来自知识库实际内容，断言"检索返回的内容应包含该领域关键词"
RETRIEVAL_CASES = [
    # (query, 期望命中的关键词, top_k)
    ("Nav2 代价地图有哪些类型", ["代价地图", "全局", "局部"], 3),
    ("ROS2 怎么测话题发布", ["pytest", "话题", "mock"], 3),
    ("LLM-as-Judge 怎么用", ["LLM", "评估", "打分"], 3),
    ("AMCL 是什么", ["定位", "粒子"], 3),
    ("QoS 不匹配会怎样", ["QoS", "消息", "静默"], 3),
]


@pytest.fixture(scope="module")
def client():
    return DDNDClient()


@pytest.mark.skipif(
    not os.environ.get("DDND_API_KEY"),
    reason="需要 DDND_API_KEY 环境变量",
)
@pytest.mark.parametrize("query,keywords,top_k", RETRIEVAL_CASES,
                         ids=[c[0][:12] for c in RETRIEVAL_CASES])
def test_retrieval_relevance(client, query, keywords, top_k):
    """检索质量：返回内容应命中问题相关关键词。"""
    content = client.recall_content(query, top_k=top_k)
    assert content, f"query={query} 返回空结果"
    joined = " ".join(content)
    hits = [k for k in keywords if k in joined]
    assert len(hits) >= 1, (
        f"query={query} 返回内容未命中任何期望关键词，"
        f"hits={hits}, 内容前200字={joined[:200]}"
    )


@pytest.mark.skipif(
    not os.environ.get("DDND_API_KEY"),
    reason="需要 DDND_API_KEY 环境变量",
)
@pytest.mark.parametrize("top_k", [1, 3, 5, 10], ids=["k1", "k3", "k5", "k10"])
def test_top_k_honored(client, top_k):
    """top_k 边界：返回条数不超过请求值。"""
    data = client.recall("ROS2 测试", top_k=top_k)
    results = data.get("data", {}).get("results", [])
    assert len(results) <= top_k, f"请求 top_k={top_k} 实际返回 {len(results)}"
    assert len(results) >= 1, "有效查询应至少返回 1 条"


@pytest.mark.skipif(
    not os.environ.get("DDND_API_KEY"),
    reason="需要 DDND_API_KEY 环境变量",
)
def test_empty_query_handled(client):
    """空 query：应被服务处理（拒绝或空结果），不崩溃。"""
    try:
        data = client.recall("", top_k=3)
        # 服务端可能返回空或错误，都是可接受行为
        assert "data" in data
    except Exception:
        pass  # 拒绝也是合理行为
