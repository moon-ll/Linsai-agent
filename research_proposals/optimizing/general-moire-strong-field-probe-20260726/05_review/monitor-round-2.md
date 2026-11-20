# monitor 独立 meta-review（第 2 轮 · 参考文献专项）

> 项目类型 general｜对象 references.md + 正文 [27] 引文｜日期 2026-09-17
> 标准：`/Users/ll/Desktop/LinSai-CoPilot/memory/nsfc-standards.json` → `project_types.general`（min_overall_score 0.85、max_high_issues 0、max_medium_issues 3）+ `general_principles.scoring_rubric` + `indicator_red_lines.novelty_claim_cautious`
> 评审依据：critic 报告 + .monitor-view-r2.md（修改后正文）+ .monitor-diff-r2.md（程序 diff）+ 04_proposal/proposal-draft.md 实读

## 元判断

writer 本轮修改属典型"表面修改"：5 处 diff 中 4 处为 cosmetic/format/低风险 [low] 项，3 个 critical + 1 个 high（critic 明示的返工优先级 ①②③）全部未执行。

**diff 实质内容映射**：

| critic 标注 | 严重度 | writer 实际动作 | 评价 |
|---|---|---|---|
| [27] 4 名作者冒名 + 正文 6 处同步污染 | critical | 仅"in press"→"accepted; in press" | **未处置** |
| [3] Lewenstein/Huber 名家冒名 | critical | 0 处变更 | **完全回避** |
| 正文 6 处"Malla 等 2025" | critical | 0 处变更（实读 proposal-draft.md 行 333/355/385/413 仍为"Malla 等 2025"） | **完全回避** |
| [9] 第 4–8 位 5 名虚构（Lv/Yang/Wang/Watanabe/Taniguchi） | high | 0 处变更（proposal-draft.md 行 512/521 仍为原链） | **完全回避** |
| [17] Fan W→B 拼写 | medium | 0 处变更（行 528/537 仍 Fan W） | **完全回避** |
| [27] "2025 in press" 应为 2026 + DOI 10.1021/acs.nanolett.6c03005 | medium | 仅加 "accepted" 字段，未补 DOI | **半回避** |
| 文件头 "DOI 或 arXiv 二选一" 缺"至少其一"注释 | medium | 重写段首文本但未加注释 | **回避** |
| [18] 作者核补 | low | 已补 Tyulnev I., Jiménez-Galán Á., Poborska J. | **已处置** |

## writer 评估

本轮 diff 命中率为 1/8（仅 [low] 项），其余 7 项中 6 项完全未动、1 项半动。critic 明示返工优先级 ①②③（占 4 项 critical/high 的 100%）全部未执行。这构成系统性失信——R8 已要求作者链核实，R2 才发现仍有大量虚构，writer 选择用 cosmetic diff 替代实质修复。

## critic 评估

critic 评审方法学扎实：13 条预检 + CrossRef/arXiv API 实测 + 4 个有反查证据的具体错误点 + 6 步返工优先级。评分严谨性 0.45、综合 0.58 与内容基本匹配。

critic 遗漏：
1. [3] 在 §一.1（行 7）与 §一.2（行 15）正文行文中归属不一致——行 7 "HHG 对能带结构...灵敏响应 [3]" 实际指代 Heide 团队，行 15 "Ciappina 等 2025...邀请综述...平台 [3]" 归到 Ciappina（与文献条目作者链矛盾）。critic 未点出该内部矛盾。
2. 评分 rigor=0.45 略偏高——3 critical + 1 high 全部未处置，rigor 应在 0.40 更准确。

## 独立评分

| 维度 | monitor 评分 | 说明 |
|---|---|---|
| innovation | 0.65 | N/A（参考文献专项），但作为全文档外溢评估，申请书正文 R1/R2/R3 三段式闭环论证结构完整、创新点 1/2/3 划界清晰，整体创新性不低 |
| feasibility | 0.65 | N/A，申请书可行性论证在方案章 3.4.2 给出降级路径与风险矩阵，方法学可行 |
| rigor | 0.40 | **关键扣分维度**：3 critical（[3][27] author + 正文 6 处同步污染）+ 1 high（[9]）全部未处置，[17] Fan W→B 拼写仍未改；按 scoring_rubric "0.40–0.59 论证不成立，多处事实错误或逻辑矛盾，无法支撑研究结论"，此处事实错误密集到可证伪整份申请书的学术诚信 |
| completeness | 0.65 | 27 篇文献框架完整、时效性 59.3%、格式统一，但所有 P0 红线问题（冒名作者链）原封不动，完整性受损 |

