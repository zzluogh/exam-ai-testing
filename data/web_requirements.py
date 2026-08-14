"""考试系统 Web 端需求清单 — 覆盖报名/组卷/在线考试/阅卷/成绩五大模块。

每条需求对齐 src/exam_testing/business.py 的可测业务逻辑，
供 AI 生成测试用例。来源字段标注需求出处，体现"入参可追溯"。
"""
WEB_REQUIREMENTS = [
    # ── 在线考试（P0 核心） ──
    {"id": "W01", "module": "在线考试", "priority": "P0",
     "requirement": "考生进入考试后，考试会话必须处于 started 状态，且只有 started 状态才能答题",
     "source": "需求明确"},
    {"id": "W02", "module": "在线考试", "priority": "P0",
     "requirement": "交卷后会话进入 submitted 状态，禁止再次答题和重复交卷",
     "source": "需求明确"},
    {"id": "W03", "module": "在线考试", "priority": "P0",
     "requirement": "考生答案长度不得超过 2000 字，超限应抛出 AnswerOutOfRangeError 且不保存答案",
     "source": "测试假设（基于业务上限）"},
    {"id": "W04", "module": "在线考试", "priority": "P1",
     "requirement": "未开始考试（started=false）时尝试答题或交卷，应抛出 SessionNotOpenError",
     "source": "需求明确"},
    {"id": "W05", "module": "在线考试", "priority": "P1",
     "requirement": "同一会话多次交卷只允许一次，重复交卷应抛出 AlreadySubmittedError",
     "source": "需求明确"},
    {"id": "W06", "module": "在线考试", "priority": "P2",
     "requirement": "考生可对多道题依次提交答案，提交后 answered_count 正确累加",
     "source": "测试假设"},
    {"id": "W07", "module": "在线考试", "priority": "P2",
     "requirement": "开始考试后立即交卷（空答案）应允许，提交次数返回 1",
     "source": "边界值"},

    # ── 自动阅卷（P0 核心） ──
    {"id": "W08", "module": "自动阅卷", "priority": "P0",
     "requirement": "客观题答案精确匹配标准答案得满分，不匹配得 0 分",
     "source": "需求明确"},
    {"id": "W09", "module": "自动阅卷", "priority": "P0",
     "requirement": "主观题两位阅卷人评分偏差在阈值内时，取两者平均分",
     "source": "需求明确"},
    {"id": "W10", "module": "自动阅卷", "priority": "P0",
     "requirement": "主观题两位阅卷人评分偏差超过阈值时，触发三评仲裁，最终分需介于两者之间",
     "source": "需求明确"},
    {"id": "W11", "module": "自动阅卷", "priority": "P1",
     "requirement": "对不存在的题目进行客观题判分，应抛出 InvalidQuestionTypeError",
     "source": "测试假设"},
    {"id": "W12", "module": "自动阅卷", "priority": "P1",
     "requirement": "主观题评分超出 0-100 范围，应抛出 InvalidQuestionTypeError",
     "source": "边界值"},

    # ── 考生报名（P1） ──
    {"id": "W13", "module": "考生报名", "priority": "P1",
     "requirement": "报名审核通过后状态为 VERIFIED，才能进入报名（enroll）",
     "source": "需求明确"},
    {"id": "W14", "module": "考生报名", "priority": "P1",
     "requirement": "审核未通过（REJECTED）时尝试 enroll 应抛出 RegistrationClosedError",
     "source": "需求明确"},
    {"id": "W15", "module": "考生报名", "priority": "P2",
     "requirement": "审核次数超过上限（3 次）应抛出 RegistrationClosedError 且状态不改变",
     "source": "边界值"},
    {"id": "W16", "module": "考生报名", "priority": "P2",
     "requirement": "已报名（ENROLLED）状态再次审核应抛出 RegistrationClosedError",
     "source": "状态机边界"},

    # ── 组卷（P2） ──
    {"id": "W17", "module": "组卷", "priority": "P2",
     "requirement": "试卷发布后考生可见题目，未发布不可见",
     "source": "测试假设（组卷发布逻辑待接入）"},
    {"id": "W18", "module": "组卷", "priority": "P3",
     "requirement": "组卷时随机抽题需保证题目不重复",
     "source": "测试假设（随机抽题逻辑待接入）"},
]
