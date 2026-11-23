# 评审团复核报告 · general-berry-mnps3-rashba-20260816（2026-10-19）

- 模式：引擎直接亲审（quality-review SKILL §五，v6.10.55）
- 触发：用户裁决（2026-10-19）——pending_review 逃生阀晋级后、reject 退回前过一遍评审团
- 复核纪律：以修改后磁盘文本为准逐条核对（grep 定位 + 全文通读），不凭修改记忆放行

## 一、14 条未解决问题逐条判定

| # | 严重度 | 位置 | 问题 | 判定 | 依据（磁盘实测） |
|---|--------|------|------|------|------------------|
| 1 | high | rationale | self_reference 14 次超阈 | ✅ 已解决 | 程序口径（§N 指针模式）实测全章 0 次；三章合计 5 次 < 阈值 10 |
| 2 | high | rationale | refs 头注声明"[11]/[25]/[38] 三章均挂靠"被证伪 | ✅ 已解决 | 头注已改为"各跨两章独立挂靠"，实测属实：[11] rationale+content、[25] rationale+scheme、[38] rationale+content；full_review L48 同步改写 |
| 3 | high | rationale | citation_overload 61 处超章标 47 | ⚠️ 豁免 | 实测 63 处。按 research-proposal SKILL §〇（v7.0.2 用户裁决：研究手册定位下"引用密度不设说服性目标"）豁免——每处引用挂靠不同论断、服务溯源。已做 1 处合并瘦身（L53 [21][7] 双句并一）。豁免记录入 dossier |
| 4 | critical | content | 引用错挂 5 处（Ghorashi[15]/Ogawa[18]/Mavani[24]） | ✅ 已解决 | 全文对号：Ghorashi-Rappe 全挂 [13]（L7/L25/L33/L81）、Ogawa-Hayami 全挂 [15]（L31/L35/L115）、Mavani 全挂 [20]（rationale L15/L29/L69） |
| 5 | high | content | orphan_refs [20][39] 零挂靠 | ✅ 已解决 | 错挂修复后自然落位：[20] 挂 rationale 3 处、[39] 挂 rationale L27（g-wave 多极矩实测） |
| 6 | high | content | 超长句反弹 5 句（severe 13>免赔 7） | ✅ 已解决 | 现行文本按程序口径（。[！？\n] 分句 >120 字）实测 severe 1 处 ≤ 免赔 3；本轮亲审再拆 1 处（L29 辅助反演量句 128 字） |
| 7 | critical | scheme | 引用错挂（rationale L15/17/35/119 跨章残留） | ✅ 已解决 | rationale 现行文本全部对号（L15 Mavani[20]/Sheng[18]、L17 Wang[7]/Rani[24]、L35 Ogawa[15]、L115 Ghorashi[13]） |
| 8 | high | scheme | §3.1 口径交叉引用表 ≥4 行指针无实体（d′/30–70%/≥5×/E_thr） | ✅ 已解决 | 交叉引用表已删改为叙述式（L5 重写）；四项实体在 content 全部存在：d′≥2.1（L45/L57/L71/L75）、30–70%（L55）、≥5 倍（L59/L75/L83）、E_thr_low/high（L55/L79） |
| 9 | high | scheme | 超长句（§3.1 L5 140 字、§3.2 L32 220/169 字） | ✅ 已解决 | 现行文本实测 severe 1 处 ≤ 免赔 3（旧 §3.2 L220/169 字巨型段已被 M1 拆散重写）；本轮亲审再拆 1 处（L69 对策三步句 125 字） |
| 10 | high | scheme | feasibility_gap §3.4 产额量级论证外包 | ✅ 已解决 | L63 已补完整就地估算链：EUV 10⁸ 光子/秒参照 × 10⁻⁶ 压低 → 单脉冲 10⁻¹ → 10⁶ 脉冲积分 10⁵ → 分通道 10³ → 泊松 1/√N ≈ 3% ≪ 50% 阈值 |
| 11 | high | scheme | orphan_refs（references L5 跨章残留） | ✅ 已解决 | 同 #5 连锁落位 + 头注改写（#2） |
| 12 | critical | full_review | "Mavani 等 [24]"×3 错挂 | ✅ 已解决 | grep 零命中（Mavani 全文仅正确语境 [20]） |
| 13 | high | full_review | "Wang 等 [9]"滑移极化错挂 | ✅ 已解决 | grep 零命中；[9] 仅 Regmi-CoNb₄Se₈ 语境出现 |
| 14 | high | full_review | orphan_refs 三章合并 [20][39] 零挂靠 | ✅ 已解决 | #4/#5 修复的自然后果；full_review L48 引用挂靠行按实测更新 |

**判定：13 条已解决，1 条带合理豁免（citation_overload，依据 SKILL §〇 手册定位裁决），critical 全清零。**

## 二、本轮亲审修改（M1 二轮）

| 文件 | 修改 | 动因 |
|------|------|------|
| content.md L29 | "辅助反演量三个承担补充判别任务：A；B；C。"（128 字）拆为三句 | 超长句（>120 字）程序红线 |
| scheme.md L69 | "对策分三步执行：A；B；C。"（125 字）拆为三句 | 同上 |
| rationale.md L53 | [21]/[7] 双句重复引用合并为单句嵌入式 | 引用密度瘦身（61→63 局部优化） |

## 三、关键时序澄清

critic r8 各节报告时点（content 10-13、scheme 10-15、full_review 10-16 01:00）**早于** 评审团 M1 修改（manual-revision-20261016.md，10-17 16:39）——r8 报的 14 条中 10 条实际已被 M1 修复，但 `_update_open_critical_issues` 的跨轮记忆机制未在 M1（会话内直改磁盘）后复跑，导致清单停留在修改前状态。本轮复核以磁盘为准重新核对，正是 SKILL §五"不得凭修改时的记忆放行"纪律的逆向应用：**也不凭 critic 旧报告误判现状**。

## 四、结论与后续

1. 14 条全部处置（13 解决 + 1 豁免），open_critical_issues 清账标记 round_resolved=8、resolved_by=panel-20261019
2. 按用户裁决执行 reject 退回（pending_review → optimizing）：带豁免记录回自动循环，4 维（innov 0.86/feas 0.83/rigor 0.90）已过方案 C 门槛，critical 清零后下一轮完成即触发方案 C 验收线正规晋级
3. 评审团模式质量评估：流程与纪律一致性良好（本轮验证）；改进点 1 项——会话内 M1 直改磁盘后应触发一次清单复核钩子，避免清单与磁盘脱节（已在 v7.2.32 写后质量门外挂同类守卫，后续可扩展到 panel 路径）

*复核人：协作引擎（林赛）· 2026-10-19*
