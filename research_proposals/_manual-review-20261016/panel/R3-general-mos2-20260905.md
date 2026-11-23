# R3 引用审校 — general-mos2-20260905

审校范围：04_proposal/sections/{rationale,content,scheme,references}.md（refs 41 条，[1]–[41] 连续无跳号；无 P0 清单，按常规审校）。
审校日期：2026-10-17。对账脚本：/tmp/r3_citation_audit.py（终端执行故障，以等价正则提取+人工比对完成，脚本可复跑复核）。

## 编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 占位符 | 0 | 无未填编号 |
| 死条目 | **1** | **[6] H. Kim et al., ACS Photon. 4, 1627 (2017) 三章零引用**（rationale/content/scheme 逐行正则提取确认，无 [6] 单引、无含 6 的区间/列表 token）。且 refs 尾注声称"剩余 39 条承担论证主链，全部按编号被引用、无未引用条目与跳号"——声明被实物证伪（[6] 既未引用也未进入"[2][7] 背景文献"豁免清单） |
| 超界 | 0 | 正文最大引用号 41 = refs 最大号 |
| 一号两用 | 0 | refs 每编号唯一条目 |
| 断链 | 0 | 正文引用编号在 refs 全部有对应条目 |

附注：refs 尾注自认"本表 41 条超出区间上限 1 条（参考体量 30—40 条）"。删除死条目 [6] 后恰回落 40 条上限内，与该待办一并化解。

## 联网核实记录（7 条：被引最多+支撑关键判据+近年抽查，含证据 URL）

1. **[15] Peterka, APL Photonics 8, 086103 (2023)（被引最多，方向一激子基线支柱）**：真实 ✓。Charles 大学组，标题 "High harmonic generation in monolayer MoS2 controlled by resonant and near-resonant pulses on ultrashort time scales"，0.62 eV 中红外驱动+共振/近共振预激发 pump-probe，与正文"A 激子近共振抑制、瞬态吸收对照"声称匹配 ✓。https://pubs.aip.org/app/article/8/8/086103/2905253 ；https://physics.mff.cuni.cz/kchfo/ooe/publ_en.htm
2. **[22] C. Ma, PRL 135, 166902 (2025)（短 DOI 10.1103/kskc-qlb3 可疑项）**：真实 ✓。"Phase Matching of High Harmonic Generation in Twisted van der Waals Crystals"，Chenju Ma, Chen Huang, +12, Kaihui Liu（北大），2025-10-15 刊出；APS 新短 DOI 格式有效。扭转相位匹配主题与正文"扭转相位匹配补偿动量失配"匹配 ✓（"5 阶效率 4×10⁻⁵"数值在原文正文，未从摘要复核，无矛盾迹象）。https://www.semanticscholar.org/paper/3a469d4259429aca13e150ed8195d5d7397a3cf0
3. **[17] Nebgen, Sci. Adv. 12, eadz5621 (2026)（2026 新条目抽查）**：真实 ✓。"Isostructural electronic transition in MoS2 probed by solid-state high-harmonic generation spectroscopy"，2026-03-18，DAC 中 2H-MoS₂ 加压 30 GPa，K→Γ 带隙交叉致谐波强度尖锐极小+偏振各向异性旋转 30°，与 rationale L77 声称匹配 ✓。https://www.science.org/doi/full/10.1126/sciadv.adz5621
4. **[21] V. Chang Lee, Nat. Commun. 15, 6228 (2024)**：真实 ✓。作者 Victor Chang Lee, Lun Yue, Mette B. Gaarde, Yang-hao Chan, Diana Y. Qiu，卷期页 DOI 与条目一致；多体（GW）增强 MoS₂ HHG 主题匹配 ✓。https://par.nsf.gov/biblio/10536769
5. **[25] X. Liu, APL 126, 191101 (2025)（国内工艺引用）**：真实 ✓。华科超快光学实验室（组主页直接托管该文 PDF），作者 Xuyang Liu…Xiaosong Zhu, Pengfei Lan, **Peixiang Lu**——正文"Liu 等人[25]（陆培祥团队）"归属正确 ✓；DBR 半开放腔增强 2D TMD HHG 与正文"DBR 弱信号增强"匹配 ✓。https://ufolab.phys.hust.edu.cn/191101_1_5.0266306.pdf
6. **[26] S.-Q. Hu, PNAS 121(6), e2316775121 (2024)**：真实 ✓。"Solid-state high harmonic spectroscopy for all-optical band structure probing of high-pressure quantum states"（H₃S 理论），"理论角度给出 HHG 探测高压能带变化的方法学路线"声称完全匹配 ✓。https://www.pnas.org/doi/full/10.1073/pnas.2316775121
7. **[39] M. Kim, Nat. Commun. 16, 9825 (2025)（2025 条目抽查）**：真实 ✓。"Quantum interference and occupation control in high harmonic generation from monolayer WS2"（MPSD 出版列表，作者链 M. Kim, T. Kim, A. Galler, D. Kim, A. Chacon… 与条目一致）；微扰区谷间多光子共振增强+强场区占据控制与 rationale L45 声称匹配 ✓。https://www.mpsd.mpg.de/1119849/publications?print=yes

