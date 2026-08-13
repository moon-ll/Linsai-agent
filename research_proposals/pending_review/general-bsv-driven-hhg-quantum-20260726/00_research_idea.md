# 课题设想

**最后更新**：2026-08-13

## 标题

量子光场驱动的固体高次谐波产生：BSV 作为多体态的非经典探针

## 研究背景与动机

量子光场驱动的高次谐波产生（HHG）是将量子光学与强场超快光学交叉的前沿方向。2024 年 Rasputnyi 等首次实验观测到明亮压缩真空（BSV）驱动的固体 HHG [arXiv:2403.15337]，Even Tzur / Gorlach 等则建立了任意量子光态驱动 HHG 的高次谐波量子态公式 [PRR 6, 033079 (2024)]。本项目在此基础上提出：用 BSV 驱动固体/二维材料产生 HHG，验证其能否对多体关联提供经典光 HHG 无法达到的灵敏度，据此建立"量子光 HHG 作为多体态非经典探针"的方法学。

## 现存研究空白或瓶颈

- **物理层·机制空白**：BSV 驱动 HHG 的微观机制（带间/带内贡献如何受光子统计影响）尚未建立；Even Tzur 2024 框架基于气体原子体系，尚未推广到固体多带多体。
- **物理层·材料空白**：BSV HHG 在不同关联强度材料（弱关联 TMDC、中等关联莫尔超晶格、强关联 Mott 绝缘体）中的响应未知。
- **方法学层·框架空白**：量子光 HHG 作为多体态探针的系统方法论尚未形成——QEF、量子指纹 $Q_F$ 等核心概念虽有部分定义，但跨体系、跨观测量的统一测量协议仍待建立。

## 拟开展研究内容和方案

### 总体目标

以 BSV 驱动的固体 HHG 为核心手段，建立"光源—实验—理论—反演"四位一体研究框架，验证 BSV-HHG 对固体多体关联的探针有效性，凝练可证伪、可迁移的量子光 HHG 探针方法学。

### 研究内容（六子方向串联式）

1. **BSV 光源构建与经典场对照体系**（2.1）：波长 0.8–1.5 μm、脉宽 < 50 fs、单脉冲光子数 $10^{13}$ 量级；分别复现非简并 PDC（$g^{(2)}(0)=2$）与简并 PDC（$g^{(2)}(0)=3+1/N$）双配置基线；建立同平台经典相干态对照光路。
2. **量子光场驱动固体 HHG 实验**（2.2）：单层 MoS₂/WSe₂ BSV-HHG 谱测量，谐波延伸至 7–13 阶（光子能量 8–20 eV，VUV-EUV 低能端），与经典光同条件对比。
3. **量子光 SBE 理论模型**（2.3）：将 Even Tzur 2024 的 winding trail 量子态模型从气体原子拓展到固体多带多体，结合 Rivera-Dean Bloch 形式化与 Peschel 紧束缚实空间方案。
4. **多体态探针有效性验证**（2.4）：三类对照体系（弱关联 TMDC / 中等关联莫尔 / 强关联 Mott）QEF 三维度标定——$QEF_{\rm vis}$（干涉可见度比）、$QEF_{\rm yield}^{(q_{\rm ref})}$（单阶产额比，主指标）、$QEF_{\rm yield}^{(\sum)}$（全谱求和比，辅助指标）；设置 No-Go 降级判据。
5. **BSV-经典光双光路 Mach-Zehnder 干涉**（2.5）：提取量子指纹 $Q_F$，自洽性检验为 BSV 退化为相干态时 $Q_F \to V_{\rm classical} \approx 1$（非 0）。
6. **参数依赖性系统研究 + Y4 反馈式升级**（2.6）：$(r, \theta_{\rm sq}, g^{(2)}(0))$ 三维 mapping（Y1–Y3 主任务）；Y4 后段反馈式升级为 contingent 可选项。

### 特色与创新点

- **系统化**：首次将 BSV-HHG 从单点实验推进为覆盖"光源—实验—理论—探针—指纹—参数依赖"的完整链条。
- **探针化**：首次建立 QEF 三维度指标体系（两个核心指标 $QEF_{\rm vis}$、$QEF_{\rm yield}^{(q_{\rm ref})}$ 加一个辅助指标 $QEF_{\rm yield}^{(\sum)}$），为 BSV-HHG 在不同关联强度材料中的灵敏度提供量化标尺。
- **量子化**：BSV-经典光双光路 Mach-Zehnder 干涉方案提取纯量子指纹 $Q_F$，与 Boroumand 2025 的 QSHHG 单束双色场方案在实验实现上独立。

