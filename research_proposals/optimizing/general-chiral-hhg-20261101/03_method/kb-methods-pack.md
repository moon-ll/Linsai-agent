# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-chiral-hhg-20261101
- 生成时间：2026-11-20T11:41:00Z
- 方法关键词：Berry、SHG、与幅值唯一由测量、与椭圆度全光调控、作非手性模的测量、全态偏振测量、关断泵浦、定要求为重复测量、射背景区分的泵浦、常散射等大型装置、应的大幅磁致调控、度属场操控观测量、手性探测、拟采用技术

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 〇、方法专题（4，谱系/选型层）

### [[method-topics/量子几何量测量方法谱系|量子几何量测量方法谱系（Berry 曲率 / 量子度规 / 拓扑数）]]
页：knowledge/wiki/method-topics/量子几何量测量方法谱系.md
专题定位：面向「用 HHG 读出凝聚态量子几何量」这一测量目标的路线谱系——

### [[method-topics/HHG反演方法学|HHG 反演方法学（贝叶斯推断 / 神经网络正则化 / 约束优化）]]
页：knowledge/wiki/method-topics/HHG反演方法学.md
专题定位：从谐波谱反推凝聚态参数（能带色散、跃迁偶极、退相干时间、Berry 曲率、

### [[method-topics/固体HHG数值计算方法体系|固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）]]
页：knowledge/wiki/method-topics/固体HHG数值计算方法体系.md
专题定位：强激光入射晶体后谐波谱的数值预言方法——四套范式的理论原理、

### [[method-topics/材料体系HHG方法|材料体系 HHG 方法（Weyl 半金属 / 交变磁体 / moiré / 高阶拓扑）]]
页：knowledge/wiki/method-topics/材料体系HHG方法.md
专题定位：四类量子材料的 HHG 指纹、模型栈与判据——每类材料「用什么模型、

## 一、匹配的知识库方法页（8）

### [[methods/berry|Berry 曲率偶极（BCD）分析]]
页：knowledge/wiki/methods/berry.md
摘要：Berry 曲率偶极（BCD）分析以动量空间中 Berry 曲率分布的一阶矩描述非中心对称体系的二阶响应，解析框架可推广至温度梯度驱动的横向非线性能斯特/热输运并与电学非线性霍尔形成互补读出通道，光驱动体系亦存在 Berry 曲率闭式公式可定位能隙处曲率热点，且作为弱场半经典基准其在强场完全非平衡区被非微扰理论对照检验并证明失效；本轮新证据进一步把 Berry 曲率类分析拓展为拓扑量读出窗口——轨道磁矩算符与 Berry 曲率/Chern 数的关联使逆法拉第（IFE）二阶光响应张量与能带 Chern 数建立解析联系，Berry 曲率/Chern 数计算亦可直接表征光致能隙拓扑、证明螺旋度可控 Chern 数符号的 Chern 绝缘体相。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | hBN 五次谐波（5ω）转换效率 | ~4×10⁻⁵ |

### [[methods/tr-shg|时间分辨二次谐波产生（TR-SHG）]]
页：knowledge/wiki/methods/tr-shg.md
摘要：TR-SHG 采用泵浦–探测构型，通过对称性敏感的二阶非线性光学通道读出瞬态对称破缺，作为分辨量子材料中隐藏相与结构序演化的互补探针（注：本轮另一线索属 HHG 方法，不并入本页）。  ## 参数表  **库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）： | 样品 | 46 nm 厚 3R-MoS₂ 人工晶体（HQ Graphene 块体干法剥离 + 电子束光刻 + 聚碳酸酯印章按 0°/120°/240°/360° 拼接，四区边长 ~8 µm）；偏振分辨 SHG 花瓣图案确认取向 | 研究方法  | 光路 | 1030 nm Yb 飞秒（150 fs、76 MHz）；参考光 2 mm BBO 倍频；75 mm 透镜聚焦、NA=0.5 物镜收集 + 光谱滤波；TWINS 最小延迟步长 ~0.07 fs | 研究方法  | 切换结果 | 四种延迟下分别产生

