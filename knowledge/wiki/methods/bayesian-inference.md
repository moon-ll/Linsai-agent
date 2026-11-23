---
title: "bayesian-inference"
type: "methods"
created: "2026-09-12T23:20:39Z"
updated: "2026-11-21T01:35:51Z"
tags: ["方法学", "type/method"]
related: ["2025-2508.13845-extraction-of-the-self-energy-and-eliashberg-function-from-a", "2026-2608_09378-parameter-dimension-aware-reconstruction-of-hhg-spectra-via", "2402.08151", "2404.05671", "2407.11288", "2506.18802", "2508.13845", "2608.09378", "FROG", "Perturbative adaptive importance sampling for Bayesian LOO cross-validation", "Trans-dimensional Hamiltonian 模型选择与参数估计笔记", "arXivID", "协方差矩阵", "混合几何自适应MCMC在高阶Ising模型贝叶斯推断中的应用", "物理信息神经网络（PINN）", "高次谐波产生"]
source_raw: ""
growth_stage: "mature"
confidence: 0.8
updated_at: "2026-11-21T01:35:51Z"
settled_count: 19
aliases: ["Bayesian inference", "Bayesian", "MCMC", "贝叶斯推断", "贝叶斯"]
---

<!-- methods-settle:v1 -->

## 原理

贝叶斯推断以概率视角统一不确定性量化与优化：将 PINN 损失重释为负对数后验并对反演参数/函数输出后验分布与置信区间，可将超参数贝叶斯化（ZAPS 对扩散后验采样的引导系数 ζ_t 施先验并在噪声水平未知时零样本稳健选择引导强度）、将聚类模型贝叶斯化（BDMC 为含间断 PDE 反问题的界面分类与混合成分数选择提供不确定性量化）、经拉格朗日乘子把约束并入目标函数使约束 BO 退化为标准 BO并推广到泊松逆问题（泊松似然×先验与计数统计严格一致 + 经验贝叶斯由数据自动确定正则强度 + NUTS 输出不确定性带）；其采样与模型比较工具箱持续扩展：混合几何自适应 MCMC 在噪声观测下对耦合参数输出完整后验并以 ESS/R-hat 诊断采样混合效率与后验估计可靠性，高阶 Ising 模型从自旋构型数据反演 k 体耦合参数、属配分函数不可解而需似然近似的困难推断场景，RJMCMC 经细致平衡跳转在不同维数参数空间间迁移、把模型选择本身纳入后验采样，贝叶斯证据（含 Occam 因子的边际似然）在稀疏数据下自动实现简约性-拟合度权衡并自动惩罚过参数化，熔点、声子、MD 等异构不同保真度数据可经多源数据同化融合进统一后验相图并输出相界置信区间而非单一线条，可复现基准套件以图像修复/X 射线断层/相位恢复三类前向算子与真值已知的标准任务系统量化重建误差、后验覆盖度等指标以便横向比较求解器、可对其他反演算法（含超快光学重建）做对照评测，bayes_spec 以 PyMC/NUTS 完整后验替代点估计、为自定义谱线模型参数给出可信区间与参数简并诊断并内建先验敏感性与模型比较、层次贝叶斯超先验可对多源/多谱线数据联合约束在低信噪比下稳定参数估计，McFine 以 emcee 仿射不变系综 MCMC 把多分量谱线拟合从单点最小二乘解升级为后验分布采样、输出超精细拟合 Tex/τ/v/σ 完整后验并显式量化多分量间参数简并与不确定度、其模块化正向模型-采样器架构与开源 Python 实现可作其他谱学拟合问题的软件工程参考，Bhattacharyya 距离/贝叶斯误差界可免训练预测光电混合系统下游分类精度，扰动自适应重要性采样免重新采样/拟合获得可信留一预测密度（ELPD）估计，贝叶斯顺序更新支持新评测证据增量并入后验实现连续学习、BayesFlow 把离散工作流搜索空间统一为后验分布上的采样问题、自适应序贯蒙特卡洛以 MCMC 重生核在重采样后恢复粒子多样性、贝叶斯层次建模的组间条件独立似然结构使数据删除可解析分解，摊销贝叶斯推理（仿真式推断/神经后验估计）在模拟器数据上一次性离线训练后对新观测毫秒级输出完整后验、k-hat 超阈值（分布外数据或模型错设）时回退到针对精确后验的 MCMC，AXE 类近似交叉验证以一次全数据 MCMC 拟合的后验均值与协方差替代固定效应+随机效应层次回归的逐簇重拟合；Gelman–Vehtari 贝叶斯工作流提供「问题构建→先验预测→SBC→拟合→后验预测→模型比较」的完整可复用流水线并以层次贝叶斯部分池化建模各事故年损失发展给出含尾部不确定度的准备金后验，高斯过程/核岭回归方差与核方法+贝叶斯线性回归的预测不确定度为力场能量/力预测提供误差棒、作为不确定性驱动主动学习（预测方差超阈值即触发 DFT 标注与再训练）的判据，贝叶斯联合参数优化/后验采样把自能与 Eliashberg 函数提取中电声、电电子、电杂质各通道参数与谱形状纳入统一后验联合反演、替代各通道手工赋值并量化不确定度；贝叶斯/主动学习方法已深入超快光学核心任务：FROG 脉冲检索以似然×先验构造脉冲场后验分布并经 MCMC 给出谱相位、时间强度等检索量的统计误差棒，BayesHHG 将高次谐波谱学拟合转化为后验分布估计并系统传播实验噪声与模型误差，量子动力学参数估计以物理先验×实验似然定量化超快电子动力学参数置信区间，分布化参数估计以参数后验替代单一最优拟合并动态刻画参数简并带随观测通量的演化与解除；优化端：物理信息 BO 以极少量昂贵的 HHG 效率评估在多参数驱动空间逼近全局最优驱动条件，本轮新增（简报级）：主动学习/贝叶斯优化实验控制在高维参数空间中实现超快科学装置实验的自动寻优与实时反馈，把贝叶斯优化谱系从单一目标寻优（HHG 效率）扩展到装置级在线实验闭环控制。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 实验噪声水平 σ（高斯与运动去模糊、图像修复、超分辨率四类噪声逆问题） | 0.05（无量纲） | arXiv:2407.11288 |
| LDMOS 功率晶体管 FOM 物理极限探索的目标击穿电压（BV）范围 | 30–50 V | arXiv:2308.09612 |
| 谐波数相对于偶极响应矩阵秩的条件 | N_HHG−r ≥ 1（无量纲计数） | arXiv:2608.09378 |

