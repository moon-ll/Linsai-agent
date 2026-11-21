# 对抗评审报告（第 3 轮·参考文献专项）

项目类型 general｜对象 references.md（27 条）｜日期 2026-09-17｜范围：真实性/格式/相关性/缺失/时效性（编号一致性采信程序预检）

## 核验方法与总体结果

- 真实性：R2 报告 4 处 P0/严重问题（[3][9][17][27]），R3 实测：[9][17] 已修，[3][27] 未修；新增 [15] critical 3 名虚构作者。
- 格式：R2 low "Wu/Nie/Lu 待复核" 实锤为虚构作者；其余条目格式统一。
- 相关性：27 条全部围绕莫尔/HHG/Floquet/Berry/Mott，无关引用 0 条。
- 时效性：2024–2026 共 16 条（59.3%）> NSFC ≥30%；总量 27 在 20–40 区间。
- [27] 正文 scheme.md 4 处同步污染（"Malla 等 2025"）仍全部残留。

## 关键事实核查（CrossRef/arXiv 实测）

| 编号 | 文件作者 | 实测作者 | 状态 |
|------|----------|----------|------|
| [3]  | Heide C., Lewenstein M. G., Boolakee T., Huber R. | Heide C., Kobayashi Y., Haque S. R. U., Ghimire S. | critical 未修（R2 旧 P0） |
| [9]  | Du L., Huang Z., Zhang J., Ye F., Dai Q., Deng H., Zhang G., Sun Z. | 一致 | high 已修（R2 high） |
| [15] | Shan J.-Y., Ye M., Chu H., Lee S., Park J.-G., Balents L., Wu L., Nie Y., Lu Y. | Shan J.-Y., Ye M., Chu H., Lee S., Park J.-G., Balents L., Hsieh D. | critical 新增 3 名虚构 |
| [17] | Zhou S., Bao C., Fan B. | 一致 | medium 已修（R2 拼写） |
| [27] | Malla R., Mandal A., Ghonge S., Kar A., … | Kumar A., Chatterjee S., Watanabe K., Taniguchi T., Majumdar K. | critical 未修（R2 旧 P0）+ 正文 4 处残留 |

## 问题清单

[critical]｜[3] 作者链｜3 名冒名（Lewenstein/Huber/Boolakee）仍滞留｜按 CrossRef 替换为 Heide C., Kobayashi Y., Haque S. R. U., Ghimire S.
[critical]｜[27] 作者链｜4 名虚构（Malla/Mandal/Ghonge/Kar）+ 年份 2025→2026｜按 arXiv:2607.22532 替换为 Kumar A., Chatterjee S., Watanabe K., Taniguchi T., Majumdar K. 并改 2026
[critical]｜[15] 作者链｜Wu L., Nie Y., Lu Y. 三名虚构（替换真作 Hsieh D.）｜按 PubMed/Crossref 改为 Hsieh D.（删 Wu/Nie/Lu 三位）
[critical]｜[27] 正文 scheme.md 4 处｜写"Malla 等 2025 年 [27]"｜grep 全部替换为"Kumar-Chatterjee 2026 [27]"
[high]｜[27] DOI 著录｜arXiv:2607.22532 无 DOI 著录｜补 DOI: 10.1021/acs.nanolett.6c03005（如已正式发表）
[medium]｜[4] Matter 文献｜cell.com 仅引 Wang/Ciappina 待前三位复核｜按 cell.com S2590-2385(25)00368-6 实测补 Wang L., Han S., Wu Y. 等
[medium]｜[2] [18] 著录细节｜卷期与起讫页需逐字比对 PubMed/Crossref｜按实测复卷期
[low]｜文件头 L3 承诺｜"DOI 或 arXiv 二选一"语义缺注释｜补"至少其一"
[low]｜[12] 著录｜arXiv 2508.00296 v2 last revised 2026-08-13｜补版本与日期

## 对抗结论

- 本轮发现 9 个问题（critical:4, high:1, medium:2, low:2）。4 个 critical：R2 旧 P0 [3][27] 未修 + 新增 [15] + 正文 4 处同步污染。
- 相比 R2：3 critical 仍存（[3][27] + [27] 正文污染），新增 1 critical（[15]）。R2 已修项 2 处（[9][17]）确认验收。
- 是否达到输出标准：**否**——P0 红线当轮必清。
- 返工优先级：① [27] 条目+正文 4 处全量替换 → ② [3] 作者更正 → ③ [15] 删 Wu/Nie/Lu、补 Hsieh → ④ [4] 前三位复核 → ⑤ [27] DOI 兜底 → ⑥ 文件头补注释。
- 下一轮建议：references.md + 三章正文 grep 验收 0 残留；剩余 23 条作者链逐字比对 CrossRef。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.72
综合评分：0.56