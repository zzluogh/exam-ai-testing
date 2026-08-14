"""飞书 UI 测试 — 登录后功能验证（企业专属域名）。

被测对象：飞书网页版真实工作台（企业专属域名 qdlf7s11w0.feishu.cn）。
关键经验：
  - www.feishu.cn 是官网营销页，不是工作台
  - 登录后的真实工作台在 {tenant}.feishu.cn 下
  - 云文档/多维表格/知识库均可直接访问并断言内容
每个用例自动截图。
"""
import time
from pathlib import Path

import pytest

pytest.importorskip("playwright")

# 企业专属域名（登录后从真实会话获取）
TENANT = "qdlf7s11w0"
BASE = f"https://{TENANT}.feishu.cn"

SHOT_DIR = Path(__file__).resolve().parent / "screenshots"


def _shot(page, name: str):
    SHOT_DIR.mkdir(exist_ok=True)
    page.screenshot(path=str(SHOT_DIR / f"{name}.png"))


@pytest.fixture(scope="module")
def feishu_base():
    return BASE


class TestFeishuWorkbench:
    """登录后工作台功能验证。"""

    def test_docs_home_loads(self, page, feishu_base):
        """云文档主页能加载并显示核心导航。"""
        page.goto(f"{feishu_base}/", timeout=45000, wait_until="domcontentloaded")
        time.sleep(5)
        body = page.locator("body").inner_text()
        assert any(kw in body for kw in ["主页", "云盘", "知识库", "新建"]), \
            f"云文档主页未正常渲染: {body[:150]}"
        _shot(page, "docs_home")

    def test_multidimensional_table_loads(self, page, feishu_base):
        """多维表格能加载。"""
        page.goto(f"{feishu_base}/base/", timeout=45000,
                  wait_until="domcontentloaded")
        time.sleep(5)
        body = page.locator("body").inner_text()
        assert "多维表格" in body, "多维表格未渲染"
        _shot(page, "base")

    def test_wiki_loads(self, page, feishu_base):
        """知识库能加载。"""
        page.goto(f"{feishu_base}/wiki/", timeout=45000,
                  wait_until="domcontentloaded")
        time.sleep(5)
        body = page.locator("body").inner_text()
        assert "知识库" in body, "知识库未渲染"
        _shot(page, "wiki")

    def test_docs_home_has_search(self, page, feishu_base):
        """云文档主页应有搜索框。"""
        page.goto(f"{feishu_base}/", timeout=45000, wait_until="domcontentloaded")
        time.sleep(5)
        body = page.locator("body").inner_text()
        assert "搜索" in body, "未找到搜索入口"
        _shot(page, "docs_search")
