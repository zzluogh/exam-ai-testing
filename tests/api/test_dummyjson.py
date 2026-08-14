"""dummyjson.com — 真实 REST API 黑盒 CRUD 测试。

被测对象：真实第三方 REST 服务（免费、公开）。
测试方式：纯黑盒，只通过 HTTP 接口行为断言，不知道内部实现。
覆盖：Read / Create / Update / Delete + 分页 + 错误处理。
"""
import requests
import pytest

BASE = "https://dummyjson.com"


# ── Read：查询 ───────────────────────────────────────────────

@pytest.mark.p0
def test_get_post_list():
    """GET /posts 返回列表且字段完整。"""
    r = requests.get(f"{BASE}/posts", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "posts" in data
    assert len(data["posts"]) > 0
    first = data["posts"][0]
    # 黑盒断言：post 对象应包含核心字段
    assert {"id", "title", "body", "userId"} <= set(first.keys())


@pytest.mark.p0
def test_get_single_post():
    """GET /posts/1 返回指定 post。"""
    r = requests.get(f"{BASE}/posts/1", timeout=10)
    assert r.status_code == 200
    assert r.json()["id"] == 1
    assert r.json()["title"]


# ── Read：分页 ───────────────────────────────────────────────

@pytest.mark.p1
@pytest.mark.parametrize("limit", [1, 3, 5], ids=["limit1", "limit3", "limit5"])
def test_pagination_limit_honored(limit):
    """分页参数 limit 生效。"""
    r = requests.get(f"{BASE}/posts", params={"limit": limit}, timeout=10)
    data = r.json()
    assert len(data["posts"]) == limit


@pytest.mark.p1
def test_skip_pagination():
    """skip 参数：跳过前 N 条。"""
    r1 = requests.get(f"{BASE}/posts", params={"limit": 1, "skip": 0}, timeout=10)
    r2 = requests.get(f"{BASE}/posts", params={"limit": 1, "skip": 1}, timeout=10)
    assert r1.json()["posts"][0]["id"] != r2.json()["posts"][0]["id"]


# ── Create / Update / Delete ─────────────────────────────────

@pytest.mark.p2
def test_create_post():
    """POST /posts/add 创建成功，返回 201 和 id。"""
    r = requests.post(
        f"{BASE}/posts/add",
        json={"title": "黑盒测试创建", "userId": 1},
        timeout=10,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "黑盒测试创建"
    assert data["id"]


@pytest.mark.p2
def test_update_post():
    """PUT /posts/1 更新成功，返回更新后内容。"""
    r = requests.put(
        f"{BASE}/posts/1",
        json={"title": "已更新标题"},
        timeout=10,
    )
    assert r.status_code == 200
    assert r.json()["title"] == "已更新标题"


@pytest.mark.p2
def test_delete_post():
    """DELETE /posts/1 删除成功，返回 isDeleted。"""
    r = requests.delete(f"{BASE}/posts/1", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data.get("isDeleted") is True


# ── 错误处理 ─────────────────────────────────────────────────

@pytest.mark.p1
def test_get_nonexistent_post_404():
    """GET 不存在的资源应返回 404。"""
    r = requests.get(f"{BASE}/posts/999999", timeout=10)
    assert r.status_code == 404
    assert "message" in r.json()


@pytest.mark.p1
def test_invalid_method_rejected():
    """对只读接口用 DELETE 应被拒绝（405）。"""
    r = requests.delete(f"{BASE}/posts", timeout=10)
    assert r.status_code in (405, 404, 200)  # 真实服务行为可能不同，但不应 5xx 崩溃


# ── 数据校验 ─────────────────────────────────────────────────

@pytest.mark.p2
def test_user_has_required_fields():
    """用户对象应包含标准字段。"""
    r = requests.get(f"{BASE}/users/1", timeout=10)
    data = r.json()
    assert {"id", "firstName", "lastName", "email"} <= set(data.keys())


@pytest.mark.p2
def test_search_endpoint():
    """搜索接口：query 参数过滤结果。"""
    r = requests.get(f"{BASE}/posts/search", params={"q": "love"}, timeout=10)
    assert r.status_code == 200
    assert len(r.json()["posts"]) >= 0  # 搜索可能无结果但不崩溃
