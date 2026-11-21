# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-vortex-oam-hhg-20261101
- 生成时间：2026-11-15T21:40:31Z
- 方法关键词：Berry、HHG、OAM、从未在同一套测量、共用一套源与测量、的双通道读出方法、破缺量的可观测量

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 〇、方法专题（6，谱系/选型层）

### [[method-topics/HHG反演方法学|HHG 反演方法学（贝叶斯推断 / 神经网络正则化 / 约束优化）]]
页：knowledge/wiki/method-topics/HHG反演方法学.md
专题定位：从谐波谱反推凝聚态参数（能带色散、跃迁偶极、退相干时间、Berry 曲率、

### [[method-topics/固体HHG数值计算方法体系|固体 HHG 数值计算方法体系（TDSE / SBE / rt-TDDFT / 紧束缚）]]
页：knowledge/wiki/method-topics/固体HHG数值计算方法体系.md
专题定位：强激光入射晶体后谐波谱的数值预言方法——四套范式的理论原理、

### [[method-topics/材料体系HHG方法|材料体系 HHG 方法（Weyl 半金属 / 交变磁体 / moiré / 高阶拓扑）]]
页：knowledge/wiki/method-topics/材料体系HHG方法.md
专题定位：四类量子材料的 HHG 指纹、模型栈与判据——每类材料「用什么模型、

### [[method-topics/量子光驱动HHG方法|量子光驱动 HHG 方法（BSV / 压缩光 / 输出态层析）]]
页：knowledge/wiki/method-topics/量子光驱动HHG方法.md
专题定位：以非经典光场（亮压缩真空 BSV、压缩态）驱动的 HHG——谐波光的

### [[method-topics/量子几何量测量方法谱系|量子几何量测量方法谱系（Berry 曲率 / 量子度规 / 拓扑数）]]
页：knowledge/wiki/method-topics/量子几何量测量方法谱系.md
专题定位：面向「用 HHG 读出凝聚态量子几何量」这一测量目标的路线谱系——

### [[method-topics/多变量光场设计|多变量光场设计（双色 / CEP / 椭圆度 / 取向 / OAM）]]
页：knowledge/wiki/method-topics/多变量光场设计.md
专题定位：强场过程的场几何自由度设计——八维约束空间的每个维度如何

## 一、匹配的知识库方法页（8）

### [[methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理|固体 HHG 理论四路线（SBE / TDDFT / Wannier-Bloch / 规范处理）]]
页：knowledge/wiki/methods/固体_HHG_理论四路线_SBE___TDDFT___Wannier-Bloch___规范处理.md
摘要： SBE 在能带色散局部抛物近似下给出截止标度律，把能带、电流与再碰撞相位联系起来；TDDFT 直接计算强场含时电流、对层间耦合与莫尔势不依赖经验参数，但仅适用莫尔周期小（大扭转角）构型；Wannier-Bloch 轨迹把倒空间几何约束直接对应到谐波阶次与倒空间轨迹长度；Berry 连接规范处理以 London/Coulomb 规范差值检验规范不变性。局限：四条路线均只描述理想晶体，扭转角 + 激子预激发 + 层间传播共同作用下的可检验映射尚无单一路线给出，多体修正须作为参数输入耦合项。  <!-- linsai-wikilinks --> ## 关联概念  - [[TDDFT]] - [[层

### [[methods/berry|Berry 曲率偶极（BCD）分析]]
页：knowledge/wiki/methods/berry.md
摘要：Berry 曲率偶极（BCD）分析以动量空间中 Berry 曲率分布的一阶矩描述非中心对称体系的二阶响应，解析框架可推广至温度梯度驱动的横向非线性能斯特/热输运并与电学非线性霍尔形成互补读出通道，光驱动体系亦存在 Berry 曲率闭式公式可定位能隙处曲率热点，且作为弱场半经典基准其在强场完全非平衡区被非微扰理论对照检验并证明失效；本轮新证据进一步把 Berry 曲率类分析拓展为拓扑量读出窗口——轨道磁矩算符与 Berry 曲率/Chern 数的关联使逆法拉第（IFE）二阶光响应张量与能带 Chern 数建立解析联系，Berry 曲率/Chern 数计算亦可直接表征光致能隙拓扑、证明螺旋度可控 Chern 数符号的 Chern 绝缘体相。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | hBN 五次谐波（5ω）转换效率 | ~4×10⁻⁵ |

### [[methods/BSV驱动固体HHG实验|BSV驱动固体HHG实验]]
页：knowledge/wiki/methods/BSV驱动固体HHG实验.md
摘要： Rasputnyi等2024年在Mg:LiNbO₃与非晶硅中实现：单模脉冲25 fs FWHM（相干对照70 fs、同平均强度），光子数0–2×10¹³/脉冲（约2.5 μJ，1.6 μm中心波长），±1 V/Å亚周期电场涨落使4–7次谐波产额较同强度经典光提高5–15倍。  <!-- linsai-wikilinks --> ## 关联概念  _暂无关联概念_ <!-- /linsai-wikilinks --> 

### [[methods/二次谐波产生与HHG轨道角动量上转换|二次谐波产生与HHG轨道角动量上转换]]
页：knowledge/wiki/methods/二次谐波产生与HHG轨道角动量上转换.md
摘要： > ⚙ **管线工作页**（2026-11-01 分类）：本页为课题方案/管线中的操作子步骤，非独立可教学方法——不适用方法页 A 级判据，随母方法页与课题档案维护。 在ZnO/GaSe固态样品中结合二次谐波拓扑荷加倍与高次谐波轨道角动量上转换，来源报告最终TC达到36。

