"""客户端/APP/H5 端：AI 生成各端特有测试用例。

读取 data/platform_requirements.py → DeepSeek 生成用例 → 保存 outputs/。
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exam_testing.llm_client import chat
from data.platform_requirements import PLATFORM_REQUIREMENTS

HINTS = {
    "client": "离线、断网重传、升级卸载、本地暂存",
    "app": "弱网、来电打断、前后台切换、权限、推送",
    "h5": "宿主差异、支付回调、JS-SDK、双端兼容",
}


def generate(platform: str, req: dict) -> list:
    prompt = (
        f"平台：{platform}\n"
        f"需求ID：{req['id']}\n"
        f"优先级：{req['priority']}\n"
        f"需求描述：{req['requirement']}\n"
        f"来源：{req['source']}"
    )
    # 用字符串拼接代替 .format()，避免 JSON 示例的花括号与占位符冲突
    sp = (
        "你是一名" + platform + "测试工程师，擅长设计针对" + platform + "特有场景的可执行测试用例。\n\n"
        "对每一条需求，严格按以下 JSON 格式输出 3 条测试用例（不要输出其他内容）：\n"
        '{"cases": [{"id": "TC_' + req["id"] + '_001", "title": "用例标题", '
        '"priority": "高/中/低", "precondition": "前置条件", "steps": ["步骤1", "步骤2"], '
        '"expected": "预期结果（可量化）"}]}\n\n'
        "要求：\n"
        "1. 用例体现" + platform + "终端形态的特有风险（如" + HINTS[platform] + "）\n"
        "2. 至少 1 条正常 + 1 条边界/异常场景\n"
        "3. 只输出 JSON"
    )
    raw = chat(sp, prompt, temperature=0.3, max_tokens=1200)
    text = raw.strip()
    if "```" in text:
        text = text.split("```")[1].lstrip("json").strip()
    try:
        return json.loads(text).get("cases", [])
    except json.JSONDecodeError:
        return [{"error": "JSON解析失败", "raw": raw[:200]}]


def main():
    out_dir = Path(__file__).resolve().parents[1] / "outputs"
    for platform, reqs in PLATFORM_REQUIREMENTS.items():
        results = []
        for i, req in enumerate(reqs):
            print(f"[{platform}] {i+1}/{len(reqs)} {req['id']}...")
            try:
                cases = generate(platform, req)
            except Exception as e:
                cases = [{"error": str(e)}]
            results.append({**req, "cases": cases})
            time.sleep(0.5)

        fname = out_dir / f"{platform}_cases.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        total = sum(len(r["cases"]) for r in results)
        print(f"  → {platform}: {len(reqs)} 需求, {total} 用例 → {fname}")


if __name__ == "__main__":
    main()
