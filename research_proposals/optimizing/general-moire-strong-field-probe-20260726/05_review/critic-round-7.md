# 对抗评审报告（第 7 轮 — 参考文献专项检验）

## 元信息
- 申请书：general-moire-strong-field-probe-20260726
- 项目类型：general（面上）
- 评审聚焦：参考文献检验（格式、编号一致性、相关性、数量、时效性、缺失引用）
- 评审日期：2026-08-05
- profile：critic

## 综合评分
0.79 / 1.00

本轮参考文献总体质量良好，30 篇文献覆盖了理论奠基、实验原标定、反演方法学、调控先例、关联态证据五大维度，时效性高（53.3% 为 2024-2026 文献），DOI 完整度 93%（27/29 + 1 arXiv + 1 路线图）。**但本轮发现 2 个 critical 级问题**（编号 17 重复 + 编号 6 格式不一致）+ 3 个 medium 级问题（5 篇标注"备选"但正文未引用、ikeda 映射表位置声称错误、changelog 自指矛盾）。

## 维度评分
| 维度 | 权重 | 得分 | 问题数 |
|------|------|------|--------|
| 严谨性（rigor） | 0.5 | 0.70 | 4 |
| 完整性（completeness） | 0.5 | 0.88 | 2 |

**严谨性扣分原因**：(1) 编号 17 在 §3 与 §4 重复使用（critical 级别，引文编号体系崩塌）；(2) 编号 6 格式不一致（无 `[CITE:]` 标签且无加粗），与其他 1-5、7-29 不一致；(3) ikeda_arxiv_2020 在引文—使用位置映射表中声称"§三.1 历史脉络"，但 scheme.md 的 §3.1 实际未引用该文献（仅 rationale.md 用了 1 次），位置声称与实际不符。

**完整性扣分原因**：(1) 5 篇文献（bistritzer_macdonald_pnas_2011、xu_morimoto_nat_rev_phys_2021、pisanty_prl_2019、vampa_nature_2015、wang_chu_liu_cps_2023）出现在参考文献列表和引文—使用位置映射表中，但正文三个文件（rationale.md / content.md / scheme.md）均未引用——这些"备选/远期展望"文献虽有意为之（保留作背景参考），但未在正文做出任何暗示性引用的仍显冗余；(2) zhang_nat_mater_2023 同样正文未引用，标注为"备选/扩展支撑"，作为"三方佐证"中的第三篇但未实际使用。

## 问题清单

### [critical] numbering — 编号 17 在 §3 与 §4 重复使用
- **位置**：references.md 第 55 行（§3 实验方法与产额标定）与第 61 行（§4 反演方法学与 QGT）
- **问题**：两个完全不同章节的文献均使用了编号 17。§3 中编号 17 是 `[CITE:yamada_salmon2_2026]`，§4 中编号 17 是 `[CITE:hu_meng_pnas_2024]`。NSFC 评审专家在按编号检索时会直接撞上重复，无法定位文献。这是 r14 新增 yamada_salmon2_2026 时未对后续编号做平移造成的：yamada 加入 §3 后，§3 应新增一条使后续全部编号顺延，但只改了 §3 的数量（4→5），未将 §4 的 hu_meng_pnas_2024 改为 18、bauer_hansen 改为 19、prj_2024_2dberry 改为 20、pisanty_prl_2019 改为 21。
- **建议**：将 §4 的 hu_meng_pnas_2024 编号由 17 改为 17（合并到 §3？不合适），更稳妥的做法：将 §3 的 yamada_salmon2_2026 编号改为 17（当前已是 17），§4 的 hu_meng_pnas_2024 编号改为 18，bauer_hansen_prl_2018 改为 19，prj_2024_2dberry 改为 20，pisanty_prl_2019 改为 21——后续 §5/§6/§7 编号全部顺延 1 位（即 §5 从 21 改为 22... 直至 §7 的 29 改为 30）。同时更新正文三个文件中可能出现的"编号 N"行内引用（核查结果显示正文未直接使用编号，只用 `[CITE:]` 标签，所以正文无需修改，但需确认映射表的"§X.X"位置描述准确）。
- **action**：rewrite（将 §4 起所有编号平移 1 位）