## 适用边界

推断与优化结果依赖先验分布与似然/代理模型的选择，后验采样与超参数贝叶斯化的计算成本显著高于确定性方法；去卷积类泊松逆问题中前向算符病态致发射谱亚分辨高频分量仅被弱约束且经验贝叶斯对 Richardson-Lucy 参考谱先验构造敏感，扩散后验采样假定已知前向算符且 ζ_t 需固定采样步数做零样本微调，拉格朗日乘子约束 BO 的有效性依赖乘子自适应策略，BDMC 界面分类建立在 GMM 混合建模假设之上，跨维 RJMCMC 与边际似然模型比较的可靠性依赖采样混合效率（需 ESS/R-hat 类收敛诊断保障），高阶 Ising k 体耦合反演因配分函数不可解须依赖似然近似、结论受似然近似对真实似然逼近质量的约束，基准套件结论仅在图像修复/X 射线断层/相位恢复等受控正向算子/噪声/先验失配设定下可迁移，谱线建模后验（bayes_spec、McFine）对先验规范敏感且参数简并的边缘后验解读依赖采样器混合质量，Bhattacharyya 距离/贝叶斯误差界给出的是贝叶斯误差的界而非精确分类精度，免重拟合 ELPD 估计的可信度依赖扰动自适应重要性采样对留一后验偏移的近似质量，贝叶斯顺序更新依赖各轮评测间候选模型的一致性，BayesFlow 式工作流后验采样以代理后验对离散搜索空间的充分覆盖与训练分布代表性为前提，SMC 重生核的效果依赖变异核选择且强似然偏移下权重退化仍可能发生，层次建模数据删除解析分解严格以组间条件独立的似然结构为前提，摊销贝叶斯毫秒级即时后验以模拟器生成数据对真实观测分布的覆盖为前提、k-hat 超阈值时须回退 MCMC 而重担小时级采样成本，AXE 类近似的可信度依赖其对逐簇重拟合结果的逼近质量，Gelman–Vehtari 工作流的可复用性依赖全流程逐阶段执行及其仿真与多次拟合的计算成本，层次贝叶斯准备金模型结论目前仅在 ILS 证券化场景系统验证，GP/KRR 方差与核方法+贝叶斯线性回归误差棒作为主动学习触发判据时跨相区外推可靠性取决于不确定度估计的校准质量且 DFT 标注与再训练成本显著，自能/Eliashberg 函数提取的多通道联合贝叶斯优化建立在通道分解模型假设之上、后验对谱形状参数化与各通道耦合建模方式敏感，相图多保真数据同化与分布化参数估计的简并带位置及「解除」判定依赖采样混合质量、先验规范及观测通量变化范围的覆盖，FROG/HHG 谱学/量子动力学贝叶斯检索的可信区间以前向模型与噪声/模型误差传播设定的准确性为前提且高维 MCMC 采样成本显著，物理信息 BO 在 HHG 效率寻优中「极少量评估逼近全局最优」的效力依赖代理模型/物理先验对多参数 HHG 响应面的近似精度与采集函数在极少评估预算下的探索-利用平衡、BO 输出最优驱动条件而非后验分布本身不提供不确定度量化；本轮新增：主动学习/BO 实验控制的自动寻优与实时反馈效力依赖高维参数空间中代理模型/采集函数的近似质量与装置实时反馈的时延和噪声水平，且为简报级线索、细节待回原文核实。

