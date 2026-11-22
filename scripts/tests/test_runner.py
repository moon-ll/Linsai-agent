#!/usr/bin/env python3
"""
test_runner.py — 轻量级内测框架

用途：
    为 LinSai-CoPilot 提供零依赖的自动化测试基础设施。
    支持隔离环境、临时项目根目录、中文报告输出。

用法：
    被 self_test.py 统一调度，也可单独运行某个测试模块。
"""

import os
import sys
import time
import traceback
import unittest
from pathlib import Path
from typing import List, Dict, Optional

# 确保 scripts/ 在路径中
_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

REAL_ROOT = _SCRIPTS_DIR.parent.resolve()

# v7.3.70：测试模式标记——供生产侧识别"当前为测试进程"并跳过不可隔离的
# 子进程写盘（如 micro_scheduler → kb_proposal_reorg 子进程绕过 patch_module_root）
os.environ.setdefault("LINSAI_TEST_MODE", "1")


class TestResult:
    """单个测试用例的结果"""
    def __init__(self, name: str, passed: bool, duration: float, msg: str = ""):
        self.name = name
        self.passed = passed
        self.duration = duration
        self.msg = msg


class TestSuite:
    """测试套件基类。子类重写 setup / teardown / run_tests。"""
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.errors: List[str] = []
        self.duration: float = 0.0

    def setup(self):
        """套件级初始化，子类可重写"""
        pass

    def teardown(self):
        """套件级清理，子类可重写"""
        pass

    def run_tests(self):
        """子类必须实现：执行所有测试用例并填充 self.results"""
        raise NotImplementedError

    def assert_true(self, condition: bool, name: str, msg: str = "") -> bool:
        """断言条件为真，记录结果"""
        passed = bool(condition)
        self.results.append(TestResult(name, passed, 0.0, msg if not passed else ""))
        return passed

    def assert_eq(self, actual, expected, name: str, msg: str = "") -> bool:
        """断言相等"""
        passed = actual == expected
        detail = msg if msg else f"期望 {expected!r}，实际 {actual!r}"
        self.results.append(TestResult(name, passed, 0.0, "" if passed else detail))
        return passed

    def assert_in(self, item, container, name: str, msg: str = "") -> bool:
        """断言包含"""
        passed = item in container
        detail = msg if msg else f"期望包含 {item!r}"
        self.results.append(TestResult(name, passed, 0.0, "" if passed else detail))
        return passed

    def assert_no_exception(self, callable_obj, name: str, *args, **kwargs) -> bool:
        """断言执行不抛出异常"""
        try:
            callable_obj(*args, **kwargs)
            passed = True
            msg = ""
        except Exception as e:
            passed = False
            msg = f"{type(e).__name__}: {e}"
        self.results.append(TestResult(name, passed, 0.0, msg))
        return passed

    def summary(self) -> Dict:
        """返回套件统计"""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        return {
            "name": self.name,
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "duration": round(self.duration, 3),
            "results": self.results,
        }


class _CollectingResult(unittest.TestResult):
    """unittest 结果收集器——逐用例记录成败（标准库 TestResult 子类）。

    必须是 `unittest.TestResult` 的真子类：`TestSuite.run` 会读
    `result.shouldStop` **属性**（不是方法），自建委托实现会把
    `shouldStop` 变成绑定方法（恒真）→ 第一个用例后即 break → 0 断言。
    """

    def __init__(self):
        super().__init__()
        self.outcomes = []  # [(case_id, passed, msg)]

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.append((self._case_id(test), True, ""))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes.append((self._case_id(test), False, self._fmt(err)))

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes.append((self._case_id(test), False, self._fmt(err)))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes.append((self._case_id(test), True, f"跳过：{reason}"))

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.outcomes.append((self._case_id(test), True, "预期失败"))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.outcomes.append((self._case_id(test), False, "意外通过"))

    @staticmethod
    def _case_id(test) -> str:
        return f"{type(test).__name__}.{test._testMethodName}"

    @staticmethod
    def _fmt(err) -> str:
        import traceback as _tb
        exc_type, exc, tb = err
        return "".join(_tb.format_exception(exc_type, exc, tb)).strip()


