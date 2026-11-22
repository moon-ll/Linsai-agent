#!/usr/bin/env python3
"""
test_kb_merger_methods.py — methods 同命名空间确定性归并回归测试（v7.3.77）

覆盖能力（决策包 C1，2026-11-09 用户裁决）：
    wiki/methods「磁/自旋群对称性分析」家族 15+ 近同名变体页 + hash 散页
    归并。kb_merger 新增归一键自动聚组通道与显式家族策展合并通道。

注意：
    kb_wiki 以字典桩替换（合并/改写/aliases 全链零真实落盘），
    aliases.json 指向隔离临时目录。
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from test_runner import TestSuite, create_isolated_env


class KbMergerMethodsTests(TestSuite):
    def __init__(self):
        super().__init__("kb_merger methods 同命名空间归并测试")
        self.tmp_root = None

    def setup(self):
        self.tmp_root = create_isolated_env()

    def teardown(self):
        pass

    def run_tests(self):
        import kb_merger
        import kb_wiki

        # ---------- 1. 归一键纯逻辑 ----------
        self.assert_eq(
            kb_merger.normalize_method_name("磁点群/自旋群对称性分析"),
            kb_merger.normalize_method_name("磁点群自旋群对称性分析"),
            "分隔符剥离：斜杠组合名与连写名同键")
        self.assert_eq(
            kb_merger.normalize_method_name("磁性空间群对称性分析（拓扑量子化学框架）"),
            kb_merger.normalize_method_name("磁性空间群对称性分析"),
            "括号限定词剥离：框架变体同键")
        self.assert_true(
            kb_merger.normalize_method_name("磁空间群对称性分析与线性自旋波建模")
            != kb_merger.normalize_method_name("磁空间群对称性分析"),
            "MSG+LSWT 组合方法页与纯对称性分析页不同键（防语义误并）")

        # ---------- 2. 归一键分组检测（注入式，零 IO） ----------
        fake_ns = [
            {"path": "wiki/methods/a.md", "title": "磁点群/自旋群对称性分析", "merged_into": ""},
            {"path": "wiki/methods/b.md", "title": "磁点群自旋群对称性分析", "merged_into": ""},
            {"path": "wiki/methods/c.md", "title": "自旋空间群对称性分析",
             "merged_into": "wiki/methods/b.md"},
            {"path": "wiki/methods/d.md", "title": "磁点群对称性选择定则分析", "merged_into": ""},
        ]
        groups = kb_merger.detect_method_name_groups(pages=fake_ns)
        self.assert_eq(len(groups), 1, "变体聚成一组")
        self.assert_eq(sorted(groups[0]["paths"]),
                       ["wiki/methods/a.md", "wiki/methods/b.md"],
                       "stub 排除、单页不成组")

        # ---------- 3. 家族合并全链（字典桩 kb_wiki） ----------
        store = {}

        def fake_get(rel):
            return store.get(rel)

        def fake_save(rel, content, meta=None):
            store[rel] = {"path": rel, "frontmatter": dict(meta or {}), "body": content}

        def fake_list(wiki_type=None):
            return [dict(v) for v in store.values()]

        orig = (kb_wiki.get_wiki_page, kb_wiki.save_wiki_page,
                kb_wiki.list_wiki_pages, kb_wiki._ensure_dirs)
        kb_wiki.get_wiki_page = fake_get
        kb_wiki.save_wiki_page = fake_save
        kb_wiki.list_wiki_pages = fake_list
        kb_wiki._ensure_dirs = lambda: None
        aliases_path = self.tmp_root / "aliases.json"
        kb_merger.ALIASES_PATH = aliases_path

        try:
            primary = "wiki/methods/main.md"
            store[primary] = {
                "path": primary,
                "frontmatter": {"title": "磁点群/自旋群对称性分析",
                                "related": ["A"], "tags": ["方法学"]},
                "body": "主页面内容",
            }
            members = {
                "wiki/methods/m1.md": ("自旋空间群对称性分析", "M1 独有参数表内容", ["B"]),
                "wiki/methods/m2.md": ("磁性群/自旋群对称性分析", "M2 语义近邻内容", []),
                "wiki/methods/m3.md": ("磁点群对称性选择定则分析", "M3 选择定则内容", ["C"]),
            }
            for path, (title, body, related) in members.items():
                store[path] = {
                    "path": path,
                    "frontmatter": {"title": title, "related": list(related),
                                    "tags": ["方法学", "#type/method"]},
                    "body": body,
                }
            # 观察页：正文 wikilink + related 均指向被并页 title，验证引用改写
            watcher = "wiki/concepts/w.md"
            store[watcher] = {
                "path": watcher,
                "frontmatter": {"title": "观察页", "related": ["自旋空间群对称性分析"]},
                "body": "参见 [[自旋空间群对称性分析]] 与 [[磁性群/自旋群对称性分析]]。",
            }

            result = kb_merger.merge_name_family(primary, [primary] + list(members))
            self.assert_true(result["success"], "家族合并成功")
            self.assert_eq(result["merged"], 3, "三个成员全部处理")
            self.assert_eq(result["failed"], 0, "零失败")

            # 主页面：附录并置 + 边迁移
            merged = store[primary]
            for path, (title, _, _) in members.items():
                self.assert_true("## 合并自「%s」" % title in merged["body"],
                                 "附录含成员标题：%s" % title)
            self.assert_true("B" in merged["frontmatter"]["related"]
                             and "C" in merged["frontmatter"]["related"],
                             "related 边迁移至主页面")
            self.assert_true("#type/method" in merged["frontmatter"]["tags"],
                             "tags 并集迁移")

            # 成员页：转 stub
            for path in members:
                fm = store[path]["frontmatter"]
                self.assert_eq(fm.get("merged_into"), primary,
                               "成员转重定向 stub：%s" % path)

            # 引用改写：观察页 wikilink 与 related 指向主页面 title
            w = store[watcher]
            self.assert_true("[[磁点群/自旋群对称性分析]]" in w["body"],
                             "观察页 wikilink 改写至主 title")
            self.assert_true("[[自旋空间群对称性分析]]" not in w["body"],
                             "旧 wikilink 不残留")
            self.assert_eq(w["frontmatter"]["related"],
                           ["磁点群/自旋群对称性分析"],
                           "观察页 related 改写至主 title")

            # aliases 注册
            import json
            data = json.loads(aliases_path.read_text(encoding="utf-8"))
            canon = data.get("磁点群/自旋群对称性分析", [])
            self.assert_eq(sorted(canon),
                           sorted(["自旋空间群对称性分析",
                                   "磁性群/自旋群对称性分析",
                                   "磁点群对称性选择定则分析"]),
                           "aliases.json 注册三个被并名")

            # 幂等重放：成员已 stub → 全跳过，无二次附录，aliases 无重复
            body_before = merged["body"]
            result2 = kb_merger.merge_name_family(primary, [primary] + list(members))
            skipped = [d for d in result2["detail"] if d.get("mode") == "skipped-stub"]
            self.assert_eq(len(skipped), 3, "重放时 stub 成员全部跳过")
            self.assert_eq(store[primary]["body"], body_before, "重放不产生二次附录")
            data2 = json.loads(aliases_path.read_text(encoding="utf-8"))
            self.assert_eq(len(data2["磁点群/自旋群对称性分析"]), 3, "aliases 幂等无重复")

            # dry-run：零写入
            store["wiki/methods/m4.md"] = {
                "path": "wiki/methods/m4.md",
                "frontmatter": {"title": "自旋劳厄群对称性分析", "tags": []},
                "body": "M4 内容",
            }
            before = dict(store[primary]["frontmatter"])
            result3 = kb_merger.merge_name_family(
                primary, ["wiki/methods/m4.md"], dry_run=True)
            self.assert_true(result3["dry_run"], "dry-run 标记")
            self.assert_eq(store[primary]["body"], body_before, "dry-run 零写入主页面")
            self.assert_eq(store[primary]["frontmatter"], before, "dry-run 零写入 frontmatter")
            self.assert_true(store["wiki/methods/m4.md"]["frontmatter"].get("merged_into")
                             is None, "dry-run 不写 stub")
        finally:
            kb_wiki.get_wiki_page, kb_wiki.save_wiki_page = orig[0], orig[1]
            kb_wiki.list_wiki_pages, kb_wiki._ensure_dirs = orig[2], orig[3]


if __name__ == "__main__":
    import time
    suite = KbMergerMethodsTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])
