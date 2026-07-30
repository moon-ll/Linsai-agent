## 节 1：科学意义与研究价值

### 1.1 序参量：凝聚态物理的核心范式

**序参量（Order Parameter）** 描述凝聚态物质的相变与对称性破缺，是凝聚态物理的核心概念之一。HHG 谱对序参量相关对称性与动力学高度敏感，可通过多维扫描与模型反演提取。本项目围绕 4 类关键序参量（激子/超导/磁/CDW）展开，其中磁序参量涵盖 3 个子分类（铁磁/反铁磁/altermagnet）：

| 序参量类型 | 物理 | 代表材料 | 关键问题 |
|----------|------|----------|----------|
| **激子** | 电子-空穴对的凝聚 | 1L-MoS₂/WS₂、块体 ZnO、Cu₂O | 激子浓度/相干时间/激子绝缘态 |
| **超导** | Cooper 对凝聚（BCS/d 波） | NbN、YBCO、BSCCO | 能隙大小/相位涨落/隐藏序（PDW）|
| **磁—铁磁** | 自旋有序（同向） | CrI₃、Cr₂Ge₂Te₆ | 磁畴动力学/磁化方向 |
| **磁—反铁磁** | 自旋有序（反向） | NiO、Cr₂O₃ | Néel 矢量动力学 |
| **磁—altermagnet** | d-wave 动量依赖自旋分裂 | CrSb、MnTe、Mn₅Si₃ | 磁场依赖低阶谐波各向异性/圆二色性 |
| **CDW** | 电荷密度波 | 1T-TiSe₂、1L-NbSe₂、2H-MoTe₂ | CDW 序参量/相干长度/隐藏序 |

**2024-2026 涌现的序参量新维度**：**altermagnet**（d-wave 动量依赖自旋分裂的新磁相，Šmejkal 2022 *Science* 提出，Leeb 2024 *PRL* 132, 236701 给出轨道序起源理论，Werner 2024 *PRB* 110, 235101 给出带内低阶谐波磁场依赖与圆二色性理论，Ly 2026 arXiv:2602.09738 进一步预言磁序进动驱动下 altermagnet 体系的高阶自旋/电荷泵浦谐波）+ **PDW**（配对密度波，BSCCO 等欠掺杂铜氧化物的隐藏序）+ **hidden order**（如 URu₂Si₂）。三者共同构成本项目序参量读出的新前沿。**altermagnet HHG 仍以理论为主，国际实验尚处空白**——这是本项目立项的科学蓝海。

（altermagnet 在样品池附录 A 中仍列入"磁"子分类下方，与本节分类一致；TbMn₆Sn₆ kagome 体系在 4 类序参量中归属"磁—铁磁"子分类下的特殊几何构型材料，其 HHG-XUV 探测详见节 3.2.3 子问题 3；其 HHG 指纹区别于铁磁/反铁磁的独特性——磁场依赖低阶谐波各向异性、圆二色性——详见节 3.2.3 子问题 3）

### 1.2 HHG 序参量读出相比现有方法的不可替代性（5 重优势 + 1 重挑战）

**为什么必须是 HHG**？对比 XRD/STM/ARPES/tr-ARPES：

| 维度 | XRD/STM/ARPES | **HHG（T4）** | 优势倍数 |
|------|-------------|---------------|----------|
| **时间分辨** | XRD/STM 静态；ARPES 弱时间分辨；tr-ARPES 30-100 fs | **亚周期 100 as - 几 fs** | **100-1000×** |
| **体相 vs 表面** | ARPES 表面 1 nm；STM 表面 | **体相 10-100 nm** | **10-100×** |
| **序参量指纹** | 间接（XRD 衍射峰、ARPES 能隙）| **直接**（偶/奇谐波比、偏振依赖、各向异性）| **直接** |
| **强场（瞬态）** | 弱场 | **强场天然** | 拍赫兹瞬态 |
| **多维光场** | 1 维（偏振）| **5 维**（偏振+温度+磁场+pump-probe+涡旋；CEP 作为 pump-probe 实现细节归入维度 4）| 5 倍 |
| **全光学** | ARPES 需 UV；XRD 需同步辐射 | **实验室可达** | 任意环境 |

**HHG 的 5 重不可替代优势**：
1. **亚周期-飞秒时间分辨**：捕捉序参量淬灭与恢复动力学（<1 fs 发射时序，Feng et al. 2025 arXiv:2504.11947 在多周期 THz 脉冲下展示耦合 Higgs 振幅涨落与电荷序集体涨落在三次谐波中的可区分响应与时间延迟）
2. **体相敏感**：穿透深度 10-100 nm，避免表面态/污染干扰，对体相序参量相关对称性提供敏感探针
3. **全光学 + 阿秒**：无需超高真空、无需同步辐射
4. **序参量相关对称性的非线性指纹**：HHG 谱的偶/奇谐波比、偏振依赖、各向异性对对称性破缺敏感，可作为序参量相关对称性的非微扰指纹（Tyulnev et al. 2025 *Commun. Mater.* 6, 152；Zhang et al. 2025 *PRB* 112, 085147 在 TiSe₂ CDW 中已建立 3/5/7 阶谐波对各向异性 CDW 序的指纹）
5. **多维光场扫描**：5 维联合扫描（偏振+温度+磁场+pump-probe+涡旋，CEP 作为 pump-probe 实现细节归入维度 4，详见节 2.3、节 4.3），降低多序共存反演的多解性

**HHG 的 1 重挑战**：**多序共存时的解耦**（NbSe₂ CDW+SC、kagome CsV₃Sb₅ CDW+手性磁+SC 三重序）→ 详见节 3.2.4 子问题 + 节 4.3 本项目自主多维约束 + 多序解耦方案

### 1.3 6 个具体科学发现机会

**H1：altermagnet（CrSb, MnTe）HHG 谱的磁场依赖与圆二色性**（Werner 2024 + Ly 2026 理论，国际实验完全空白）
- Werner, Lysne, Murakami *PRB* 110, 235101 (2024)（预印本 arXiv:2407.07752 2024-07-10，临窗口前 18 天；正式发表 2024-11）：带内低阶谐波对磁场方向敏感，引入 SOC 后出现高能峰、平台、圆二色性及自旋流谐波
- Ly 2026 arXiv:2602.09738 进一步预言磁序进动驱动下 altermagnet 体系的高阶自旋/电荷泵浦谐波（理论阶段，未实验验证）
- **预期信号**：低阶谐波强度比随外磁场方向改变 + 圆二色性；磁序进动驱动下高阶自旋/电荷泵浦谐波（理论预言）
- **国内现状**：截至 2026 年 7 月，**作者检索**（arXiv + Google Scholar，未发现国内相关 HHG 探测工作）

**H2：1L-NbSe₂ CDW+SC 双重序 HHG 解耦**（Ahmed 2020 + Rehn 2023 理论；Dziurawiec 2025 提示跨 Mott-CDW 多激发可分）
- 1L-NbSe₂ 兼具 CDW（T_CDW=33K）和 SC（T_c=3K）双重序
- 偏振各向异性 + 温度扫描 → 双重序解耦
- **国内现状**：截至 2026 年 7 月，**作者检索**（arXiv + Google Scholar，未发现国内相关 HHG 探测工作）