## 正文声称与文献内容匹配性抽查

- ✓ 匹配：[15] 0.62 eV 驱动/共振预激发/非单调抑制；[22] 扭转相位匹配；[17] 压致强度极小+偏振旋转；[21] 多体增强；[25] DBR 增强+团队归属；[26] 高压理论路线；[39] WS₂ 量子干涉与谷占据。
- △ 弱匹配：scheme L93 "Nebgen 等人[17]在金刚石压腔中**以约 100 fs 分辨追踪体相 MoS₂ 谐波强度随压力的瞬态响应**"——论文为 DAC 稳态逐压力点测量（sHHG 谱学），"100 fs 分辨/瞬态响应"表述超出论文工作方式（见 R3-02）。
- 其余抽查（[28] Patra & Cocchi arXiv:2607.19937 已接收 PRB、[37] Bondy EPJ D 78, 106 已刊版）：条目自带的"下轮联动改写"待办与实物一致（scheme L73 仍内联 arXiv:2404.02985 旧号，R3-03）。

## 意见清单

[R3-01|high] references｜L13 条目 [6]｜[6] H. Kim 三章零引用为死条目，尾注"全部按编号被引用"声明被证伪｜原文摘录："剩余 39 条承担论证主链，全部按编号被引用、无未引用条目与跳号"｜删除 [6]（41→40 条，同步化解自认的超限 1 条），尾注声明按删除后实物重写。

[R3-02|low] scheme｜L93｜[17] 被述为"以约 100 fs 分辨追踪…瞬态响应"，论文实为 DAC 稳态逐压力点 sHHG 测量｜原文摘录："以约 100 fs 分辨追踪体相 MoS₂ 谐波强度随压力的瞬态响应"｜改"在金刚石压腔中逐压力点记录体相 MoS₂ 谐波强度与偏振（压致强度极小+偏振旋转 30°）"，删"100 fs 分辨/瞬态"限定。

[R3-03|low] scheme+references｜sch L73、refs L77｜[37] Bondy 已刊 EPJ D 78, 106 (2024) 且 refs 已换正式版，但 scheme 正文仍内联旧 arXiv:2404.02985 号（条目自记待办未执行）｜原文摘录："Bondy 等人[37]（arXiv:2404.02985）的三边带 RABBITT 计算"｜删除括注 arXiv 号改纯编号引用，执行条目内自记的联动改写。

## 结论

三个课题中引用质量最好的一份：联网核实 7 条（含 5 条 2024–2026 近年条目）全部真实可溯、作者链卷期页可信、正文声称与文献内容匹配度高，无虚构、无错挂作者。唯一结构性问题是 [6] 死条目与尾注"全部被引用"的自证矛盾（连带 41 条超限），删除即收敛；另有两处 low 级措辞/联动待办。
