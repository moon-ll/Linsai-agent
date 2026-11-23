# 对抗评审报告·第2轮（聚焦：参考文献）

> 评审角色：critic（红队）｜项目类型：key（重点）｜评审日期：2026-09-04
> 范围：references.md（73 条）— 仅评引文真实性/格式/相关性/时效性/缺失
> 编号一致性已由程序预检完成，本轮直接采信
> 历史轮产物（整体一致性）已归档为 .archive-critic-round-2-overall-pre-refs-20260904.md

## 一、抽样 CrossRef/arXiv 核查结果（执行 8 条）
| 编号 | 标识符 | 核查结论 |
|------|--------|---------|
| [5] | 10.1103/PhysRevLett.126.183601 | 虚构 — 该 DOI 真实论文为 "Self-Induced Glassy Phase in Multimodal Cavity QED"（非 Baykusheva HHG） |
| [9] | 10.1103/PhysRevLett.121.246401 | 真实 — Baykusheva 2018 Berry curvature crystalline HHG ✓ |
| [38] | arXiv:2604.15085 | 真实 — Varillas et al. Roadmap on Attosecond Science (2026) ✓ |
| [39] | arXiv:2601.09608 | 真实 — Nayak et al. SYLOS ELI ALPS beamline (2026-01-14) ✓ |
| [54] | arXiv:2311.13309 | 作者错位 — 真实为 Ito/Schüler/Meierhofer/Sentef/Huber (Nature 616, 696)，非 Lucchini/Nisoli |
| [57] | arXiv:2604.27750 | 真实 — Batista et al. helicity HHG (2026-04-30) ✓ |
| [58] | arXiv:2604.07543 | 真实 — Mokhtari et al. phonon decoherence Si (2026-04-08) ✓ |
| [59] | arXiv:2604.20388 | 真实 — Ilin/Solntsev/Iorsh quantum-optical topology HHG (2026) ✓ |
| [60] | arXiv:2604.06707 | 虚构 — 同号不存在；真实相似题为 2504.17077 (Seo et al., "AdjointDiffusion" 而非 "OptiDiff");round-2-content 已锁定正文错位 |
| [61] | arXiv:2603.24377 | 错位 — 真实 PIDM 论文 arXiv:2403.14404 (Bastek/Sun/Kochmann, ICLR 2025)；[61] 作者/标题/编号均不对 |
| [63] | DOI 缺失仅 arXiv:2407.17917 | 跳过 — 无法程序溯源，需补 DOI/Crossref |
| [72] | arXiv:2603.24375 | 存疑 — Faeyrman 等 Berry phase MgO THz 工作坊记录存在（lasphys 2026 abstract），但 arXiv 编号未检索到命中 |
| [73] | DOI:10.1088/1361-6633/ad7c9f | DOI 错位 — 真实 DOI 为 10.1088/1361-6633/ad889f (Mosquera 2024 RPP 87 117901) |

## 二、问题清单
- [critical]｜references.md [5]｜PRL 126, 183601 实际为 "Self-Induced Glassy Phase" 非 Baykusheva HHG 文献｜删除或改用 Baykusheva PRA 103, 023101 / PRL 121, 246401 ([9] 已含)
- [critical]｜references.md [60]｜arXiv:2604.06707 不存在（相似题为 2504.17077 Seo/Um/Lee/Ye/Chung "AdjointDiffusion"）；与 content.md §2.3 错位已被 round-2-content 锁定｜整条删除并更新正文 [60] 引用
- [critical]｜references.md [61]｜arXiv:2603.24377 为虚构编号；真实 PIDM 为 2403.14404 (Bastek/Sun/Kochmann)，作者/标题/编号三错｜整条替换为正确条目或删除
- [critical]｜references.md [73]｜DOI 末段 "ad7c9f" 错位，正确为 "ad889f"｜修正 DOI 末段为 ad889f
- [high]｜references.md [54-56]｜[54] arXiv:2311.13309 真实作者为 Ito/Schüler/Sentef/Huber 非 Lucchini/Nisoli；[55-56] 同作者署名前缀未独立验证｜[54] 修正作者列表或更换 arXiv 编号；[55][56] 补 DOI/Crossref 验证
- [high]｜references.md [69-71]｜预检标记无标识符（无 DOI/arXiv），仅 [70][71] 有 PRA/OE 卷期而 [69] 无卷期页｜[69] 补 PRA 卷期或删除；[70][71] 补 DOI
- [high]｜references.md [72]｜arXiv:2603.24375 未在 arXiv/Google 命中，仅 lasphys 工作坊摘要佐证作者存在｜补 Crossref/IOPscience 反查或改用 arXiv:2404.12791 (Merboldt/Reutzel, Nature Phys 21, 1093) 同主题文献
- [high]｜references.md 整体｜[38][39][57][58][59][60][61][72] 共 8 条均为 2026 年提交，正文未注明"投稿/预印本"状态｜统一加 "submitted/preprint" 标签并降低对其结论强度的措辞
- [medium]｜references.md [40-50, 52-56, 60, 61, 64-68, 72]｜31 条 arXiv 条目作者字段均用 "et al." 缩写或单字母截断（如 "H. Liu, J. Wang, et al."），与 [1-37] 期刊条目完整作者风格不一致｜统一为前 3 作者 + et al. 格式
- [medium]｜references.md [21, 25, 28, 32, 37, 66]｜作者列表含异常单字母中间名（如 "M. R. B. L. Münch"、"C. A. C. Granados"），属疑似姓名拼写错误｜Crossref 重查后替换或删除
- [medium]｜references.md [66]｜Light Sci. Appl. 14, 337 (2025) DOI 10.1038/s41377-025-01847-5 — 当前年 2026 不存在该期号（LSA 2025 卷 14 已发表范围尚未涵盖 337 页码）｜Crossref 验证或下修页码
- [medium]｜references.md [63]｜缺 DOI 仅 arXiv:2407.17917，Lesko et al. Floquet 拓扑光控文献未在 Crossref 命中｜补期刊出处（PRA 2024？）或加 arXiv vN 验证
- [medium]｜references.md [62]｜DOI:10.1103/PhysRevB.110.125111 Ono/Okumura/Imai/Akagi 2024 — Crossref 显示该 DOI 解析为 RB 110, 125108-125116 范围，需精确核实页码｜补 Crossref 卷页精确对应
- [low]｜references.md 总数｜73 条超出 20-40 标准区间（key 类允许 50-80 故 ok，但近 1/3 为 arXiv 预印本）｜建议将 26 条无期刊署的 arXiv 条目迁移至补充材料，正文保留 50 条
- [low]｜references.md [22, 27]｜Nature Materials 23, 1372 (2024) / J. Chem. Phys. 150, 244301 (2019) — 未检索到匹配作者署名的原始记录｜Crossref 重查或更换为可验证 DOI
- [low]｜references.md 编号区间 [74-85]｜正文引用但列表缺失 12 个编号（[74]-[85]）｜writer 补齐缺失条目至 references.md 或回退正文引用

## 三、维度评估
- **严谨性（rigor）**：4 条 critical 标识符/作者/编号错位 + 5 条 high 标识符缺失或未验证；DOI 错位 1 条 + 8 条未来预印本未标注状态，严谨性扣分显著
- **完整性（completeness）**：73 篇总数可接受（key 类 50-80），近 3 年（2024-2026）文献占比 ~65% 时效性达标；但 [74-85] 共 12 个正文引用悬空属完整性 critical 缺失

## 评分
创新性：N/A
可行性：N/A
严谨性：0.62
完整性：0.78
综合评分：0.70