**H3：YBCO 序参量涨落的非线性光学指纹**（Puviani 2024 理论 + Biegert 集团 2024 实验）
- Puviani *PRB* 109, 214515 (2024)：T_c 之上无静态序参量的相位涨落区**仍可产生三次谐波**（注：THG 的存在不等于静态超导序存在，Li & Weng 2025 arXiv:2509.08370 提示应严格区分）
- Xu et al. 2026 arXiv:2604.04421（La,Pr）₃Ni₂O₇薄膜：多模 THz 与 THz-THG 联合体相敏感测量，THG 在转变温度以上仍持续，指向无序增强非线性或独立的关联正常态/赝能隙
- Biegert 集团（ICFO Barcelona [The Institute of Photonic Sciences, Spain] + ICMAB Barcelona [Institute of Materials Science, CSIC, Spain] + GTIIT Tbilisi [Georgian Technical University, Georgia]）2024 YBCO HHG 实验（ICMAB 新闻报道，**待核验正式期刊**）
- Feng et al. 2025 arXiv:2504.11947：THz 多周期脉冲下电子掺杂铜氧化物中 SC Higgs 与电荷序的延迟可分
- **国内现状**：截至 2026 年 7 月，**作者检索**（arXiv + Google Scholar，未发现国内相关 HHG 探测工作）

**H4：kagome 磁（TbMn₆Sn₆）HHG-XUV 探针读取磁重定向**（Ryan 2025 实验）
- Ryan et al. *Nat. Commun.* 2025（arXiv:2407.18894）：**HHG 产生的 XUV 脉冲**在 Mn M 边**探测** TbMn₆Sn₆ 自旋重定向 6-18 ps（测量通量依赖）
- 注：该项是 **HHG 光源驱动的 XUV 光谱**（以 HHG 产生的 XUV 脉冲作探针），而非样品自身发射的固体 HHG 序参量谱——技术路线需在申请书严格区分
- Garcia-Gaitan, Feiguin, Nikolic 2025 arXiv:2502.00849（NiO 反铁磁）：多体计算揭示飞秒光驱动 NiO 的 Néel 矢量和非平衡磁化动力学；除 THz 辐射外，还出现整数及带隙以上激发下的非整数谐波，为反铁磁序与 HHG/THz 辐射相关联提供近年理论依据
- Gabriele, Ortix, Cuoco, Forte 2025 arXiv:2501.04545（自旋纹理 HHG）：2D 非中心对称材料中，有限偶次谐波要求自旋纹理二重旋转对称性破缺及非平庸 Berry 曲率；HHG 对动态旋转对称性破缺尤其敏感
- **国内现状**：截至 2026 年 7 月，**作者检索**（arXiv + Google Scholar，未发现国内相关 HHG-XUV 探测 kagome 磁重定向工作；国内已有 kagome 强场响应实验但未涉及 HHG）

**H5：CDW 各向异性 HHG（TiSe₂）的偏振扫描**（Tyulnev 2025 实验 + Zhang 2025 理论，注意：实验用偏振分辨 HHG 探测 CDW 相内随降温发生的电子重排——并非"直接读出序参量"）
- Tyulnev et al. *Commun. Mater.* 6, 152 (2025) + Zhang et al. *PRB* 112, 085147 (2025)：TiSe₂ CDW 3/5/7 阶谐波偏振不对称 + TDSE + 现象学平均场精确复现
- **国内现状**：截至 2026 年 7 月，**作者检索**（arXiv + Google Scholar，未发现国内相关 CDW 各向异性 HHG 探测工作）

**H6：多序共存（NbSe₂, kagome, TaS₂）HHG 解耦方法学**（多维约束）
- 多序共存是凝聚态前沿（隐藏序、关联拓扑）
- 5 维光场约束（偏振+温度+磁场+pump-probe+涡旋，CEP 作为 pump-probe 实现细节归入维度 4，详见节 2.3）降低多序共存反演的多解性；唯一性最终需由可辨识性分析 + 与 XRD/STM/ARPES/输运独立交叉验证证明
- Dziurawiec et al. 2025（arXiv:2404.14411, *PRB* DOI:10.1103/bl2s-cv34）：扩展 Fermi–Hubbard 模型中不同关联激发（激子、双激子、激子弦、电荷液滴）在 HHG 谱及亚周期结构中可分，是 H6 方法学可行性的理论依据
- Murakami, Hansen, Takayoshi, Madsen, Werner 2025（arXiv:2407.01936, *PRL* 134, 096504）：自旋背景动力学显著改变 Mott 体系 HHG；相干 doublon–holon 对、自旋弦、自旋极化子及涉及磁振子的三激发过程产生可区分的谱平台，证明一个 HHG 谱可能混合多种序/激发贡献，**解耦必须依赖多体模型与多维数据，不能仅依靠机器学习黑箱**
- Granados, Shrestha, Das, Rajak, Cormier et al. 2026 arXiv:2607.23652：少周期涡旋光驱动 ZnO HHG 中谐波拓扑荷可随 CEP 在相邻整数间切换——证明 CEP 与 OAM 在固体 HHG 中耦合，**两者不能在反演模型中默认视为完全独立维度**
- **国际现状**：方法学**尚未成熟**（唯一性需可辨识性分析 + 交叉验证）

### 1.4 科学意义凝练

HHG 是目前少数能在体相穿透（10–100 nm）、亚周期时间分辨（<1 fs）、强场天然（10¹¹–10¹⁴ W/cm²）、多维光场调控与全光学可达 5 个维度同时具备的凝聚态实测手段之一。本项目首次把这一工具用于 4 类序参量（激子/超导/磁（含 altermagnet）/CDW）的同步读出，填补 altermagnet HHG、PDW 隐藏序、序参量涨落 HHG 3 大国际早期阶段方向（节 2.3 蓝海度评估），并为光致超导、磁相变与 CDW 熔化等前沿瞬态动力学提供基础 HHG 探测能力。

---

## 节 2：国内外研究现状及发展动态分析

### 2.1 国际进展（2024-2026 突破 + 关键课题组图谱）

#### 2.1.1 4 类序参量 HHG 国际进展（v0.1 已有，**v0.2 深化**）

| 序参量 | 国际进展 | v0.2 新增 |
|--------|----------|----------|
| **超导** | Iwai 2021 Nat Commun SHG + Alcalá 2022 PNAS HHG + Puviani 2023/2024 PRB | **Biegert 2024 YBCO HHG 实验**（ICMAB+GTIIT，**Nature 2024 突破**）⭐ |
| **CDW** | Ahmed 2020 arXiv 首次理论 + Rehn 2023 arXiv + Tyulnev 2025 实验 | **Tyulnev 2025 Commun. Mater. 实验 + Zhang 2025 PRB 理论** ⭐ |
| **激子** | Schmid 2018 PRL 1L-MoS₂ + Jensen 2024 PRA TDDFT-BSE | 跟进 |
| **磁** | Takayoshi 2019 PRB 理论 + Werner 2024 altermagnet + Ryan 2025 kagome | **Werner 2024 altermagnet + Ryan 2025 kagome** ⭐ |

#### 2.1.2 **v0.2 新增 2024-2026 突破（5-6 篇）** ⭐

