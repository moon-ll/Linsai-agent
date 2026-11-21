---
title: "2025-2506.13063-high-harmonic-generation-in-solids-interplay-between-defect"
type: "papers"
created: "2026-11-01T16:13:10Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["2310.17007", "固体HHG"]
source_raw: "2025-2506.13063-high-harmonic-generation-in-solids-interplay-between-defect.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
---

• 我先读取原始文献和 skill 规范。

• 无法蒸馏——按纪律跳过，输出失败报告而非编造内容。

  ## 蒸馏结果：SKIP（拒绝落盘）

  **raw 路径**：`raw/papers/2025-2506.13063-high-harmonic-generation-in-solids-interplay-between-defect.md`
  **arxiv_id**：2506.13063

  **拒绝原因（三重核验，均为硬证据）**：

  1. **raw 条目本身是占位条目**：正文仅一行——"占位条目：本次检索未获得独立可核实的新文献 ID，建议由系统去重阶段剔除"。`abstract` 字段为空，无任何可蒸馏的正文内容。
  2. **arxiv_id 与标题严重不符**：arXiv 2506.13063 实为计算病理学论文 PRISM2（Vorontsov 等，病理基础模型），与"固体 HHG / 缺陷态与能带结构"完全无关。条目元数据（作者字段也写"see 2310.17007 companion works"）不可核实。
  3. **无全文可回退**：`_text_cache` 无对应全文（raw 也标 `has_pdf: false`）；联网检索该标题无独立可核实的对应论文。

  **处置依据**：
  - literature-reading skill §四.3「无法核实的元数据保持原样并标注，绝不填充」——按五要素写一页只能是编造，违反数值/挂靠纪律。
  - raw 条目自带的系统建议即"由去重阶段剔除"——这正是它该走的路，而非蒸馏入库。
  - kb_distill 契约「单篇失败跳过不中断批次」。

  **建议后续动作（供编排层参考）**：
  - 本页不计入蒸馏完成数；
  - 将 raw 条目转交 `kb_merger.py --dedup-papers` / 去重清理流程剔除，或按其 `status_history` 标注为 `unverifiable` 隔离，避免反复进入蒸馏工作清单消耗 worker 轮次（此条目已在 `used_by_proposals` 中挂有课题，剔除前建议先核对该课题的文献引用是否需要替换）。

<!-- linsai-wikilinks -->
## 关联概念

- [[2310.17007]]
- [[固体HHG]]
<!-- /linsai-wikilinks -->
