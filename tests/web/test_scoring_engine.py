"""自动阅卷业务逻辑测试（接口级）— 客观题/主观题多评仲裁。

对应需求 W08-W12。
"""
import pytest
from exam_testing.business import ScoringEngine, InvalidQuestionTypeError


@pytest.fixture
def engine():
    return ScoringEngine(
        objective_answer={"Q1": "A", "Q2": "C"},
        max_discrepancy=2.0,
    )


# ── W08: 客观题精确匹配 ─────────────────────────────────────

@pytest.mark.p0
def test_objective_correct_full_score(engine):
    """客观题答案匹配得满分。"""
    assert engine.score_objective("Q1", "A") == 100.0


@pytest.mark.p0
def test_objective_wrong_zero(engine):
    """客观题答案不匹配得 0 分。"""
    assert engine.score_objective("Q1", "B") == 0.0


@pytest.mark.p2
def test_objective_answer_with_whitespace(engine):
    """答案首尾空白应不影响判分（strip 后匹配）。"""
    assert engine.score_objective("Q2", "  C  ") == 100.0


# ── W09: 主观题偏差内取平均 ─────────────────────────────────

@pytest.mark.p0
def test_subjective_within_threshold_average(engine):
    """偏差在阈值内取平均。"""
    assert engine.score_subjective(80, 82) == 81.0


# ── W10: 主观题偏差过大触发三评 ─────────────────────────────

@pytest.mark.p0
def test_subjective_over_threshold_arbitration(engine):
    """偏差超过阈值触发三评，结果介于两者之间。"""
    score = engine.score_subjective(70, 90)
    assert 70 <= score <= 90
    # 仲裁结果应低于简单平均(80)，更偏向低分侧（min + 中值）/2
    assert score < 80.0


# ── W11: 未知题目 ───────────────────────────────────────────

@pytest.mark.p1
def test_unknown_question_raises(engine):
    """对不存在的题目判分应报错。"""
    with pytest.raises(InvalidQuestionTypeError):
        engine.score_objective("Q999", "A")


# ── W12: 分数越界 ───────────────────────────────────────────

@pytest.mark.p1
def test_subjective_score_out_of_range(engine):
    """主观题评分超出 0-100 应报错。"""
    with pytest.raises(InvalidQuestionTypeError):
        engine.score_subjective(-1, 80)
    with pytest.raises(InvalidQuestionTypeError):
        engine.score_subjective(80, 101)


@pytest.mark.p2
def test_subjective_boundary_101_rejected(engine):
    """边界值 100 分应允许，101 应拒绝。"""
    assert engine.score_subjective(100, 100) == 100.0
    with pytest.raises(InvalidQuestionTypeError):
        engine.score_subjective(100, 101)