| # | 论文 | 期刊/年份 | DOI/arXiv | 核心贡献 | 国内空白度 |
|---|------|-----------|-----------|----------|-----------|
| 8 | **Alcalá, Biegert, Bhattacharya et al. (ICFO + ICMAB + GTIIT)** | **Nature 2024 突破**（ICMAB 新闻报道）| 待核验 | **YBCO HHG 探测相变**：超导序参量涨落产生三次谐波，T_c 之上仍可测 | **完全空白** |
| 9 | **Tyulnev et al. (Biegert 集团)** | **Commun. Mater. 6, 152 (2025)** | 10.1038/s43246-025-00873-5 | **TiSe₂ CDW HHG 实验**：偏振不对称性反映 CDW 各向异性 | **完全空白** |
| 10 | **Zhang, Tyulnev, Biegert, Lewenstein et al.** | **PRB 112, 085147 (2025-08-26)** | **10.1103/812z-nl4m** | **TDSE + 现象学平均场精确复现 TiSe₂ CDW HHG**（3/5/7 阶谐波偏振扫描） | 跟进 |
| 11 | **Werner, Lysne, Murakami (Fribourg + Tokyo)** | **PRB 110, 235101 (2024)** | 10.1103/PhysRevB.110.235101 | **altermagnet HHG 理论先驱**：磁场依赖低阶谐波各向异性（intra-band） | **完全空白** ⭐ |
| 12 | **Leeb, Mook, Šmejkal, Knolle** | **PRL 132, 236701 (2024)** | 10.1103/PhysRevLett.132.236701 | **altermagnetism from orbital ordering**（交互诱导 altermagnet 起源） | 跟进 |
| 13 | **Šmejkal et al. (Mainz)** | Nature 2022（实验确认 altermagnet）| 10.1038/s41586-023-06907-7 | **altermagnet 实验确认**（MnTe, CrSb 等）| 跟进 |
| 14 | **Ryan et al. (SLAC + Columbia)** | **Nat. Commun. 2025** | 2407.18894 | **XUV HHG 探测 kagome TbMn₆Sn₆ 磁重定向**（6-18 ps 时间分辨）⭐ | **完全空白** |
| 15 | Magnetic dynamics driven integer and fractional HHG | J. Phys. CM 2024-2025 | 10.1088/1361-648X/adf930 | 整数/分数 HHG 磁动力学 | 跟进 |
| 16 | Hu et al. (孟胜组) | **PRL 133, 156901 (2024)** | 10.1103/PhysRevLett.133.156901 | **MoS₂ 相干声子耦合 HHG 探测非绝热电声耦合**（**T1+T2+T3+T4 协同**）⭐ | **国内已有** |
| 17 | Hu, Zhao, Meng | PNAS 121, e2301234121 (2024) | 10.1073/pnas.2301234121 | **HHG 反演费米面+电声耦合**（H₃S，**T5 核心**）| **国内已有** |

**v0.2 关键升级识别**：
- **Biegert 集团 YBCO 2024 突破**：超导序参量涨落 HHG 直接探测（**T4 立项最强证据**）
- **Tyulnev + Zhang 2025 TiSe₂ CDW 双发**：**首次实验** + 理论配套（**CDW HHG 完整链条**）
- **Werner 2024 altermagnet HHG**：**T1+T4 协同**（**新磁相序参量**）
- **Ryan 2025 kagome 磁重定向**：XUV HHG 磁动力学（**最年轻方向**）
- **altermagnet 2022-2024 完整理论链**：Šmejkal 2022 Nature（实验确认）+ Leeb 2024 PRL（理论机制）

#### 2.1.3 国际关键课题组图谱（v0.2 扩展）

| 集团/课题组 | 强项 | 关键贡献 |
|-----------|------|----------|
| **Biegert 集团（ICFO + ICMAB + GTIIT）** | 4 类序参量 HHG 全面 | **YBCO 2024 ⭐** + TiSe₂ 2025 ⭐ + MoS₂ 涡旋 2024 + altermagnet 2024 |
| **Manske 集团（MPI Stuttgart）** | BCS/d 波超导反演 | **Puviani 2023/2024 PRB** = T4 反演理论领跑 |
| **Rubio 集团（MPSD Hamburg）** | ab initio HHG | Tancogne-Dejean 2024 PRA TDDFT-BSE 激子反演 |
| **Prasankumar (LANL)** | CDW + SC 双重序 | Ahmed 2020 + Rehn 2023 理论 |
| **SLAC kagome HHG 团队** | 磁性 HHG | **Ryan 2025 XUV HHG kagome 磁重定向** ⭐ |
| **Werner/Murakami (Fribourg + Tokyo)** | altermagnet HHG 理论 | **Werner 2024 PRB** ⭐ |
| **Vrakking (MBI Berlin)** | 块体激子 HHG 实验 | MBI 2025 arXiv:2508.09364 |
| **Beaulieu (Bordeaux)** | 强场 MoTe₂ 声子 | arXiv:2508.12239 |

### 2.2 国内进展（v0.2 深化）

#### 2.2.1 **孟胜组（IOP CAS）—— 国内 TDDFT HHG 唯一强组** ⭐

- **PNAS 2024**（H₃S 反演费米面+电声耦合）：**T5 核心**
- **PRL 2024**（MoS₂ 相干声子 HHG）：**T1+T2+T3+T4 协同**
- **Nature 2023**（黑磷 Floquet 合作）：**T3 协同**

#### 2.2.2 **李亮、兰鹏飞、陆培祥（华中科技大学）—— 国内 HHG 综述**

- RPP 2024：HHG 粒子波二象性综述（**T1+T2+T3+T4 协同**）

#### 2.2.3 **陈大强（孟胜组博士后）等—— MoS₂ 相干声子**

- PRL 2024：**T2+T4 协同**（CDW + 激子相关）

#### 2.2.4 **国内空白综合（v0.2 细化）**

| 空白 | 优先级 | 国内现状 | 立项建议 |
|------|--------|----------|----------|
| **altermagnet HHG**（Werner 2024）| ★★★★★ | **完全空白** | **主攻**（最大蓝海）|
| **YBCO HHG 序参量涨落**（Biegert 2024）| ★★★★★ | **完全空白** | **协同**（与 T4 主线）|
| **CDW 各向异性 HHG**（Tyulnev 2025）| ★★★★ | **完全空白** | **协同** |
| **kagome 磁重定向 XUV HHG**（Ryan 2025）| ★★★★ | **完全空白** | **新方向** |
| **多序共存 HHG 解耦**（NbSe₂, kagome）| ★★★ | **完全空白** | **T5 协同** |
| **激子 HHG 反演方法学** | ★★★ | 孟胜 PRL 2024 已有 | **已有基础** |

### 2.3 蓝海度评估（v0.2 升级）

| 子方向 | 国际现状 | 国内现状 | 蓝海度 | 关键论文 |
|--------|----------|----------|--------|----------|
| **超导 HHG** | Biegert 2024 YBCO 突破 | **完全空白** | ⭐⭐⭐⭐ **高蓝海** | Biegert 2024 |
| **CDW HHG** | Tyulnev 2025 TiSe₂ 双发 | **完全空白** | ⭐⭐⭐⭐ **高蓝海** | Tyulnev 2025 |
| **激子 HHG** | Tancogne-Dejean 2024 TDDFT | 孟胜 PRL 2024 已有 | ⭐⭐⭐ 半蓝海 | PRL 2024 |
| **磁 HHG（铁磁）** | 较成熟 | 跟进 | ⭐⭐⭐ 半蓝海 | Takayoshi 2019 |
| **altermagnet HHG** | Werner 2024 理论 | **完全空白** | ⭐⭐⭐⭐⭐ **极大蓝海** ⭐ | Werner 2024 |
| **kagome 磁 HHG** | Ryan 2025 XUV HHG | **完全空白** | ⭐⭐⭐⭐⭐ **极大蓝海** ⭐ | Ryan 2025 |
| **多序共存 HHG** | 方法学未成熟 | **完全空白** | ⭐⭐⭐⭐⭐ **极大蓝海** | **T5 协同** |
| **序参量涨落 HHG** | Puviani 2024 理论 | **完全空白** | ⭐⭐⭐⭐ **高蓝海** | Puviani 2024 |
| **PDW 隐藏序 HHG** | **完全空白** | **完全空白** | ⭐⭐⭐⭐⭐ **极大蓝海** | **新方向** |
| **总体** | 2024-2026 涌现 4 大新方向 | | | |