### [critical] format — 编号 6 的格式与 1-5、7-29 不一致
- **位置**：references.md 第 21 行（编号 6）
- **问题**：编号 6 是无 `[CITE:]` 标签的 2026 路线图（Valleytronics in 2D Materials Roadmap, arXiv:2603.01427），但其格式与其他条目不一致：
  - 其他条目统一为 `数字. **[CITE:xxx]** 作者. *标题*. **期刊 卷, 页 (年)**. DOI: ...`
  - 编号 6 是 `6. *Valleytronics in 2D Materials Roadmap*. arXiv:2603.01427 (2026). ...`，无 `[CITE:]` 标签、无作者署名（综合路线图确实可能无单一作者）、无期刊卷期、无 DOI、也未加粗期刊名
- **建议**：要么删除此路线图（占位价值不高），要么补全格式——例如：`6. *Valleytronics in 2D Materials Roadmap*. **arXiv:2603.01427 (2026)**.` 并明示"综合路线图，无单一作者"。至少应在格式说明中明确标注该条目是"格式例外"——如在条目开头加 `(路线图, 无 DOI, 无 [CITE:] 标签)` 注释，使评审专家可识别。
- **action**：rewrite（统一格式）

### [medium] orphan_cite — 5 篇文献在 references.md 中存在但正文三个文件均未引用
- **位置**：references.md 引文—使用位置映射表及 §1-§7 各组
- **问题**：以下 5 篇文献在 references.md 中有完整条目，且在引文—使用位置映射表中声明了"§X.X（备选）"位置，但核查显示 rationale.md / content.md / scheme.md 三个正文文件中均无实际 `[CITE:]` 标签出现：
  1. `bistritzer_macdonald_pnas_2011`：映射表声明"§三.2 第二层（备选）"
  2. `xu_morimoto_nat_rev_phys_2021`：映射表声明"§三.4（备选） / §一.1 引言延展"
  3. `wang_chu_liu_cps_2023`：映射表声明"§三.4（备选） / §一.1 国内协同"
  4. `pisanty_prl_2019`：映射表声明"§三.4（备选，远期展望） / §三.5 创新点 3"
  5. `vampa_nature_2015`：映射表声明"§三.2（备选/历史奠基） / 手册 §3B.2"
  6. `zhang_nat_mater_2023`：映射表声明"§三.4（备选）/ §二.2 关联材料边界的扩展支撑"（实际也被"三方佐证"提法引用为依据，但正文未直接 `[CITE:]`）
- 这些"备选"文献占据总文献数的 6/30 = 20%。NSFC 评审专家若按映射表核查会找不到引用，给出"参考文献冗余/未实际使用"的质疑。
- **建议**：方案 A（推荐）：在正文相应章节中至少添加 1 处 `[CITE:]` 引用，使"备选"标注与实际使用一致——例如 §1.1 末尾对"光 Floquet 工程"与"光致相变"的国际路线图综述补 `[CITE:xu_morimoto_nat_rev_phys_2021]`、`[CITE:wang_chu_liu_cps_2023]`；§1.4 末尾对"莫尔能带理论奠基"补 `[CITE:bistritzer_macdonald_pnas_2011]`；§3.4 末尾对"OAM-HHG 远期展望"补 `[CITE:pisanty_prl_2019]`；§3.2 R1 末尾对"HHG 重碰撞经典方法"补 `[CITE:vampa_nature_2015]`；§1.2 反演段对"三方佐证"的第三篇补 `[CITE:zhang_nat_mater_2023]`。
- **建议**：方案 B：在引文—使用位置映射表中明确标注"⚠ 正文未直接引用，仅作背景知识保留"，并考虑从 references.md 中删除 2-3 篇与正文关联最弱的（如 vampa_nature_2015、pisanty_prl_2019——这两篇分别只是"HHG 重碰撞经典方法"和"OAM 远期展望"，未在论证链中起承重作用），将总文献数降至 27-28 篇以提升密度。
- **action**：research（确认这些文献是否真的无用）+ rewrite（正文添加引用 或 移除冗余文献）

### [medium] consistency — ikeda_arxiv_2020 映射表位置声称与实际不符
- **位置**：references.md 引文—使用位置映射表（ikeda_arxiv_2020 行）
- **问题**：映射表声称"§一.2 / §三.1 历史脉络"，但核查显示：
  - `scheme.md` 中 `[CITE:ikeda_arxiv_2020]` 出现次数：**0**
  - `content.md` 中出现次数：**0**
  - `rationale.md` 中出现次数：**1**（仅 §一.2）
  即 ikeda 仅在 rationale.md 中被引用一次，且未出现在 scheme.md 的 §3.1 中。"§三.1 历史脉络"的声明是 r10 时期延续下来的过时映射。
