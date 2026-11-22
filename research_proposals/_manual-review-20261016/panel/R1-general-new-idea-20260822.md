# R1 科学性评审 — general-new-idea-20260822

- 评审人：R1（科学性，强场超快光学/凝聚态方向 PI）
- 评审日期：2026-10-16（落盘 2026-10-18）
- 评审对象：`04_proposal/sections/` 四模块（rationale / content / scheme / references），r2 版本
- 预存在缺陷核实：死条目 [27] + 超界引用 [100]（连同科学性一并核实）

## 总评分（五项明细）

**总评分：0.78**（rigor 五项过三：①✓ ②✗ ③✗ ④✓ ⑤✓；锚定纪律：过三=0.78，禁折中）

| # | 核查项 | 判定 | 依据 |
|---|--------|------|------|
| ① | 数值链一致 | 过 | 复算全部通过：SNR 链（10² counts/s×60 s→泊松 1.3%→差分 0.55→√30 单元→3:1）、脉冲能量（0.15–2.4 μJ @ 1/e² 半径 25–50 μm）、温度点阵（15+5+4=24 点、顺磁 6 点）、三光子能量导数 0.41 eV/μm（=3×hc/λ²，自洽但符号表述模糊，R1-06）、H_SF=√(2H_E H_A)≈14 T>7 T、MCMC 4×10⁴ CPU·h |
| ② | 指标定义可操作 | **未过** | R1-01（目标 1 校核线 Γ–M 躺在自设 k_z=0 节点面内，g 波劈裂为零，且 Osumi 实测峰位在 Γ–L 切，"逐点对照劈裂幅值"物理上不可能成立）；其余指标（σ_posterior 与 δ 双量纲、κ 三档、6–13 阶复现 ≤10%、偶次 <1% 内参）定义清晰可操作 |
| ③ | 文献支撑真实 | **未过** | R1-02（死条目 [27]，正文四文件零引用）、R1-03（超界 [100]，实为密勒指数被误判为引用格式）；量化锚文献本身（[3][13][21] 等）全部核实为真，无伪造 |
| ④ | 逻辑闭环 | 过 | "理论正演→实验验证→定量反演"单向递进链产出-输入关系明确；可辨识性三档、产额三步对策、SOC 双工作点、失败收口（边界界定报告替代含糊失败）完整自洽 |
| ⑤ | 模块自洽 | 过 | rationale/content/scheme 间 0.3–0.8 eV 劈裂、T_N≈310 K、0.41 eV 光子、SNR≥3:1、κ<10²、复现判据口径一致；"自旋分辨"命名落差已在文内自我声明（R1-04，minor 不整项扣） |

**与 monitor 0.84 的差异说明**：扣分集中在 ②（校核线物理选址错误，R1-01）与 ③（两类引用格式缺陷），均为可复核的客观问题。

## 意见清单

