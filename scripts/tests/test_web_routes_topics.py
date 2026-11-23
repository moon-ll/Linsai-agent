# -*- coding: utf-8 -*-
"""web_routes_topics（/api/topics/* 课题工作台路由）单元测试。

隔离策略：patch topic_pipeline.constants.TOPICS_ROOT 到临时目录（state/
registration/migration 均经 _C 动态读取），handler 用 stub self 捕获 _send_json，
不经 HTTP 子进程。覆盖：看板/详情/自检/启动/否决/归档 + 阶段即目录不变量 +
参数校验（否决缺 reason 400、未知课题 404、非法阶段流转 400）。
"""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from topic_pipeline import (  # noqa: E402
    acceptance,
    assemble,
    constants,
    deep_research,
    registration,
    state as tstate,
)
from topic_pipeline.card import render_card  # noqa: E402
import web_routes_topics  # noqa: E402


class _StubHandler:
    """捕获 _send_json 的最小 stub（MixIn 方法只依赖该接口）。"""

    def __init__(self):
        self.responses = []

    def _send_json(self, payload, status=200):
        self.responses.append((status, payload))

    @property
    def last(self):
        return self.responses[-1] if self.responses else (0, {})


def _parsed(path: str) -> SimpleNamespace:
    return SimpleNamespace(path=path)


