# 对抗评审报告（第6轮 — 参考文献专项检验）

## 综合评分
0.83 / 1.00（参考文献专项；分维度见末尾评分块）

## 检查范围与方法
本轮专项检验参考文献章节 `04_proposal/sections/references.md` 与正文三章（`rationale.md` / `content.md` / `scheme.md`）的交叉一致性。
- 提取 `references.md` 中所有 `[CITE:标签]` 占位符：27 个标签（条目 1–28，其中条目 6 无标签 = 2026 路线图）
- 提取正文三章所有 `[CITE:标签]`：22 个不同标签（实际占位符出现 126 次）
- 程序化核验：断链、冗余、字段完整性、年份分布、主题相关性、引用频次
- 第 6 轮（critic-round-6）数据快照：rationale.md 45 处 / content.md 59 处 / scheme.md 22 处

## 维度评分

| 维度 | 权重（参考） | 得分 | 问题数 |
|------|------|------|--------|
| 严谨性（rigor） | 60% | 0.78 | critical 0, high 1, medium 2, low 1 |
| 完整性（completeness） | 40% | 0.90 | high 1, medium 2, low 1 |

## 问题清单

### [high] consistency — scheme.md 第 59 行元描述引用次数与正文实际不符
- 位置：scheme.md 第 59 行「*优化记录：2026-08-11（r11）— …保留全部 21 处 [CITE:xxx] 引用…」
- 问题：方案 §三 末尾的优化记录元描述写「保留全部 21 处 [CITE:xxx] 引用」，而正文（rationale + content + scheme 三章合算）实际占位符共 126 次，覆盖 22 个不同标签。这是 r9 时期的元数据残留，未在 r10/r11/r12 中同步更新。当评审专家据此核对时会发现数字明显不一致，可能引申出"内部自检未闭环"的质疑。
- 建议：将「21 处」改为「22 个独立文献标签、126 次占位符引用（覆盖全部 28 篇文献中的 21 篇 + 1 篇无标签 roadmap；7 篇为备选/历史奠基未直接引用）」。
- action：rewrite

### [high] completeness — 6 篇备选文献未在正文任何位置引用，需评估是否保留
- 位置：references.md 标签 → 正文
  - `[CITE:bistritzer_macdonald_pnas_2011]`（PNAS 2011，莫尔紧束缚奠基）
  - `[CITE:pisanty_prl_2019]`（PRL 2019，OAM-HHG 守恒）
  - `[CITE:vampa_nature_2015]`（Nature 2015，固体 HHG 重碰撞）
  - `[CITE:wang_chu_liu_cps_2023]`（物理学报 2023，国内 Floquet 综述）
  - `[CITE:xu_morimoto_nat_rev_phys_2021]`（Nat. Rev. Phys. 2021，光致 2D 现象综述）
  - `[CITE:zhang_nat_mater_2023]`（Nat. Mater. 2023，WSe₂/MoS₂ 莫尔相关相）
- 问题：这 6 篇在正文（rationale + content + scheme）中均未被直接引用，且 references.md 自身的"引文—使用位置映射"表也将它们统一标记为「备选（建议引用）」。NSFC 面上项目惯例下"占而不引"的文献容易被评审专家质疑为凑数或与正文割裂，尤其 `bistritzer_macdonald_pnas_2011`（莫尔能带理论奠基）在 §一.2/§一.3 论述"连续莫尔紧束缚"模型源头时未显式 cite，但 §三.2 已引用 `zhang_su_wang_nat_mater_2024` 与 `xu_zhou_npj_qm_2024` 替代，导致此奠基性工作缺席论证链。
- 建议：
  1. 必引 2 篇：`bistritzer_macdonald_pnas_2011`（莫尔能带理论奠基，R1 降阶框架源头）+ `vampa_nature_2015`（固体 HHG 重碰撞，R1 理论工具支撑）—— 这两条在 references.md 映射表内已标记「备选（建议引用）」，正好可作为 reviewer 质疑"奠基性工作缺席"时的反制证据。
  2. 可删 1–2 篇：`pisanty_prl_2019`（OAM-HHG 守恒仅在 §三.1 远期展望出现，正文未提及 OAM）+ `wang_chu_liu_cps_2023`（国内 Floquet 综述，与 `xu_morimoto_nat_rev_phys_2021` + `nikola_nature_2021` 存在功能重叠）。
  3. 视情况：`xu_morimoto_nat_rev_phys_2021`（光致 2D 现象综述可补充到 §一.2 主动调控段首句作为开篇背景），`zhang_nat_mater_2023`（WSe₂/MoS₂ 莫尔相关相可补充到 §一.3 调控空白段的"关联态存在性"佐证，呼应 `lian_natphys_2024`）。