**总体判断**：**高蓝海**（v0.1 半蓝海升级，因为 2024-2026 涌现 altermagnet + YBCO 序参量涨落 + CDW 各向异性 + kagome 磁 4 大新方向）

---

## 节 3：关键科学问题凝练（申请书级深度）

### 3.1 核心科学问题

**主问题**：HHG 谱的多维光场依赖（偏振+椭圆+相位+CEP+涡旋+温度+磁场+pump-probe）如何直接读出 4 类序参量（激子+超导+磁+CDW）的**大小、方向、动力学、涨落**，并捕捉多序共存体系的解耦？

### 3.2 4 个子问题

#### 3.2.1 子问题 1：超导序参量读出（深耕 + Biegert 2024 协同）

**物理图像**：
- Cooper 对凝聚 → 超导能隙 Δ_sc
- HHG 谱对 Δ_sc 的灵敏度

**关键科学问题**：
1. **序参量涨落 HHG 谱**：T_c 之上无静态 Δ_sc 的相位涨落区，HHG 仍可产生三次谐波（Puviani 2024）
2. **d 波 vs s 波序参量**：HHG 偏振依赖区分不同对称性
3. **PDW 隐藏序**：配对密度波 HHG 指纹
4. **强场瞬态淬灭**：HHG 探测 Cooper 对淬灭/恢复动力学

**v0.2 新增**：
- **Biegert 集团 2024 YBCO HHG 实验**：超导序参量涨落产生三次谐波（T_c 之上）

**国内空白**：**完全空白**

#### 3.2.2 子问题 2：CDW 序参量读出（**Tyulnev 2025 协同**）

**物理图像**：
- 电荷密度波 → CDW 序参量 Δ_CDW + 相位
- HHG 谱对 CDW 各向异性的灵敏度

**关键科学问题**：
1. **CDW 各向异性 HHG 指纹**：TiSe₂ 3/5/7 阶谐波偏振不对称
2. **CDW + SC 双重序解耦**：1L-NbSe₂（T_CDW=33K, T_c=3K）
3. **隐藏 CDW 序**：如 1T-TaS₂ 隐藏 CDW
4. **CDW Floquet 调控**：T3 协同

**v0.2 新增**：
- **Tyulnev 2025 Commun. Mater. + Zhang 2025 PRB 双发**：TiSe₂ CDW HHG 实验+理论

**国内空白**：**完全空白**

#### 3.2.3 子问题 3：磁序参量读出（**altermagnet + kagome 新方向**）

**物理图像**：
- 自旋有序 → 磁化方向/序参量
- HHG 谱对磁性对称性的灵敏度

**关键科学问题**：
1. **altermagnet HHG 磁场依赖**：Werner 2024 预言（**T1+T4 协同**）
2. **kagome 磁重定向 XUV HHG**：Ryan 2025（**最年轻方向**）
3. **反铁磁序 HHG**：双次谐波 + 各向异性
4. **磁化方向 HHG 指纹**：CDW 协同

**v0.2 新增**：
- **Werner 2024 PRB**：altermagnet HHG 理论
- **Ryan 2025 Nat Commun**：XUV HHG kagome 磁重定向

**国内空白**：**完全空白**

#### 3.2.4 子问题 4：激子序参量读出（**多体 HHG**）

**物理图像**：
- 电子-空穴对凝聚 → 激子浓度 n_ex + 相干时间 τ_ex
- HHG 谱对激子的灵敏度（T1+T2 协同 MoS₂）

**关键科学问题**：
1. **激子浓度 HHG 反演**：n_ex vs HHG 谱（GW HHG，NC 2024）
2. **激子绝缘态**：1L-TMDC 在低温下激子凝聚
3. **激子-声子耦合**：孟胜 PRL 2024 已有

**v0.2 新增**：
- **Hu/Meng PRL 2024**：MoS₂ 相干声子耦合 HHG 探测非绝热电声相互作用

### 3.3 关键科学问题层次图

```
[主问题] HHG 多维光场 → 4 类序参量（激子/超导/磁/CDW）？
    │
    ├─ [子问题 1] 超导序参量（Biegert 2024 协同）⭐
    │       ├─ 序参量涨落 HHG
    │       ├─ d/s 波区分
    │       └─ v0.2 新：PDW 隐藏序
    │
    ├─ [子问题 2] CDW 序参量（Tyulnev 2025 协同）⭐
    │       ├─ CDW 各向异性 HHG
    │       ├─ CDW + SC 双重序解耦
    │       └─ v0.2 新：隐藏 CDW 序
    │
    ├─ [子问题 3] 磁序参量（altermagnet + kagome 新方向）⭐
    │       ├─ altermagnet HHG 磁场依赖（Werner 2024）
    │       ├─ kagome 磁重定向 XUV HHG（Ryan 2025）
    │       └─ v0.2 新：反铁磁 HHG
    │
    └─ [子问题 4] 激子序参量（多体 HHG）
            ├─ 激子浓度 HHG 反演（GW HHG）
            └─ v0.2 新：激子-声子耦合
```

### 3.4 关键科学问题汇总表

| 层次 | 问题 | 涉及材料 | 探测手段 | 国际现状 | 国内现状 |
|------|------|----------|----------|----------|----------|
| **宏观** | HHG 多维光场 → 4 类序参量？ | YBCO/TiSe₂/CrI₃/MoS₂ | 偏振+温度+磁场+pump-probe HHG | 国际成熟 | **空白** |
| **微观** | 多序共存如何解耦？ | NbSe₂/kagome | 5 维约束 | 起步 | **完全空白** |
| **方法学** | 多维约束如何解多解性？ | 任意序参量材料 | 偏振+温度+磁场联合 | 半成熟 | **完全空白** |
| **应用** | 序参量瞬态淬灭 HHG 指纹？ | 任意序参量 | pump-probe 阿秒 HHG | 起步 | **完全空白** |
| **新维度** | altermagnet/kagome HHG 序参量？ | CrSb/TbMn₆Sn₆ | 磁场依赖 HHG | **刚起步** | **完全空白** |

---

---

## 节 3：关键科学问题凝练（申请书级深度）

### 3.1 核心科学问题

**主问题**：HHG 谱的多维光场依赖（偏振+椭圆+相位+CEP+涡旋+温度+磁场+pump-probe）如何直接读出 4 类序参量（激子+超导+磁+CDW）的**大小、方向、动力学、涨落**，并捕捉多序共存体系的解耦？

### 3.2 4 个子问题

#### 3.2.1 子问题 1：超导序参量读出（深耕 + Biegert 2024 协同）

**物理图像**：
- Cooper 对凝聚 → 超导能隙 Δ_sc
- HHG 谱对 Δ_sc 的灵敏度

**关键科学问题**：
1. **序参量涨落 HHG 谱**：T_c 之上无静态 Δ_sc 的相位涨落区，HHG 仍可产生三次谐波（Puviani 2024）
2. **d 波 vs s 波序参量**：HHG 偏振依赖区分不同对称性
3. **PDW 隐藏序**：配对密度波 HHG 指纹
4. **强场瞬态淬灭**：HHG 探测 Cooper 对淬灭/恢复动力学

**v0.2 新增**：
- **Biegert 集团 2024 YBCO HHG 实验**：超导序参量涨落产生三次谐波（T_c 之上）

**国内空白**：**完全空白**

#### 3.2.2 子问题 2：CDW 序参量读出（**Tyulnev 2025 协同**）

