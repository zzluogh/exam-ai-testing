"""考生报名业务逻辑测试（接口级）— 状态机流转。

对应需求 W13-W16。
"""
import pytest
from exam_testing.business import (
    Registration,
    RegistrationClosedError,
)


@pytest.fixture
def reg():
    return Registration(candidate_id="C001", id_number="4401...")


# ── W13: 审核通过后可报名 ───────────────────────────────────

@pytest.mark.p1
def test_enroll_after_verified(reg):
    """审核通过后状态 VERIFIED，可 enroll。"""
    reg.verify(passed=True)
    assert reg.status == "VERIFIED"
    reg.enroll()
    assert reg.status == "ENROLLED"


# ── W14: 审核未通过不能报名 ─────────────────────────────────

@pytest.mark.p1
def test_enroll_when_rejected_raises(reg):
    """审核未通过（REJECTED）时 enroll 应报错。"""
    reg.verify(passed=False)
    assert reg.status == "REJECTED"
    with pytest.raises(RegistrationClosedError):
        reg.enroll()


# ── W15: 审核次数超限 ───────────────────────────────────────

@pytest.mark.p2
def test_verify_count_exceeded(reg):
    """审核超过 3 次应报错。"""
    for _ in range(3):
        reg.verify(passed=True)  # 第3次时 count=3 未超限
    # 第4次 count=4 > 3 超限
    with pytest.raises(RegistrationClosedError):
        reg.verify(passed=True)


@pytest.mark.p2
def test_verify_count_not_exceeded_at_limit(reg):
    """恰好 3 次审核应允许（边界）。"""
    reg.verify(passed=True)   # 1
    reg.verify(passed=True)   # 2
    reg.verify(passed=True)   # 3 → 未超限
    assert reg.status == "VERIFIED"


# ── W16: 已报名不能再审核 ───────────────────────────────────

@pytest.mark.p2
def test_verify_after_enrolled_raises(reg):
    """已报名（ENROLLED）后再次审核应报错。"""
    reg.verify(passed=True)
    reg.enroll()
    with pytest.raises(RegistrationClosedError):
        reg.verify(passed=True)