### [[methods/现代极化理论与Berry相位计算|现代极化理论/Berry相位极化计算]]
页：knowledge/wiki/methods/现代极化理论与Berry相位计算.md
摘要：现代极化理论将晶体极化定义为绝热过程中占据态布洛赫波函数沿k点串累积的Berry相位，极化仅在两结构差值意义下有定义（以量子eR/Z取模），本组据此定量提取滑移铁电的面外极化及其随层间堆叠的翻转，并支撑滑移极化与自旋-能谷耦合强度的线性标度；新证据进一步将Berry联络/曲率纳入量子几何张量统一框架——其实部为量子度规（支配光吸收、非线性电导、体光伏等光学响应），虚部为Berry曲率（其布里渊区积分经TKNN公式给出Hall输运），子丛几何表述与X波磁体综述均在该框架下统一刻画度规与曲率，Berry相位极化计算即这一几何对象在极化差分提取中的具体实现。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 量子度规-曲率逐点约束 det g_n^{μν}(k) | ≥ (Ω_n^{xy}/2)^2，无量纲 | paper:2025-2512.054

### [[methods/Berry_连接规范的交叉检验方法|Berry 连接规范的交叉检验方法]]
页：knowledge/wiki/methods/Berry_连接规范的交叉检验方法.md
摘要： > ⚙ **管线工作页**（2026-11-01 分类）：本页为课题方案/管线中的操作子步骤，非独立可教学方法——不适用方法页 A 级判据，随母方法页与课题档案维护。 分别在 London 规范和 Coulomb 规范下计算带间、带内电流密度，并比较二者差异，以此进行规范不变性检验；物理结论优先建立在规范无关的总电流上。

### [[methods/瞬态吸收光谱|瞬态吸收光谱]]
页：knowledge/wiki/methods/瞬态吸收光谱.md
摘要：瞬态吸收光谱通过泵浦—延迟探测记录样品微分吸收（ΔT/T或ΔR/R）随延迟的演化，时间分辨地重建电子与激发态动力学，时间窗口既下探阿秒域、也可延伸到常规fs–ns之外的微秒—秒域（μs–s TA），直接捕捉被俘获载流子、晶格冷却与光电压衰减等慢过程并充当热、光电压与缺陷三类贡献分解的信号源；宽带阿秒XUV瞬态吸收进一步以单脉冲带宽覆盖元素整套芯边（如Ti全M2,3边），首次实现长程电荷密度波（CDW）有序与激子指纹的同时时域追踪，把芯能级探测从单一谱线拓展到全边指纹的同时读出；并可在特征共振（如WS2 A激子）处作差分探测以识别异质结构中来自空间分离层的邻近贡献信号；偏振分辨变体可解耦各向同性布居响应与各向异性矢量响应——瞬态二向色性用XUV偏振相对泵浦偏振平行/垂直两通道差分读出载流子/激子的取向与对称性弛豫，其圆二色性延伸（阿秒圆二色性光谱）则以左/右旋探测光的差分信号直接读出空穴环电

### [[methods/应变工程晶格与单轴应变扫描|应变工程（晶格常数/单轴应变扫描）]]
页：knowledge/wiki/methods/应变工程晶格与单轴应变扫描.md
摘要：应变工程通过扫描晶格常数或施加双轴/单轴应变连续调制能带结构、费米面nesting与量子几何（shift矢量、量子度规、Berry联络三重相位积），在不破坏晶格与金属性的前提下诱导反常霍尔电导（AHC）的连续可调通道，并可驱动半导体→半金属→极性金属的序贯相变，实现二阶非线性极化率χ^(2)的量级增强（~1 nm/V量级）与分量开关。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 应变驱动SHG极化率χ^(2)（Bi2O2X，应变诱导相变后） | ~1 nm/V（与2D材料最高报道值相当） | 2501.16741 | | 演示应变幅度（Bi2O2X晶体/能带结构计算） | 6% | 2501.16741 | | 应变扫描DFT计算平面波截断能（VASP/PBE） | 600 eV | 2501.16741 | | 结构弛豫力收敛判据 |