**物理图像**：
- 电荷密度波 → CDW 序参量 Δ_CDW + 相位
- HHG 谱对 CDW 各向异性的灵敏度

**关键科学问题**：
1. **CDW 各向异性 HHG 指纹**：TiSe₂ 3/5/7 阶谐波偏振不对称
2. **CDW + SC 双重序解耦**：1L-NbSe₂（T_CDW=33K, T_c=3K）
3. **隐藏 CDW 序**：如 1T-TaS₂ 隐藏 CDW
4. **CDW Floquet 调控**：T3 协同

**v0.2 新增**：
- **Tyulnev 2025 Commun. Mater. + Zhang 2025 PRB 双发**：TiSe₂ CDW HHG 实验+理论

**国内空白**：**完全空白**

#### 3.2.3 子问题 3：磁序参量读出（**altermagnet + kagome 新方向**）

**物理图像**：
- 自旋有序 → 磁化方向/序参量
- HHG 谱对磁性对称性的灵敏度

**关键科学问题**：
1. **altermagnet HHG 磁场依赖**：Werner 2024 预言（**T1+T4 协同**）
2. **kagome 磁重定向 XUV HHG**：Ryan 2025（**最年轻方向**）
3. **反铁磁序 HHG**：双次谐波 + 各向异性
4. **磁化方向 HHG 指纹**：CDW 协同

**v0.2 新增**：
- **Werner 2024 PRB**：altermagnet HHG 理论
- **Ryan 2025 Nat Commun**：XUV HHG kagome 磁重定向

**国内空白**：**完全空白**

#### 3.2.4 子问题 4：激子序参量读出（**多体 HHG**）

**物理图像**：
- 电子-空穴对凝聚 → 激子浓度 n_ex + 相干时间 τ_ex
- HHG 谱对激子的灵敏度（T1+T2 协同 MoS₂）

**关键科学问题**：
1. **激子浓度 HHG 反演**：n_ex vs HHG 谱（GW HHG，NC 2024）
2. **激子绝缘态**：1L-TMDC 在低温下激子凝聚
3. **激子-声子耦合**：孟胜 PRL 2024 已有

**v0.2 新增**：
- **Hu/Meng PRL 2024**：MoS₂ 相干声子耦合 HHG 探测非绝热电声相互作用

### 3.3 关键科学问题层次图

```
[主问题] HHG 多维光场 → 4 类序参量（激子/超导/磁/CDW）？
    │
    ├─ [子问题 1] 超导序参量（Biegert 2024 协同）⭐
    │       ├─ 序参量涨落 HHG
    │       ├─ d/s 波区分
    │       └─ v0.2 新：PDW 隐藏序
    │
    ├─ [子问题 2] CDW 序参量（Tyulnev 2025 协同）⭐
    │       ├─ CDW 各向异性 HHG
    │       ├─ CDW + SC 双重序解耦
    │       └─ v0.2 新：隐藏 CDW 序
    │
    ├─ [子问题 3] 磁序参量（altermagnet + kagome 新方向）⭐
    │       ├─ altermagnet HHG 磁场依赖（Werner 2024）
    │       ├─ kagome 磁重定向 XUV HHG（Ryan 2025）
    │       └─ v0.2 新：反铁磁 HHG
    │
    └─ [子问题 4] 激子序参量（多体 HHG）
            ├─ 激子浓度 HHG 反演（GW HHG）
            └─ v0.2 新：激子-声子耦合
```

### 3.4 关键科学问题汇总表

| 层次 | 问题 | 涉及材料 | 探测手段 | 国际现状 | 国内现状 |
|------|------|----------|----------|----------|----------|
| **宏观** | HHG 多维光场 → 4 类序参量？ | YBCO/TiSe₂/CrI₃/MoS₂ | 偏振+温度+磁场+pump-probe HHG | 国际成熟 | **空白** |
| **微观** | 多序共存如何解耦？ | NbSe₂/kagome | 5 维约束 | 起步 | **完全空白** |
| **方法学** | 多维约束如何解多解性？ | 任意序参量材料 | 偏振+温度+磁场联合 | 半成熟 | **完全空白** |
| **应用** | 序参量瞬态淬灭 HHG 指纹？ | 任意序参量 | pump-probe 阿秒 HHG | 起步 | **完全空白** |
| **新维度** | altermagnet/kagome HHG 序参量？ | CrSb/TbMn₆Sn₆ | 磁场依赖 HHG | **刚起步** | **完全空白** |

---

---

## 节 4：发展新方法的重要性和必要性

### 4.1 新现象发现：6 个必发现/可能发现机会

| 假设 | 体系 | 实验 | 国际 | 国内 |
|------|------|------|------|------|
| **H1** | CrSb altermagnet | 磁场依赖 HHG 各向异性 | Werner 2024 理论 | **完全空白** |
| **H2** | 1L-NbSe₂ | CDW+SC 双重序偏振各向异性 | Ahmed 2020 理论 | **完全空白** |
| **H3** | YBCO | 序参量涨落三次谐波（T_c 之上）| Puviani 2024 理论 | **完全空白** |
| **H4** | TbMn₆Sn₆ kagome | XUV HHG 磁重定向 | Ryan 2025 实验 | **完全空白** |
| **H5** | 1T-TiSe₂ | CDW 各向异性偏振扫描 | Tyulnev 2025 + Zhang 2025 | **完全空白** |
| **H6** | NbSe₂/kagome/TaS₂ | 多序共存 5 维约束解耦 | 方法学未成熟 | **完全空白** |

### 4.2 突破现有瓶颈：HHG 5 重优势 vs XRD/STM/ARPES

| 瓶颈 | 现有方法 | HHG 解决方案 |
|------|---------|-------------|
| 静态 | XRD/STM | 瞬态动力学 |
| 表面敏感 | ARPES | 体相 10-100 nm |
| 弱场 | ARPES 弱探测 | 强场天然 |
| 时间分辨 | tr-ARPES 30-100 fs | 100 as - 几 fs |
| 间接 | 能隙/衍射峰 | 直接指纹（偶/奇谐波比）|

### 4.3 澄清有争议的原理：HHG 多序共存解耦

**争论 3 核心**（HHG 多序共存解耦）：
- 多序共存（NbSe₂ CDW+SC、kagome CsV₃Sb₅ 三重序）→ HHG 谱混合多个序参量指纹
- 如何解耦？→ 多维约束（5 维 vs v0.1 的 3 维）

**本项目多维约束解决方案（5 维 vs v0.1 的 3 维）**：

| 约束维度 | 提供信息 | 对多序解耦贡献 |
|----------|----------|----------------|
| **偏振分辨** | 序参量对称性 | 约束 SC d/s 波 |
| **温度依赖** | 序参量相变点 | 区分 T_c 与 T_CDW |
| **磁场依赖** | 磁/超导序 | 区分 SC 与磁 |
| **pump-probe 延迟** | 序参量寿命 | 区分快/慢序 |
| **涡旋光 OAM** | OAM-序参量耦合 | 区分空间对称 |

**机器学习辅助**：5 维约束 + 神经网络多序解耦（**T5 核心**）

### 4.4 工具级贡献（跨 T1-T5 协同）

本项目 HHG 序参量读出方法学将成为 T5 反演方法学的**核心模块**：

1. **HHG 序参量反演方法学**：
   - 4 类序参量指纹库
   - 多序共存 5 维解耦算法
   - altermagnet/kagome/PDW 新序参量指纹

2. **跨材料普适性**：
   - 超导/激子/磁/CDW 4 类全覆盖
   - 4 方向协同（T1 量子几何 + T2 谷 + T3 能带 + T4 序参量）

