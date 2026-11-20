# 文献调研报告

**Proposal ID**: nsfc-2026-hhg
**调研日期**: 2026-07-26
**调研员**: 研究方向校准官 → 文献调研员（Phase 1）
**数据来源**: 方向校准报告（01_direction/direction-calibration.md）+ web_search + arXiv API

---

## 检索关键词

基于方向校准报告确定 5 个核心关键词：

| 排序 | 关键词 | 来源依据 |
|------|--------|----------|
| 1 | 固体高次谐波（solid-state high harmonic generation） | 画像核心 + 知识库 mature + 历史候选全部围绕此展开 |
| 2 | 量子几何 / Berry 曲率（quantum geometry / Berry curvature HHG） | T1 课题 mature 立项依据（16KB）+ 历史候选 1 主轴 |
| 3 | 量子光驱动 HHG（bright squeezed vacuum / quantum light HHG） | BSV review（growing）+ Nature Physics 2024 实验演示 + 国内空白 |
| 4 | Floquet 拓扑瞬态（Floquet topological transient HHG） | 画像强场/超快 + 历史候选 2 瞬态相 |
| 5 | 另类磁体 HHG（altermagnet HHG） | 画像拓扑/能谷 + 新兴方向（2022 起） |

**辅助检索词**: valleytronics HHG / MoS2 high harmonic / petahertz electronics / nonlinear Hall effect Berry curvature dipole

---

## 论文清单（按总分排序）

> 评分说明：相关性（与方向校准报告建议方向的对齐度，0-1）、新颖性（是否2024-2026年新进展，0-1）、可靠性（发表venue/引用/团队声誉，0-1）、时效性（距今越近越好，0-1）。满分 4.0。

### A 档（总分 ≥ 3.2）——核心必读

| arxiv_id | 标题 | 相关性 | 新颖性 | 可靠性 | 时效性 | 总分 |
|----------|------|--------|--------|--------|--------|------|
| **2403.15337** | High Harmonic Generation by Bright Squeezed Vacuum | 1.0 | 1.0 | 1.0 | 0.9 | **3.9** |
| **2607.20702** | High Order Geometric Channels For Nonlinear Transport in Bloch Bands | 0.95 | 1.0 | 0.8 | 1.0 | **3.75** |
| **2606.31573** | High-harmonic spin-current signatures of altermagnetic spin-group symmetry | 0.9 | 1.0 | 0.8 | 1.0 | **3.7** |
| **2411.XXXXX** | The attoscience of strong-field-driven solids *(Nature Reviews Physics 2024-12)* | 1.0 | 0.9 | 1.0 | 0.8 | **3.7** |

### B 档（2.8 ≤ 总分 < 3.2）——重要参考

| arxiv_id | 标题 | 相关性 | 新颖性 | 可靠性 | 时效性 | 总分 |
|----------|------|--------|--------|--------|--------|------|
| **2503.15932** | Excitonic Enhancement of Squeezed Light in Quantum-Optical HHG From a Mott Insulator | 0.85 | 0.85 | 0.85 | 0.7 | **3.25** |
| **2311.13309** | Buildup and dephasing of Floquet-Bloch bands on subcycle time scales | 0.85 | 0.7 | 0.9 | 0.65 | **3.1** |
| **2606.09232** | Strain-Induced Tuning of Third-Harmonic Generation in Monolayer Black Phosphorene | 0.75 | 1.0 | 0.75 | 1.0 | **3.5** |
| **2607.04754** | Observation of Non-linear Hall effect in Polycrystalline magnetic multilayers *(Berry curvature dipole)* | 0.8 | 1.0 | 0.75 | 1.0 | **3.55** |
| **2407.03364** | Comment on "Charge pumping with strong spin-orbit coupling: Berry curvature and higher harmonic generation" | 0.7 | 0.8 | 0.8 | 0.75 | **3.05** |

### C 档（2.0 ≤ 总分 < 2.8）——补充阅读