### [[methods/压缩光_HHG_截止方差关系|压缩光 HHG 截止方差关系]]
页：knowledge/wiki/methods/压缩光_HHG_截止方差关系.md
摘要： 对压缩光驱动 HHG，归一化截止方差满足 ΔH²(r)/ΔH²_SQL=exp(−2r)。该指数关系不依赖绝对真空场幅度，因此对纳米尺度模体积的不确定性较稳健。

### [[methods/8_带紧束缚___Houston_基自旋分辨_HHG_正演|8 带紧束缚 + Houston 基自旋分辨 HHG 正演]]
页：knowledge/wiki/methods/8_带紧束缚___Houston_基自旋分辨_HHG_正演.md
摘要： 构造 8 带（4 价带 + 4 导带）紧束缚模型，k 点默认 20³、收敛判据 30³；能带参数取自 ARPES 实验（Krempaský 2024；Osumi 2024），与判据口径表一致。  <!-- linsai-wikilinks --> ## 关联概念  - [[arpes]] <!-- /linsai-wikilinks --> 

### [[methods/EFT_框架下的_valley-resolved_HHG|EFT 框架下的 valley-resolved HHG]]
页：knowledge/wiki/methods/EFT_框架下的_valley-resolved_HHG.md
摘要：构造分层 Hamilton 族 **H_λ(k)=|t/λ|[f(K_τ+λq)σ₊ + h.c.]**：通过尺度变换 a_cc→λa_cc、t→t/λ，在固定 Fermi 速度 v_F 下把 trigonal warping（晶格三度对称破缺）算符从 0 连续调到最近邻紧束缚真实石墨烯强度（λ=1）；λ=0 极限为各向同性 Dirac 锥。  该对称极限构成**严格空检验**：ω-2ω 反旋圆极化场下的谷对比度 P_N 在 λ=0 由选择定则严格为零（非数值巧合）。激光矢势幅 A_0 充当「碰撞能量」角色，**x=λa_cc·A_0 为唯一展开参数**；EFT 幂次计数预言谷奇谐波产量 ∝λ 线性增长、谷偶谐波 ∝λ²，与高维算符的标准 EFT 行为一致。带内动力学用 SBE 求解：H4 在 x≲0.5 内领头 warping 修正即可解释真实石墨烯谷对比至 10% 以内；H4/H5 旋

### [[methods/现代极化理论与Berry相位计算|现代极化理论/Berry相位极化计算]]
页：knowledge/wiki/methods/现代极化理论与Berry相位计算.md
摘要：现代极化理论将晶体极化定义为绝热过程中占据态布洛赫波函数沿k点串累积的Berry相位，极化仅在两结构差值意义下有定义（以量子eR/Z取模），本组据此定量提取滑移铁电的面外极化及其随层间堆叠的翻转，并支撑滑移极化与自旋-能谷耦合强度的线性标度；新证据进一步将Berry联络/曲率纳入量子几何张量统一框架——其实部为量子度规（支配光吸收、非线性电导、体光伏等光学响应），虚部为Berry曲率（其布里渊区积分经TKNN公式给出Hall输运），子丛几何表述与X波磁体综述均在该框架下统一刻画度规与曲率，Berry相位极化计算即这一几何对象在极化差分提取中的具体实现。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 量子度规-曲率逐点约束 det g_n^{μν}(k) | ≥ (Ω_n^{xy}/2)^2，无量纲 | paper:2025-2512.054

## 二、带方法卡的论文页（6）

### [[papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter|BSV 微扰双色 HHG：单发光子统计 + 原位四缝干涉量子态层析 + 隧穿涨落阿秒分辨]]
页：knowledge/wiki/papers/2025-2511_18362-attosecond-resolved-quantum-fluctuations-of-light-and-matter.md
参数样例：参数；---；驱动构型；对称性关系

### [[papers/2026-2607_16477-measuring-the-dipole-phase-of-bloch-trajectory-har|单片共路干涉仪测量固体 HHG 偶极相位（强度-z 联合扫描 + Bloch 振荡轨迹归因）]]
页：knowledge/wiki/papers/2026-2607_16477-measuring-the-dipole-phase-of-bloch-trajectory-har.md
参数样例：参数；---；激光系统；样品

### [[papers/2025-2510_16672-phase-matching-of-high-harmonic-generation-in-twisted-van-de|扭转范德华晶体的 Pancharatnam–Berry 相位匹配——moiré 倒格矢准动量补偿实现 hBN 五次谐波 4×10⁻⁵ 转换效率纪录与纯圆偏振发射（北大刘开辉/洪昊组，PRL 135, 166902, 2025）]]
页：knowledge/wiki/papers/2025-2510_16672-phase-matching-of-high-harmonic-generation-in-twisted-van-de.md
参数样例：参数；---；关键数据；机制

### [[papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic|固体 HHG 的非共线相位匹配（不对称光子上转换：强场 N+1 光子 + 弱场 1 光子横向动量补偿）]]
页：knowledge/wiki/papers/2024-241119046-noncollinear-phase-matching-of-high-harmonic.md

### [[papers/2610.15251|EFT 分层 Hamilton 族 H_λ（可调 trigonal warping 的谷分辨 HHG 探针框架）]]
页：knowledge/wiki/papers/2610.15251.md
参数样例：参数；---；warping 耦合 λ；EFT 展开参数 x=λa_cc·A_0

### [[papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i|菱方石墨鼓面态近理想量子几何的第一性原理核验（DFT+Wannier+Wilson loop+Kubo QGT 空间分辨）]]
页：knowledge/wiki/papers/2026-2607_28491-drumhead-surface-states-of-rhombohedral-graphite-with-near-i.md
参数样例：参数；---；计算设置；DSS 曲率定量
