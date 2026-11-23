#!/usr/bin/env python3
"""
test_structure_guard_calibration.py — 方案结构守卫判别力回归测试
（v7.3.39 / BUG-44）

背景（2026-11-05 12h 健康检查第二层定位）：
    `scripts/proposal_structure_guard.py` 自 v7.2.30 起承担「6 章节硬模板」
    守卫职责（SKILL.md §七），但实现存在三处结构性缺陷，导致
    **守卫在 11/11 课题上恒判 fail，且判别力为零**：

      ① 读的是陈旧备份而非当前正文
         `_latest_proposal_file` 优先取 `proposal-draft-r*.md`——那是
         executor.py:1381 在 writer 修改前做的**上一轮快照**；writer 返回后
         optimize.py:2259 从 sections/ 重新组装 `proposal-draft.md`
         （live 正文），此后修改只落在 live 正文上，备份不再前进。
         实测 11 课题全部命中，备份落后 live 正文 0.5h ~ 1043.9h。

      ② 合并式标题只取首个命中项
         生产 scheme.md 的标题是「（三）研究方案、特色与创新、预期研究成果」
         ——一个标题含 3 个标准章节。旧 `_classify_h2` 命中第一个即返回，
         另外两章被丢弃 → 误报缺 2 章节。

      ③ 中文数字兜底无条件生效
         旧实现只要标题以「一、」「二、」「三、」开头就映射为
         立项依据/研究内容/研究方案。full_review 骨架的三条序号标题
         （一、主线论证链 / 二、章节衔接点 / 三、跨章节统一口径表）
         因此被误判为标准章节 → 既污染章节集合，又造成顺序检查假阳性
         （out_of_order=True）。

    另有一处同义词表漏收：生产产物实际用「预期**研究**成果」
    （berry content.md 2.9 / 3.7），旧表只收「预期成果」→ 落「其他」。

修复要点：
    - `_latest_proposal_file` 优先读 live 正文，回退备份时按轮号取最大
      （非字典序——轮号 ≥10 时字典序会把 r9 排到 r10 之后）
    - 新增 `_classify_h2_all`：一个标题可命中多个标准章节
    - 中文数字兜底仅在「标题本体就是该序号」（纯序号标题）时生效
    - 同义词表补「预期研究成果」

测试覆盖：
    1. 章节分类：合并式标题 / 骨架序号标题 / 括号补充说明 / 变体词
    2. 判别力：合规→pass、缺 1→warn、缺 2→fail、错序→fail
    3. 生产 5 模块架构不被骨架序号误判（no false ooo）
    4. 文件选择：live 优先于陈旧备份；备份回退取最大轮号
    5. 反向断言：复刻旧实现必然误报——确保测试非自证绿

注意：本测试不调用 hermes/LLM，不写生产目录（临时目录 + 用完即删）。

用法示例：
    python3 scripts/tests/test_structure_guard_calibration.py
"""

import shutil
import sys
import tempfile
from pathlib import Path

from test_runner import TestSuite, create_isolated_env