class UnittestSuiteAdapter:
    """把标准库 `unittest.TestCase` 子类适配为本框架的套件接口。

    v7.3.52（BUG-48）：回归框架只识别 `TestSuite` 子类，而
    `unittest.TestCase` 与 `TestSuite` 无继承关系（两者都直接继承
    `object`）→ 以 `unittest.TestCase` 写的测试文件**永不被收集**，
    断言数恒为 0，却因"未收集即未失败"而显示全绿。

    生产实证：BUG-46 / BUG-47 的回归测试写成 `unittest.TestCase`，
    `self_test --module` 报 3620/3620 全绿，但这两个套件单独跑是
    5 失败 + 2 错误——即"声称已测实则未测"。

    本适配器用标准库 `unittest.TestLoader` 跑真实用例，把每个用例
    的成败折算成本框架的 `TestResult`，从而让 unittest 风格测试
    进入统一计数与报告。失败用例同样计入 failed，不会被静默吞掉。
    """

    def __init__(self, test_case_cls):
        self._cls = test_case_cls
        self.name = test_case_cls.__name__
        self.results: List[TestResult] = []
        self.errors: List[str] = []
        self.duration: float = 0.0

    def setup(self):
        """unittest 用例自带 setUp，适配层无需额外初始化。"""
        pass

    def teardown(self):
        """unittest 用例自带 tearDown，适配层无需额外清理。"""
        pass

    def run_tests(self) -> None:
        """用标准库 TestLoader 跑该类的全部用例并折算结果。"""
        import unittest as _unittest

        loader = _unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(self._cls)
        collector = _CollectingResult()
        suite.run(collector)
        for case_id, passed, msg in collector.outcomes:
            self.results.append(TestResult(case_id, passed, 0.0, msg))

    def summary(self) -> Dict:
        """返回套件统计（与 TestSuite 同形）。"""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        return {
            "name": self.name,
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "duration": round(self.duration, 3),
            "results": self.results,
        }


def _make_isolated_root() -> Path:
    """创建隔离项目根目录（仅目录结构，不复制大文件）"""
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="linsai_test_"))
    dirs = [
        "sessions", "memory", "tasks/active", "tasks/backlog", "tasks/completed",
        "knowledge/raw/papers", "knowledge/wiki/concepts", "knowledge/captures",
        "skills", "persona", "logs", "references/notes",
    ]
    for d in dirs:
        (tmp / d).mkdir(parents=True, exist_ok=True)
    return tmp


def _copy_essentials(tmp_root: Path):
    """复制测试必需的静态文件到隔离环境"""
    import shutil
    import json

    # 人格文件
    persona_src = REAL_ROOT / "persona" / "lin-sai-persona.md"
    if persona_src.exists():
        shutil.copy(persona_src, tmp_root / "persona" / "lin-sai-persona.md")

    # 知识库索引（如有）
    # v7.2.49：**不复制 index.json**。该文件当前已达 184MB（倒排索引），
    # 每套件复制一次 → 单套件隔离根 189MB。15 个套件用 create_isolated_env
    # 后未清理临时目录 → 累计泄漏 238GB，把磁盘写满（2026-10-26 20h 实测：
    # 磁盘 100% / 剩 117Mi，导致本轮健康检查的 Shell 工具全线崩溃）。
    # 索引并非测试必需——kb_index 在缺失时会按需重建，测试断言针对的是
    # 写入逻辑而非索引存量。若某套件确需索引，自行构造小样本索引。
    for fname in ["aliases.json", "graph.json", "growth-log.json"]:
        src = REAL_ROOT / "knowledge" / fname
        if src.exists():
            shutil.copy(src, tmp_root / "knowledge" / fname)

    # 技能文件
    skills_src = REAL_ROOT / "skills"
    if skills_src.exists():
        for skill_dir in skills_src.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                dst = tmp_root / "skills" / skill_dir.name
                dst.mkdir(exist_ok=True)
                shutil.copy(skill_dir / "SKILL.md", dst / "SKILL.md")

    # memory 初始模板
    (tmp_root / "memory" / "user-profile.json").write_text(
        json.dumps({
            "communication_style": {"avg_input_length": 0, "uses_formulas": False},
            "interaction_history": {"total_sessions": 0, "total_messages": 0},
            "last_updated": "2026-05-11T00:00:00Z",
            "research_field": None,
            "_confidence": {"research_field": 0.0}
        }, ensure_ascii=False, indent=2)
    )
    (tmp_root / "memory" / "working-context.json").write_text(
        json.dumps({
            "active_projects": [],
            "pending_decisions": [],
            "key_insights": [],
            "last_updated": "2026-05-11T00:00:00Z"
        }, ensure_ascii=False, indent=2)
    )
    (tmp_root / "memory" / "llm-config.json").write_text(
        json.dumps({"force_provider": None}, ensure_ascii=False, indent=2)
    )
    (tmp_root / "memory" / "skills-state.json").write_text(
        json.dumps({"mode": "manual", "active_skills": []}, ensure_ascii=False, indent=2)
    )


