# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）

- 课题：general-t-tise2-2-2-2-cdw-20261108
- 生成时间：2026-11-16T15:42:06Z
- 方法关键词：与多时窗重建测量、与多模态超快探测、两观测量、准简并态计算、双泵浦与涨落谱学、四模联合泵浦、固定泵浦、在固定泵浦、声子计算、子弛豫五类观测量、拟采用技术、模先把衍射观测量、现方构成一致测量、的四模联合泵浦

> 用途：update_method_manual / writer 写方案时的可实施细节来源。
> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，
> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。
> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。

## 一、匹配的知识库方法页（2）

### [[methods/dfpt|第一性原理电子结构与声子计算（DFT/DFPT）]]
页：knowledge/wiki/methods/dfpt.md
摘要：基于密度泛函理论（DFT）求解基态电子结构，并以密度泛函微扰理论（DFPT）线性响应计算声子色散与声子本征矢，从而判定声子的红外/拉曼活性及圆偏振特性——如碲中用于确定声子模式红外/拉曼活性与基态电子结构以为驱动方案设计提供依据，在左/右手性α石英中则揭示手性对圆偏振分支标记的锁定。  ## 适用边界  成立条件为玻恩–奥本海默近似与简谐（线性响应）基态框架，结果依赖交换关联泛函精度且计算成本随体系规模增长，不直接描述强场实时驱动的非线性动力学。  ## 代表作  - arXiv:2411.18843 - arXiv:2401.17158  ## 证据日志  - 2026-11-07｜r120｜仅简报｜[paper:2024-2411.18843-laser-controlled-nonlinear-hall-effect-in-tellurium-solids-v] 第一性原理电子结构与

### [[methods/高通量DFT计算流程|高通量 DFT 计算流程]]
页：knowledge/wiki/methods/高通量DFT计算流程.md
摘要：高通量 DFT 流程以统一标准化设置对大批量体系批量计算，通过 PBE 与 PBE+U 等泛函方案的批量比较给出泛函级方法学误差的统计分布，对含过渡金属 3d 的强关联体系可在特定轨道（如 Ni 3d）引入在位 Hubbard U 复现实验能隙与杂化带并分离磁序与关联各自对能带重构的贡献；第一性原理电子结构计算（可结合声子计算）还可从能带对称性量化交替自旋劈裂与磁各向异性能（MAE）以确认亚铁-交替磁性电子结构，并确认费米面附近平带的存在、从能带层面阐明电荷/自旋两种不稳定性的微观根源。  ## 参数表  | 参数 | 数值 | 出处 | | --- | --- | --- | | 统一流程批量计算体系数 | 638 个体系 | paper:2024-2411.10790-effect-of-hubbard-u-corrections-on-the-electronic-and-magne

## 二、带方法卡的论文页（6）

### [[papers/2609.08478|自旋层群声子编程：相干声子动态激活 MnPSe₃ 的 i/d/s 波非常规磁性]]
页：knowledge/wiki/papers/2609.08478.md
参数样例：参数；---；冻结声子计算；动力学模拟

### [[papers/2026-2606_14254-dose-efficient-quantum-phase-estimation-in-lossy-optical-int|损耗干涉仪的剂量高效量子相位估计（多通序列 MP + 控制增强序列 CS，QFI per dose 优化）]]
页：knowledge/wiki/papers/2026-2606_14254-dose-efficient-quantum-phase-estimation-in-lossy-optical-int.md
参数样例：参数；---；量子极限与基准；实验装置

### [[papers/2026-2604_07462-free-space-quasi-phase-matched-second-harmonic-generation-in|石英晶体自由空间准相位匹配二次谐波产生（62 通多通池：弱非线性过程多通积累增强 >1000 倍 + 光束质量 M²=1.1 线偏振保持）]]
页：knowledge/wiki/papers/2026-2604_07462-free-space-quasi-phase-matched-second-harmonic-generation-in.md
参数样例：参数；---；转换效率；输出品质

### [[papers/2024-2409_05419-super-bunching-light-with-giant-high-order-correlations-and|超聚束光的 PCF 产生与高阶光子统计测量（31 路 SPCM 阵列 + N 重符合关联成像）]]
页：knowledge/wiki/papers/2024-2409_05419-super-bunching-light-with-giant-high-order-correlations-and.md
参数样例：参数；---；PCF 结构；种子/泵浦

### [[papers/2025-2502_11452-photoinduced-twist-and-untwist-of-moiré-superlattices-in-tmd|TMD 莫尔超晶格光致扭-解扭的超快电子衍射观测（莫尔卫星峰 + 耦合 ODE 动力学 + 电声耦合第一性）]]
页：knowledge/wiki/papers/2025-2502_11452-photoinduced-twist-and-untwist-of-moiré-superlattices-in-tmd.md
参数样例：参数；---；泵浦；电声耦合

### [[papers/2024-2411_12905-nonlinear-optics-in-2d-materials-from-classical-to-quantum|二维材料非线性光学综述方法框架（SHG 取向/转角/谷极化/磁序探针归纳）]]
页：knowledge/wiki/papers/2024-2411_12905-nonlinear-optics-in-2d-materials-from-classical-to-quantum.md
参数样例：参数；---；单层 MoS₂ SHG 参考
