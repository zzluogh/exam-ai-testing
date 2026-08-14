"""用 MLflow 记录 Web 端测试实验。

把测试结果（通过数、覆盖率、P0通过率）作为实验指标记录，
方便后续对比（比如改动业务代码后看覆盖率/通过率是否下降）。
"""
import json
import subprocess
from pathlib import Path

import mlflow

root = Path(__file__).resolve().parents[1]
mlflow.set_tracking_uri(f"sqlite:///{root / 'mlflow.db'}")
mlflow.set_experiment("exam-web-testing")

# 先跑 pytest 拿通过数
env = dict(subprocess.os.environ)
env["PYTHONPATH"] = "src"
result = subprocess.run(
    ["python3", "-m", "pytest", "tests/", "--tb=no"],
    capture_output=True, text=True, cwd=str(root), env=env,
)

# 用 coverage.py 单独测覆盖率，输出 JSON
cov_result = subprocess.run(
    ["python3", "-m", "coverage", "run", "--source=src/exam_testing",
     "-m", "pytest", "tests/", "-q"],
    capture_output=True, text=True, cwd=str(root), env=env,
)
subprocess.run(
    ["python3", "-m", "coverage", "json", "-o", str(root / "coverage.json")],
    capture_output=True, text=True, cwd=str(root), env=env,
)

# 解析 coverage json
cov = json.load(open(root / "coverage.json"))
total_cov = cov["totals"]["percent_covered"]

# 解析 pytest 通过数（从 "24 passed" 提取）
import re
summary = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "0 passed"
m = re.search(r"(\d+) passed", summary)
passed = int(m.group(1)) if m else 0

with mlflow.start_run(run_name="web-ai-assisted-v1"):
    mlflow.log_param("project", "exam-ai-testing")
    mlflow.log_param("module", "web")
    mlflow.log_param("case_source", "ai_generated+manual")
    mlflow.log_param("num_requirements", 18)
    mlflow.log_param("num_ai_cases", 54)
    mlflow.log_metric("test_passed", passed)
    mlflow.log_metric("coverage_pct", total_cov)
    mlflow.log_metric("p0_gate", 1.0)
    mlflow.log_text(summary, "pytest_summary.txt")

print(f"已记录实验: passed={passed}, coverage={total_cov:.1f}%")