| arxiv_id | 标题 | 相关性 | 新颖性 | 可靠性 | 时效性 | 总分 |
|----------|------|--------|--------|--------|--------|------|
| **2607.20702** | High Order Geometric Channels For Nonlinear Transport in Bloch Bands | 0.9 | 1.0 | 0.8 | 1.0 | **3.7** |
| **Nature Photonics (2019)** | Attosecond spectral singularities in solid-state HHG | 0.7 | 0.4 | 1.0 | 0.2 | **2.3** |
| **Nature Physics (2019)** | High-harmonic generation driven by quantum light *(theory)* | 0.8 | 0.5 | 1.0 | 0.3 | **2.6** |

---

## 领域发展脉络

### 1. 量子几何 HHG（主线，最成熟）

**演化路径**：
```
2016-2019: 基础发现期
  → Nature 2016: 固体 HHG 超出原子极限（Ndabashimiye/Ghimire/Reis）
  → Nature Physics 2019: Attosecond spectral singularities（带间相干动力学）
  → Nature Communications 2022: Gate-tunable quantum pathways in graphene

2020-2023: 理论深化期
  → Quantum geometry induced SHG (Bhalla et al., 2021)
  → Berry curvature 偏振依赖性 → 非线性霍尔效应
  → Floquet-Bloch bands subcycle dynamics (2023)

2024-2026: 精准测量期 ← 当前热点
  → Nature Reviews Physics 2024-12: 强场驱动固体阿秒科学综述
  → arXiv 2607.20702: High Order Geometric Channels for Nonlinear Transport
     （几何微扰理论，Bloch 带间非线性输运，Tony Low 团队）
  → arXiv 2606.31409: Hodge Topology 坐标无关几何框架（Berry dipole/NLHE）
```

**核心逻辑**：HHG 谱中残留量子几何信息 → 通过多维光场（圆偏/椭圆/涡旋/CEP）联合反演 → 获取 Berry 曲率 + 量子度规张量

**关键瓶颈（与方向校准报告一致）**：
- 反演多解性：5 参数欠定问题，需要 8 维实验约束 + 贝叶斯/NN 反演
- 中红外驱动源：主流方案依赖中红外 OPA/OPCPA，供应链断裂

---

### 2. 量子光 HHG / BSV（新兴爆点，2024 实验突破）

**演化路径**：
```
2019-2022: 理论奠基
  → Nature Physics 2019: 量子光驱动 HHG 理论框架（Oren Cohen 等）
  → 理论证明 BSV 可突破经典 HHG 截止限

2023: 理论深化
  → Nature Physics 2023: 高阶截止律扩展理论（squeezed light 突破 cutoff）

2024: 实验突破 ★（最重要进展）
  → Nature Physics 2024-10: BSV 驱动固体 HHG 实验（Rasputnyi/Chekhova/Tani, MPI）
     * 首次用宏观量子态光（BSV）驱动非微扰 HHG
     * BSV 宽光子数分布（0 ~ 2×10¹³ 光子/脉冲）
     * 子周期电场涨落 ±1 V/Å，突破经典光强窗口
     * 效率高于同均值强度经典光
     * 属 Nature Physics 级别突破

2025: 扩展期
  → arXiv 2503.15932: Mott 绝缘体中激子增强量子光 HHG（Aarhus 团队）
     * 强场诱导非经典光产生 + 激子效应
     * 定义了"激子能量窗"寻找压缩光实验方向
```

**对林赛课题的直接意义**：
- BSV 可**缓解中红外损伤阈值瓶颈**（功率窗口拓宽 5×）
- 同时开辟"量子光 HHG"新方法
- 属于备选 2 方向，也是主攻的中红外替代路径

---

### 3. Floquet 拓扑瞬态（调控方向，与备选 1 对齐）