class TestWebRoutesTopics(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "research_topics"
        self.root.mkdir(parents=True)
        self._orig = constants.TOPICS_ROOT
        constants.TOPICS_ROOT = self.root
        self.h = _StubHandler()
        self.addCleanup(self._teardown)

    def _teardown(self):
        constants.TOPICS_ROOT = self._orig
        self._tmp.cleanup()

    def _call(self, method, path, body=None):
        """经 Mixin 类绑定调用 handler（stub self 不继承 Mixin）。"""
        return getattr(web_routes_topics.TopicsRoutesMixin, method)(self.h, _parsed(path), body=body)

    def _register(self, title="工作台路由测试课题", slug="wb-route-test"):
        res = registration.register_question(
            title=title, problem="路由层测试问题陈述", source="test",
            slug=slug, knowledge_card="k", related=[])
        self.assertTrue(res["registered"], res.get("reason"))
        return res["topic_id"]

    def _to_ready(self, tid):
        # 直接在 kickoff 阶段铺设满足验收的材料（不经 hermes）
        tdir = Path(tstate.topic_dir(tid))
        bg = tdir / "01_background"
        bg.mkdir(parents=True, exist_ok=True)
        for i in range(8):
            (bg / f"note-{i}.md").write_text(f"笔记 {i}（2026-01）[[知识页{i}]] 关键数值 1.2 eV 带出处说明。" * 6, encoding="utf-8")
        pr = tdir / "02_problem"
        pr.mkdir(parents=True, exist_ok=True)
        (pr / "problem.md").write_text(
            "## 问题一句话陈述\n\n测试问题：在隔离环境中验证课题工作台路由的验收口径与流转不变量。\n\n"
            "## 新颖性对照（差异点）\n\n1. 与既有工作差异一：对象不同。\n2. 差异二：方法路径不同。\n"
            "3. 差异三：判据口径不同。\n\n## 可检验判据\n\n- [V] 谐波圆二色性符号翻转（文献已核实）\n"
            "- [P] 判据阈值 0.1（自设阈值，理由：信噪比经验）\n- [D] 响应幅度待预研标定\n", encoding="utf-8")
        sc = tdir / "03_scheme"
        sc.mkdir(parents=True, exist_ok=True)
        (sc / "scheme.md").write_text(
            "".join(f"## S{i} 步骤{i}\n方法：{m}。\n输入：样品与激光。\n输出：谐波谱数据。\n"
                    f"判据：信噪比大于 3 且重复三次一致。\n预计工作量：{i} 周。\n\n"
                    for i, m in enumerate(["样品表征", "光路搭建", "谐波采集"], 1))
            + "## 里程碑\nM1 完成表征。\n\n## 首月路线\n先做 S1 样品表征，随后 S2 光路搭建。\n"
              "\n## 风险与备选\n样品退化则更换衬底。\n", encoding="utf-8")
        (sc / "kb-methods-pack.md").write_text("# 素材包\n", encoding="utf-8")
        rf = tdir / "04_references"
        rf.mkdir(parents=True, exist_ok=True)
        (rf / "references.bib").write_text(
            "@article{a2026,\n  title={A},\n  source: [[知识页0]]\n}\n", encoding="utf-8")
        # 报告含 ≥5 wikilink + related 字段
        report = "# 报告\n\n[[知识页0]] [[知识页1]] [[知识页2]] [[知识页3]] [[知识页4]]\n"
        (tdir / "topic-report.md").write_text(report, encoding="utf-8")
        # check 只从 kickoff 晋级 ready——先模拟深研进入 kickoff
        tstate.transition(tid, "kickoff", "测试进入深研")
        chk = acceptance.check_topic(tid)
        self.assertTrue(chk["verdict"]["passed"], chk["verdict"]["gaps"])

    # -------------------------------------------------- GET

    def test_board_lists_stages(self):
        tid = self._register()
        self._call("_topics_board", "/api/topics")
        status, payload = self.h.last
        self.assertEqual(status, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["stages"]["questions"]["count"], 1)
        self.assertEqual(payload["stages"]["questions"]["items"][0]["id"], tid)

    def test_detail_returns_report_and_check(self):
        tid = self._register()
        self._call("_topics_detail", f"/api/topics/{tid}")
        status, payload = self.h.last
        self.assertEqual(status, 200)
        self.assertEqual(payload["id"], tid)
        self.assertIn("problem", payload["card"])
        self.assertEqual(payload["report"], "")

    def test_detail_unknown_topic_404(self):
        self._call("_topics_detail", "/api/topics/general-nope-20260101")
        status, payload = self.h.last
        self.assertEqual(status, 404)
        self.assertFalse(payload["success"])

    # -------------------------------------------------- POST

    def test_activate_moves_dir_and_stage(self):
        tid = self._register()
        self._call("_topics_activate", f"/api/topics/{tid}/activate")
        status, payload = self.h.last
        self.assertEqual(status, 200, payload)
        self.assertEqual(payload["stage"], "active")
        self.assertTrue((self.root / "active" / tid).exists())
        self.assertFalse((self.root / "questions" / tid).exists())

    def test_activate_rejects_archive_stage_400(self):
        tid = self._register()
        tstate.transition(tid, "archive", "测试")
        self._call("_topics_activate", f"/api/topics/{tid}/activate")
        status, payload = self.h.last
        self.assertEqual(status, 400)
        self.assertFalse(payload["success"])

    def test_reject_requires_reason_400(self):
        tid = self._register()
        self._call("_topics_reject", f"/api/topics/{tid}/reject", body={})
        status, payload = self.h.last
        self.assertEqual(status, 400)
        # 课题未被否决
        data = tstate.load_state()
        self.assertIn(tid, data["topics"])

    def test_reject_moves_any_stage_dir(self):
        tid = self._register()
        self._call("_topics_reject", f"/api/topics/{tid}/reject", body={"reason": "重复"})
        status, payload = self.h.last
        self.assertEqual(status, 200)
        self.assertTrue((self.root / "_rejected-questions" / tid).exists())
        self.assertFalse((self.root / "questions" / tid).exists())
        data = tstate.load_state()
        self.assertNotIn(tid, data["topics"])
        self.assertEqual(data["rejected"][tid]["reason"], "重复")

    def test_reject_unknown_topic_404(self):
        self._call("_topics_reject", "/api/topics/general-nope-20260101/reject",
                              body={"reason": "x"})
        status, payload = self.h.last
        self.assertEqual(status, 404)

    def test_archive_moves_dir_from_active(self):
        tid = self._register()
        tstate.transition(tid, "active", "测试")
        self._call("_topics_archive", f"/api/topics/{tid}/archive")
        status, payload = self.h.last
        self.assertEqual(status, 200)
        self.assertTrue((self.root / "archive" / tid).exists())
        self.assertFalse((self.root / "active" / tid).exists())
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "archive")

    def test_check_promotes_to_ready(self):
        tid = self._register()
        self._to_ready(tid)
        # check 前课题应在 ready（_to_ready 内 check 已触发晋级）
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "ready")
        self.assertTrue((self.root / "ready" / tid).exists())
        # 再次经 API 自检（幂等）
        self._call("_topics_check", f"/api/topics/{tid}/check")
        status, payload = self.h.last
        self.assertEqual(status, 200)
        self.assertTrue(payload["verdict"]["passed"])


if __name__ == "__main__":
    unittest.main()
