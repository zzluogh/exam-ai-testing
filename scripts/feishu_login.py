"""飞书登录辅助脚本（非无头，需要你手动输验证码）。

用法：
  python3 scripts/feishu_login.py
流程：
  1. 打开浏览器到飞书网页版
  2. 你手动登录（输手机号 + 验证码）
  3. 登录成功后按回车
  4. 等待 5 秒让会话完全加载（SPA 异步初始化）
  5. 保存登录态到 tests/ui/storage_state.json
  6. 自检：用保存的状态重新打开，验证消息列表是否渲染
     若未渲染，提示重新登录

注意：这个脚本只需要跑一次，直到自检通过。
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "tests" / "ui" / "storage_state.json"


def check_login_complete(state_path: Path) -> tuple[bool, str]:
    """用保存的登录态验证会话是否完整（消息列表是否渲染）。

    Returns:
        (是否完整, 详情)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(state_path))
        page = context.new_page()
        try:
            page.goto("https://www.feishu.cn/", timeout=45000,
                      wait_until="domcontentloaded")
            time.sleep(8)  # 等 SPA 渲染
            body = page.locator("body").inner_text()
            has_download = "Download" in body
            has_search = "Search" in body
            # 消息列表是否渲染：sidebar 里有内容而非空
            sidebar = page.locator("[class*=sidebar]").count()
            # 简单判断：如果页面文本只有 Search/Download 而没有其他，
            # 说明消息列表没渲染出来
            text_len = len(body.strip())
            ok = text_len > 50 and has_search and not has_download
            detail = f"文本长度={text_len}, Search={has_search}, Download引导={has_download}, sidebar={sidebar}"
            browser.close()
            return ok, detail
        except Exception as e:
            browser.close()
            return False, f"自检异常: {type(e).__name__}: {str(e)[:120]}"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 有头模式，让你看到页面
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.feishu.cn/", timeout=30000)
        print("=" * 50)
        print("请在浏览器中完成飞书登录（手机验证码）")
        print("登录成功后，请手动确认能正常看到【消息列表】")
        print("确认无误后，回到这里按回车")
        print("=" * 50)
        input("登录完成后按回车继续...")

        # 关键：等会话完全初始化，再保存
        print("等待 5 秒让会话完全加载...")
        time.sleep(5)

        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(STATE_PATH))
        print(f"✅ 登录态已保存: {STATE_PATH}")

    # 自检
    print("\n开始自检保存的登录态是否完整...")
    ok, detail = check_login_complete(STATE_PATH)
    if ok:
        print(f"✅ 自检通过！登录态完整。{detail}")
        print("现在可以运行 UI 测试：FEISHU_UI_TEST=1 pytest tests/ui/ -v")
    else:
        print(f"❌ 自检未通过：{detail}")
        print("说明保存的登录态不完整（消息列表未渲染）。")
        print("请重新运行本脚本，登录后多等一会再按回车。")


if __name__ == "__main__":
    main()
