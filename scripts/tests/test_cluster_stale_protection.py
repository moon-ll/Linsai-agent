#!/usr/bin/env python3
"""簇 stale 清理保护测试（v6.10.7）。

验证"2 成员 + 高相关（accumulate 信号）"簇超期不被自动关闭，
转人工裁决标记；off_topic/无信号簇照旧关闭。

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_cluster_stale_protection.py
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


def _mk_cluster(cid: str, signal=None, updated="2026-06-01T00:00:00Z",
                status="open", pending=False):
    return {
        "cluster_id": cid, "title": f"cluster {cid}", "keywords": ["kw"],
        "summary": "", "member_source_ids": ["a", "b"], "member_summaries": [],
        "status": status, "linked_proposal_id": None,
        "created_at": updated, "updated_at": updated,
        **({"route_signal": signal} if signal else {}),
        **({"pending_human_review": pending} if pending else {}),
    }


class ClusterStaleProtectionTests(TestSuite):
    def __init__(self):
        super().__init__("簇 stale 清理保护测试（v6.10.7）")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from weekend_pipeline import clusters as cl
        from weekend_pipeline.input_jobs import _defer_signal
        from human_queue import _pending_cluster_reviews
        import json
        from datetime import datetime, timezone

        # ── 1. accumulate 信号簇超期被保护 ──────────────────────
        registry = {"clusters": [
            _mk_cluster("cl_protect", signal="accumulate"),
        ], "orphans": []}
        res = cl.close_stale_clusters(registry)
        self.assert_eq(res["closed"], 0, "accumulate 簇不应被关闭")
        self.assert_eq(res["protected"], 1, "accumulate 簇应被保护")
        c = registry["clusters"][0]
        self.assert_eq(c["status"], "open", "保护簇应保持 open")
        self.assert_eq(c.get("pending_human_review"), True, "应标记人工裁决")
        self.assert_true(c.get("stale_notified_at"), "应记录通知时间")

        # ── 2. off_topic / 无信号簇超期照旧关闭 ─────────────────
        registry = {"clusters": [
            _mk_cluster("cl_off", signal="off_topic"),
            _mk_cluster("cl_nosig"),
        ], "orphans": []}
        res = cl.close_stale_clusters(registry)
        self.assert_eq(res["closed"], 2, "off_topic/无信号簇应被关闭")
        self.assert_eq(res["protected"], 0, "不应有保护")
        self.assert_eq(registry["clusters"][0]["status"], "closed", "off_topic 应 closed")
        self.assert_eq(registry["clusters"][1]["status"], "closed", "无信号应 closed")

        # ── 3. 未超期簇不动 ─────────────────────────────────────
        from datetime import datetime, timedelta, timezone
        fresh = (datetime.now(timezone.utc) - timedelta(days=3)).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        registry = {"clusters": [
            _mk_cluster("cl_fresh", signal="accumulate", updated=fresh),
            _mk_cluster("cl_fresh2", updated=fresh),
        ], "orphans": []}
        res = cl.close_stale_clusters(registry)
        self.assert_eq(res["closed"], 0, "未超期不应关闭")
        self.assert_eq(res["protected"], 0, "未超期不应保护")
        self.assert_eq(
            registry["clusters"][0].get("pending_human_review", False), False,
            "未超期不应标记人工裁决")

        # ── 4. 幂等：二次运行不重复记时、仍统计保护 ─────────────
        registry = {"clusters": [
            _mk_cluster("cl_p2", signal="accumulate"),
        ], "orphans": []}
        cl.close_stale_clusters(registry)
        t1 = registry["clusters"][0]["stale_notified_at"]
        res2 = cl.close_stale_clusters(registry)
        self.assert_eq(res2["protected"], 1, "二次运行仍统计保护")
        self.assert_eq(registry["clusters"][0]["stale_notified_at"], t1,
                       "幂等：通知时间不覆盖")

        # ── 5. linked/closed 簇不受保护分支影响 ─────────────────
        registry = {"clusters": [
            _mk_cluster("cl_linked", signal="accumulate", status="linked"),
        ], "orphans": []}
        res = cl.close_stale_clusters(registry)
        self.assert_eq(res["closed"], 0, "linked 簇不在清理范围")
        self.assert_eq(res["protected"], 0, "linked 簇不进保护统计")

        # ── 6. _defer_signal 判定（精确成员正则，防 off_topic 误标）──
        self.assert_eq(_defer_signal("new 门槛未过：成员 2 < 3，继续积累"),
                       "accumulate", "成员不足 defer 应为 accumulate")
        self.assert_eq(_defer_signal("new 门槛未过：成员 1 < 3"),
                       "accumulate", "无逗号变体也应命中")
        self.assert_eq(_defer_signal("主题不对齐，应继续积累等待范式嫁接"),
                       "off_topic", "off_topic 理由常含继续积累字样，不应误标")
        self.assert_eq(_defer_signal("无范式嫁接点，不应开创新课题，判defer继续积累"),
                       "off_topic", "判 defer 继续积累话术应为 off_topic")
        self.assert_eq(_defer_signal("该簇为纯平衡态理论，无范式嫁接点"),
                       "off_topic", "主题不对齐应为 off_topic")
        self.assert_eq(_defer_signal(""), "off_topic", "空理由保守 off_topic")

        # ── 7. 人工队列聚合 cluster_stale 条目 ─────────────────
        # 只读真实 clusters.json（expect 动态同源计算，断言自洽零污染）
        now = datetime.now(timezone.utc)
        real_path = _SCRIPTS_DIR.parent / "memory" / "weekend-input" / "clusters.json"
        if real_path.exists():
            data = json.loads(real_path.read_text(encoding="utf-8"))
            expect = sum(
                1 for c in data.get("clusters", [])
                if c.get("pending_human_review") and c.get("status") == "open"
            )
            got = _pending_cluster_reviews(now)
            self.assert_eq(len(got), expect,
                           f"人工队列条目数应等于 pending_human_review open 簇数（{expect}）")
            for it in got:
                self.assert_eq(it["type"], "cluster_stale", "条目类型")
                self.assert_true("suggested_action" in it, "条目应含建议动作")
                # v6.10.10 回归：cluster_stale 条目必含 proposal_id 字段
                # 供消费者以 id 维度遍历 items 不抛 KeyError
                self.assert_true(
                    "proposal_id" in it and it["proposal_id"],
                    "v6.10.10：cluster_stale 条目必须含 proposal_id 字段",
                )
                self.assert_eq(it["proposal_id"], it["cluster_id"],
                               "v6.10.10：proposal_id 应等于 cluster_id")

        # ── 8. route_signal 常量与 close 函数签名稳定 ───────────
        self.assert_eq(cl.ROUTE_SIGNAL_ACCUMULATE, "accumulate", "accumulate 常量")
        self.assert_eq(cl.ROUTE_SIGNAL_OFF_TOPIC, "off_topic", "off_topic 常量")

        # ── 9. v7.3.29 跨领域降级理由不得误标 accumulate ───────
        # 触发场景（2026-11-05 00h 健康检查生产实测）：v7.3.22 新增的
        # 跨领域降级理由结构上同样是「成员 N < 3」，被原正则误判为
        # accumulate → 簇拿到 stale 保护 → 超期不关闭反而进人工队列，
        # 与「降级补充文献池、不立题」处置语义相反。
        self.assert_eq(
            _defer_signal("new 门槛未过：跨领域簇核心范式成员 2 < 3，"
                          "降级补充文献池（不立题）"),
            "off_topic",
            "v7.3.29：跨领域降级补充文献池不得误标 accumulate（核心范式成员 2）",
        )
        self.assert_eq(
            _defer_signal("new 门槛未过：跨领域簇核心范式成员 0 < 3，"
                          "降级补充文献池（不立题）"),
            "off_topic",
            "v7.3.29：跨领域降级补充文献池不得误标 accumulate（核心范式成员 0）",
        )
        # 反向断言：独立成员不足仍须 accumulate（stale 保护不能被误伤）
        self.assert_eq(
            _defer_signal("new 门槛未过：独立成员 2 < 3，继续积累"),
            "accumulate",
            "v7.3.29：独立成员不足仍为 accumulate（保护语义未被误伤）",
        )

        # ── 10. v7.3.29 跨领域降级簇不得获得 stale 保护 ─────────
        registry = {"clusters": [
            _mk_cluster("cl_cross_degrade", signal="off_topic"),
        ], "orphans": []}
        res = cl.close_stale_clusters(registry)
        self.assert_eq(res["closed"], 1,
                       "v7.3.29：off_topic 跨领域降级簇超期应关闭，不受保护")
        self.assert_eq(res["protected"], 0,
                       "v7.3.29：跨领域降级簇不应进入人工裁决保护")

        # ── 11. v7.3.29 门控/compose 成员数口径一致 ───────────
        # 生产实测 cl_20260816_a21e61：3 条成员中 2 条同 arXiv，
        # 门控按标题去重计 3（放行），compose 按身份归并计 2（丢弃）。
        from weekend_pipeline.input_jobs import _gate_member_count
        dup_members = [
            {"title": "Strain-induced valley transport in CrBr3/WSe2 heterostructure",
             "source_id": "paper:2026-2403.02188-strain-induced"},
            {"title": "Strain-induced valley transport in CrBr$_3$/WSe$_2$ heterostructure",
             "source_id": "paper:2403.02188"},
            {"title": "Van der waals engineering of valley polarization in WSe2",
             "source_id": "paper:2606.15666"},
        ]
        gate_n = _gate_member_count({"member_summaries": dup_members,
                                     "member_source_ids": [m["source_id"] for m in dup_members]})
        self.assert_eq(gate_n, 3, "v7.3.29：门控口径按标题去重计 3（unique_paper_count 缺失时）")
        up_cluster = {"unique_paper_count": 5, "member_summaries": [],
                      "member_source_ids": ["a"]}
        self.assert_eq(_gate_member_count(up_cluster), 5,
                       "v7.3.29：unique_paper_count 优先于标题去重")
        self.assert_eq(_gate_member_count({"member_summaries": [], "member_source_ids": ["x", "y", "z"]}), 3,
                       "v7.3.29：source_ids 为最后回退口径")


def main() -> None:
    suite = ClusterStaleProtectionTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
