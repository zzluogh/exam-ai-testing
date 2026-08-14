"""自动阅卷 — pytest 高级特性综合演示。

集中使用：
  - @pytest.mark.parametrize：数据驱动多组用例
  - pytest.approx：浮点分数断言（避免精度误差）
  - pytest.importorskip：可选依赖，缺失时跳过
  - pytest.mark.timeout：防挂死
  - 来自 conftest 的 fixture 链（engine_standard）
"""
import pytest

pytest.importorskip("exam_testing", reason="exam_testing 未安装")

from exam_testing.business import ScoringEngine, InvalidQuestionTypeError


# ── parametrize + approx：客观题判分数据驱动 ─────────────────

@pytest.mark.parametrize(
    "qid, answer, expected",
    [
        ("Q1", "A", 100.0),        # 精确匹配满分
        ("Q1", "B", 0.0),          # 不匹配零分
        ("Q1", "  A  ", 100.0),    # 首尾空白 strip 后匹配
        ("Q2", "C", 100.0),
        ("Q2", "c", 0.0),          # 大小写敏感
        ("Q2", "", 0.0),           # 空答案
    ],
    ids=["exact-match", "wrong", "whitespace", "q2-match",
         "case-sensitive", "empty"],
)
def test_objective_scoring_parametrized(engine_standard, qid, answer, expected):
    """客观题判分：数据驱动覆盖 6 种场景。"""
    assert engine_standard.score_objective(qid, answer) == pytest.approx(expected)


# ── parametrize + approx：主观题多评仲裁 ─────────────────────

@pytest.mark.parametrize(
    "s1, s2, expected_range",
    [
        (80.0, 82.0, (81.0, 81.0)),      # 偏差2内，平均
        (70.0, 90.0, (70.0, 90.0)),      # 偏差20，仲裁介于两者间
        (100.0, 100.0, (100.0, 100.0)),  # 同分
        (0.0, 100.0, (0.0, 100.0)),      # 极端分歧
    ],
    ids=["within-threshold", "arbitration", "identical", "extreme"],
)
def test_subjective_scoring_parametrized(engine_standard, s1, s2, expected_range):
    """主观题仲裁：结果落在预期区间。"""
    score = engine_standard.score_subjective(s1, s2)
    assert expected_range[0] <= score <= expected_range[1]
    # 偏差在阈值内时，必须精确等于平均值（用 approx 防浮点误差）
    if abs(s1 - s2) <= engine_standard.max_discrepancy:
        assert score == pytest.approx((s1 + s2) / 2, abs=1e-9)


# ── parametrize + raises：非法输入 ───────────────────────────

@pytest.mark.parametrize(
    "s1, s2",
    [
        (-1.0, 80.0),   # 负分
        (80.0, 101.0),  # 超上限
        (120.0, 50.0),  # 超上限
        (-5.0, -1.0),   # 双负
    ],
    ids=["negative", "over-100", "s1-over", "both-negative"],
)
def test_subjective_invalid_range_raises(engine_standard, s1, s2):
    """非法分数必须抛异常（parametrize + raises 组合）。"""
    with pytest.raises(InvalidQuestionTypeError):
        engine_standard.score_subjective(s1, s2)


# ── timeout：防挂死 ──────────────────────────────────────────

@pytest.mark.timeout(5)
def test_scoring_completes_within_timeout(engine_standard):
    """加 timeout 保护，防止异常实现导致挂死。"""
    for i in range(100):
        engine_standard.score_objective("Q1", "A")
    assert True


# ── approx 精度演示：0.1+0.2 类浮点陷阱 ─────────────────────

@pytest.mark.parametrize(
    "s1, s2",
    [(0.1, 0.2), (0.3, 0.6), (1.0, 2.0)],
    ids=["0.1+0.2", "0.3+0.6", "1+2"],
)
def test_approx_handles_float_precision(engine_standard, s1, s2):
    """平均分用 approx 断言，规避 (0.1+0.2)/2 != 0.15 的浮点陷阱。"""
    avg = (s1 + s2) / 2
    score = engine_standard.score_subjective(s1, s2)
    assert score == pytest.approx(avg, abs=1e-9)