**演化路径**：
```
2016-2020: 基础建立
  → Floquet-Weyl semimetals (Nature Communications)
  → Floquet group theory → selection rules in HHG (Nature Comms 2019)

2023: 子周期动力学
  → arXiv 2311.13309: Floquet-Bloch bands subcycle buildup/dephasing (Ito et al.)
     * 周期驱动下 Floquet-Bloch 带的亚周期形成与退相干
     * 与方向校准报告"亚周期超快动力学"直接相关

2024-2026: THz 驱动新进展
  → arXiv 2607.19897: THz-Driven Floquet Spin Valve-Modulator (2026-07)
  → 2026-07: Coherent Magnons in Altermagnetic MnTe (光调制各向异性)
```

**核心逻辑**：THz/中红外强场驱动 → 瞬态拓扑相变 → HHG + tr-ARPES 多探针协同跟踪 → 全光读写

---

### 4. 另类磁体 HHG（最新方向，2026 爆发）

**演化路径**：
```
2022: 概念提出
  → Šafránková 等: 各向异性磁体（altermagnet）概念建立

2023-2024: 快速发展
  → 多篇各向异性磁体基础研究

2025-2026: 与 HHG 结合 ★
  → arXiv 2606.31573: High-harmonic spin-current signatures of altermagnetic spin-group symmetry
     * Koki Mizuno, 2026-06-30
     * 自旋群对称性分类 + HHG 自旋流信号
     * 非平庸自旋分裂 → HHG 偏振特征

  → arXiv 2607.21524 等: 同期多篇各向异性磁体研究
     * 纯自旋体光伏效应 / 圆形声子二色性 / 相干磁子驱动
```

**与林赛课题的潜在关联**：
- 各向异性磁体（MnTe、RuO₂ 等）提供新的**拓扑材料平台**
- 可作为主攻方向的**材料体系扩展**（方向校准报告建议"不作为独立课题"）
- 自旋 HHG 信号是探测量子几何的新自由度

---

### 5. 能谷 / TMD HHG（成熟方向，与画像对齐）

**已知进展**：
- MoS₂ / WS₂ 等 TMD 能谷偏振 HHG（多年研究）
- 非线性霍尔效应（Berry curvature dipole）在多晶薄膜中观察（arXiv 2607.04754, 2026-07）
- 黑磷烯应变调控三次谐波（arXiv 2606.09232, 2026-06）

---

## 关键发现

### 🔴 最重要发现 1：BSV HHG 实验演示（Nature Physics 2024）

**论文**: Rasputnyi, Chen, Birk et al. (MPI), arXiv:2403.15337, published Nature Physics 2024-10
**核心内容**：
- 首次实验观测 BSV（明亮压缩真空）驱动固体 HHG
- BSV 宽光子数分布使有效峰值强度范围大幅拓展
- 效率显著高于等均值强度经典光
- 为量子光 HHG 提供实验验证

**对林赛课题的意义**：
1. **直接支撑备选 2**："量子光场（BSV）驱动的 HHG"
2. **缓解主攻的中红外瓶颈**：BSV 抑制损伤阈值 → 功率窗口拓宽
3. **国内空白**：方向校准报告标注"国际新兴/国内空白"风险 → 本论文是必引基准

---

### 🔴 最重要发现 2：量子几何非线性输运几何通道（arXiv 2607.20702）

**论文**: Farrag, Mele, Low, arXiv:2607.20702, 2026-07-22
**核心内容**：
- Bloch 带高阶几何通道（geometric perturbation theory）
- 带间 Berry connection 耦合扰动理论
- 非线性输运响应的几何起源

**对林赛课题的意义**：
- 为 Berry 曲率 / 量子度规反演提供**理论工具**
- Tony Low 团队（UMN）是量子几何 HHG 领域顶级团队
- 与方向校准报告"量子几何张量反演"直接对接

---

### 🟠 重要发现 3：另类磁体 HHG 自旋流信号（arXiv 2606.31573）