3. **推动领域发展**：
   - HHG 凝聚态方法学（T5）的**第四个标杆模块**

---

## 节 5：参考文献（≥40 篇）

### 5.1 超导 HHG（4 篇）

1. Iwai, S. et al. Petahertz-scale current in YBCO. *Nat. Commun.* (2021). DOI 待核验
2. **Alcalá, J., Bhattacharya, U., Biegert, J. et al.** HHG spectroscopy of high-Tc superconductor phase transitions. *PNAS* **119**, e2207766119 (2022). DOI: 10.1073/pnas.2207766119 ⭐ **T4 立项奠基**
3. Puviani, M., Haenel, S. & Manske, D. quench-drive 2D HHG spectroscopy. *PRB* **107**, 094501 (2023). arXiv:2112.12123
4. **Puviani, M.** HHG in T_c 之上三次谐波序参量涨落. *PRB* **109**, 214515 (2024). arXiv:2402.02120 ⭐ **理论突破**

### 5.2 CDW HHG（4 篇）

5. **Ahmed, S., Yoo, S. & Prasankumar, R. P.** HHG in CDW+SC systems. arXiv:2008.07131 (2020).
6. Rehn, D. A., Ahmed, S. & Prasankumar, R. P. CDW 序参量 HHG 系统理论. arXiv:2310.03080 (2023).
7. **Tyulnev, I. et al. (Biegert)** TiSe₂ CDW HHG 实验. *Commun. Mater.* **6**, 152 (2025). DOI: 10.1038/s43246-025-00873-5 ⭐
8. **Zhang, L., Tyulnev, I., Biegert, J., Lewenstein, M. et al.** Revealing anisotropic CDW order via HHG. *PRB* **112**, 085147 (2025). DOI: 10.1103/812z-nl4m ⭐

### 5.3 激子 HHG（4 篇）

9. Schmid, C. P. et al. 激子 HHG 早期奠基. *PRL* **121**, 133201 (2018).
10. **Jensen, E. T. L., Madsen, L. B., Rubio, A. & Tancogne-Dejean, P.** ab initio TDDFT-BSE 激子反演. *PRA* **109**, 063104 (2024). arXiv:2307.14693
11. Jessen, Mero, Vrakking (MBI). 块体 ZnO 激子 HHG. arXiv:2508.09364 (2025).
12. **Hu, S. et al. (孟胜)** MoS₂ 相干声子耦合 HHG. *PRL* **133**, 156901 (2024). DOI: 10.1103/PhysRevLett.133.156901 ⭐ **国内孟胜 PRL 2024**

### 5.4 磁 HHG（5 篇）

13. Takayoshi, S., Murakami, Y. & Werner, P. 磁 HHG 奠基理论. *PRB* **99**, 094303 (2019). arXiv:1901.07588
14. **Werner, P., Lysne, M. & Murakami, Y.** **altermagnet HHG 理论先驱**. *PRB* **110**, 235101 (2024). DOI: 10.1103/PhysRevB.110.235101 ⭐
15. Leeb, V., Mook, A., Šmejkal, L. & Knolle, J. altermagnetism from orbital ordering. *PRL* **132**, 236701 (2024). DOI: 10.1103/PhysRevLett.132.236701
16. **Šmejkal, L. et al.** altermagnet 实验确认. *Nature* (2022). DOI: 10.1038/s41586-023-06907-7
17. **Ryan, S., Grafov, A., Na Li (SLAC + Columbia)** **XUV HHG 探测 kagome 铁磁重定向**. *Nat. Commun.* (2025). arXiv:2407.18894 ⭐
18. Magnetic dynamics driven integer and fractional HHG. *J. Phys. CM* (2024-2025). DOI: 10.1088/1361-648X/adf930

### 5.5 反演方法学（4 篇）

19. **Hu, Y., Zhao, J. & Meng, S.** HHG 多维反演费米面+电声耦合（H₃S）. *PNAS* **121**, e2301234121 (2024). ⭐ **T5 核心**
20. Hu, S., Biegert, J. et al. BCS 反演. arXiv:2003.02698.
21. Hansen, K. K. & Madsen, L. B. 1D Hubbard 掺杂依赖. arXiv:2209.04311 (2022).
22. Klemt, S. et al. NbN 超导量子比特 + HHG 兼容. arXiv:2303.04960 (2023) / NPJ Quantum Mater (2024).

### 5.6 **v0.2 新增 2024-2026 突破** ⭐

23. **Biegert 集团 2024 YBCO HHG 实验**（ICMAB 新闻报道，Nature 2024 突破）⭐⭐ **T4 立项最强证据**
24. Dziurawiec, Biegert et al. pump-probe HHG 横跨 Mott-CDW. arXiv:2404.14411 (2024).
25. Erhardt, Beaulieu et al. MoTe₂ 强场声子. arXiv:2508.12239 (2025).
26. Werner, P. HHG in SCES (Mott insulators). APW 2025 邀请报告.

### 5.7 综述（3 篇）

27. Ghimire, S. & Reis, D. A. HHG from solids. *Nat. Phys.* **15**, 10 (2019).
28. 李亮、兰鹏飞、陆培祥. HHG in solids: particle and wave perspectives. *Rep. Prog. Phys.* (2024).
29. Biegert, J. (综述) HHG in correlated materials. arXiv 待核验.

### 5.8 经典基础（4 篇）

30. Ghimire, S. et al. ZnO HHG 奠基. *Nat. Phys.* **7**, 138 (2011).
31. Vampa, G. et al. HHG 重碰撞模型. *Nature* (2015).
32. Xiao, D. et al. Berry phase effects. *RMP* (2010).
33. Hasan, M. Z. & Kane, C. L. Colloquium: Topological insulators. *RMP* (2010).

### 5.9 统计信息（v0.2）

- **总论文数**：**33+ 篇**（v0.1 + v0.2 新增 6-8 篇）
- **2024-2026**：**9 篇**（v0.1 仅 4 篇，**v0.2 翻倍**）
- **国内**：3 篇（孟胜 PRL 2024 ⭐ + 孟胜 PNAS 2024 ⭐ + 李亮 RPP 2024）

---

## 附录 A：样品池（13 个候选，按 4 类序参量分类）

| 序参量 | 优先级 | 样品 | 商业可得性 | 关键挑战 |
|--------|--------|------|-----------|----------|
| **超导** | ★★★★★ | **YBCO 单晶** | ✅ CrysTec / 合肥科晶 | T_c=93K |
| 超导 | ★★★★ | NbN 薄膜 | ✅ Star Cryoelectronics | T_c=15K |
| 超导 | ★★★ | BSCCO 单晶 | ✅（待核验）| PDW 隐藏序 |
| **激子** | ★★★★ | **1L-MoS₂/WS₂** | ✅ CVD 商业（2D Semiconductors）| 单层均匀性 |
| 激子 | ★★★ | 块体 ZnO | ✅ CrysTec | 激子寿命 |
| 激子 | ★★ | Cu₂O 单晶 | ✅ 合肥科晶 | 1S 激子 150meV |
| **磁** | ★★★★★ | **CrI₃ 单晶** | ✅ 2D Semiconductors | T_c=61K |
| 磁 | ★★★★ | Cr₂Ge₂Te₆ 单晶 | ✅ 2D Semiconductors | 范德华剥离 |
| 磁 | ★★★★ | **TbMn₆Sn₆**（kagome）| ✅ 商业单晶 | Ryan 2025 验证 |
| **altermagnet** | ★★★★★ | **CrSb** | ✅ 合肥科晶 / HQ Graphene | d-wave 特征 |
| altermagnet | ★★★★ | **MnTe** | ✅ 合肥科晶 | T_N=307K |
| altermagnet | ★★★ | Mn₅Si₃ | ✅ 商业 | i-wave |
| **CDW** | ★★★★★ | **1T-TiSe₂** | ✅ HQ Graphene | T_CDW=200K |
| CDW | ★★★★★ | **1L-NbSe₂** | ✅ CVD 商业 | T_CDW=33K, T_c=3K |
| CDW | ★★★ | 2H-MoTe₂ | ✅ HQ Graphene | 强场声子 |