def isolate_logger(tmp_root: Path) -> None:
    """将 logger 文件输出重定向到隔离目录，防止测试日志污染真实 linsai.log。

    根因：logger.py 的 LOGS_DIR 在模块导入时绑定真实路径，
    patch_module_root 无法覆盖；_root_configured 全局标志阻止重新初始化。
    此函数强制重置 logger 状态，将文件 handler 指向 tmp_root/logs/。
    """
    import logging
    import logger as _logger_mod

    # 重置全局配置标志
    _logger_mod._root_configured = False

    # 更新 LOGS_DIR 指向隔离目录
    _logger_mod.LOGS_DIR = tmp_root / "logs"
    (tmp_root / "logs").mkdir(parents=True, exist_ok=True)

    # 清除旧 handlers，避免写入真实日志文件
    root = logging.getLogger("linsai")
    root.handlers = []

    # 重新初始化（文件 handler 将指向隔离目录）
    _logger_mod.setup_logging()


def create_isolated_env() -> Path:
    """创建完整隔离环境并返回根目录"""
    tmp = _make_isolated_root()
    _copy_essentials(tmp)
    isolate_logger(tmp)
    # v6.8.36: 隔离锁目录——避免测试与真实 cron/web 进程争用 /tmp 下的同一锁文件
    # （此前工作时段 file_lock("proposal-lifecycle") 与 lc-micro-scheduler 竞争，
    # 导致 test_round_complete_break 等测试挂起）。common.file_lock 读取此变量。
    os.environ["LINSAI_LOCK_DIR"] = str(tmp / "locks")
    # v7.2.49：登记到全局回收表——即便套件自身忘记清理，进程退出/下一套件
    # 启动时也会回收，避免临时目录无限堆积写满磁盘。
    _ISOLATED_ENVS.append(tmp)
    return tmp


# v7.2.49：隔离环境回收表 + 集中清理。
# 缺陷：15 个套件用 create_isolated_env() 建隔离根但 teardown 未 rmtree，
# 每次 self_test --module 泄漏约 15 × 189MB ≈ 2.8GB（index.json 已不再复制，
# 单套件降至约 5MB）；累积数百次后磁盘写满（2026-10-26 20h 实测 238GB
# / 磁盘 100% / 剩 117Mi，Shell 工具全线崩溃）。
# 处置：create_isolated_env 登记 + 套件结束后集中回收 + 进程退出兜底。
_ISOLATED_ENVS: List[Path] = []


def cleanup_isolated_envs() -> int:
    """回收本次进程创建的所有隔离环境目录，返回回收数量。

    由 self_test 在全部套件结束后调用；同时注册 atexit 兜底，
    覆盖「套件崩溃 / Ctrl-C / 异常退出」等未走到集中清理的路径。
    """
    import shutil
    n = 0
    while _ISOLATED_ENVS:
        tmp = _ISOLATED_ENVS.pop()
        try:
            shutil.rmtree(tmp, ignore_errors=True)
            n += 1
        except Exception:
            pass
    return n


import atexit  # noqa: E402  —— 放在此处以便 _ISOLATED_ENVS 已定义
atexit.register(cleanup_isolated_envs)


# patch 注册表（v6.9.54）：记录每个模块被 patch 前的原始属性值，
# 支持同一进程内多次 patch_module_root 时先还原再打新补丁。
_PATCH_REGISTRY: dict = {}