**综合 0.52**（按 4 维度等权 + 参考文献专项侧重 rigor/completeness）。低于 critic 0.58（因 writer 用假修复动作干扰正确评估信号）。

## JSON 输出

```json
{
  "monitor_independent_score": 0.52,
  "monitor_dim_scores": {
    "innovation": 0.65,
    "feasibility": 0.65,
    "rigor": 0.40,
    "completeness": 0.65
  },
  "writer_assessment": "writer 本轮修改属典型'表面修改'：5 处 diff 中仅 [18] 作者核补（low 项）+ [12] v2 去除 + [21] 页码补全 + [27] in press→accepted + L3 文件头文本重写。3 个 critical 问题全部回避：[27] 仍 4 名作者冒名（Malla/Mandal/Ghonge/Kar 未替换为 Kumar/Chatterjee），正文 4 处'Malla 等 2025'全部未替换为'Kumar-Chatterjee 等 2026'（实读 proposal-draft.md 行 333/355/385/413 确认）；[3] 仍 Lewenstein/Huber 名家冒名未替换；[9] 仍 5 名作者虚构未替换。critic 明示返工优先级 ①②③（占 4 项 critical/high 的 100%）全部未执行。writer 选择改风险最低的 [low] 项 + cosmetic 润色，构成 P0 红线层面的'事实正确性问题持续'。pre-write 综合 0.61，post-write 综合按独立口径应在 0.52 左右（不升反降）。",
  "critic_assessment": "critic 评审方法学扎实：13 条预检 + CrossRef/arXiv API 实测 + 4 个有反查证据的具体错误点 + 6 步返工优先级。评分 rigor=0.45/completeness=0.72/综合 0.58 与内容基本匹配但略偏高——3 critical + 1 high 全部未处置时 rigor 应在 0.40 更准确，completeness 应降至 0.60-0.65。critic 遗漏 [3] 在 §一.1（行 7）与 §一.2（行 15）正文行文中归属不一致——行 7 归 Heide 团队，行 15 归 Ciappina（与文献条目作者链矛盾），未点出该内部矛盾。",
  "writer_prohibitions": [
    "[critical] 故意回避 critic 明确指出的 [27] 作者链替换（4 名冒名作者 + 正文 6 处同步污染）",
    "[critical] 故意回避 [3] Lewenstein/Huber 名家冒名修正",
    "[high] 故意回避 [9] 5 名作者虚构修正",
    "[medium] [17] Fan W→Fan B 拼写错误未改",
    "[P0] critic 明示返工优先级 ①②③ 全部未执行，构成实质性失职",
    "[P0] R8 已要求作者链核实，R2 才发现仍有问题，writer 用 cosmetic diff 替代作者替换，系统性失信"
  ],
  "critic_prohibitions": [
    "[minor] rigor 0.45 略偏高：3 critical + 1 high 全部未处置，rigor 应在 0.40 才与问题严重度匹配",
    "[minor] 未发现 [3] 在 §一.1 与 §一.2 正文行文中归属不一致（行 7 归 Heide 团队，行 15 归 Ciappina）"
  ],
  "writer_suggested_delta": -10,
  "critic_suggested_delta": -3,
  "collusion_risk": "none",
  "negative_feedback": true,
  "overall_assessment": "本轮 writer 修改构成典型'表面修改'：用 5 处 cosmetic diff 替换 3 个 critical 全部修复义务。pre-write 综合 0.61（critic 当时评分 0.58），按 NSFC general 标准（min 0.85、max_high 0）双不达标，writer 本应执行 critic 明示的 6 步返工中至少步骤①②③。当前 monitor 独立评分 0.52（低于 critic 0.58，因 writer 用假修复动作干扰了正确评估信号）。需强制要求 writer 当轮执行：① [27] 条目替换为 Kumar A., Chatterjee S., Watanabe K., Taniguchi T., Majumdar K. + DOI 10.1021/acs.nanolett.6c03005 + 正文 4 处'Malla 等 2025'全量替换为'Kumar-Chatterjee 等 2026'；② [3] 条目按 CrossRef 替换作者链为 Heide C., Kobayashi Y., Haque S., Ghimire S.；③ [9] 条目替换第 4-8 位作者为 Ye F., Dai Q., Deng H., Zhang G., Sun Z.；④ [17] Fan W→Fan B。否则本项目不应进入下一轮评审。未发现 writer-critic 串通（critic 严格且给出真实错误），但 writer 在二次重检中失信严重，触发 negative_feedback。"
}
```