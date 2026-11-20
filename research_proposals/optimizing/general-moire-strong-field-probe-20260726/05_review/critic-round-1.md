# 参考文献检验报告（第 1 轮 · general）

项目：general-moire-strong-field-probe-20260726
聚焦章节：04_proposal/sections/references.md
审查日期：2026-09-16
审查方式：CrossRef / arXiv 全量反查 25 条 DOI + 1 条 arXiv（共 26 条），并以正文 [N] 内联引用反向核对作者/期刊/年份

---

## 一、综合评分

0.62 / 1.00

## 二、维度评分

| 维度 | 权重 | 得分 | 问题数 | 依据 |
|------|------|------|--------|------|
| 严谨性 | 1.00 | 0.45 | 1 critical / 1 medium | [3] 作者列表 4/4 错 3 个 + 编号双重错位；"等/et al." 不统一 |
| 完整性 | 1.00 | 0.78 | 2 medium / 1 low | 26 条数量合规；61.5% 近 3 年；DOI 完整度 96.2%；[3] 编号错位衍生"应补 Ciappina 综述"问题 |

## 三、问题清单

### [critical] 内容错位 — [3] 编号双重错位（references.md ↔ rationale 正文）
- 位置：references.md L11 + rationale.md 第 1/2 处 [3] 引用行
- 问题：references.md [3] 为 Heide 2024 Nat. Phys. 综述；正文两处 [3] 均称 "Ciappina 2025 Adv. Phys. 邀请综述"，编号/作者/期刊三者全错位
- 建议：①核实 "Ciappina 2025 Adv. Phys. 综述" 是否真实存在；②若存在，重建 [3] 条目并调正文两处引用；③若放弃引用，将正文两处 [3] 改回 [N] 指向现有 Heide 2024
- action：rewrite

### [critical] 作者错位 — references.md [3] 4/4 错 3 个
- 位置：references.md L11 `Heide C., Lewenstein M. G., Boolakee T., Huber R. 等`
- 问题：CrossRef 10.1038/s41567-024-02640-8 真实作者为 Heide / Kobayashi / Haque / Ghimire（SLAC+Stanford 团队）；现列 Lewenstein/Boolakee/Huber 为 Regensburg 团队，系典型"占位 DOI + 替换作者"伪装
- 建议：替换为真实 4 作者 `Heide C., Kobayashi Y., Haque S. R. U., Ghimire S.`
- action：rewrite

### [medium] 风格不统一 — "等" / "et al." 混用
- 位置：references.md L39 [17]、L49 [22] 用 "et al."，其余 24 条用 "等"
- 问题：26 条中 2 条用英文 "et al."，违反 references.md 整体中文规范
- 建议：统一改 "等"，删除 [17] [22] 的 "et al."
- action：patch

### [medium] 卷期格式不统一 — 8 条缺 issue
- 位置：[1][4][7][11][14][15][22][25] 缺 issue 号
- 问题：与 [2][3][6][9][10][18][26] 等规范写法不齐
- 建议：补全 issue；至少 [7] PRR 2, 032015 → 2(3), 032015；[14] PRL 133, 156901 → 133(15), 156901
- action：patch

### [low] 数量偏少 — 26 条略低于 general 标杆
- 位置：references.md 整体
- 问题：general 标杆 30-40 篇，本轮 26 条处于 20-40 区间下沿
- 建议：本轮不强制扩；下一轮若聚焦 references.md，可补 4-6 条 Floquet/谷极化/反演算法近 2 年新文献
- action：research

### [low] [12] 缺 DOI — 仅 arXiv 预印本
- 位置：references.md L29 [12] Ikeda 2025 arXiv:2508.00296v2
- 问题：2025-08 提交、v2 仍无期刊 DOI；与 25 条有 DOI 条目格式不齐
- 建议：保留 arXiv 标注 + 增加"截至 2026-09 未见正式发表"脚注；下一轮复查是否已刊
- action：verify

## 四、关键验证记录

### DOI 反查（25/26 全量 CrossRef / Nature 页核对）
- 25 条 DOI 全部对应真实论文，标题/期刊/卷期/年份（print year）/作者首字母无错位
- 唯一例外：[3] DOI 真实但作者列表 4/4 错 3 个
- 13 条"凭学科知识"条目中 12 条（[2][9][10][11][13][16][17][19][20][23][24][26]）正文/条目完全一致
- [12] arXiv:2508.00296 反查：标题/作者/日期/DMFT-Sr2CuO3 内容均与正文引用一致 ✓
- [15] Erratum 10.1038/s41586-021-04368-4：Nature 602(7895) E19 (2022) ✓

### 正文 ↔ references.md 双向核对
- 26 条全部正文被引用（rationale 26 / content 14 / scheme 11），无幽灵编号、无孤儿条目
- 唯一编号错位：[3] 正文指向 Ciappina 综述，references.md [3] 指向 Heide 综述

## 五、锚点对比

引用 1 条原文（references.md L11）：
> `[3] Heide C., Lewenstein M. G., Boolakee T., Huber R. 等. *Ultrafast high-harmonic spectroscopy of solids*. **Nature Physics 20, 1546–1557 (2024)**. DOI: 10.1038/s41567-024-02640-8.`

CrossRef 真实记录（DOI 10.1038/s41567-024-02640-8）：
- 标题：Ultrafast high-harmonic spectroscopy of solids ✓
- 期刊/卷期/页：Nature Physics 20(10) 1546-1557 (2024) ✓（仅 issue 10 现条目缺）
- 作者：Heide, Christian / Kobayashi, Yuki / Haque, Sheikh Rubaiat Ul / Ghimire, Shambhu
- 差距：现列第 2-4 作者（Lewenstein/Boolakee/Huber）全为虚构；属典型"占位 DOI + 替换作者"伪装

## 六、对抗结论

- 本轮发现 6 个问题（critical:2 / medium:2 / low:2），1 处为编号+作者双重 critical
- 25/26 DOI 真实性已逐条反查通过；[3] 是当前主病灶
- 上一轮（round 10 优化报告）已修：DOI 重复 / §8 整段 / [CITE:...] 占位符 / 引言"31 篇"与实际矛盾 / 一号两用 / 主题错配 / 标题乱码
- 本轮新增：[3] 编号+作者错位（round 10 未涉及）
- 是否达输出标准：**否**（[3] 错位属 critical，须当轮修复）
- 下一轮必改：①核实 "Ciappina 2025 Adv. Phys. 综述" 真实性（references.md 需补/替换 [3]）；②统一"等"；③补全卷期 issue

## 评分
创新性：N/A
可行性：N/A
严谨性：0.45
完整性：0.78
综合评分：0.62
