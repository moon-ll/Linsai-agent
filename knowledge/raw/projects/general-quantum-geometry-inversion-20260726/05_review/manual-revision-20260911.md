# manual-revision-20260911 修改报告

> 课题：general-quantum-geometry-inversion-20260726（BSV 量子几何反演）
> 操作：人工介入（P0 机械修复 + 保守裁减），依据 critic-round-5（2026-09-11 19:28，references 专轮 0.72）意见逐项执行。
> 背景：负反馈告警（monitor 独立分连续 3 轮下降 0.82→0.74→0.72，等待 210h）；R4 令裁至 ≤45 跨轮未执行；退回对比报告（pass4 vs pass3）判定"反馈注入未转化为通过能力"。
> 修改对象：`04_proposal/sections/` 下 references.md / rationale.md / content.md / scheme.md / full_review.md（重编号涉及全部 5 文件）。
> 脚本：程序化执行（删句 + 重编号 + 对账校验），原文件备份于临时目录。

---

## 一、死链 DOI 与版本状态修复（critic R5 P0）

| 条目 | 问题 | 处置 |
|---|---|---|
| [42]→[41] | PRR.7.043284 旧式拼法 404 | DOI 改 10.1103/8lhh-gq58（critic 核实） |
| [15][47][54] | 旧式死链 DOI | writer 已于 19:34 自行换新式短码（本次核查确认，无需处理） |
| [13] | v1 旧题 | 标题按 v2 更新为 "Ultrafast melting of a Mott insulating state." |
| [14] | Nat. Mater. 无卷页 | 标注 (2026, advance online) |
| [19] | 已发表仍标 arXiv | 补 *Adv. Phys.* **74**, 1–9 (2025) |
| [20] | 已发表仍标 arXiv | 补 *Phys. Rev. Lett.* **135**, 043603 (2025) |
| [23] | 已发表仍标 arXiv | 补 *Chin. Phys. Lett.* **43**, 020712 (2026) + DOI 10.1088/0256-307x/43/2/020712 |
| [6][43] | 作者链 ", et al." 与他条不统一 | 统一为 "前三 + et al."（与 [29] 一致） |

## 二、保守裁减（4 条，critic 裁减名单中挂点性质判断后的安全子集）

| 删除条目 | 主题 | 挂点处置 |
|---|---|---|
| [25] Loaiza | GQPE 量子相位估计 | content §2.5 末整段删除（NN 框架外备选路线，非必要论证） |
| [45] Xiang | 自旋量子几何张量 | rationale §1.4 铺垫句删除 |
| [51] Cui | 非厄米 Zeeman 张量 | rationale §1.4 两句删除 |
| [52] Tesfaye | Harper-Hofstadter 解析谱 | rationale §1.4 两句删除 + "上述两条多带/多扇区的拓展"改写为"上述量子几何张量的多扇区拓展" |

**保留判断**（critic 名单内但挂点为实质论证，不裁）：
- [22] Rivera-Dean：$r \gtrsim 1.5$ 高斯性破坏边界是三层描述对比的物理根源（rationale/content 双挂）
- [48] Molinero SWE：与动量空间 SBE 平行的方法学参照（content 实质段）
- [55] Uchida：准一维/准二维维度效应 HHG 对比实验（rationale/content/full_review 三处实质挂点）
- [24] Sumaya-Martinez：R2 条件数判据的 Fisher 信息支撑（scheme 3 处挂点）

## 三、重编号与对账（程序化）

- 映射：1–24 不变；26–44 各减 1；46–50 各减 2；53–54 各减 3；55→51
- 重编号处数：references 51 / rationale 58 / content 33 / scheme 70 / full_review 7
- 校验：✓ 总条目 51、编号连续无空洞；✓ 正文引用全部在册（无越界/无孤儿）；✓ arXiv-only 14 条（红线 ≤16 达标）

## 四、残留（交下轮）

- 总数 51 仍 > 45（critical #1 部分完成）：剩余裁减候选均有实质挂点，需 writer 做改挂级内容处理（改写句子 + 换挂相邻条目），非机械操作
- [48] PRR 发表版卷页待联网核实补全（critic 未给卷页值，不杜撰）
- 下轮验收口径（critic 原文）：references 内 grep '043284｜063111｜063107｜245147' 于 DOI 字段归零（本次已达成）、总数 ≤45、arXiv-only ≤16（已达成）

## 五、运维动作

- 人工清除 qgi 负反馈告警（210h 等待，自动清除额度已用尽），恢复链路轮转资格
- 本报告随修改一并提交 git