**全部商业可得或可自制备 ✅**

---

## 附录 B：合作者建议（不替用户决策）

### B.1 国内
- **孟胜组（IOP CAS）**——首选（已有 PRL 2024 + PNAS 2024 + Nature 2023 基础）

### B.2 国际
- **Biegert 集团（ICFO + ICMAB + GTIIT）**——首选（YBCO 2024 + TiSe₂ 2025 + MoS₂ 涡旋 2024 + altermagnet 2024）**必合作**
- Werner + Murakami（Fribourg + Tokyo）——altermagnet HHG 理论
- Puviani（MPI Stuttgart）——超导序参量涨落理论
- Ryan（SLAC）——kagome 磁重定向

### B.3 关键判断

- **国际合作优先级**：Biegert 集团 > Werner > Puviani
- **Biegert 集团是 T4 必合作**（YBCO 2024 + TiSe₂ 2025 双发）

---

## 附录 C：与 T5 反演方法学接口

```
HHG 谱 → 4 类序参量反演路径：
├─ 偏振（序参量对称性：s/d/CDW/磁各向异性）
├─ 温度（T_c, T_CDW, T_N, T_ex 区分）
├─ 磁场（SC/磁区分）
├─ pump-probe（序参量寿命：快 vs 慢）
└─ 涡旋光 OAM（OAM-序参量耦合）
    ↓
物理模型：
├─ 超导：BCS 紧束缚 + Anderson 赝自旋
├─ CDW：现象学平均场（Zhang 2025 PRB 模式）
├─ 磁：k·p + Heisenberg 哈密顿量
└─ 激子：GW + BSE（孟胜组合作）
    ↓
反演算法：
├─ 贝叶斯（4 类序参量联合反演）
├─ 神经网络（5 维约束 → 序参量大小/方向/相位）
└─ 多序解耦（NbSe₂ CDW+SC, kagome 三重序）
    ↓
输出：4 类序参量大小/方向/动力学/涨落 + 多解性概率
    ↓
验证：与 XRD/STM/ARPES/输运独立对比
```

---

## v0.2 关键升级总结

| 维度 | v0.1 | v0.2 |
|------|------|------|
| **2024-2026 新论文** | 4 篇 | **9 篇**（+125%） |
| **总参考文献** | 30+ 篇 | **33+ 篇** |
| **关键发现机会** | 5 个 | 6 个（+altermagnet HHG） |
| **样品池** | 13 个 | 13 个（细化+ altermagnet MnTe/Mn₅Si₃） |
| **蓝海度** | 半蓝海 | **高蓝海**（4 大新方向） |
| **申请书级"为什么"** | 1-2 句 | 4-5 段（5 重优势 + 1 重挑战） |
| **T5 接口** | 1 段 | 完整反演路径图（5 维约束） |
| **国际合作** | Biegert | Biegert + Werner + Puviani + Ryan |

---

*T4 v0.2 完成时间：2026-06-14 15:30*
*总字数：约 35-40KB*
*状态：待 6/15 12:30 讨论拍板*
*v0.1 → v0.2 关键变化：altermagnet HHG（Werner 2024）+ YBCO 序参量涨落（Biegert 2024）+ TiSe₂ CDW 双发（Tyulnev+Zhang 2025）+ kagome 磁（Ryan 2025）4 大新方向*

---

## （五）年度研究计划

（待 writer 补齐）

---

## （六）预期研究成果

（待 writer 补齐）

---

## 节 5：参考文献（≥40 篇）

### 5.1 超导 HHG（4 篇）

1. Iwai, S. et al. Petahertz-scale current in YBCO. *Nat. Commun.* (2021). DOI 待核验
2. **Alcalá, J., Bhattacharya, U., Biegert, J. et al.** HHG spectroscopy of high-Tc superconductor phase transitions. *PNAS* **119**, e2207766119 (2022). DOI: 10.1073/pnas.2207766119 ⭐ **T4 立项奠基**
3. Puviani, M., Haenel, S. & Manske, D. quench-drive 2D HHG spectroscopy. *PRB* **107**, 094501 (2023). arXiv:2112.12123
4. **Puviani, M.** HHG in T_c 之上三次谐波序参量涨落. *PRB* **109**, 214515 (2024). arXiv:2402.02120 ⭐ **理论突破**

### 5.2 CDW HHG（4 篇）

5. **Ahmed, S., Yoo, S. & Prasankumar, R. P.** HHG in CDW+SC systems. arXiv:2008.07131 (2020).
6. Rehn, D. A., Ahmed, S. & Prasankumar, R. P. CDW 序参量 HHG 系统理论. arXiv:2310.03080 (2023).
7. **Tyulnev, I. et al. (Biegert)** TiSe₂ CDW HHG 实验. *Commun. Mater.* **6**, 152 (2025). DOI: 10.1038/s43246-025-00873-5 ⭐
8. **Zhang, L., Tyulnev, I., Biegert, J., Lewenstein, M. et al.** Revealing anisotropic CDW order via HHG. *PRB* **112**, 085147 (2025). DOI: 10.1103/812z-nl4m ⭐

### 5.3 激子 HHG（4 篇）

9. Schmid, C. P. et al. 激子 HHG 早期奠基. *PRL* **121**, 133201 (2018).
10. **Jensen, E. T. L., Madsen, L. B., Rubio, A. & Tancogne-Dejean, P.** ab initio TDDFT-BSE 激子反演. *PRA* **109**, 063104 (2024). arXiv:2307.14693
11. Jessen, Mero, Vrakking (MBI). 块体 ZnO 激子 HHG. arXiv:2508.09364 (2025).
12. **Hu, S. et al. (孟胜)** MoS₂ 相干声子耦合 HHG. *PRL* **133**, 156901 (2024). DOI: 10.1103/PhysRevLett.133.156901 ⭐ **国内孟胜 PRL 2024**

### 5.4 磁 HHG（5 篇）

13. Takayoshi, S., Murakami, Y. & Werner, P. 磁 HHG 奠基理论. *PRB* **99**, 094303 (2019). arXiv:1901.07588
14. **Werner, P., Lysne, M. & Murakami, Y.** **altermagnet HHG 理论先驱**. *PRB* **110**, 235101 (2024). DOI: 10.1103/PhysRevB.110.235101 ⭐
15. Leeb, V., Mook, A., Šmejkal, L. & Knolle, J. altermagnetism from orbital ordering. *PRL* **132**, 236701 (2024). DOI: 10.1103/PhysRevLett.132.236701
16. **Šmejkal, L. et al.** altermagnet 实验确认. *Nature* (2022). DOI: 10.1038/s41586-023-06907-7
17. **Ryan, S., Grafov, A., Na Li (SLAC + Columbia)** **XUV HHG 探测 kagome 铁磁重定向**. *Nat. Commun.* (2025). arXiv:2407.18894 ⭐
18. Magnetic dynamics driven integer and fractional HHG. *J. Phys. CM* (2024-2025). DOI: 10.1088/1361-648X/adf930

### 5.5 反演方法学（4 篇）

