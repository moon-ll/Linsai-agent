# 对抗评审报告（第 7 轮·参考文献专项）

- 项目类型：key（transient-quantum-phase-optical）
- 审查日期：2026-09-21
- 审查范围：04_proposal/sections/references.md（38 条，编号 1-48 不连续）
- 方法：38/38 全量反查（CrossRef DOI 解析 18 条 + arXiv API 24 条，比对标题/作者链/卷期页/年份）；编号一致性采信预检
- 预检口径：13 条凭知识引用条目 12 条经 CrossRef 验证全真（仅 [47] 错位），虚构风险未成批兑现

## 核验统计
- arXiv 条目 24 条：24/24 ID 真实、标题年份匹配；作者错位 2 条（[31][46]）
- DOI 条目 18 条：17/18 解析正确且卷页年份一致；[47] DOI 指向无关论文
- 无 DOI 期刊条目 3 条：[14] RPP 89,047901(2026) 为真（DOI 10.1088/1361-6633/ae5847）；[33] Ultrafast Science 6, 0171 (2026) 为真（DOI 10.34133/ultrafastscience.0171）；[38] PRB 114, 065133 (2026) 独立验证为真
- 数量：38 条，处于 20-40 区间，达标
- 时效性：2024-2026 文献 27/38 = 71%（2026×13、2025×9、2024×5、2023×0），达标
- 缺失/冗余引用：预检双向核对无缺失、无未引用条目

## 锚点对比（实锤条目逐字比对）
- 申请书 [46]：K. Watanabe. Symmetry-enforced agreement of Kohn-Sham and many-body Berry phases in the SSH-Hubbard chain. arXiv:2510.12990
- arXiv:2510.12990 官方记录：Egor I. Kiselev（单作者），标题逐年
- 差距：标题、ID、年份全真，唯独作者整名虚构；正文 scheme.md 写"SHG 信号的物理根源已由 Kiselev[46]……"——正文与列表作者互相矛盾，属"ID+题名全真掩盖虚构作者链"典型形态

## 问题清单
[critical]｜references.md L73 条目[46]｜作者虚构：arXiv:2510.12990 实为 E. I. Kiselev 单作者，列表写 K. Watanabe；正文称"Kiselev[46]"与列表自相矛盾｜作者改 E. I. Kiselev；grep 全文"Watanabe"清残留；action: rewrite
[high]｜L45 条目[31]｜第一作者错位：arXiv:2604.20388 实际作者链 D. Ilin, A. S. Solntsev, I. Iorsh，Solntsev 系第二作者被提前｜按实际顺序改写三作者；action: rewrite
[high]｜L75 条目[47]｜DOI 错位：10.1021/acs.jpclett.4c01545 解析至无关 Nanozyme 论文；真实 DOI 为 4c01383，且真实卷页 15, 8642-8649 非所写 9568-9577｜DOI 改 10.1021/acs.jpclett.4c01383，卷页改 8642-8649；action: verify+rewrite
[medium]｜L23 条目[14]｜已见刊 Rep. Prog. Phys. 89, 047901 (2026) 仍并列 arXiv:2511.01097，违反 DOI/arXiv 二选一｜删 arXiv 号，补 DOI: 10.1088/1361-6633/ae5847；action: rewrite
[medium]｜L51 条目[34]｜卷页缺失：CrossRef 记录为 Nat. Rev. Phys. 7, 38-49 (2024)｜补"7, 38-49"；action: add
[medium]｜L25 条目[15]｜卷页缺失：CrossRef 已登记 Nat. Phys. 22, 1282-1286 (2026)｜补"22, 1282-1286"；action: add
[medium]｜全表编号｜编号不连续：缺口 [7,9,10,17,19,23,24,26,27,42]，NSFC 列表须连续编号｜按现行顺序 1-38 重排并同步正文全部引用标记；action: rewrite
[low]｜L9 条目[4]｜期刊归属未验证：CrossRef 未命中 J. Phys. Photonics 刊出记录，仅 arXiv:2604.15085 版本真实（作者匹配）｜核实刊出状态，未刊则删期刊名仅存 arXiv；action: verify
[low]｜L33 条目[21]｜在线首发无卷页，与 [16] 等已刊条目格式不统一｜维持现状可接受，或统一标注 advance online；action: rewrite
[low]｜L27/L59 等 6 条｜DOI 与 arXiv 并列标识共 6 条（[5][14][15][16][21][38]），全表标识制式不统一｜统一"见刊留 DOI、未刊留 arXiv"二选一；action: rewrite

## 对抗结论
- 本轮发现 10 个问题（critical:1, high:2, medium:4, low:3）
- 相比上一轮：预检标记的 13 条虚构风险集中区经全量反查 12 条洗清，风险未成批兑现；但新增 2 条作者链错位（[31][46]）与 1 条 DOI 错位（[47]），均不在预检标记名单内——印证"仅核 ID+题名"不足以验收，作者链须逐条全量反查
- 是否达到输出标准：否——存在 1 个 critical（虚构作者），须当轮修复验收；[46][31][47] 三条修复后 grep 复核（Watanabe 残留、Ilin 顺序、4c01383/8642 数值变体）
- 返工优先级：[46] → [47] → [31] → 编号重排（重排会移动全部编号，须最后做并全量同步正文）
- 下一轮建议：修复后对全部 38 条重跑 CrossRef/arXiv 自动比对；writer 补充检索时将 02_literature 命中文献回录检索池

## 评分
创新性：N/A
可行性：N/A
严谨性：0.72
完整性：0.88
综合评分：0.80