def patch_module_root(module_name: str, tmp_root: Path):
    """Monkey-patch 指定模块的 PROJECT_ROOT 指向隔离目录。

    v6.9.54 可重入修复：派生路径替换条件是"属性值含真实根字符串"，
    同一模块被第二个套件 patch 时这些属性已指向上一个套件的隔离根
    （不含真实根字符串）→ 替换静默失效 → 套件拿到已删除的旧根，
    relative_to / FileNotFoundError 崩套件（实测：test_idea_review →
    test_optimize_v6817 → test_proposal_kb_sync 链条只有第一个能跑）。
    现在先按注册表还原上次 patch 的原始值，再重新替换。
    """
    import importlib
    mod = importlib.import_module(module_name)

    # 1. 还原上一次 patch（若有）
    for attr, old in _PATCH_REGISTRY.pop(module_name, []):
        try:
            setattr(mod, attr, old)
        except Exception:
            pass

    saved = []  # (attr, old_value)

    # 2. 常见模式：PROJECT_ROOT 全局变量
    if hasattr(mod, "PROJECT_ROOT"):
        saved.append(("PROJECT_ROOT", getattr(mod, "PROJECT_ROOT")))
        mod.PROJECT_ROOT = tmp_root
    # 常见模式：_get_project_root 函数
    if hasattr(mod, "_get_project_root"):
        saved.append(("_get_project_root", getattr(mod, "_get_project_root")))
        mod._get_project_root = lambda: tmp_root
    # 3. 覆盖派生路径（还原后属性值恢复为真实根，替换条件重新成立）
    for attr in dir(mod):
        val = getattr(mod, attr)
        if isinstance(val, Path) and str(REAL_ROOT) in str(val):
            try:
                new_path = Path(str(val).replace(str(REAL_ROOT), str(tmp_root)))
                saved.append((attr, val))
                setattr(mod, attr, new_path)
            except Exception:
                pass

    _PATCH_REGISTRY[module_name] = saved


def patch_kb_sync_noop(micro_scheduler_module) -> None:
    """把 micro_scheduler 的 KB 同步替换为 no-op，避免写穿真实 knowledge/。

    根因（v6.8.33）：micro_scheduler._sync_proposal_to_kb → proposal_kb_sync.sync_proposal
    → knowledge_base.save_proposal_sync → kb_wiki.save_wiki_page，链路上的
    kb_wiki.KNOWLEDGE_DIR / kb_graph.GRAPH_PATH 是模块级绝对常量，patch_module_root
    只覆盖传入的单个模块、覆盖不到整条链，故 sync 会写进真实 knowledge/wiki/projects/。

    对于只验证调度/轮转/stale 清理等逻辑、不验证 KB 同步产物的 micro_scheduler 测试，
    直接把 _sync_proposal_to_kb 替换为 no-op（micro_scheduler 内部以模块全局裸调用，
    setattr 模块属性即可拦截），符合「测试零污染、不碰真实 knowledge/ 数据域」原则。
    """
    micro_scheduler_module._sync_proposal_to_kb = lambda *a, **kw: None


def print_report(suites: List[TestSuite]):
    """打印中文测试报告"""
    print("\n" + "=" * 60)
    print("  LinSai-CoPilot 内测报告")
    print("=" * 60)

    total_passed = 0
    total_failed = 0
    total_duration = 0.0

    for suite in suites:
        s = suite.summary()
        total_passed += s["passed"]
        total_failed += s["failed"]
        total_duration += s["duration"]

        status_icon = "✓" if s["failed"] == 0 else "✗"
        print(f"\n{status_icon} {s['name']}")
        print(f"   通过 {s['passed']}/{s['total']}  |  耗时 {s['duration']:.3f}s")

        for r in s["results"]:
            if not r.passed:
                print(f"   ✗ {r.name}")
                if r.msg:
                    print(f"      → {r.msg}")

    print("\n" + "-" * 60)
    grand_total = total_passed + total_failed
    if total_failed == 0:
        print(f"🟢 全量通过  {total_passed}/{grand_total}  总耗时 {total_duration:.3f}s")
    else:
        print(f"🔴 存在失败  {total_passed}/{grand_total}  总耗时 {total_duration:.3f}s")
    print("=" * 60 + "\n")


