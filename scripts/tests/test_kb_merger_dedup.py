#!/usr/bin/env python3
"""
test_kb_merger_dedup.py — 论文页双世代去重回归测试（v6.10.52）

覆盖缺陷（2026-09-25 知识库体检实锤）：
    wiki/papers 同一 arXiv 论文两套页面并存（旧代 slug 命名 vs 新代裸 id），
    561 组重复占 54%。既有 detect_merge_pairs 按 title 分组对这类重复失明
    （两代 title 不同），_entity_key 按文件名首段取键还会把同名组误判为
    "不同实体"排除。修复按 arxiv_id 文件名分组 + slug 代为主 + 确定性
    附录并置（零 LLM）。

注意：
    仅验证纯逻辑（id 解析 / 分组 / 选主），不触发 LLM 与磁盘写入。
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from test_runner import TestSuite, create_isolated_env


class KbMergerDedupTests(TestSuite):
    def __init__(self):
        super().__init__("kb_merger 论文双世代去重测试")
        self.tmp_root = None

    def setup(self):
        self.tmp_root = create_isolated_env()

    def teardown(self):
        pass

    def run_tests(self):
        from kb_merger import (
            extract_arxiv_id,
            detect_paper_generation_groups,
            _pick_paper_primary,
            _entity_key,
        )

        # 1. arxiv id 文件名解析：裸 id / slug 代 / doi 排除
        self.assert_eq(extract_arxiv_id("1006.1827"), "1006.1827",
                       "裸 id 解析")
        self.assert_eq(extract_arxiv_id("1006.1827v2"), "1006.1827",
                       "裸 id 带版本号解析")
        self.assert_eq(
            extract_arxiv_id("2010-1006_1827-attosecond-streaking-enables"),
            "1006.1827", "slug 代下划线 id 解析")
        self.assert_eq(
            extract_arxiv_id("2021-1910.07893-collective-excitations"),
            "1910.07893", "slug 代点号 id 解析")
        self.assert_eq(
            extract_arxiv_id("2025-s41566-025-01700-6-attosecond-virtual"),
            "", "doi 源文件名无 arxiv id")
        self.assert_eq(extract_arxiv_id("RABBITT"), "", "概念名返回空")

        # 2. 分组检测：同 id 聚组 / stub 排除 / 单页不成组
        fake_pages = [
            {"path": "wiki/papers/1006.1827.md", "merged_into": ""},
            {"path": "wiki/papers/2010-1006_1827-attosecond-x.md", "merged_into": ""},
            {"path": "wiki/papers/1905.10109.md", "merged_into": ""},
            {"path": "wiki/papers/2020-1905_10109-properties-of-bsv.md", "merged_into": ""},
            {"path": "wiki/papers/old.md", "merged_into": "wiki/papers/other.md"},
            {"path": "wiki/papers/2601.12345.md", "merged_into": ""},
        ]
        groups = detect_paper_generation_groups(fake_pages)
        ids = sorted(g["arxiv_id"] for g in groups)
        self.assert_eq(ids, ["1006.1827", "1905.10109"],
                       "同 id 双世代聚组，stub 排除，单页不成组")

        # 3. 选主：slug 代优先于裸 id 代（即使裸 id 正文更长）
        fake_getter = {
            "wiki/papers/1006.1827.md": {
                "frontmatter": {"title": "1006.1827"},
                "body": "x" * 5000,
            },
            "wiki/papers/2010-1006_1827-attosecond-x.md": {
                "frontmatter": {"title": "Attosecond streaking…"},
                "body": "y" * 100,
            },
        }
        primary = _pick_paper_primary(
            ["wiki/papers/1006.1827.md",
             "wiki/papers/2010-1006_1827-attosecond-x.md"],
            lambda p: fake_getter.get(p),
        )
        self.assert_eq(primary, "wiki/papers/2010-1006_1827-attosecond-x.md",
                       "slug 代优先为主页面（与蒸馏产出命名一致）")

        # 4. 全裸 id 组回退到正文最长者（防御：不应抛异常）
        primary2 = _pick_paper_primary(
            ["wiki/papers/a1.00001.md", "wiki/papers/1006.1827.md"],
            lambda p: fake_getter.get(p),
        )
        self.assert_eq(primary2, "wiki/papers/1006.1827.md",
                       "无 slug 代时回退正文最长者")

        # 5. v7.2.48：实体键不得退化为年份（slug 代同标题跨论文误合并）
        # 缺陷：_entity_key 按 "-" 取首段 → slug 代 `2024-2406_14320-…`
        # 取到纯年份 `2024`，同年所有论文页共用一个键 → 实体一致性守卫
        # 对同年同名论文彻底失效 → kb_merge 把两篇不同论文并成一篇
        # （10-26 12h 实测 2406.14320 被并入 2407.16350）。
        self.assert_eq(
            _entity_key("2024-2406_14320-many-body-enhancement-of-high"),
            "arxiv:2406.14320", "slug 代实体键取 arxiv id 而非年份")
        self.assert_eq(
            _entity_key("2024-2407_16350-many-body-enhancement-of-high"),
            "arxiv:2407.16350", "同年另一篇论文实体键互不相同")
        self.assert_true(
            _entity_key("2024-2406_14320-many-body-enhancement-of-high")
            != _entity_key("2024-2407_16350-many-body-enhancement-of-high"),
            "同年两篇不同论文的实体键必须不同（守卫据此拦截误合并）")
        self.assert_eq(
            _entity_key("2010-1006_1827-attosecond-streaking-enables"),
            "arxiv:1006.1827", "裸 id 代与 slug 代同论文实体键一致")
        self.assert_eq(
            _entity_key("1006.1827"), "arxiv:1006.1827",
            "裸 id 代实体键取 arxiv id")
        # 模板标题组（非 arXiv 命名）不受影响，仍走旧启发式
        self.assert_eq(
            _entity_key("general-moire-strong-field-probe-20260726"),
            "general-moire", "模板标题组实体键回退旧启发式")
        self.assert_eq(
            _entity_key("讨论-20260619-记录"), "讨论-20260619",
            "中文模板标题组实体键回退旧启发式")

        # 6. v7.2.48：arXiv 新式字母数字 id 同样不得退化为年份
        self.assert_eq(
            extract_arxiv_id("2026-9jcm-8gd8-rainbow-retrieval"),
            "9jcm-8gd8", "新式字母数字 id 的 slug 命名解析")
        self.assert_eq(
            extract_arxiv_id("2607.23652"), "2607.23652",
            "新式字母数字 id 的裸命名解析")
        self.assert_eq(
            _entity_key("2026-9jcm-8gd8-rainbow-retrieval"),
            "arxiv:9jcm-8gd8", "新式 id 实体键取 id 而非年份")
        self.assert_true(
            _entity_key("2026-2403_05073-rainbow-retrieval")
            != _entity_key("2026-9jcm-8gd8-rainbow-retrieval"),
            "新式 id 与旧式 id 实体键不同（同名但不同 id 的论文不得互相合并）")

        # 7. v7.2.49：紧凑序号代 `<年份>-<YYMM><NNNNN>-slug` 必须归一到
        # 同一 arxiv id 空间（否则与 slug 代被判为不同实体 → 真重复漏合并）
        self.assert_eq(
            extract_arxiv_id("2026-260723652-carrier-envelope-phase-control"),
            "2607.23652", "紧凑序号代解析为 YYMM.NNNNN")
        self.assert_eq(
            _entity_key("2026-260723652-carrier-envelope-phase-control"),
            "arxiv:2607.23652", "紧凑序号代实体键取 arxiv id 而非年份")
        # 与 slug 代同 id → 实体键必须一致（真重复可被识别并合并）
        self.assert_eq(
            _entity_key("2026-2607_23652-carrier-envelope-phase-control"),
            "arxiv:2607.23652", "紧凑序号代与 slug 代同论文实体键一致")
        self.assert_eq(
            _entity_key("2607.23652"), "arxiv:2607.23652",
            "紧凑序号代与裸 id 代同论文实体键一致")

        # 8. v7.2.49：analyses 代 `<arxivid>-slug` 必须与裸 id 代归一
        self.assert_eq(
            extract_arxiv_id("2407.19609-attosecond-transient-grating"),
            "2407.19609", "analyses 代解析出 arxiv id")
        self.assert_eq(
            _entity_key("2407.19609-attosecond-transient-grating"),
            "arxiv:2407.19609", "analyses 代实体键与裸 id 代一致")

        # 9. v7.2.49：反例——紧凑序号代不得与「不同 id 的同名论文」合并
        self.assert_true(
            _entity_key("2026-260723652-carrier-envelope-phase-control")
            != _entity_key("2026-2606_20372-high-order-harmonic-generation"),
            "紧凑序号代下不同 id 的同名论文实体键必须不同")
        # 非 arXiv 命名不受影响（模板标题组仍走旧启发式）
        self.assert_eq(
            extract_arxiv_id("general-moire-strong-field-probe-20260726"),
            "", "模板标题组不解析出 arxiv id")


if __name__ == "__main__":
    import time
    suite = KbMergerDedupTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])
