"""Web 端：AI 生成测试用例 → 保存 JSON 供评审。

流程：读取 web_requirements.py → DeepSeek 生成用例 → 保存 outputs/web_cases.json
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exam_testing.llm_client import chat
from data.web_requirements import WEB_REQUIREMENTS

SYSTEM_PROMPT = """你是一名考试系统 Web 端测试工程师，擅长设计可执行、可验证的测试用例。

对每一条需求，严格按以下 JSON 格式输出 3 条测试用例（不要输出其他内容）：
{
  "cases": [
    {
      "id": "TC_<需求ID>_001",
      "title": "用例标题",
      "priority": "高/中/低",
      "precondition": "前置条件",
      "steps": ["步骤1", "步骤2"],
      "expected": "预期结果"
    }
  ]
}

要求：
1. 用例可执行，步骤具体到能直接操作
2. 至少 1 条正常场景 + 1 条边界/异常场景
3. 预期结果可量化，避免"工作正常"这类模糊描述
4. 针对考试系统 Web 端业务（在线考试/自动阅卷/考生报名/组卷）
5. 只输出 JSON，不要输出任何解释文字"""


def generate(req: dict) -> list:
    user_prompt = (
        f"需求ID：{req['id']}\n"
        f"模块：{req['module']}\n"
        f"优先级：{req['priority']}\n"
        f"需求描述：{req['requirement']}\n"
        f"来源：{req['source']}"
    )
    raw = chat(SYSTEM_PROMPT, user_prompt, temperature=0.3, max_tokens=1200)
    text = raw.strip()
    if "```" in text:
        text = text.split("```")[1].lstrip("json").strip()
    try:
        return json.loads(text).get("cases", [])
    except json.JSONDecodeError:
        return [{"error": "JSON解析失败", "raw": raw[:200]}]


def main():
    results = []
    for i, req in enumerate(WEB_REQUIREMENTS):
        print(f"[{i+1}/{len(WEB_REQUIREMENTS)}] {req['id']} ({req['module']})...")
        try:
            cases = generate(req)
        except Exception as e:
            cases = [{"error": str(e)}]
        results.append({**req, "cases": cases})
        time.sleep(0.5)

    out = Path(__file__).resolve().parents[1] / "outputs" / "web_cases.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    total = sum(len(r["cases"]) for r in results)
    print(f"\n完成：{len(results)} 条需求，{total} 条用例 → {out}")


if __name__ == "__main__":
    main()
