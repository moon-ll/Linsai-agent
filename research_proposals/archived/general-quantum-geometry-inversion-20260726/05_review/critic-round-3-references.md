# 对抗评审报告（第 3 轮·参考文献专项）
- 项目类型：general｜对象：sections/references.md（55 条）｜日期：2026-10-07
- 方法：不限于预检点名 15 条，55/55 全量反查——38 个 DOI 走 CrossRef CSL JSON（38/38 解析成功），25 个 arXiv ID 走 abs 页/Semantic Scholar（arXiv export API 429 限流，改抓 abs 页）逐条五件套比对（题名/首作/作者链/刊卷页/年）；grep 三正文章节核相关性。
- 采信预检：编号 1–55 连续无缺口、无双向缺失、无内联 "(Author, Journal…)" 型引用（grep 0 处）。

## 核验结论（先核实再下结论）
- 真实性：53/55 与公开记录匹配。R2 的 critical（[45] 作者链虚构）已按真身重录（González-Monge/Willemann/Feist ✓）；R2 点名 DOI 错挂（[32][38]）均已更正；[43] 已去 † 录 PRA 正式版 ✓；[49] 第 5 作已改 Trevisan ✓。
- 预检点名 15 条实际全部为真，但本轮全量反查在点名集之外检出 2 条题名失真（[10][46]）——"预检点名≠虚构风险全集"再次验证。
- 作者链抽验：[5] Chowdhury✓ [10] Ikeda 等 6 人✓ [12][44] Khurelbaatar 3 人✓ [40] Cárdenas 3 人✓ [16] Faeyrman✓ [29] Baykusheva 15 人✓ [45]✓；仅 [9] 首作归属存疑。
- 双著录 8 条 DOI 版与 arXiv 版题名/作者一致，无跨篇错挂；无重复 DOI/arXiv（[12]/[44]、[13]/[43] 同组不同文，均真）。
- 时效：2023+ 40/55（73%）、2024+ 37/55（67%），优。
- 数量：55 条超 20–40 区间 15 条；† 预印本 17/55（31%）过载。

## 问题清单
[high]｜[10] L23｜题名与 arXiv:2508.00296 原文不符，系意译改写｜action:rewrite｜改录原题"High harmonic generation reflecting the sub-cycle evolution of the Mott transition under a mid-infrared electric field"
[high]｜[46] L95｜题名与 arXiv:2410.15503 原文不符，不可检索匹配｜action:rewrite｜改录原题"Information-theoretic perspective on energy conservation in high harmonic generation"
[medium]｜[52] L107｜arXiv:2412.17809 已刊 Nat. Phys. (2024)，仍标 † 仅录 arXiv｜action:rewrite｜去 †，补 Nat. Phys. 卷页与 DOI 10.1038/s41567-024-02678-8
[medium]｜[50] L103｜FAIR 数据管理原则书与科学问题无关联（正文无 FAIR/数据管理语境）｜action:remove｜删除或改挂数据规范断言处；删之可助压总数
[medium]｜[9] L21｜首作存疑：arXiv 提交人为 Granados，条目列 Stammer 为首作｜action:verify｜按 abs 页作者序重录；若 Stammer 非作者即按真身改写
[medium]｜[4] L11｜AOP 卷期第 3 轮仍未回填（R1 起跨轮未解决）｜action:verify｜CrossRef 已录该 DOI 但无卷页，投稿前再查回填
[medium]｜全表｜总数 55 超区间 15 条，† 17 条预印本占比过高｜action:remove｜删 [50] 后再筛：同组 [12]/[44] 二选一等，压至 ≤40
[low]｜[52] L107｜"Kang, M. et al."与全表全作者链体例不一｜action:rewrite｜补全作者链或全表统一 et al. 规则
[low]｜[24] L51｜年份 2011，CrossRef 刊版为 2010（在线先行）｜action:verify｜统一按刊版年份 2010
[low]｜L3 凡例｜"待 CrossRef 回填"等过程性工作日志残留文内（膨胀告警联动）｜action:remove｜回填状态记录迁移 05_review，正文只留 † 凡例
[low]｜[2] L7｜DOI 小写"0256-307x"与他条大写体例不一｜action:rewrite｜统一 DOI 大小写格式

## 锚点对比
- 引用（L95 原文）："Energy conservation in quantum optical high harmonic generation. arXiv:2410.15503"
- 对比（arXiv abs 页）："Information-theoretic perspective on energy conservation in high harmonic generation"，作者 Stammer 单人（From: Pablo Stammer），内容为能量守恒子空间方法。
- 差距：ID 真实但题名整体改写，复现检索按题名即失配——须逐字回录 arXiv 原题。
- 锚点结论：[46] 题名失真坐实，high 立案。

## R2 问题对账（9 项）
已解决 7：[45] 作者链重录、[32][38] DOI 更正、[42]-[46] 补正文挂钩且假挂钩注释块已删、[43] 去 † 录正式版、[49] 第 5 作更正、工作日志注释块迁移（大项，正文侧完成）。未解决 2：总数超标（50→55 反向恶化）、[4] AOP 卷期。新增 5：[10][46] 题名失真、[52] † 过期、[50] 相关性、[9] 首作存疑（[2][24][52 体例] 为本轮新立案低危）。

## 对抗结论
本轮 11 个问题（critical:0, high:2, medium:5, low:4）。相比 R2：改善 7（含全部 R2 critical/high），新增 5，未解决 2。虚构风险已清零，但两条题名失真属"真 ID 错题名"残留，且总数连续两轮反向膨胀（50→55），"先入检索池再入表"纪律仍未落地。未达输出标准。返工优先级：① [10][46] 回录原题；② [52] 升级著录；③ 核 [9] 作者序；④ 删 [50] 并压总数至 ≤40；⑤ [4] 卷期回填。writer 后续补充检索命中文献须回录 02_literature 检索池。

## 评分依据
严谨性 0.72：53/55 五件套与公开记录精确匹配、作者链抽验通过、无虚构；扣 2 条题名失真（high）、1 条首作存疑、1 条跨轮卷期缺口、1 处年份与刊版不一。完整性 0.68：时效优（2024+ 67%）、编号无缺口无幽灵、无具名断言缺源；扣总数超区间 15 条、† 过载 31%、1 条疑似无关引用。

## 评分
创新性：N/A
可行性：N/A
严谨性：0.72
完整性：0.68
综合评分：0.70
