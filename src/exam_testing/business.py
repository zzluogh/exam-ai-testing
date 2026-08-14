"""考试系统核心业务模块 — 被测对象（模拟实现）。

这是"被测系统"，不是测试代码。后续所有测试用例都针对这里的业务逻辑设计。
模拟讯飞考试系统的真实业务：
  - ExamSession: 在线考试会话（进入/答题/交卷/超时/断线）
  - ScoringEngine: 自动阅卷（客观题/主观题多评）
  - Registration: 考生报名（校验/状态流转）
  - PaperBuilder: 组卷（随机抽题/难度分布）
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── 在线考试会话 ─────────────────────────────────────────────

class ExamError(Exception):
    """考试业务异常基类"""


class SessionNotOpenError(ExamError):
    pass


class AlreadySubmittedError(ExamError):
    pass


class AnswerOutOfRangeError(ExamError):
    pass


@dataclass
class ExamSession:
    """一场考试会话。

    Args:
        session_id: 会话 ID
        duration_minutes: 考试时长（分钟）
        max_attempts: 最大提交次数
    """
    session_id: str
    duration_minutes: int = 120
    max_attempts: int = 1

    _started: bool = False
    _submitted: bool = False
    answers: Dict[str, str] = field(default_factory=dict)

    def start(self) -> None:
        """进入考试（开考）。"""
        if self._submitted:
            raise AlreadySubmittedError("已交卷的会话不能重新开始")
        self._started = True

    def is_started(self) -> bool:
        return self._started

    def submit_answer(self, question_id: str, answer: str) -> None:
        """提交一道题的答案。"""
        if not self._started:
            raise SessionNotOpenError("考试未开始，不能答题")
        if self._submitted:
            raise AlreadySubmittedError("已交卷，不能修改答案")
        if len(answer) > 2000:
            raise AnswerOutOfRangeError("答案超过 2000 字上限")
        self.answers[question_id] = answer

    def submit_exam(self) -> int:
        """交卷，返回提交次数（第几次提交）。"""
        if not self._started:
            raise SessionNotOpenError("考试未开始，不能交卷")
        if self._submitted:
            raise AlreadySubmittedError("重复交卷")
        self._submitted = True
        return self.max_attempts

    def is_submitted(self) -> bool:
        return self._submitted

    def answered_count(self) -> int:
        return len(self.answers)


# ── 自动阅卷 ─────────────────────────────────────────────────

class InvalidQuestionTypeError(ExamError):
    pass


class ScoringEngine:
    """自动阅卷引擎。

    - 客观题：标准答案精确匹配
    - 主观题：多评仲裁（两个阅卷人打分，取平均；偏差过大触发三评）
    """

    def __init__(self, objective_answer: Dict[str, str], max_discrepancy: float = 2.0):
        self.objective_answer = objective_answer
        self.max_discrepancy = max_discrepancy

    def score_objective(self, question_id: str, answer: str) -> float:
        """客观题判分：精确匹配得满分，否则 0 分。"""
        if question_id not in self.objective_answer:
            raise InvalidQuestionTypeError(f"未知题目: {question_id}")
        return 100.0 if answer.strip() == self.objective_answer[question_id] else 0.0

    def score_subjective(self, score1: float, score2: float) -> float:
        """主观题多评仲裁：
        - 偏差 ≤ max_discrepancy：取平均
        - 偏差 > max_discrepancy：触发三评，取两个较接近值的平均
        """
        if score1 < 0 or score1 > 100 or score2 < 0 or score2 > 100:
            raise InvalidQuestionTypeError("分数超出 0-100 范围")
        if abs(score1 - score2) <= self.max_discrepancy:
            return (score1 + score2) / 2
        # 偏差过大，需第三评
        score3 = (score1 + score2) / 2  # 模拟三评取中
        return (min(score1, score2) + score3) / 2


# ── 考生报名 ─────────────────────────────────────────────────

class RegistrationClosedError(ExamError):
    pass


class InvalidIdNumberError(ExamError):
    pass


@dataclass
class Registration:
    """考生报名记录，状态机: PENDING → VERIFIED → ENROLLED / REJECTED"""
    candidate_id: str
    id_number: str
    status: str = "PENDING"
    verify_limit: int = 3

    _verify_count: int = 0

    def verify(self, passed: bool) -> None:
        """审核报名。passed=True 通过，否则拒绝。"""
        if self.status == "ENROLLED":
            raise RegistrationClosedError("已通过审核，不能重复操作")
        self._verify_count += 1
        if self._verify_count > self.verify_limit:
            raise RegistrationClosedError("审核次数超限")
        self.status = "VERIFIED" if passed else "REJECTED"

    def enroll(self) -> None:
        """完成报名（审核通过后）。"""
        if self.status != "VERIFIED":
            raise RegistrationClosedError("报名未通过审核，不能选考区")
        self.status = "ENROLLED"