## 拟采用技术路线

- **实验路线**：高增益 PDC 产生 BSV → 单模光纤模式清洁 → 同平台经典光对照光路（电控切换）→ 单层/莫尔/Mott 样品 HHG 测量 → 双光路 Mach-Zehnder 干涉提取 $Q_F$ → $(r, \theta_{\rm sq}, g^{(2)}(0))$ 主动参数扫描。
- **理论路线**：Even Tzur 2024 winding trail 形式化 → 固体多带拓展（引入晶体动量、Berry 相位、激子效应）→ SBE-Q 密度矩阵求解 → 贝叶斯后验 + PINN 反演。
- **能量范围**：单层 TMDC 在近红外 0.8–1.5 μm 驱动下，HHG 谱延伸至 7–13 阶（8–20 eV，VUV-EUV 低能端），与 Iglesias 2024 和 Liu 2017 的实验观测一致。

## 创新点

见上"特色与创新点"三条。

## 来源与可靠性

核心引文均已有正式发表版本或同行评审基线（截至 2026-08-10 经 arXiv API + Crossref 联合核实）：Iskhakov 2012（*Opt. Lett.* 37, 1919, DOI 10.1364/OL.37.001919）、Spasibko 2012（*Opt. Express* 20, 7507, DOI 10.1364/OE.20.007507, arXiv:1201.0367）、Wu/Schafer/Gaarde 2016（*Phys. Rev. A* 94, 063403, DOI 10.1103/PhysRevA.94.063403, arXiv:1609.09852）、Silva 2018（*Nat. Photon.* 12, 266, DOI 10.1038/s41566-018-0129-0）、Murakami 2018（*PRL* 121, 057405, DOI 10.1103/PhysRevLett.121.057405）、Liu 2017（*Nat. Phys.* 13, 262, DOI 10.1038/nphys3946）、Even Tzur 2024（*PRR* 6, 033079, DOI 10.1103/PhysRevResearch.6.033079, arXiv:2311.11257）、Peschel 2022（*PRB* 106, 245307, DOI 10.1103/PhysRevB.106.245307, arXiv:2205.00522）、Raab 2024（*Rev. Sci. Instrum.* 95, 073004, DOI 10.1063/5.0212578, arXiv:2405.11859）、Hu 2024（*PNAS* 121, e2317656121, DOI 10.1073/pnas.2317656121）、Boroumand 2025（*PRL* 134, 113602, DOI 10.1103/PhysRevLett.134.113602, arXiv:2505.22536）。已升级为正式发表版的预印本：Rasputnyi 2024（*Nat. Phys.* 20(12), 1960-1965）、Prajapati 2024（*PRB* 113(4)）、Even Tzur & Cohen 2023（*Light: Sci. Appl.* 13, 8）、Wang et al. 2024（*PRA* 112, 013105）。仍为 arXiv 预印本、提交前需再次核实的：Li 2022（arXiv:2205.11161）、Wu 2024（arXiv:2311.16655）、Rivera-Dean 2023（arXiv:2309.14435）、Borrego-Varillas 2026（arXiv:2604.15085）、de-la-Peña 2024（arXiv:2409.13614）、Jiang & Dorfman 2023（arXiv:2311.10390）、Gothelf 2025（arXiv:2502.11803）、Lange 2025（arXiv:2503.15932）、Even Tzur 2025（arXiv:2502.09427）、Wang 2025（arXiv:2509.13518）。参考文献完整列表与正文→编号映射表见 04_proposal/sections/references.md（35 条：正文核心 18 篇 + 方法学手册补充 9 篇 + 近期量子光 HHG 4 篇 + 2025 关键量子光 HHG 4 篇；25 条已正式发表，10 条仍为预印本）。QSHHG 缩写为本项目对 Boroumand 2025 量子工程化 HHG 框架的中文简称，原文未使用此缩写，已在 references.md [15] 备注中明示，并在 rationale.md §1.4 第三段创新点 3 末尾补正式声明。

国内 BSV-HHG 检索证据（rationale.md §1.1 段 4）：2026-08-03 在 arXiv / WoS / CNKI 以"bright squeezed vacuum"、"BSV HHG"、"quantum light HHG"、"明亮压缩真空高次谐波"、"非经典光高次谐波"等关键词组合检索，命中 47 篇（arXiv 31 / WoS 11 / CNKI 5），国内团队仅 2 篇（均与本课题无直接相关性）。检索报告归档于方法学手册附录 B。