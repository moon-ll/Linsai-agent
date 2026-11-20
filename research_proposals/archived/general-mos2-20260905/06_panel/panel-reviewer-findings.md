# 评审团定点核查 findings — reviewer（整体一致性）

核查员：engine 亲审（reviewer 视角）｜ 课题：general-mos2-20260905 ｜ 时间：2026-10-05
方法：关键指标逐章列数值与出处行号对账；正文 [N] 与 references 条目程序化对账；全部"见 §X"指针逐一落点核实；full_review 字数与骨架语义复查。

## RV-1 [medium] 关键指标跨章口径对账（唯一违例＝RS-1，其余全部一致）

| 指标 | 各章数值与出处 | 判定 |
|---|---|---|
| 选择定则 R² ≥ 0.90（灰区 0.85—0.90，<0.85 逐段重拟合） | rationale L149；content L63（目标二）、L73（Q1）、L85（指针）；scheme L15、L129；full_review L14 | 一致 ✓ |
| α_syn ≥ 0.15（同样品双基线，30% 分母切换几何平均） | rationale L151、L161；content L35/L37/L39；scheme L65/L99/L125/L131/L141；full_review L15 | 一致 ✓ |
| 统计置信度（δ≤5%→约 2.1σ；δ≈10%→上调 0.30） | content L39/L65/L75；scheme L65/L99；full_review L16 | 一致 ✓；唯 content L85 旧句"判据上调由方案章统一管理"方向相反（CT-1 修复项） |
| η(N) R² ≥ 0.85（σ_dis rad²） | rationale L153；content L63/L77；scheme L19；full_review L17 | 一致 ✓ |
| 反演三阈值 r≥0.8 / σ_Ω≤0.15（Ω_max）/ Δt≤100 as（AND 关系） | rationale L125/L127/L155；content L51/L67/L79；scheme L91/L93/L117/L119/L133/L137；full_review L18/L19 | 一致 ✓ |
| 失谐点 0、±50、±100 meV（五点） | content L19；scheme L63；full_review L23 | 一致 ✓ |
| 莫尔周期/失配（a≈0.32 nm、δ≈4.1%、1.35/0.61/7.07 nm、δ²≈4.6θ²） | rationale L97—L99；content L27；full_review L22 | 一致 ✓（δ=4.1% 来源待核＝RS-6） |
| 谐波范围 5—15 阶（含 6/8/10/12/14 偶阶），213—640 nm/1.9—5.8 eV，13 阶 5.04 eV | rationale L33/L147/L163；content L9；scheme L35/L37/L59/L67；full_review L20 | 一致 ✓ |
| 泵浦窗口双口径（Peterka 1.25—2 eV vs 本项目 1.4—2.1 eV） | rationale L17；scheme L33；full_review L26 | 一致 ✓；唯 content L63 目标一括注"驱动 0.62 eV 中红外"错挂本项目基线（RS-1 违例，修复为 3.2 μm 驱动） |
| CEP 压缩路径 380→150→59 mrad（Δt 四档 100/170/300/定性） | scheme L43—L55、L93、L103；content L87（指针）；full_review L19 | 一致 ✓ |
| 样品配置（5 角×3＝主线 15；单层+TBG 对照 8；魔角 1.1°±0.2°） | scheme L25/L27 | 内部自洽 ✓ |
| 剥离测试 RMS 残差 25%→18%→16%→σ_Ω 0.15 三步映射 | scheme L81—L87；full_review L8 | 一致 ✓ |

- 违例明细：content.md L63 "（驱动 0.62 eV 中红外、A 激子近共振窗口）"——0.62 eV 属 Peterka 文献配置（full_review L26 双口径行），且与 content L37"两条基线与协同条件共享驱动波长与场强"冲突。修复：改"（本项目 3.2 μm 中红外驱动、A 激子近共振窗口）"。

## RV-2 [合规复查] 参考文献编号闭合（程序化）

- 正文（四章合计）引用编号 ⊂ [1]—[41]，无越界；未被正文引用编号恰为 [2]、[7]，与 references 凡例"研读基础：[2]、[7]……其余 39 条直接承担"逐字一致 ✓。
- 条目—人名抽查：[29] Molinero、[30] Mrudul、[31] de Almeida、[38] Serov & Kheifets、[40] Gao、[41] Csizmadia 与 KB 页作者一致 ✓。
- 处置：不适用+理由（合规；本轮改动后已二次复验，见修改报告）。

## RV-3 [合规复查] full_review 仍是 ≤3000 字"全文骨架"语义

- 实测：全文 2444 字符（非空白 2099）≤3000 ✓；①主线论证链、②章节衔接点（含 Δt 级联与 σ_Ω 映射两个单点出处分声明）、③口径表 17 行三件套语义完整，无处置记录语残留（r1 RV-7 修后未复发）。
- 处置：不适用+理由（合规）。

## RV-4 [合规复查] 交叉指针落点逐一核实（12 处）

content L11→§2.6 ✓；content L25→§2.6 ✓；content L41→§2.0 总述段 ✓（"与方案章"落空部分＝CT-6，修复）；content L51→§2.6 ✓；content L85→立项依据章第三部分第一问 ✓；content L87→方案章 §3.3 末段 ✓；scheme L15→立项依据第一问＋研究内容 §2.6 ✓；scheme L19→研究内容 §2.1/§2.6 ✓；scheme L35→立项依据 §2.1/§3.4 末段/立项依据 §4 ✓；scheme L65/L99/L125→研究内容 §2.2 ✓；scheme L93/L103→§3.3 末段 ✓；scheme L117→研究内容 §2.3 ✓。修复 CT-6 与 CT-1 后全部指针落点有效。
- 处置：不适用+理由（除两处修复项外合规）。

## RV-5 [low·不改] references 作者列体例存在两种风格并存

- 位置：references.md L49/L75/L79（[24][37][39]）
- 原文：[24]"H. Zhong, X. Cai, C. Bao et al."、[37]"A. T. Bondy, J. C. del Valle, S. Saha et al."、[39]"M. Kim, T. Kim, A. Galler et al."（前三作+et al.）；其余 >3 作者条目用"首作 et al."（如 [15] "P. Peterka et al."）。
- 问题：>3 作者条目两种列法并存；r1 RV-9 仅统一了被点名的 [26][33]。
- 处置：不适用+理由——统一需改动约 20 条且无权威体例裁决（NSFC GB/T 7714 与 APS 风格均常见），收益低、引入新错风险高；r1 仅处理点名项的先例沿用。记录在案供终稿统稿时定夺。

## RV-6 [合规复查] 章节衔接链

§2.0 解析锚点（content L9"由立项依据章给出"）→ rationale §2.3.1/§2.3.2 点群归属与适用条件 → scheme §2（L15）映射执行，三点闭合 ✓；§2.6 降级路径、scheme §3.3 四档级联、rationale §4 兜底条款（L163"仅报告实际达到的截止范围，不外推"）三处口径一致 ✓；§2.0（content L7）数据链约束指针与 rationale §4 产出描述无同构展开（r1 CR-7 修后未复发）✓。
- 处置：不适用+理由（合规）。