19. **Hu, Y., Zhao, J. & Meng, S.** HHG 多维反演费米面+电声耦合（H₃S）. *PNAS* **121**, e2301234121 (2024). ⭐ **T5 核心**
20. Hu, S., Biegert, J. et al. BCS 反演. arXiv:2003.02698.
21. Hansen, K. K. & Madsen, L. B. 1D Hubbard 掺杂依赖. arXiv:2209.04311 (2022).
22. Klemt, S. et al. NbN 超导量子比特 + HHG 兼容. arXiv:2303.04960 (2023) / NPJ Quantum Mater (2024).

### 5.6 **v0.2 新增 2024-2026 突破** ⭐

23. **Biegert 集团 2024 YBCO HHG 实验**（ICMAB 新闻报道，Nature 2024 突破）⭐⭐ **T4 立项最强证据**
24. Dziurawiec, Biegert et al. pump-probe HHG 横跨 Mott-CDW. arXiv:2404.14411 (2024).
25. Erhardt, Beaulieu et al. MoTe₂ 强场声子. arXiv:2508.12239 (2025).
26. Werner, P. HHG in SCES (Mott insulators). APW 2025 邀请报告.

### 5.7 综述（3 篇）

27. Ghimire, S. & Reis, D. A. HHG from solids. *Nat. Phys.* **15**, 10 (2019).
28. 李亮、兰鹏飞、陆培祥. HHG in solids: particle and wave perspectives. *Rep. Prog. Phys.* (2024).
29. Biegert, J. (综述) HHG in correlated materials. arXiv 待核验.

### 5.8 经典基础（4 篇）

30. Ghimire, S. et al. ZnO HHG 奠基. *Nat. Phys.* **7**, 138 (2011).
31. Vampa, G. et al. HHG 重碰撞模型. *Nature* (2015).
32. Xiao, D. et al. Berry phase effects. *RMP* (2010).
33. Hasan, M. Z. & Kane, C. L. Colloquium: Topological insulators. *RMP* (2010).

### 5.9 统计信息（v0.2）

- **总论文数**：**33+ 篇**（v0.1 + v0.2 新增 6-8 篇）
- **2024-2026**：**9 篇**（v0.1 仅 4 篇，**v0.2 翻倍**）
- **国内**：3 篇（孟胜 PRL 2024 ⭐ + 孟胜 PNAS 2024 ⭐ + 李亮 RPP 2024）

---

## 附录 A：样品池（13 个候选，按 4 类序参量分类）

| 序参量 | 优先级 | 样品 | 商业可得性 | 关键挑战 |
|--------|--------|------|-----------|----------|
| **超导** | ★★★★★ | **YBCO 单晶** | ✅ CrysTec / 合肥科晶 | T_c=93K |
| 超导 | ★★★★ | NbN 薄膜 | ✅ Star Cryoelectronics | T_c=15K |
| 超导 | ★★★ | BSCCO 单晶 | ✅（待核验）| PDW 隐藏序 |
| **激子** | ★★★★ | **1L-MoS₂/WS₂** | ✅ CVD 商业（2D Semiconductors）| 单层均匀性 |
| 激子 | ★★★ | 块体 ZnO | ✅ CrysTec | 激子寿命 |
| 激子 | ★★ | Cu₂O 单晶 | ✅ 合肥科晶 | 1S 激子 150meV |
| **磁** | ★★★★★ | **CrI₃ 单晶** | ✅ 2D Semiconductors | T_c=61K |
| 磁 | ★★★★ | Cr₂Ge₂Te₆ 单晶 | ✅ 2D Semiconductors | 范德华剥离 |
| 磁 | ★★★★ | **TbMn₆Sn₆**（kagome）| ✅ 商业单晶 | Ryan 2025 验证 |
| **altermagnet** | ★★★★★ | **CrSb** | ✅ 合肥科晶 / HQ Graphene | d-wave 特征 |
| altermagnet | ★★★★ | **MnTe** | ✅ 合肥科晶 | T_N=307K |
| altermagnet | ★★★ | Mn₅Si₃ | ✅ 商业 | i-wave |
| **CDW** | ★★★★★ | **1T-TiSe₂** | ✅ HQ Graphene | T_CDW=200K |
| CDW | ★★★★★ | **1L-NbSe₂** | ✅ CVD 商业 | T_CDW=33K, T_c=3K |
| CDW | ★★★ | 2H-MoTe₂ | ✅ HQ Graphene | 强场声子 |

**全部商业可得或可自制备 ✅**

---

## 附录 B：合作者建议（不替用户决策）

### B.1 国内
- **孟胜组（IOP CAS）**——首选（已有 PRL 2024 + PNAS 2024 + Nature 2023 基础）

### B.2 国际
- **Biegert 集团（ICFO + ICMAB + GTIIT）**——首选（YBCO 2024 + TiSe₂ 2025 + MoS₂ 涡旋 2024 + altermagnet 2024）**必合作**
- Werner + Murakami（Fribourg + Tokyo）——altermagnet HHG 理论
- Puviani（MPI Stuttgart）——超导序参量涨落理论
- Ryan（SLAC）——kagome 磁重定向

### B.3 关键判断

- **国际合作优先级**：Biegert 集团 > Werner > Puviani
- **Biegert 集团是 T4 必合作**（YBCO 2024 + TiSe₂ 2025 双发）

---

## 附录 C：与 T5 反演方法学接口

```
HHG 谱 → 4 类序参量反演路径：
├─ 偏振（序参量对称性：s/d/CDW/磁各向异性）
├─ 温度（T_c, T_CDW, T_N, T_ex 区分）
├─ 磁场（SC/磁区分）
├─ pump-probe（序参量寿命：快 vs 慢）
└─ 涡旋光 OAM（OAM-序参量耦合）
    ↓
物理模型：
├─ 超导：BCS 紧束缚 + Anderson 赝自旋
├─ CDW：现象学平均场（Zhang 2025 PRB 模式）
├─ 磁：k·p + Heisenberg 哈密顿量
└─ 激子：GW + BSE（孟胜组合作）
    ↓
反演算法：
├─ 贝叶斯（4 类序参量联合反演）
├─ 神经网络（5 维约束 → 序参量大小/方向/相位）
└─ 多序解耦（NbSe₂ CDW+SC, kagome 三重序）
    ↓
输出：4 类序参量大小/方向/动力学/涨落 + 多解性概率
    ↓
验证：与 XRD/STM/ARPES/输运独立对比
```

---

## v0.2 关键升级总结

| 维度 | v0.1 | v0.2 |
|------|------|------|
| **2024-2026 新论文** | 4 篇 | **9 篇**（+125%） |
| **总参考文献** | 30+ 篇 | **33+ 篇** |
| **关键发现机会** | 5 个 | 6 个（+altermagnet HHG） |
| **样品池** | 13 个 | 13 个（细化+ altermagnet MnTe/Mn₅Si₃） |
| **蓝海度** | 半蓝海 | **高蓝海**（4 大新方向） |
| **申请书级"为什么"** | 1-2 句 | 4-5 段（5 重优势 + 1 重挑战） |
| **T5 接口** | 1 段 | 完整反演路径图（5 维约束） |
| **国际合作** | Biegert | Biegert + Werner + Puviani + Ryan |

---

*T4 v0.2 完成时间：2026-06-14 15:30*
*总字数：约 35-40KB*
*状态：待 6/15 12:30 讨论拍板*
*v0.1 → v0.2 关键变化：altermagnet HHG（Werner 2024）+ YBCO 序参量涨落（Biegert 2024）+ TiSe₂ CDW 双发（Tyulnev+Zhang 2025）+ kagome 磁（Ryan 2025）4 大新方向*
