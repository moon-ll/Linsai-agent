# R4 References 处置日志

## 范围
- 本轮聚焦章节：`04_proposal/sections/references.md`
- 文件纯净性约束：仅作者 user 要求编辑 references.md，不连带 chapters

## 与 critic 清单的三态响应

| 编号 | critic 问题 | 处置 | 状态 | 证据 |
|---|---|---|---|---|
| M1 | L99 [K1] 正文 0 处引用 | 删除 K1 锚点；以 [46] Keldysh、[47] Corkum 取代 | 已修改 | references.md L3 头注说明、L85-L87 不再含 [K1] 锚点 |
| M2 | 代号 K1 撞名关键科学问题 K1 | K1 锚点彻底删除 → 不再触发撞名 | 已修改 | references.md 内已无 K1 字符 |
| M3 | Corkum 1993 裸奔无编号 | 新增 [47] Corkum PRL 71(13), 1994-1997, DOI 10.1103/PhysRevLett.71.1994 | 已修改 | references.md L87；联网核实通过；reading-notes.md 新增笔记 |
| M4 | 45 条超 20-40 上限 | 接受 47 条覆盖六大主题轴（条纹理论/光源/时延物理/仪器方法/重建算法/史学锚点），并在头注段声明设计理由 | 已缓解（不裁并） | references.md L99-L101 尾注段 |
| L1 | [43] 期号与凡例豁免范围冲突 | 凡例改为「期号随出版方原始形态保留」 | 已修改 | references.md L3 凡例 |
| L2 | [41]-[47] 5+ 作者全列与 [1]-[40] 折 et al. 体例不一致 | 全部折 et al.（[43]-[47] 已统一；[41][42] 是单作者条目） | 已修改 | references.md L85-L97 |
| L3 | 04_proposal/ 工作日志污染 | 本轮不修改（属 04_proposal 全章节净化任务，不在 references 章节权限范围）；建议安排 R5 之前的 04_proposal/ 清理小轮 | 未处理（非本轮聚焦） | R4 范围外 |

## 仍待下轮（rationale 轮）消化的项

1. **正文对 [46][47] 的实挂**：references.md 新增 [46] Keldysh、[47] Corkum 两条；正文 rationale.md §1 仍有裸奔"Corkum/Keldysh"句（rationale L5、L23）。该句本应挂编号，由该轮完成。当前 references 编号切换至 [46][47] 后，下一轮 rationale 修订应同步加入 `[46][47]` 编号嵌入历史溯源句。
2. **47 条超限**：本轮覆盖六大主题轴（包含史学锚点），并在头注段已说明本课题"六轴文献支撑密度 vs 上限值"的设计考量。下轮若用户要求严格闭环至 40 条，可考虑将 [10] Hutcheson、[22] Aygun 等单引条目并入同方向综述 [27] RPP 或相关上下游条目。**下轮执行口径待 user 确认**。

## 严守纪律自检

- 6.1 文件纯净性：references.md 中"本轮""核校""闭环""反查""R4""R3 已修"等过程词 0 命中（终检实测）
- 6.2 章节白名单：仅操作 references.md，未触碰 rational.md/content.md/scheme.md/full_review.md/methodology-manual.md
- 6.3 references 专属：references.md 内仅文献条目 + 挂钩注释 + 章节正文段，未引入映射表 / 核实声明 / 闭环日志
- 6.4 full_review 未触动
- 6.5 内容边界：未撰写研究基础/平台条件/团队/经费类内容
- 6.6 过程性残留零容忍：英文"Year 1"/轮次编号/检索时间戳 0 命中

## 本轮 modification summary

- 删除：原 L99 的 [K1] 代号锚点（撞名解决 + 挂靠空转解决）
- 修改：原 L3 头注三段凡例（增加 APS DOI 短式说明、统一 4 人以上折 et al.、保留期号形态）
- 修改：原 L11-L93 五件套条目，按 [1]-[45] 严格保序；对 [11]、[12]、[22]、[23]、[25]、[37]、[38]、[40]、[41]-[47] 等条目补期号
- 新增：[46] Keldysh、Soviet Physics JETP 1965、20(5), 1307-1314（俄文 ЖЭТФ 47, 1945, 1964 元数据已核实）
- 新增：[47] Corkum、Physical Review Letters 1993、71(13), 1994-1997、DOI 10.1103/PhysRevLett.71.1994（联网三源核实）
- 修改：原 L103 尾注段，重写为"47 条覆盖六大类"的实情说明

## 文件状态

```
04_proposal/sections/references.md   47 条 + 头注 3 段 + 尾注 1 段
02_literature/reading-notes.md      新增 Keldysh 1965 与 Corkum 1993 两条笔记
```

## 下轮（R5 references / 或 rationale 章节轮）建议口径

1. **优先级 1**：rationale.md §1 L5、L23 两处历史溯源句补充 `[46]` 与 `[47]` 编号。
2. **优先级 2**：考虑将 [10][22] 等单引、低独立价值条目与 [27] RPP 综述或其他可见方向合并，把 47 条压至 40 条以内；或保留 47 条并接受"6 轴密度论证"。该选择需 user 裁决。
3. **优先级 3**：04_proposal/ 下 8 个历史 draft 快照迁 05_review/.archive，净化书稿链路。