- **建议**：将映射表的 ikeda_arxiv_2020 行的"已引用位置"列更新为"§一.2 / 手册 §3B.2（待补）"——保持核验准确性。
- **action**：rewrite

### [low] self_reference — changelog 自指矛盾
- **位置**：references.md r14 changelog 第 3 段
- **问题**：r14 changelog 中第 3 点写道"`[CITE:xxx]` 占位标签（r10 遗留待办 2）已替换为 `[CITE:ghimire_natphys_2011]` 并完成核验"。但 r10 changelog 第 1 段已声明"§1 引言段落由 r9 的'短句罗列'扩展为 r10 的'主题递进'... 本轮未触动其它章节文件"，r10 没有声明"已替换 xxx 占位标签"。r14 changelog 的"r10 遗留待办 2"用语暗示 r10 已声明替换但未执行，存在 changelog 之间的逻辑不一致。
- **建议**：r14 changelog 应明确为"本轮新增事项：占位标签 [CITE:xxx] 已从引文—使用位置映射表全量清理"。建议简化表述。
- **action**：rewrite（changelog 文字微调）

### [low] inline_doi — Nikola 2021 缺少页码（Erratum 特殊处理）
- **位置**：references.md 编号 22 `[CITE:nikola_nature_2024]`（应为 nikola_nature_2021）
- **问题**：Nikola 2021 的描述是 "Nature 600, E10 (2021)"，未给出页码范围"E10"是单页 Erratum 的标准缩写，本身是完整页码，但与其它条目的格式（如 Nature Materials 23, 844–855）格式不一致。需在条目内说明"E10 系 Erratum（更正）"——已实现（条目注释中明确）。
- **建议**：保持现状即可，无需修改。
- **action**：verify（确认当前描述已充分）

### [low] metadata — 编号 5 页码 230202 与编号 13 页码 086103 是 article ID 而非页码
- **位置**：references.md 编号 5（wang_chu_liu_cps_2023）与编号 13（kozak_apl_2023）
- **问题**：编号 5 期刊《物理学报》使用文章编号 230202（2023 年第 72 卷第 23 期 article 230202），编号 13 APL Photonics 使用文章编号 086103——这都是物理/应用物理期刊的现代 article ID 格式（非页码），但与其它条目"卷, 页–页"格式不一致。审稿人可能误以为是页码。
- **建议**：在条目注释中明示"文章编号"，例如"Physica Sinica 72(23), 230202 (2023)"——已在条目中显示"(23)"issue 号，但 article ID 230202 需读者熟悉中国物理学报惯例。
- **action**：verify（建议在条目末尾添加"(文章编号)"小字注释以避免误读，但优先级低）

## 时效性分析
- 2024-2026 文献：**16 篇**（53.3%），含 13 篇 2024 + 1 篇 2025 + 2 篇 2026
- 2020-2023 文献：**8 篇**（26.7%）
- 2010-2019 文献：**6 篇**（20.0%）
- arXiv 预印本：**3 篇**（ikeda_arxiv_2020, joya_arxiv_2026, yamada_salmon2_2026 + 1 篇 2026 路线图 arXiv:2603.01427）
- DOI 完整度：**93%**（27/29 带标签文献有 DOI；arXiv 3 篇标 "无 DOI"）
- 评估：时效性优秀，无过于陈旧文献（最早 2011 年 Bistritzer/Cao 等奠基工作合理），近 3 年文献占比超过 NSFC 面上惯例。

## 编号一致性双向核查
| 检查项 | 结果 |
|--------|------|
| 正文引用 [CITE:] 但 references.md 缺失 | 0 个 ✓ |
| references.md 列出但正文未引用 | 6 个（5 个"备选" + zhang_nat_mater_2023） ⚠ |
| 编号 1-29 唯一性 | ✗ 编号 17 重复使用 |
| 编号连续性 | 1-16、18-29 连续 ✓，17 重复 |
| 编号 30 是否存在 | 不存在（与"30 篇"统计一致） |