def execute_suite(instance: "TestSuite", name: str, suites: list) -> None:
    """执行单个测试套件，保证清理与可见性（v6.9.54）。

    此前 setup/run_tests/teardown 直接串联：run_tests 中途抛异常时
    teardown 被跳过（WebApiSuite 场景下 web_server 子进程泄漏为孤儿，
    8 月累计 50+ 个），且崩溃套件不进 suites 报告——"全量通过"掩盖
    了从未跑完的套件。规则：
    - teardown 放 finally，setup 成功后必然执行；
    - 崩溃的套件也计入报告，并追加 1 条失败结果（套件完整执行）。
    """
    t0 = time.time()
    crash_msg = ""
    try:
        instance.setup()
        instance.run_tests()
    except Exception as e:  # noqa: BLE001 —— 崩溃套件必须可见且计入失败
        crash_msg = f"{type(e).__name__}: {e}"
        print(f"⚠ 运行 {name} 失败: {crash_msg}")
        traceback.print_exc()
    finally:
        try:
            instance.teardown()
        except Exception as e:  # noqa: BLE001 —— 清理失败不能吞掉测试结果
            print(f"⚠ 清理 {name} 失败: {e}")
        instance.duration = time.time() - t0
        if crash_msg:
            instance.results.append(TestResult("套件完整执行", False, 0.0, crash_msg))
        suites.append(instance)
        # v6.9.54 模块卫生：多数测试文件用"del sys.modules + 重导入 +
        # patch_module_root"隔离且不在 teardown 还原——重导入产生的模块
        # 对象绑定当时的隔离根，泄漏给后续套件（实测使
        # test_optimize_v6817 拿到已删除的旧根崩套件）。每套件结束后
        # 弹出 proposal_lifecycle / lifecycle 系（本次确认的污染域），
        # 强制下一套件从真实根重新导入后再做自己的 patch。
        # 注意范围：kb_graph/kb_wiki/kb_index/kb_health/knowledge_base
        # **不可**纳入弹出——它们之间存在大量模块级 from-import 函数
        # 绑定（如 kb_health 的 from kb_wiki import list_wiki_pages），
        # 只弹一部分会造成"新旧对象分裂"：测试 patch 新对象而未弹出的
        # 旧模块仍调用旧对象（实测 KbSubmoduleTests 因此读到真实知识库
        # 920 节点）。这些 KB 模块由各测试自身 setup/teardown 管理。
        for mod_name in [
            m for m in list(sys.modules)
            if m.startswith(("proposal_lifecycle", "lifecycle"))
            or m == "lifecycle_cron_framework"
        ]:
            sys.modules.pop(mod_name, None)


def iter_suite_factories(mod, mod_name: str):
    """产出该测试模块中应运行的套件实例（生成器）。

    v7.3.52（BUG-48）：此前只识别 `TestSuite` 子类，`unittest.TestCase`
    子类（与 TestSuite 无继承关系）永不被收集 → 断言数恒 0 而报告显示
    全绿。本函数同时产出两类：

    1. `TestSuite` 子类 → 原生实例；
    2. `unittest.TestCase` 子类 → `UnittestSuiteAdapter` 包装实例。

    `__module__` 过滤保留（v6.9.54）：from 别的测试文件 import 进来的
    套件类会被重复执行（叠加模块卫生弹出后 setup 假设失效）。
    """
    import unittest as _unittest

    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if not isinstance(attr, type):
            continue
        if getattr(attr, "__module__", None) != mod_name:
            continue
        if issubclass(attr, TestSuite) and attr is not TestSuite:
            yield attr_name, attr
        elif issubclass(attr, _unittest.TestCase) and attr is not _unittest.TestCase:
            yield attr_name, attr


def run_all() -> int:
    """发现并运行所有测试套件，返回退出码（0=全过）"""
    import importlib
    suites: List[TestSuite] = []

    test_dir = Path(__file__).parent
    for fpath in sorted(test_dir.glob("test_*.py")):
        mod_name = fpath.stem  # 如 test_core
        try:
            # self_test.py 已将 scripts/tests 加入 sys.path
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"⚠ 加载测试模块 {mod_name} 失败: {e}")
            continue

        for attr_name, attr in iter_suite_factories(mod, mod_name):
            try:
                if issubclass(attr, TestSuite):
                    execute_suite(attr(), attr_name, suites)
                else:
                    # v7.3.52（BUG-48）：unittest 风格套件经适配器纳入统一计数
                    execute_suite(UnittestSuiteAdapter(attr), attr_name, suites)
            except Exception as e:
                print(f"⚠ 实例化 {attr_name} 失败: {e}")

    print_report(suites)
    return 0 if all(s.summary()["failed"] == 0 for s in suites) else 1


if __name__ == "__main__":
    sys.exit(run_all())