## 代表作

- arXiv:2512.02495
- arXiv:2407.11288
- arXiv:2308.09612
- arXiv:2606.24971
- arXiv:2510.14656
- arXiv:2503.03007
- arXiv:2404.05671
- arXiv:2506.18802

## 证据日志

- 2026-10-18｜r83｜仅简报｜[paper:2025-2504.15211-position-bayesian-statistics-facilitates-stakeholder-partici] 贝叶斯更新/顺序推断：新评测证据可增量并入后验，实现评估的连续学习而无需从头重跑评测。
- 2026-10-18｜r83｜仅简报｜[paper:2026-2601.22305-bayesflow-a-probability-inference-framework-for-meta-agent-a] 贝叶斯后验采样：把离散的工作流搜索空间统一为后验分布上的采样问题，提供了区别于贪心生成与网格搜索的概率视角。
- 2026-10-18｜r83｜仅简报｜[paper:2025-2501.07685-adaptive-sequential-monte-carlo-for-structured-cross-validat] MCMC rejuvenation核：重采样后对粒子施加变异更新，恢复样本多样性、抑制SMC路径上的权重退化。
- 2026-10-18｜r83｜仅简报｜[paper:2025-2501.07685-adaptive-sequential-monte-carlo-for-structured-cross-validat] 贝叶斯层次建模：组间条件独立的层次似然结构使数据删除可解析分解，是桥接方案高效可行的前提。
- 2026-10-18｜r84｜仅简报｜[paper:2026-2409.04332-amortized-bayesian-workflow] 摊销贝叶斯推理（仿真式推断 / 神经后验估计）：在模拟器生成的数据上一次性离线训练，之后对新观测即时输出完整后验分布，把贝叶斯推断成本从小时级采样降到毫秒级前向传播。
- 2026-10-18｜r84｜仅简报｜[paper:2026-2409.04332-amortized-bayesian-workflow] MCMC 回退采样：当 k-hat 超阈值（摊销结果不可信，典型为分布外数据或模型错设）时切换到针对精确后验的 MCMC，保证最坏情况下的统计正确性。
- 2026-10-18｜r84｜仅简报｜[paper:2024-2407.19779-approximate-cross-validated-mean-estimates-for-bayesian-hier] 贝叶斯层次回归模型（固定效应+随机效应）：本文建模框架，其分层/聚类结构正是精确交叉验证必须逐簇重拟合、成本高昂的根源。
- 2026-10-18｜r84｜仅简报｜[paper:2024-2407.19779-approximate-cross-validated-mean-estimates-for-bayesian-hier] MCMC 后验抽样：只需一次全数据 MCMC 拟合即可提取 AXE 所需的后验均值与协方差矩阵。
- 2026-10-18｜r85｜仅简报｜[paper:2024-2407.14666-a-bayesian-workflow-for-securitizing-casualty-insurance-risk] Gelman–Vehtari 贝叶斯工作流：提供'问题构建→先验预测→SBC→拟合→后验预测→模型比较'的完整可复用流水线，本文首次系统应用于 ILS 证券化场景。
- 2026-10-18｜r85｜仅简报｜[paper:2024-2407.14666-a-bayesian-workflow-for-securitizing-casualty-insurance-risk] 层次贝叶斯损失发展/准备金模型：以部分池化刻画各事故年损失发展的共性与个体差异，给出最终损失与准备金的后验分布（含尾部不确定度）。
- 2026-10-18｜r85｜仅简报｜[paper:2019-1903.09613-phase-transitions-of-hybrid-perovskites-simulated-by-machine] 贝叶斯推断不确定度估计（高斯过程/核岭回归方差）：为力场的能量/力预测提供误差棒，作为触发在线采样的判据，是保证跨相区外推可靠性的关键。
- 2026-10-18｜r85｜仅简报｜[paper:2024-2203.03824-uncertainty-aware-molecular-dynamics-from-bayesian-active-le] 不确定性驱动的贝叶斯主动学习：MD中预测方差超阈值即触发DFT标注与再训练，使训练集自动聚焦于相变等罕见关键构型。
- 2026-10-18｜r85｜仅简报｜[paper:2024-2402.13450-on-the-fly-machine-learned-force-fields-for-warm-dense-matte] 核方法 + 贝叶斯线性回归力场：以核描述符映射能量/力并天然输出预测不确定性，作为主动学习的触发判据
- 2026-10-30｜r102｜仅简报｜[paper:2025-2508.13845-extraction-of-the-self-energy-and-eliashberg-function-from-a] 贝叶斯推断（联合参数优化/后验采样）：对电声、电电子、电杂质各通道参数与谱形状联合优化，替代手工赋值并量化不确定度。
- 2026-11-01｜r112｜仅简报｜[paper:2025-2503.03007-benchmarking-diffusion-annealing-based-bayesian-inverse-prob] 贝叶斯逆问题基准框架（图像修复/X射线断层/相位恢复）：提供前向算子与真值已知的三类标准任务，可系统量化重建误差、后验覆盖度等指标，便于横向比较求解器。
- 2026-11-01｜r112｜仅简报｜[paper:2024-2404.05671-hybrid-geometry-adaptive-mcmc-for-bayesian-inference-in-high] 高阶Ising模型贝叶斯参数反演：从自旋构型数据反演k体耦合参数，属于配分函数不可解、需似然近似的困难推断场景。
- 2026-11-01｜r112｜仅简报｜[paper:2025-2506.18802-trans-dimensional-hamiltonian-model-selection-and-parameter] 贝叶斯模型选择与边缘似然（证据）：通过证据与Occam因子对不同维数模型进行比较，自动惩罚过参数化。
- 2026-11-01｜r113｜仅简报｜[paper:2023-2309.01271-bayesian-inference-of-composition-dependent-phase-diagrams] 贝叶斯推断/多源数据同化：把熔点、声子、MD 等异构、不同保真度的数据统一进相图后验，输出相界置信区间而非单一线条。
- 2026-11-01｜r113｜仅简报｜[paper:2024-2411.00924-bayes_spec-a-bayesian-spectral-line-modeling-framework-for-a] 贝叶斯 MCMC 参数推断（PyMC / NUTS）：以完整后验分布替代点估计，为谱线拟合参数给出可信区间与参数简并诊断。
- 2026-11-01｜r113｜仅简报｜[paper:2024-2411.00924-bayes_spec-a-bayesian-spectral-line-modeling-framework-for-a] 层次贝叶斯建模：通过超先验对多源/多谱线数据联合约束，在低信噪比数据下稳定参数估计。
- 2026-11-01｜r113｜仅简报｜[paper:2024-2409.03835-mcfine-python-based-monte-carlo-multi-component-hyperfine-st] MCMC 仿射不变集成采样（emcee）：把多分量谱线拟合从单点最小二乘解升级为后验分布采样，显式量化多分量间的参数简并与不确定度。
- 2026-11-01｜r113｜仅简报｜[paper:2024-2409.03835-mcfine-python-based-monte-carlo-multi-component-hyperfine-st] 贝叶斯正向建模 + Python 开源包（McFine）：提供模块化正向模型-采样器架构与开源实现，可作为其他谱学拟合问题的软件工程参考。
- 2026-11-06｜r115｜仅简报｜[paper:2026-2609.21545-single-best-fits-can-be-misleading-resolving-common-trapping] 贝叶斯后验推断（分布化参数估计）：以参数后验分布替代单一最优拟合，显式暴露参数简并带及其在通量变化下的解除方式，是本文方法论核心。
- 2026-11-15｜r139｜仅简报｜[paper:2023-2310.07079-frog-retrieval-via-bayesian-inference] 贝叶斯推断与后验采样：以似然×先验构造脉冲场后验分布，把'单一最优解'升级为'解+可信区间'的完整统计描述。
- 2026-11-15｜r139｜仅简报｜[paper:2023-2310.07079-frog-retrieval-via-bayesian-inference] MCMC（马尔可夫链蒙特卡洛）：在高维脉冲自由度上采样后验分布，直接给出谱相位、时间强度等检索量的统计误差棒。
- 2026-11-15｜r139｜仅简报｜[paper:2023-2301.08636-bayeshhg-bayesian-inference-for-high-harmonic-generation-spe] 贝叶斯参数推断与 MCMC 后验采样：将谱学拟合转化为后验分布估计，输出参数可信区间而非单点值，并系统传播实验噪声与模型误差。
- 2026-11-15｜r139｜仅简报｜[paper:2024-2403.17274-bayesian-parameter-estimation-for-quantum-dynamics] 马尔可夫链蒙特卡洛（MCMC）：对模型参数后验分布进行采样，给出点估计之外的完整不确定度信息与参数间相关结构。
- 2026-11-15｜r139｜仅简报｜[paper:2024-2403.17274-bayesian-parameter-estimation-for-quantum-dynamics] 贝叶斯推断与后验分布：将物理先验与实验似然结合，把超快电子动力学模型参数的置信区间定量化。
- 2026-11-15｜r140｜仅简报｜[paper:2026-2611.14119-physics-informed-bayesian-optimization-of-high-ord] 贝叶斯优化（BO）：以极少量昂贵的HHG效率评估在多参数空间中逼近全局最优驱动条件。
- 2026-11-21｜r1｜仅简报｜[paper:2026-2610.12146-harnessing-machine-learning-for-ultrafast-science-] 主动学习/贝叶斯优化实验控制：在高维参数空间中实现装置实验的自动寻优与实时反馈

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2508.13845-extraction-of-the-self-energy-and-eliashberg-function-from-a]]
- [[2026-2608_09378-parameter-dimension-aware-reconstruction-of-hhg-spectra-via]]
- [[2402.08151]]
- [[2404.05671]]
- [[2407.11288]]
- [[2506.18802]]
- [[2508.13845]]
- [[2608.09378]]
- [[FROG]]
- [[Perturbative adaptive importance sampling for Bayesian LOO cross-validation]]
- [[Trans-dimensional Hamiltonian 模型选择与参数估计笔记]]
- [[arXivID]]
- [[协方差矩阵]]
- [[混合几何自适应MCMC在高阶Ising模型贝叶斯推断中的应用]]
- [[物理信息神经网络（PINN）]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