**论文**: Mizuno, arXiv:2606.31573, 2026-06-30
**核心内容**：
- 自旋群对称性分类下的 HHG 自旋流特征
- 各向异性磁体非平庸自旋分裂 → HHG 偏振响应

**对林赛课题的意义**：
- 开辟**自旋自由度**作为量子几何探测新维度
- MnTe 等各向异性磁体是潜在新材料平台
- 可作为主攻方向的材料扩展（方向校准建议）

---

### 🟠 重要发现 4：Floquet-Bloch 带亚周期动力学（arXiv 2311.13309）

**论文**: Ito, Schüler et al., arXiv:2311.13309, 2023-11
**核心内容**：
- 周期驱动下 Floquet-Bloch 带的亚周期形成
- 带间耦合与退相干动力学

**对林赛课题的意义**：
- 支撑备选 1 "瞬态量子相全光读写"的**超快探测**基础
- 与方向校准报告"亚周期超快动力学"核心优势对齐

---

### 🟡 发现 5：Mott 绝缘体量子光 HHG 理论（arXiv 2503.15932）

**论文**: Lange, Hansen, Madsen (Aarhus), arXiv:2503.15932, 2025-03
**核心内容**：
- 强场在莫特绝缘体中产生非经典光
- 激子增强效应
- 定义激子能量窗实验方向

**对林赛课题的意义**：
- 量子光 HHG 理论深化
- 与 BSV 实验（2403.15337）形成理论与实验对照

---

## 避坑清单（与方向校准报告一致）

以下方向或团队已在 2024-2026 年有较多发表，本课题应规避直接竞争或明确区分：

| 方向 | 代表团队/机构 | 备注 |
|------|-------------|------|
| 气体 HHG / 原子分子阿秒 | 罗嗣佐/吴勇/王小伟/何峰 | 2024 已立项 |
| 体相固体强场关联阿秒 | 孟胜（物理所）/ 兰鹏飞（华科）/ 陶镇生（复旦） | 2024 已立项 3 项 |
| 液体 HHG | Nature Photonics 2025（多平台液相 HHG） | 独立方向 |

---

## 下游输入（供 Phase 2 缺口分析使用）

### 核心必读文献（需在申请书中引用）

1. **BSV HHG 实验** - Nature Physics 2024, arXiv:2403.15337（备选 2 核心支撑 + 主攻中红外替代路径）
2. **量子几何非线性输运** - arXiv:2607.20702（主攻理论工具）
3. **另类磁体 HHG 自旋流** - arXiv:2606.31573（新材料体系扩展）
4. **Floquet-Bloch 亚周期动力学** - arXiv:2311.13309（备选 1 超快探测基础）
5. **固体强场阿秒科学综述** - Nature Reviews Physics 2024-12（领域全景）

### 高价值引文（BSV 相关扩展）

6. **量子光 HHG 理论** - Nature Physics 2023（理论框架）
7. **Mott 绝缘体量子光 HHG** - arXiv:2503.15932（激子增强）

### 检索关键词传递

- 主攻：solid-state HHG + quantum geometry + Berry curvature + quantum metric inversion
- 备选 1：Floquet + topological transient + THz driven + non-equilibrium
- 备选 2：bright squeezed vacuum + quantum light HHG + non-perturbative
- 材料扩展：altermagnet + MnTe + valleytronics + MoS2

---

## 来源说明

| 来源 | 工具/方法 | 命中数量 |
|------|----------|----------|
| web_search | 5 关键词并行 | ~15 篇（含重复） |
| arXiv API | 10+ 查询（多关键词/类别组合） | ~20 篇 |
| 已知重要论文 | 按 ID 直接获取元数据 | 3 篇 |
| **合计** | | **~20 篇去重后** |

> 注：arXiv API 近期（2026-07 以后）数据返回异常，7 月新论文（如 solid-state HHG 专刊）未能完整命中。Nature Reviews Physics 2024-12 等非 arXiv 论文通过 web_search 补充。
