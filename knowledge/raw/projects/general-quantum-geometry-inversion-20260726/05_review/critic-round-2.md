# 对抗评审报告（Round 2 · 参考文献专题）

## 元信息
| 项 | 值 |
|----|-----|
| 评审轮次 | Round 2（参考文献检验专题） |
| 项目类型 | NSFC general（面上） |
| 评审章节 | references.md + 三个正文章节 |
| 评审日期 | 2026-09-11 |
| 上一轮 | R1 评分 0.68，发现 5 critical（4 处编号—作者—内容三重错位 + 1 DOI 格式错）；本轮重点验证 R1 修复情况 |
| 评审范围 | 引文格式、引用相关性、缺失引用、引用数量、时效性；编号一致性已由预检完成 |

## 数据快照
| 指标 | 数值 |
|------|------|
| 条目总数 | 52（R1=49，本轮+3；超 30-40 标杆 12 条） |
| 1-52 编号连续 | 是 |
| 近 3 年（2024-2026）| 27/50 = 54.0%（R1=61.2%；下降 7.2 pp）|
| 预印本条目 | 23/52 ≈ 44.2%（R1=36.7%；上升 7.5 pp）|
| 正式发表条目（含 10.x 非 arXiv DOI）| 28/52 ≈ 53.8% |
| 无标识符条目 | 0（[27] Fazekas-Tosatti 1979 仍无 DOI，属合理豁免）|
| R1→R2 关键修复验证 | [12] Bauer→Cárdenas ✓；[42] DOI 修正 ✓；[26][27] 已无正文错配 ✓? ❌ |

## 综合评分
0.55 / 1.00（R1 全部 4 处 critical 编号—作者—内容错位**正文侧未同步修复**，构成 P0 红线 consistency_check / no_exaggeration；rigor 强制扣至 0.5-0.6 区间；本轮必须修复后方可进入下一轮）

## 维度评分
| 维度 | 权重 | 得分 | 问题数 |
|------|------|------|--------|
| 严谨性（rigor） | 0.50 | 0.50 | 7（6 critical, 1 low） |
| 完整性（completeness） | 0.50 | 0.60 | 5（1 critical, 3 medium, 1 low） |
| **综合** | — | **0.55** | **12** |

## 维度评分依据
严谨性 0.50：rationale.md 仍存在 4 处 critical 编号—作者—内容错位——Baykusheva→[26]、Du→[27]、Bauer→[12]、Uchida/Murakami→[12]，且本次发现 writer 仅修改 references.md 中的 [12] = Cárdenas（Bauer→Cárdenas 已修），但 rationale.md 正文叙述未同步：3 处仍写 "Bauer 等 2026 年 [12]"，2 处仍写 "Uchida、Murakami 等 2026 年 [12]"，"Baykusheva [26]" 与 "Du [27]" 各 2-3 处也未改。构成 P0 红线 consistency_check。按 v6.9.25 评分纪律，P0 红线触发 → rigor 强制扣至 0.5-0.6 区间，取 0.50。

完整性 0.60：52 条仍超 30-40 标杆 12 条（R1 已标 critical 但未压缩）；预印本 23 条占 44.2%（R1=36.7%，上升）；时效性 54% 仅勉强达 50% 门槛；正文 3 处高频引用的"Baykusheva 2026 实测 Sr₂CuO₃ 上 Floquet 调控 Hubbard 激子"在 references.md 中**仍无对应条目**（真实出处 arXiv:2601.20695）；"Du 2026 一维 Hubbard 精确对角化 doublon-holon"在 references.md 中也**仍无对应条目**（真实出处 Tao-Yuan Du PRB 2026-06-16, DOI 10.1103/n4gk-jxpc）。

---

## 锚点对比
锚点：rationale.md 中 "Baykusheva 等 2026 年 [26] 与 Du 等 2026 年 [27]"（多体 HHG 段）

benchmark：嵌入式引用要求正文作者名 + 编号 + 内容 + references.md 条目**四方严格一致**；这是 NSFC 参考文献审查最低门槛。

差距：R1 已标记该错位为 critical（报告 L65-74），writer 修复时**只改了 references.md [12] 一行**（Bauer→Cárdenas），未触动 rationale.md 正文 5 处错位叙述。当前状态是更严重的"半迁移态"：references.md 的 [12] 已变成真实论文，但正文 "Bauer 2026 [12]" 指向"一个不存在的作者+一个真实论文"，比 R1 单纯的编号错位更具误导性。这正是 memory 中"半迁移态"标准的 critical 错位模式。

