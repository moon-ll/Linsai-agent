• 我先读取五个章节文件，然后按 researcher 职责做定点核查。

• 再读 full_review.md 完成核查输入。

• 核查完成，findings 已写入 `research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/06_panel/panel-researcher-findings.md`。

  要点：

  **遗留问题核对**：本轮无历史遗留靶子。作为替代，对跨章口径表 7 组禁用旧值/旧表述做了全文 grep——**零命中**，正文 canonical 表述全部正确落位（强度换算、Zhao [18]/[21] 归属、χ⁽³⁾ 归属、覆盖概率口径、WIPM 全称、[5]/[23]/[34] 刊版保留均可确认）。

  **主动核查（researcher 范围）**：
  - 数值独立复算全部通过：I = ½cε₀E₀² 换算链、误差 RSS 合成（0.055/0.155/0.115）、σ 倍数（1.29/1.74/3.2/4.3）、时序 RSS（94/117 as）、分区矩阵全部落点、Bi₂Se₃ BZ 面积 2.7 Å⁻²、WS₂ 增量 47%。
  - 文献抽查：Crossref API 实查 6 条 DOI（[9][14][21][32][17][30]），卷期页与首作者全部吻合；预印本 † 标记与表头声明逐条对账一致。

  **新发现 4 条**（0 critical / 0 high / 2 medium / 2 low）：
  - P1（medium，scheme §2.2(c)）："20–60 eV（波长约 20–60 nm）"波长换算颠倒，20 eV 实为 62 nm，与下文"60 eV 端（21 nm）"自相矛盾——唯一的事实性错误，建议本轮修复。
  - P2（medium，rationale §3）：覆盖概率"90–96%"未注明单侧口径，双侧口径下是 80–92%。
  - P3（low，scheme §2.1(b)）：2 μm 端 5.6 分钟采集时间对应的延迟点数未交代，换算链缺一环。
  - P4（low，rationale 首段）：ℏΩ_R "0.3–5 eV" 区间的 d_cv 取值依据未交代。