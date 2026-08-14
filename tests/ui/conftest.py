"""飞书 UI 测试 conftest — 提供已登录浏览器 fixture。

复用 scripts/feishu_login.py 保存的 storage_state.json。
无登录态时，测试自动跳过（提示先跑登录脚本）。
"""
import os
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

# conftest 在 tests/ui/ 下，向上两级才是项目根
ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "tests" / "ui" / "storage_state.json"

# 环境变量：不用飞书时跳过整个 UI 测试套件
pytestmark = [
    pytest.mark.ui,
    pytest.mark.skipif(
        not os.environ.get("FEISHU_UI_TEST"),
        reason="需要 FEISHU_UI_TEST=1 环境变量（飞书 UI 测试）",
    ),
]


@pytest.fixture(scope="module")
def page():
    """提供已登录的 Playwright 页面对象（复用登录态）。"""
    if not STATE_PATH.exists():
        pytest.skip("未找到登录态文件，请先运行 scripts/feishu_login.py")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(STATE_PATH))
        pg = context.new_page()
        yield pg
        browser.close()


@pytest.fixture(scope="module")
def feishu_base_url():
    return "https://www.feishu.cn/"