### [[methods/统一Hamiltonian框架的rt-TDDFT|统一Hamiltonian框架的rt-TDDFT]]
页：knowledge/wiki/methods/统一Hamiltonian框架的rt-TDDFT.md
摘要：统一Hamiltonian框架的rt-TDDFT通过实时传播含时Kohn-Sham/TDSE方程追踪强场电子动力学，通道完备性要点依然成立——实时传播Kohn-Sham轨道直接给出含时宏观电流的傅里叶谱，带内与带间HHG发射通道同时天然包含而无需通道分离假设（第一性原理同时含带内与带间电流，全谱量化键长-截止能量关系，避免紧束缚/两带模型对能带结构的简化误差）；Floquet拓扑分支——TDDFT含时模拟在双色（ω–2ω）圆偏振强场下第一性原理重现光修饰能带结构与光电子谱，区分Floquet杂化隙与多光子边带贡献；交错磁自旋动力学分支——RT-TDDFT直接模拟线偏激光脉冲下RuO2飞秒自旋动力学，给出光致净磁化约0.2 μB/晶胞；二维全光磁控分支——实时TDDFT直接给出强场下自旋/磁矩与光电流的逐时刻微观演化，作为二维材料面内光控磁态与全光磁控验证的第一性原理工具；频率混合谱学分支—

### [[methods/自发反常霍尔效应测量|自发反常霍尔效应测量]]
页：knowledge/wiki/methods/自发反常霍尔效应测量.md
摘要：在零净磁化条件下测量贝里曲率驱动的横向电输运响应，作为交错磁对称破缺的电学指纹；反常霍尔信号是 Berry 曲率对占据态动量积分的宏观读出，可通过应变调控直接探测拓扑响应的演化。  ## 参数表  **联网检索升级**（2026-11-01，引用已核实）：半经典波包动力学方程组（Xiao–Chang–Niu RMP 2010 综述标准形式）——**$\dot{r} = (1/\hbar)∂ε_n/∂k − \dot{k}×Ω_n(k)$**（群速度 + 反常速度）、**$\hbar\dot{k} = −eE − e\dot{r}×B$**（加速度定理 + Lorentz）——Berry 曲率以反常速度进入输运与光学响应，是带内 HHG 通道几何依赖的解析来源。二阶半经典玻尔兹曼在此基础上加散射项做非线性输运。  | 要素 | 公式 | 出处 | | --- | --- | --- | |

## 二、带方法卡的论文页（6）

### [[papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz|偏振可编程 HHG 光源（多材料筛选：TMDC/拓扑绝缘体/外延双层石墨烯 + SHG/MIR 双驱动）]]
页：knowledge/wiki/papers/2026-2510_16546-high-harmonic-generation-light-source-with-polariz.md
参数样例：参数；---；材料；激光

### [[papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic|固体 HHG 的非共线相位匹配（不对称光子上转换：强场 N+1 光子 + 弱场 1 光子横向动量补偿）]]
页：knowledge/wiki/papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic.md

### [[papers/2025-2506_20873-unconventional-high-harmonic-generation-in-resonant-membrane|共振硅膜超表面的非常规 HHG（q-BIC @3.96 µm + COMSOL 频域非线性波动方程 χ³–χ⁹）]]
页：knowledge/wiki/papers/2025-2506_20873-unconventional-high-harmonic-generation-in-resonant-membrane.md
参数样例：参数；---；超表面；泵浦

### [[papers/2026-2602_12396-symmetries-of-spin-splitting-induced-by-spin-orbit-coupling|点群表示论统一分类——非磁晶体中 SOC 诱导自旋劈裂的对称性地图（Rashba/Dresselhaus/Weyl/Ising 四类原型枚举，Yang, Fernandes, Birol）]]
页：knowledge/wiki/papers/2026-2602_12396-symmetries-of-spin-splitting-induced-by-spin-orbit-coupling.md
参数样例：参数；---；分类框架

### [[papers/2603.08263|时空结构光驱动 HG/HHG 的 OAM 守恒通用标度律（L_q/N_q = q·ΔL₁/ΔN₁：由能量守恒+OAM 守恒联立导出——TC 线性标度 ℓ_q=qℓ₁ 仅为其特例；LG/畸变 LG/STOV 数值与 TSM/SFA 三重验证）]]
页：knowledge/wiki/papers/2603.08263.md
参数样例：参数；---；SHG 数值条件；HHG 数值条件

### [[papers/2026-2601_01617-magnetic-structures-database-from-symmetry-aided-high-throug|对称性辅助高通量磁性结构数据库（自旋群分类 + 交变磁材料筛选：南京大学刘奇航/万贤纲团队——磁结构对称性「底册」可查表选靶）]]
页：knowledge/wiki/papers/2026-2601_01617-magnetic-structures-database-from-symmetry-aided-high-throug.md
参数样例：参数；---；数据库定位；团队