class StructureGuardCalibrationTests(TestSuite):
    def __init__(self):
        super().__init__("方案结构守卫判别力回归测试（v7.3.39 / BUG-44）")

    def run_tests(self):
        env = create_isolated_env()
        try:
            import proposal_structure_guard as g

            # ---------- 1. 章节分类 ----------
            self.assert_eq(
                g._classify_h2("一、立项依据"), "立项依据",
                "基础：中文序号 + 章节名")
            self.assert_eq(
                g._classify_h2("〇、产出定位"), "产出定位",
                "基础：〇号 = 产出定位")
            self.assert_eq(
                g._classify_h2("立项依据"), "立项依据",
                "基础：无序号纯章节名")
            self.assert_eq(
                g._classify_h2("六、跨章口径表"), "其他",
                "基础：六号不在 6 章节内")

            # v7.3.39：合并式标题命中多个标准章节
            self.assert_eq(
                g._classify_h2_all("（三）研究方案、特色与创新、预期研究成果"),
                ["研究方案", "特色与创新", "预期成果"],
                "合并式标题应同时命中研究方案/特色与创新/预期成果")
            self.assert_eq(
                g._classify_h2("（三）研究方案、特色与创新、预期研究成果"),
                "研究方案+特色与创新+预期成果",
                "单值分类用 + 连接多命中章节")

            # v7.3.39：full_review 骨架序号标题不得被误判为标准章节
            for title in ("一、主线论证链（核心问题→研究内容→方案如何回应）",
                          "二、章节衔接点（关键承接关系）",
                          "三、跨章节统一口径表"):
                self.assert_eq(
                    g._classify_h2(title), "其他",
                    f"full_review 骨架标题不应误判为标准章节：{title[:14]}")

            # v7.3.39：「预期研究成果」变体
            self.assert_eq(
                g._classify_h2("2.9 预期研究成果"), "预期成果",
                "生产变体「预期研究成果」应归入预期成果")
            self.assert_eq(
                g._classify_h2("3.7 特色与创新、预期研究成果、年度计划（指引）"),
                "特色与创新+预期成果",
                "berry 3.7 合并标题应命中两章")

            # 纯序号标题仍走中文数字兜底
            self.assert_eq(
                g._classify_h2("一、"), "立项依据",
                "纯序号标题仍走中文数字兜底")

            # ---------- 2. 判别力（合成用例）----------
            tmp = tempfile.mkdtemp(prefix="hc_structure_guard_")
            try:
                orig = (g.ROOT, g.OPT_DIR, g.DRAFTS_DIR, g.PR_DIR)
                g.ROOT = Path(tmp)
                g.OPT_DIR = Path(tmp) / "research_proposals" / "optimizing"
                g.DRAFTS_DIR = Path(tmp) / "research_proposals" / "drafts"
                g.PR_DIR = Path(tmp) / "research_proposals" / "pending_review"

                def make(pid, text):
                    d = g.OPT_DIR / pid / "04_proposal"
                    d.mkdir(parents=True, exist_ok=True)
                    (g.OPT_DIR / pid / "00_research_idea.md").write_text("idea")
                    (d / "proposal-draft.md").write_text(text, encoding="utf-8")
                    return d

                compliant = (
                    "# t\n## 〇、产出定位\nx\n## 一、立项依据\nx\n"
                    "## 二、研究内容\nx\n## 三、研究方案\nx\n"
                    "## 四、特色与创新\nx\n## 五、预期成果\nx\n"
                )
                make("ok", compliant)
                r = g.check_proposal("ok")
                self.assert_eq(r["status"], "pass",
                               "完全合规 6 章节应判 pass")
                self.assert_eq(r["missing"], [],
                               "合规文档不应报缺章节")
                self.assert_eq(r["out_of_order"], False,
                               "合规文档不应报顺序错乱")

                make("one-missing",
                     "# t\n## 〇、产出定位\nx\n## 一、立项依据\nx\n"
                     "## 二、研究内容\nx\n## 三、研究方案\nx\n"
                     "## 四、特色与创新\nx\n")
                r = g.check_proposal("one-missing")
                self.assert_eq(r["status"], "warn",
                               "缺 1 章节应判 warn（不阻断）")
                self.assert_eq(r["missing"], ["预期成果"],
                               "缺 1 章节应精确报出缺失项")

                make("two-missing",
                     "# t\n## 〇、产出定位\nx\n## 一、立项依据\nx\n"
                     "## 二、研究内容\nx\n## 三、研究方案\nx\n")
                r = g.check_proposal("two-missing")
                self.assert_eq(r["status"], "fail",
                               "缺 2 章节应判 fail（阻断）")

                make("ooo",
                     "# t\n## 〇、产出定位\nx\n## 二、研究内容\nx\n"
                     "## 一、立项依据\nx\n## 三、研究方案\nx\n"
                     "## 四、特色与创新\nx\n## 五、预期成果\nx\n")
                r = g.check_proposal("ooo")
                self.assert_eq(r["status"], "fail",
                               "顺序错乱应判 fail")
                self.assert_eq(r["out_of_order"], True,
                               "顺序错乱应被检出")

                # 生产实际架构：5 模块 + full_review 骨架
                prod_shape = (
                    "# t\n## （一）立项依据\nx\n## （二）研究内容\nx\n"
                    "## （三）研究方案、特色与创新、预期研究成果\nx\n"
                    "## 整体一致性审查\n### 一、主线论证链\nx\n"
                    "### 二、章节衔接点\nx\n### 三、跨章节统一口径表\nx\n"
                    "## 参考文献检验\nx\n"
                )
                make("prod", prod_shape)
                r = g.check_proposal("prod")
                self.assert_eq(r["out_of_order"], False,
                               "full_review 骨架不得造成顺序假阳性")
                self.assert_eq(r["present"],
                               ["立项依据", "研究内容", "研究方案",
                                "特色与创新", "预期成果"],
                               "合并式标题应展开出全部章节")
                self.assert_eq(r["missing"], ["产出定位"],
                               "生产架构仅缺产出定位")

                # ---------- 4. 文件选择 ----------
                d = make("stale", compliant)
                (d / "proposal-draft-r7.md").write_text(
                    "# stale\n## 只有一节\nx\n", encoding="utf-8")
                r = g.check_proposal("stale")
                self.assert_eq(r["file"].split("/")[-1], "proposal-draft.md",
                               "live 正文存在时应优先读 live，而非陈旧备份")
                self.assert_eq(r["status"], "pass",
                               "陈旧备份不得影响判定结果")

                # 回退路径：无 live 正文时按最大轮号取备份
                d2 = g.OPT_DIR / "noback" / "04_proposal"
                d2.mkdir(parents=True, exist_ok=True)
                (g.OPT_DIR / "noback" / "00_research_idea.md").write_text("idea")
                for n in (2, 10, 9):
                    (d2 / f"proposal-draft-r{n}.md").write_text(
                        compliant, encoding="utf-8")
                r = g.check_proposal("noback")
                self.assert_eq(r["file"].split("/")[-1], "proposal-draft-r10.md",
                               "无 live 正文时应按最大轮号取备份（r10 而非字典序 r9）")

                self.assert_eq(
                    g._backup_round(Path("proposal-draft-r12.md")), 12,
                    "轮号解析正确")
                self.assert_eq(
                    g._backup_round(Path("proposal-draft.md")), -1,
                    "非备份文件轮号返回 -1")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
                g.ROOT, g.OPT_DIR, g.DRAFTS_DIR, g.PR_DIR = orig

            # ---------- 5. 反向断言：复刻旧实现必然误报 ----------
            def old_classify(title):
                for std_name, syns in g.SYNONYMS.items():
                    for s in syns:
                        if s in title:
                            return std_name
                import re as _re
                m = _re.match(r"^([〇零一二三四五六七八九十]+)、", title)
                if m:
                    return {
                        "〇": "产出定位", "零": "产出定位",
                        "一": "立项依据", "二": "研究内容",
                        "三": "研究方案", "四": "特色与创新",
                        "五": "预期成果",
                    }.get(m.group(1), "其他")
                return "其他"

            # 反例 1：合并式标题旧实现只取首个命中项
            merged_title = "（三）研究方案、特色与创新、预期研究成果"
            self.assert_eq(
                old_classify(merged_title), "研究方案",
                "旧实现对合并式标题只返回首个命中项——反例成立")
            self.assert_eq(
                len(g._classify_h2_all(merged_title)), 3,
                "新实现应展开出 3 个章节——正例成立")
            self.assert_true(
                old_classify(merged_title) != g._classify_h2(merged_title),
                "新旧实现必须给出相反结论，确保本测试不是自证绿")

            # 反例 2：骨架序号标题旧实现误判为标准章节
            # 旧实现按「关键词优先 + 中文数字兜底」判定，骨架标题的括号补充
            # 说明里含「研究内容」→ 关键词先命中 → 误判为研究内容。
            skeleton = "一、主线论证链（核心问题→研究内容→方案如何回应）"
            self.assert_eq(
                old_classify(skeleton), "研究内容",
                "旧实现把 full_review 骨架误判为标准章节——反例成立")
            self.assert_eq(
                g._classify_h2(skeleton), "其他",
                "新实现不误判骨架标题——正例成立")
            self.assert_true(
                old_classify(skeleton) != g._classify_h2(skeleton),
                "骨架误判的新旧结论必须相反")
            # 无括号补充说明的骨架标题同样不得被序号兜底误判
            self.assert_eq(
                old_classify("三、跨章节统一口径表"), "研究方案",
                "旧实现把「三、跨章节统一口径表」误判为研究方案——反例成立")
            self.assert_eq(
                g._classify_h2("三、跨章节统一口径表"), "其他",
                "新实现不误判——正例成立")

            # 反例 3：旧实现读备份而非 live 正文
            # 行为级断言：构造「live 正文合规 + 备份不合规」的目录，
            # 旧实现读备份会误报 fail，新实现读 live 应判 pass。
            tmp2 = tempfile.mkdtemp(prefix="hc_structure_guard_fb_")
            try:
                orig2 = (g.ROOT, g.OPT_DIR, g.DRAFTS_DIR, g.PR_DIR)
                g.ROOT = Path(tmp2)
                g.OPT_DIR = Path(tmp2) / "research_proposals" / "optimizing"
                g.DRAFTS_DIR = Path(tmp2) / "research_proposals" / "drafts"
                g.PR_DIR = Path(tmp2) / "research_proposals" / "pending_review"
                d = g.OPT_DIR / "fb" / "04_proposal"
                d.mkdir(parents=True, exist_ok=True)
                (g.OPT_DIR / "fb" / "00_research_idea.md").write_text("idea")
                (d / "proposal-draft.md").write_text(
                    "# t\n## 〇、产出定位\nx\n## 一、立项依据\nx\n"
                    "## 二、研究内容\nx\n## 三、研究方案\nx\n"
                    "## 四、特色与创新\nx\n## 五、预期成果\nx\n",
                    encoding="utf-8")
                (d / "proposal-draft-r7.md").write_text(
                    "# stale\n## 只有一节\nx\n", encoding="utf-8")
                r = g.check_proposal("fb")
                self.assert_eq(r["status"], "pass",
                               "旧实现会读 r7 备份误报 fail，新实现读 live 判 pass")

                def old_latest(prop_dir):
                    drafts = sorted((prop_dir / "04_proposal").glob(
                        "proposal-draft-r*.md"))
                    return drafts[-1] if drafts else None

                old_pick = old_latest(g.OPT_DIR / "fb")
                self.assert_eq(old_pick.name, "proposal-draft-r7.md",
                               "旧实现选中备份——反例成立")
                self.assert_eq(
                    g._latest_proposal_file(g.OPT_DIR / "fb").name,
                    "proposal-draft.md",
                    "新实现选中 live 正文——正例成立")
            finally:
                shutil.rmtree(tmp2, ignore_errors=True)
                g.ROOT, g.OPT_DIR, g.DRAFTS_DIR, g.PR_DIR = orig2

        finally:
            shutil.rmtree(env, ignore_errors=True)


if __name__ == "__main__":
    import time

    suite = StructureGuardCalibrationTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    summary = suite.summary()
    print(f"\n=== {summary['name']} ===")
    for r in summary["results"]:
        mark = "✓" if r.passed else "✗"
        print(f"  {mark} {r.name}")
        if not r.passed and r.msg:
            print(f"      {r.msg}")
    print(f"\n通过 {summary['passed']}/{summary['total']}  "
          f"耗时 {round(time.time() - t0, 3)}s")
    sys.exit(0 if summary["failed"] == 0 else 1)