- [R1-01|major] content §2.1 目标 1｜校核线选址物理错误｜Γ–M 高对称线躺在自设 k_z=0 节点面内，g 波劈裂为零，无法对照文献幅值｜原文："模型校核沿 Γ–M 高对称线（g 波节点面外的一般动量方向）……与 Osumi 等人[13]……劈裂幅值峰位逐点相对偏差不超过 10%"｜修改建议：rationale §2 自设节点面含"k_z=0 面"；Osumi 的 0.8 eV 峰位实测在 Γ–L 切非高对称动量点（k_z≈0.5π）。校核线改为 Γ–L 切非高对称动量点（对齐 Osumi cuts 2–4）；同句"高对称线"与"一般动量方向"自相矛盾，一并修正。
- [R1-02|major] references [27]｜死条目｜题录存在但正文四文件零引用｜原文："[27] Li C, Hu M……Topological Weyl altermagnetism in CrSb. Commun. Phys., 2025, 8: 311"｜修改建议：在 rationale §4 "CrSb 对照体系提供体相动量空间完备数据[8-11]"处扩引为 [8-11,27]（Weyl 交变磁主题与上下文吻合），或删除该条并全文重编号。
- [R1-03|major] rationale §4｜超界引用 [100]｜实为晶向密勒指数被引用校验误判｜原文："Ba₂CaOsO₆……属纯 g 波原子反铁磁体，节点面沿 [100]、[010]"｜修改建议：密勒指数改用晶向族记法"沿 ⟨100⟩ 与 ⟨010⟩ 晶向族"或以 LaTeX 行内转义（\([100]\)），消除 [100] 被解析为文献引用的歧义。
- [R1-04|minor] content 目标 2 vs scheme §3｜"自旋分辨"命名落差｜装置仅有偏振分析通道，自旋信息经正演模型映射推断而非直接探测｜原文："在 MnTe 单晶中实现自旋分辨 HHG 测量"｜修改建议：改称"自旋敏感的偏振分辨 HHG 测量"；文内"该映射的唯一性以可区分判据为前提"的声明保留并前置到目标处。
- [R1-05|minor] rationale §2、scheme 全篇｜T_N 取值偏差｜申请书通篇 310 K，Osumi 原文为 307 K；5 K 步长相变加密采样下 3 K 偏移影响邻域点归属｜原文："MnTe 奈尔温度约 310 K"｜修改建议：改"约 307–310 K"，并保留"以自家 SQUID 实测值（±2 K）为准"机制（正文已有，补数值出处 [13]）。
- [R1-06|minor] scheme §3 温漂段｜导数符号定义模糊｜dE/dλ≈0.41 eV/μm 未写明为三光子总能量导数（单光子仅 0.14 eV/μm）｜原文："三光子过程对波长的灵敏度 dE/dλ ≈ 0.41 eV/μm"｜修改建议：符号改 d(3ℏω)/dλ ≈ 0.41 eV/μm；后文 ±0.25 μm 补偿 0.1 eV 漂移的换算（0.25×0.414≈0.10 eV）自洽，无需改动。
- [R1-07|minor] scheme §3 泵浦-探测段｜"激发磁相变"表述偏强｜0.1–1 mJ/cm²（≈0.003–0.033 TW/cm²）泵浦远低于 HHG 驱动窗口，属微扰探测｜原文："3 μm 中红外泵浦脉冲……激发磁相变动力学"｜修改建议：改"探测磁相变临界动力学与自旋进动"，与目标 4"临界慢化"表述对齐。
- [R1-08|info] references｜量化锚全部属实｜[13] 0.8 eV 劈裂/Γ–K 0.3 eV SOC 能隙/1.3 eV 带隙、[3] 0.30 eV 基频+6–13 阶谱窗、[21] RuO₂ 题录经三源交叉确认；APS 短式 DOI（10.1103/9gv7-vhxw 等）合法｜建议：理论-实验-反演三层框架与失败收口设计是本申请书的相对强项，修复上述 3 项 major 后科学性骨架成立。

## 量化锚核实记录（证据 URL）

1. **[13] Osumi et al., PRB 109:115102 (2024)** — 全文核实（arXiv:2308.10117v2）。摘要与正文证实："The magnitude of the splitting reaches **0.8 eV** at non-high-symmetry momentum points……much larger than the spin-orbit gap of **~0.3 eV** along the ΓK high-symmetry cut"；"total band-gap size of **~1.3 eV**"；**T_N = 307 K**。关键定位：0.8 eV 峰位沿 **Γ–L 切**（k_z≈0.5π），bands 3/4 最大 ~1.0 eV（k_z≈0.7π）；原文明确"须沿非高对称切观测交变磁劈裂"。→ R1-01、R1-05 依据。
   - https://arxiv.org/html/2308.10117v2
2. **[3] Liu et al., Nat. Phys. 13:262–265 (2017)** — Nature 官方页摘要证实"even and odd harmonics extending to the **13th order**"；驱动参数经第三方综述复认："HHG spectrum from monolayer MoS₂……the sixth to the 13th harmonics of the driving light centered at a photon energy of **0.30 eV**"（图 1 复制自 Liu et al. 2017），幂律 I^3.3 非微扰标度同源确认。目标 1 复现判据锚（基频 0.30 eV、谱窗 6–13 阶）**完全属实**。
   - https://www.nature.com/articles/nphys3946
   - https://www.frontiersin.org/journals/nanotechnology/articles/10.3389/fnano.2025.1667217/pdf
3. **[21] Liu Y.Q. et al., PRB 112:L081105 (2025)（RuO₂ 交变磁 HHG 判据）** — Crossref DOI 反查命中（10.1103/9gv7-vhxw，兰州大学 Si 组，文章号 L081105，题名逐字吻合），NSFC 11874189 资助。真实。
   - https://api.crossref.org/works/10.1103/9gv7-vhxw
4. **[27] Li et al., Commun. Phys. 8:311 (2025)（死条目核实）** — 本地 grep：除题录行外，四模块正文无任何 "[27]" 出现（rationale.md:53 的命中为密勒指数 [100]）；死条目定性成立。超界 "[100]" 同源定位为"节点面沿 [100]、[010]"的晶向记法，非文献引用。→ R1-02、R1-03 依据。
   - 本地核查：`research_proposals/optimizing/general-new-idea-20260822/04_proposal/sections/rationale.md` L53