## 引用相关性评估
30 篇文献均与本课题科学问题强相关：
- **莫尔物理综述与方向奠基**（6 篇）：zhang_su_wang, heide, wang_yu_matter, xu_morimoto, wang_chu_liu, 路线图 ✓
- **莫尔超晶格 HHG 理论**（6 篇）：joya, molinero, mrudul, ikeda, bistritzer, cao ✓
- **实验方法与产额标定**（5 篇）：kozak, qiu, hu_meng_prl, zhang_nat_mater, yamada_salmon2 ✓
- **反演方法学与 QGT**（4 篇）：hu_meng_pnas, bauer_hansen, prj_2dberry, pisanty ✓
- **光 Floquet 工程**（4 篇）：xu_zhou_npj_qm, nikola, tyulnev, zhou ✓
- **关联绝缘态**（3 篇）：lian, xu_natcomm, amato ✓
- **HHG 理论基础**（2 篇）：vampa, ghimire ✓

每条参考文献均与申请书科学问题高度相关，无无关引用。✓

## 缺失引用评估
申请书中的核心论断均有文献支撑：
- "MoS₂ 单层 HHG 截止阶次 7-11 阶" → kozak_apl_2023 ✓
- "magic-angle TBG 计算规模 ~10⁸ 核时" → molinero_optica_2024 + yamada_salmon2_2026 ✓（双锚定）
- "光致熔化 > 20% HHG 跳变" → nikola_nature_2021 ✓
- "莫尔势 C₃ 对称性" → caonature_2018 ✓
- "TMDC 莫尔 HHG 多体 GW 增强" → qiu_natcomm_2024 ✓
- "莫尔势反演的多维正则化" → hu_meng_pnas_2024 + bauer_hansen_prl_2018 ✓
- "光 Floquet 调制 > 30%" → nikola_nature_2021 ✓
- "黑磷 Floquet 能带工程" → zhou_nature_2023 ✓
- "WS₂/WSe₂ 关联态" → lian_natphys_2024 + xu_natcomm_2024 ✓
- "谐波标度 α ≈ 2.5" → ghimire_natphys_2011 ✓

未发现重要论断缺少文献支撑。✓

## 引文数量
- 总文献数：**30 篇**（29 篇带 `[CITE:]` 标签 + 1 篇无标签 2026 路线图）
- NSFC 面上惯例区间：**15-30 篇**（区间上沿）
- 评估：在区间内但处于边界，5 篇"备选"文献若不主动用上则可能被评审指"冗余"，建议下一轮要么添加正文引用、要么从 references.md 中移除 2-3 篇以降至 27-28 篇

## 对抗结论

本轮参考文献检验发现：
- **Critical 级 2 个**：编号 17 重复（必须立即修复）+ 编号 6 格式不一致
- **Medium 级 2 个**：6 篇"备选"文献正文未引用 + ikeda 映射表位置声称错误
- **Low 级 3 个**：changelog 自指矛盾、Nikola 2021 页码格式、article ID 与页码混淆
- 合计：**7 个问题**

相比上一轮（r6/9/10/14）修复进展：
- ✓ 上一轮强调的"全部 verify 标注"已完成
- ✓ 上一轮强调的"Vampa/Ghimire 页码补全"已完成
- ✓ 上一轮强调的"jojya 主题归属调整"已完成
- ✗ 上一轮强调的"占位标签 [CITE:xxx] 清理"在 r14 changelog 中声称已完成，但实际 references.md 第 55-61 行（hu_meng_pnas_2024 编号错误）反映 r14 整体编号重新整理时只新增了 §3 而未对 §4 起的所有编号做平移
- ✗ **新增**：编号 17 重复是 r14 新增 yamada 引入的回归性错误

**是否达到输出标准：否**
- 原因：(1) critical 级编号错误（编号 17 重复）必须修复后再提交；(2) critical 级格式不一致（编号 6）影响专业感；(3) 6 篇"备选"文献中至少 3-4 篇应在正文做出引用或从列表移除，否则评审会质疑参考文献冗余。

**返工优先级**：
- **P0**（critical 必修）：编号 17 修复 + 编号 6 格式统一
- **P1**（medium 应修）：5-6 篇"备选"文献在正文添加引用 或 从 references.md 移除
- **P2**（low 可选）：ikeda 映射表位置更新 + changelog 文字微调 + article ID 注释

**下一轮评审建议聚焦**：
- 修复后再次确认 references.md 编号唯一性（1-29 或 1-30）
- 6 篇"备选"文献的去留决策（补引用 vs 移除）
- 引文—使用位置映射表与正文实际引用状态的最终一致性核验

## 评分
创新性：0.85
可行性：0.85
严谨性：0.70
完整性：0.88
综合评分：0.79