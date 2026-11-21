# 对抗评审报告（第 2 轮·参考文献专项）

项目类型 general｜对象 references.md（27 条）｜日期 2026-09-16｜范围：真实性/格式/相关性/缺失/时效性（编号一致性采信程序预检）

## 核验方法与总体结果

- 真实性：13 条预检"未验证"条目 + 14 条已验证条目 + [27] arXiv 单查全量反查。结果：12/13 实锤；[3] [27] 严重作者链虚构，[9] 局部虚构，[17] 拼写错。
- 格式："前三作者+等"统一；[12] 无 DOI 触发文件头语义微瑕。
- 相关性：27 条全部围绕莫尔/HHG/Floquet/Berry/Mott，无无关引用。
- 时效性：2024–2025 共 16 条（59.3%）> NSFC ≥30%；总量 27 在 20–40 区间。
- 与 R8（25 条）对比：[3][9][17][27] 四条作者链错位均属本轮新发现（R8 仅核 DOI+标题+卷期，未逐字比对全作者链）。

## 关键事实核查（CrossRef/arXiv 实测）

| 编号 | 文件作者 | 实测作者 | 状态 |
|------|----------|----------|------|
| [3] | Heide C., Lewenstein M. G., Boolakee T., Huber R. | Heide C., Kobayashi Y., Haque S., Ghimire S. | critical 虚构 |
| [9] | Du L., Huang Z., Zhang J., Lv B., Yang Y., Wang L., Watanabe K., Taniguchi T., Zhang G., Zhang Z. | Du L., Huang Z., Zhang J., Ye F., Dai Q., Deng H., Zhang G., Sun Z. | high 局部虚构 |
| [17] | Zhou S., Bao C., Fan W. | Zhou S., Bao C., Fan B. | medium 拼写 |
| [27] | Malla R., Mandal A., Ghonge S., Kar A., Watanabe K., Taniguchi T., Majumdar K. | Kumar A., Chatterjee S., Watanabe K., Taniguchi T., Majumdar K. | critical 4 名虚构 + 年份+DOI 缺失 |

## 问题清单

[critical]｜[27] 作者链｜4 名作者冒名（Malla/Mandal/Ghonge/Kar 伪造）｜按 arXiv:2607.22532 替换为 Kumar A., Chatterjee S., Watanabe K., Taniguchi T., Majumdar K.

[critical]｜[3] 作者链｜3 名作者冒名（Lewenstein/Huber 名家冒名）｜按 CrossRef 替换为 Heide C., Kobayashi Y., Haque S., Ghimire S.

[critical]｜全文 [27] 引用句｜正文 6 处写为"Malla 等 2025"｜grep 全部替换为"Kumar-Chatterjee 2026"

[high]｜[9] 作者链｜第 4–8 位 5 名虚构（Lv/Yang/Wang/Watanabe/Taniguchi）｜按 CrossRef 替换为 Ye F., Dai Q., Deng H., Zhang G., Sun Z.

[medium]｜[17] Fan W→B 拼写｜第 3 作者首字母误（W 应为 B）｜改为 Fan B.（Benshu）

[medium]｜[27] 状态著录｜写"2025, in press"，实测 2026-07-24｜改 2026 并补 DOI 10.1021/acs.nanolett.6c03005

[medium]｜文件头 L3 承诺｜"DOI 或 arXiv 二选一"语义缺注释｜补"至少其一"

[low]｜[18] 作者首 3 位｜与 CrossRef 10 位作者表比对需复核｜按实测补 Tyulnev I., Jiménez-Galán Á., Poborska J.

## 对抗结论

- 本轮发现 8 个问题（critical:3, high:1, medium:3, low:1）。3 个 critical 全部作者链虚构，命中 P0 红线。
- 相比 R8：3 critical 全新发现（[3][27] + [27] 正文 6 处同步污染）。
- 是否达到输出标准：**否**——critical 必须当轮处置。
- 返工优先级：① [27] 条目+正文 6 处全量替换 → ② [3] 作者更正 → ③ [9] 作者更正 → ④ [17] 拼写 → ⑤ [18] 复核 → ⑥ 格式兜底。
- 下一轮建议：references.md + 正文 grep 验收 0 残留；剩余 23 条作者链逐字比对。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.45
完整性：0.72
综合评分：0.58