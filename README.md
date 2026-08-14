# exam-ai-testing

> 考试系统多端 AI 辅助测试框架 — Web/客户端/APP/H5 分层测试 + CI/CD 门禁 + 实验追踪。
> 以真实考试系统业务为被测对象，完整演示"AI 生成用例 + 人工判断落地"的协作模式。

---

## 这个项目演示什么

不是又一个"AI 写测试"的 demo，而是回答一个真实问题：

> **AI 能生成 54 条用例、AI 能写脚本、AI 能修 bug——那测试工程师到底做什么？**

答案在这个项目里：**AI 负责生成，人负责判断**。每一步都有人的把关点，每一条用例都有来源标注。

## 被测系统（src/exam_testing/business.py）

模拟考试系统核心业务，覆盖三大模块：

| 模块 | 类 | 核心逻辑 |
|------|-----|---------|
| 在线考试 | `ExamSession` | 状态机（started/submitted）、答题、交卷、长度边界 |
| 自动阅卷 | `ScoringEngine` | 客观题精确匹配、主观题多评仲裁 |
| 考生报名 | `Registration` | 状态机（PENDING/VERIFIED/ENROLLED/REJECTED）、审核次数上限 |

## 测试分层（tests/）

```
tests/
└── web/
    ├── test_exam_session.py   在线考试（P0 核心）
    ├── test_scoring_engine.py 自动阅卷（P0 核心）
    └── test_registration.py   考生报名（P1/P2）
```

**优先级分层（P0-P3）**：P0 冒烟必须全绿，P1 核心高通过率，P2 常规，P3 边缘。用 pytest marker 区分，CI 分别执行。

## AI 辅助测试流程

```
① 需求清单（data/web_requirements.py）
   每条带 来源 标注：需求明确 / 测试假设 / 边界值
        ↓
② AI 生成前端用例（outputs/web_cases.json，54 条）
   DeepSeek + Prompt 工程（角色+格式+约束+容错）
        ↓
③ 人工落地为接口级测试（24 条）
   LLM 的前端操作用例是设计文档
   人提炼成可执行、可断言的业务逻辑测试 ← 人的判断
        ↓
④ 跑测试 + 覆盖率门禁
        ↓
⑤ 实验追踪（MLflow）对比每次改动
```

## 门禁体系（关键）

CI（`.github/workflows/ci.yml`）含两道门禁：

| 门禁 | 规则 | 实际值 |
|------|------|--------|
| **覆盖率门禁** | 覆盖率 < 70% 构建失败 | 89%（通过） |
| **P0 冒烟门禁** | P0 用例必须 100% 全绿 | 9/9（通过） |

已验证：人为制造一个 P0 失败，CI 退出码非 0，门禁正确拦截。

## 数据版本与实验追踪

| 工具 | 用途 | 实际产出 |
|------|------|---------|
| **DVC** | AI 生成的用例数据版本管理 | `outputs/web_cases.json` 已跟踪 |
| **MLflow** | 记录每次测试实验 | passed=24, coverage=89%（sqlite） |
| **Allure** | 测试报告可视化 | 48 个结果 JSON |

## 快速开始

```bash
pip install -r requirements.txt

# 跑全量测试 + 覆盖率门禁
PYTHONPATH=src python3 -m pytest tests/ --cov=src/exam_testing --cov-fail-under=70

# 只跑 P0 冒烟
PYTHONPATH=src python3 -m pytest tests/ -m p0

# 生成 Allure 结果
PYTHONPATH=src python3 -m pytest tests/ --alluredir=allure-results

# 记录实验到 MLflow
PYTHONPATH=src python3 scripts/mlflow_log_experiment.py
```

## 核心结论（可面试直接讲）

1. **AI 生成用例能力很强**（54 条前端用例），但那是"操作设计文档"，不是"可执行断言"
2. **人把前端用例落地成接口测试的过程，才是价值**——判断哪些能断言、哪些要人工
3. **门禁阈值是测试负责人的判断**——覆盖 70%、P0 全绿，这些红线是人定的
4. **入参来源标注**——每个值标"需求/假设/边界"，模糊需求可追溯，防止 AI 静默填值掩盖歧义

## 关联项目

- 本文档对应的完整 AI 辅助测试实验记录：`D:\ros2_time_demo\打磨记录_得到大脑RAG评测管线.md`
- LLM 评测工具包：`github.com/zzluogh/llm-eval-kit`
- ROS2 测试框架：`github.com/zzluogh/ros2-test-framework`