- action：rewrite（择 2–3 篇补引，或剔除冗余）

### [medium] consistency — references.md "引文—使用位置映射表"与方案 §三 实际引用存在遗漏
- 位置：references.md 行 99–125 "引文—使用位置映射（r9 核查版）"
- 问题：映射表中 `[CITE:ghimire_natphys_2011]` 标注为「§二 / 备选（建议引用）」，但实际正文 content.md 中出现 2 次（content.md §2.3 创新点 1 引用为标度指数基线 + content.md §2.2 R2 引用为产额对比参照基准）；而映射表却将其归入"备选"。同时 `[CITE:zhang_su_wang_nat_mater_2024]` 在映射表中说"§一 / §二 / §三"，实际正文三章均出现，是合理的；但 `[CITE:nikola_nature_2021]` 映射表标注"§一 / §二 / §三 / 手册"而 scheme.md 中仅出现 1 次（§3.4 R3）。整体映射表与 r11/r12 正文状态存在 r9 遗留偏差。
- 建议：在下一轮重写中，按当前正文实际引用位置（rationale 45 处 + content 59 处 + scheme 22 处）重新生成映射表，或在 references.md 头部加一句「映射表基于 r9 重写后核查，r10/r11/r12 后续章节改动请以正文实际引用为准」。
- action：rewrite

### [medium] format — references.md 引文格式混用"作者+et al."与"作者 全部列出"
- 位置：references.md 全部条目
- 问题：作者列表长度不统一——`[CITE:kozak_apl_2023]` "Kozák, M. et al."、`[CITE:wang_yu_matter_2025]` "Wang, L., Yu, B. & Ciappina, M."（3 位全列）、`[CITE:zhang_su_wang_nat_mater_2024]` "Zhang, Y., Su, Y., Wang, L. et al."（4 位+et al.）、`[CITE:lian_natphys_2024]` "Lian, Z., Meng, Y., Wang, Y. et al."。NSFC 申请对作者列表无强制要求，但一致性原则下建议统一规则：第一作者必列，第二作者起视条目实际列出，超过 3–5 位加 et al.。
- 建议：保留原格式但在末尾加注「作者列表遵循原文署名顺序，超过 5 位时缩写为 et al.」。
- action：format only

### [medium] completeness — R3 关联态熔化关键论断"莫尔体系 Δ_CI = 5–20 meV → I_c = 8×10¹⁰–3.2×10¹¹ W/cm²"无外部引用
- 位置：rationale.md §1.4 / content.md §2.1 / §2.2 R3 / scheme.md §3.4
- 问题：申请书核心定量推导 I_c ∝ Δ_CI²（基于 ac-Stark 等效带宽调制 δW_flat ∝ E₀²）的具体数值（5/10/20 meV → 8×10¹⁰/1.6×10¹¹/3.2×10¹¹ W/cm²）来自"方法学手册 §3F.2"，但作为支撑的关键前期文献是 `amato_prb_2024`（光致关联相熔化机制）+ `nikola_nature_2021`（>30% 调制）。`amato_prb_2024` 在正文仅出现 4 次，且全部在 §二（content.md）；rationale.md 中完全未引用该条以支撑 R3 的核心论断——这会导致 reviewer 在 §一.4 科学问题 2 阅读时找不到物理源头。
- 建议：在 rationale.md §1.4 "科学问题 2" 段末增加一句 "周期性光场诱导关联相熔化的可行性已被 Amato 等 2024 [CITE:amato_prb_2024] 在顺磁体中证明"；或在 §1.5 特色 3 论证段补充该引用。
- action：add

### [low] format — §6 "Valleytronics in 2D Materials Roadmap" 无 CITE 标签但被正文未直接引用
- 位置：references.md 条目 6（2026 路线图）
- 问题：这是唯一的"无标签"参考文献，与申请书其余 27 条 `[CITE:xxx]` 格式不一致；同时正文 rationale.md §一 引言未直接 cite（仅"国际路线图"提法映射），导致该条完全悬空。若保留应至少在 rationale.md §1.1 引言末或 §一末加入引用占位符 `[CITE:valleytronics_roadmap_2026]` 并同步在 references.md 条目 6 添加标签。
- 建议：（a）为该条添加标签 `[CITE:valleytronics_roadmap_2026]` 并在 rationale.md §1.1 末添加引用；或（b）从 references.md 删除该条（与正文无直接对应）。
- action：add（推荐 a 方案，否则路线图国际定位的"独立证据"作用失效）

