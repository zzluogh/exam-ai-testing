"""在线考试业务逻辑测试（接口级）— P0/P1 用例落地。

对应需求 W01-W07，直接测 ExamSession 的状态机与异常分支。
使用 pytest marker 标注优先级，供 CI 门禁区分（P0 必须全绿）。
"""
import pytest
from exam_testing.business import (
    ExamSession,
    SessionNotOpenError,
    AlreadySubmittedError,
    AnswerOutOfRangeError,
)


@pytest.fixture
def session():
    return ExamSession(session_id="S001", duration_minutes=120)


# ── W01: start 后才能答题 ────────────────────────────────────

@pytest.mark.p0
def test_cannot_answer_before_start(session):
    """未开始考试时答题应报错。"""
    with pytest.raises(SessionNotOpenError):
        session.submit_answer("Q1", "答案A")


@pytest.mark.p0
def test_can_answer_after_start(session):
    """开始考试后可以答题。"""
    session.start()
    session.submit_answer("Q1", "答案A")
    assert session.answers == {"Q1": "答案A"}
    assert session.is_started() is True


# ── W02/W05: 交卷后锁定 ─────────────────────────────────────

@pytest.mark.p0
def test_submit_after_start_ok(session):
    """开始后可交卷，返回提交次数 1。"""
    session.start()
    assert session.submit_exam() == 1
    assert session.is_submitted() is True


@pytest.mark.p0
def test_cannot_answer_after_submit(session):
    """交卷后不能答题。"""
    session.start()
    session.submit_exam()
    with pytest.raises(AlreadySubmittedError):
        session.submit_answer("Q2", "答案B")


@pytest.mark.p1
def test_double_submit_rejected(session):
    """重复交卷应报错。"""
    session.start()
    session.submit_exam()
    with pytest.raises(AlreadySubmittedError):
        session.submit_exam()


@pytest.mark.p1
def test_cannot_start_after_submit(session):
    """已交卷会话不能重新开始。"""
    session.start()
    session.submit_exam()
    with pytest.raises(AlreadySubmittedError):
        session.start()


# ── W04: 未开始交卷 ─────────────────────────────────────────

@pytest.mark.p1
def test_submit_without_start_rejected(session):
    """未开始考试直接交卷应报错。"""
    with pytest.raises(SessionNotOpenError):
        session.submit_exam()


# ── W03: 答案长度边界 ───────────────────────────────────────

@pytest.mark.p0
def test_answer_over_limit_rejected(session):
    """答案超过 2000 字应报错且不保存。"""
    session.start()
    long_answer = "答" * 2001
    with pytest.raises(AnswerOutOfRangeError):
        session.submit_answer("Q1", long_answer)
    assert "Q1" not in session.answers


@pytest.mark.p2
def test_answer_at_limit_ok(session):
    """答案恰好 2000 字应允许。"""
    session.start()
    session.submit_answer("Q1", "答" * 2000)
    assert len(session.answers["Q1"]) == 2000


# ── W06/W07: 计数与空卷 ─────────────────────────────────────

@pytest.mark.p2
def test_answered_count_accumulates(session):
    """多题提交后计数正确。"""
    session.start()
    session.submit_answer("Q1", "A")
    session.submit_answer("Q2", "B")
    session.submit_answer("Q3", "C")
    assert session.answered_count() == 3


@pytest.mark.p2
def test_empty_submit_allowed(session):
    """空答案交卷（立即交卷）应允许。"""
    session.start()
    assert session.submit_exam() == 1
    assert session.answered_count() == 0
