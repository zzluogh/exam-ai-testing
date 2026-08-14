"""根级 conftest — fixture 链与共享夹具。

演示 pytest fixture 链：
  app_ready → exam_session_factory → session_p0 / session_p1
每个 fixture 依赖上层，展示 scope 与依赖注入。
"""
import pytest

from exam_testing.business import ExamSession, ScoringEngine, Registration


@pytest.fixture(scope="session")
def app_ready():
    """session 级：一次会话只准备一次（模拟应用就绪检查）。"""
    assert True  # 模拟环境检查
    return {"app": "ready", "version": "1.0"}


@pytest.fixture
def exam_session_factory(app_ready):
    """function 级：依赖 app_ready，返回 ExamSession 工厂。"""
    def _make(session_id="S001", duration=120, max_attempts=1):
        return ExamSession(session_id=session_id,
                           duration_minutes=duration,
                           max_attempts=max_attempts)
    return _make


@pytest.fixture
def session_p0(exam_session_factory):
    """P0 场景标准会话：已开始、已答题。"""
    s = exam_session_factory("S-P0", 120, 1)
    s.start()
    s.submit_answer("Q1", "答案A")
    return s


@pytest.fixture
def engine_standard():
    """标准阅卷引擎：2 道客观题 + 2 分偏差阈值。"""
    return ScoringEngine(
        objective_answer={"Q1": "A", "Q2": "C"},
        max_discrepancy=2.0,
    )


@pytest.fixture
def reg_factory():
    def _make(cid="C001"):
        return Registration(candidate_id=cid, id_number="440102199001011234")
    return _make