## 对抗结论
- 本轮发现 **6 个问题**（critical:0, high:2, medium:3, low:1）
- 相比 critic-round-5（前序轮次）：参考文献体系已基本稳定，本轮新增 1 个 high（scheme.md 元描述数字不一致）与 1 个 medium（R3 论断 `amato_prb_2024` 在 §一缺位）
- **未解决问题**：方案 §三 末尾"21 处引用"元描述沿用 r9 数据（high），与实际正文 126 处不一致 — 此为本轮最关键的"内部自检未闭环"信号
- **新增问题**：
  - high：方案 §三 末尾"21 处"数字与正文实际不一致
  - medium：R3 调控论断的 `amato_prb_2024` 在 §一缺位（rationale.md 全文未出现）
  - medium：references.md "引文—使用位置映射"表的 r9 状态与正文 r11/r12 状态不一致
  - low：2026 roadmap 路线图无标签且正文未引用
- 整体判断：参考文献体系覆盖度、时效性（2024-2026 占 50%）、字段完整性（DOI/arXiv 100% 完整）均达标；主要扣分项在"占而不引"的 6 篇备选文献 + scheme.md 元描述遗留 + §一 R3 论断引用空白，需在下一轮重点处理。

## 核查细节（附录）

### A. 字段完整性核查（28 条逐条）
| 检查项 | 通过率 |
|--------|--------|
| `[CITE:...]` 标签 | 27/28（1 条 roadmap 无标签 — 见 low 问题） |
| 作者署名 | 28/28 |
| 期刊名 | 28/28 |
| 卷期页 | 28/28 |
| DOI 或 arXiv 编号 | 28/28（DOI 26 篇 + arXiv 2 篇） |
| `✓ verify` 标注 | 28/28 |

### B. 编号一致性核查
- 正文三章 `[CITE:...]` 占位符总数：**126 次**（rationale 45 + content 59 + scheme 22）
- 正文实际使用不同标签：**22 个**（不含 scheme.md 第 59 行"[CITE:xxx]"误匹配 — 该处仅为元描述文本字面提及，非真实断链）
- references.md 定义标签：**27 个**
- 断链（正文使用了但 references 未定义）：**0 条**
- 冗余（references 定义但正文未直接引用）：**6 条**（见 high 问题 2）

### C. 引用频次排序（Top 10）
| 标签 | 引用次数 | 类型 |
|------|----------|------|
| `nikola_nature_2021` | 17 | R3 调控阈值核心 |
| `molinero_optica_2024` | 15 | R2 探针对标 |
| `mrudul_prb_2024` | 15 | R2 椭偏理论 |
| `kozak_apl_2023` | 10 | 产额标定 |
| `hu_meng_pnas_2024` | 9 | 反演母方法学 |
| `tyulnev_nature_2024` | 7 | R3 划界 |
| `zhou_nature_2023` | 7 | R3 划界 |
| `xu_zhou_npj_qm_2024` | 6 | R1 方法迁移 |
| `bauer_hansen_prl_2018` | 6 | QGT 反演 |
| `lian_natphys_2024` | 5 | R3 靶标 A 存在性 |

### D. 年份分布
- 2024-2026：**14 篇（50.0%）** — 充足
- 2020-2023：**8 篇（28.6%）** — 关键奠基
- 2010-2019：**6 篇（21.4%）** — 经典基础（Bistritzer 2011, Ghimire 2011, Vampa 2015, Cao 2018, Bauer-Hansen 2018, Pisanty 2019）
- 2005 年：0 篇（首轮正则误判来自 arXiv:2005.01718 中 ikeda 真实年份为 2020）

### E. 主题组与正文契合度
| 主题组 | 总数 | 被引用 | 备选 | 契合度 |
|--------|------|--------|------|--------|
| §1 综述与方向奠基 | 6 | 4 | 2 | 高 |
| §2 莫尔 HHG/TBG 理论 | 5 | 4 | 1 | 高 |
| §3 实验方法与产额标定 | 4 | 3 | 1 | 高 |
| §4 反演方法学与 QGT | 4 | 3 | 1 | 中 |
| §5 光 Floquet 工程与主动调控 | 4 | 4 | 0 | 高 |
| §6 关联绝缘态与强关联 | 3 | 3 | 0 | 高 |
| §7 HHG 理论基础 | 2 | 1 | 1 | 中 |

---

## 评分
创新性：N/A
可行性：N/A
严谨性：0.78
完整性：0.90
综合评分：0.84