锚点对比结论：差距明显

---

## 问题清单
[critical]｜rationale.md L21/29/41（5 处）｜Baykusheva→[26] 错位未修｜正文改引真实 arXiv:2601.20695（Baykusheva 等 2026）或新建 [N]｜research+rewrite
[critical]｜rationale.md L21/29/41（5 处）｜Du→[27] 错位未修｜正文改引 Du 2026 PRB（10.1103/n4gk-jxpc）或新建 [N]｜research+rewrite
[critical]｜rationale.md L41（3 处）｜Bauer→[12] 错位未修｜正文改 "Bauer" 为 "Cárdenas" 或新建独立 Bauer 条目｜rewrite
[critical]｜rationale.md L21/41（3 处）｜Uchida/Murakami→[12] 错位未修｜核实 SrCuO₂/Pr₂CuO₄ 维度对比工作真实作者链；Uchida 在 ref 表无对应条目｜research+rewrite
[critical]｜references.md 整体｜52 条仍超 30-40 标杆 12 条｜将 12 条方法学借鉴定位条目（[15][16][18][23][24][47][48][49][51][52] 等）降级附录，主列表 ≤40｜remove
[critical]｜references.md 整体｜正文高频引用的真实 Baykusheva/Du 文献未入主列表｜新增 [Baykusheva arXiv:2601.20695] 与 [Du PRB 2026] 两条目｜add
[high]｜references.md 整体｜预印本 23 条占 44.2% 超 30% 安全线｜正式发表前预印本不纳入主列表；当前 14 条 2026 年新提交预印本应明确标注 v1/v2 时序与状态｜rewrite
[medium]｜references.md L27 [13]｜arXiv:2508.00296 v1→v2 跨 12 个月异常时序｜核实 v2 实质修订内容；条目末补 "v2 2026-08-13 实质增订" 限定语｜verify+rewrite
[medium]｜references.md L25 [12]｜arXiv:2604.13901 2026-04 提交但参考文献条目无 v 标识｜补 "v1 2026-04-15 提交" 限定语与版本号｜rewrite
[medium]｜references.md L11 [7]｜实验参数 "25 fs FWHM" 与正文 21 fs/25 fs 表述未交叉｜与 scheme.md 实测参数对齐；如 21 fs 则改 21｜verify+rewrite
[low]｜references.md 整体｜格式细节：部分条目标题后冒号、卷期格式不统一｜统一为 "作者. 标题. 期刊, 卷, 页 (年). DOI:..."｜rewrite
[low]｜references.md 整体｜[27] Fazekas-Tosatti 1979 仍无 DOI/ISSN 备用溯源｜补 Philos. Mag. B ISSN 0031-8086 或 Taylor & Francis 期刊页｜rewrite

---

## 对抗结论
- 本轮发现 12 个问题（critical: 6, high: 1, medium: 3, low: 2）
- **R1 全部 4 处 critical 编号—作者—内容错位正文侧未同步修复**：writer 仅修改 references.md [12] 单行（Bauer→Cárdenas），未触动 rationale.md 正文 5 处 Baykusheva/Du/Bauer/Uchida/Murakami 错位——构成"半迁移态" critical，致评分从 R1=0.68 跌至 R2=0.55
- 相比 R1：改善 0 个（R1 标 [42] DOI 修复 ✓、R1 标 Baykusheva 真实出处已找到 ✓）；新增 6 个 critical（正文未同步 4 + 列表膨胀 + 真实文献未入表 1）
- **是否达到输出标准**：**否**——R1 全部 4 处 critical 复发 + 新增 2 项 critical，references.md 与 rationale.md 处于"半迁移态"严重错位
- 修复优先级（按对抗思维）：
  1. **最高优先级**（critical ×6）：同步 rationale.md 正文 5 处错位叙述（Baykusheva/Du/Bauer/Uchida/Murakami）+ 压缩 52→≤40 条 + 补入 Baykusheva/Du 真实文献条目
  2. **高优先级**（high ×1）：预印本占比与版本号规范化
  3. **中优先级**（medium ×3）：[13] v2 实质修订核实、[12] 版本号、scheme.md 参数对齐
  4. **低优先级**（low ×2）：格式统一、[27] ISSN 补全
- 修复完成后，预计严谨性可由 0.50 → 0.85，完整性可由 0.60 → 0.82，综合评分可由 0.55 → 0.84

## 评分
创新性：N/A
可行性：N/A
严谨性：0.50
完整性：0.60
综合评分：0.55
