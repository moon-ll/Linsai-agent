#!/usr/bin/env python3
"""
test_runner.py — 轻量级内测框架

用途：
    为 LinSai-CoPilot 提供零依赖的自动化测试基础设施。
    支持隔离环境、临时项目根目录、中文报告输出。

用法：
    被 self_test.py 统一调度，也可单独运行某个测试模块。
"""

import sys
import time
import traceback
from pathlib import Path
from typing import List, Dict, Optional

# 确保 scripts/ 在路径中
_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

REAL_ROOT = _SCRIPTS_DIR.parent.resolve()


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
    for fname in ["index.json", "aliases.json", "graph.json", "growth-log.json"]:
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


def create_isolated_env() -> Path:
    """创建完整隔离环境并返回根目录"""
    tmp = _make_isolated_root()
    _copy_essentials(tmp)
    return tmp


def patch_module_root(module_name: str, tmp_root: Path):
    """Monkey-patch 指定模块的 PROJECT_ROOT 指向隔离目录"""
    import importlib
    mod = importlib.import_module(module_name)
    # 常见模式：PROJECT_ROOT 全局变量
    if hasattr(mod, "PROJECT_ROOT"):
        mod.PROJECT_ROOT = tmp_root
    # 常见模式：_get_project_root 函数
    if hasattr(mod, "_get_project_root"):
        mod._get_project_root = lambda: tmp_root
    # 尝试覆盖派生路径
    for attr in dir(mod):
        val = getattr(mod, attr)
        if isinstance(val, Path) and str(REAL_ROOT) in str(val):
            try:
                new_path = Path(str(val).replace(str(REAL_ROOT), str(tmp_root)))
                setattr(mod, attr, new_path)
            except Exception:
                pass


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

        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            try:
                if (isinstance(attr, type) and issubclass(attr, TestSuite)
                        and attr is not TestSuite):
                    instance = attr()
                    t0 = time.time()
                    instance.setup()
                    instance.run_tests()
                    instance.teardown()
                    instance.duration = time.time() - t0
                    suites.append(instance)
            except Exception as e:
                print(f"⚠ 运行 {attr_name} 失败: {e}")
                traceback.print_exc()

    print_report(suites)
    return 0 if all(s.summary()["failed"] == 0 for s in suites) else 1


if __name__ == "__main__":
    sys.exit(run_all())
