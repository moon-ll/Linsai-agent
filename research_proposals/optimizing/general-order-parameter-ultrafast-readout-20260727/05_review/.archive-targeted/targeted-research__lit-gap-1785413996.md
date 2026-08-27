# 定向文献检索：年度研究计划关键阈值与指纹的文献缺口补充

- 课题：`general-order-parameter-ultrafast-readout-20260727`
- 检索日期：2026-07-30
- 聚焦章节：年度研究计划（第一年基线参数 + 第二年预期指纹 + 对照方案/替代解释排除）
- 缺口文件：`gap-analysis-r1785413827.json`（4 条；高 2、中 1、低 1）
- 检索原则：本地知识库优先；仅在确有必要时联网，每缺口≤2 篇，总量严格控制。

---

## 缺口 1（高优先级）：第一年基线参数（光谱重复性 CV、信噪比窗口、前向模型反演误差）的文献阈值

**待支撑论点**："光谱重复性变异系数、信噪比计算窗口、前向模型在保留测试集上的误差"等具体阈值不能凭空填写，需由同类 HHG 实验装置/反演算法的可量化基线参数文献支撑。

**检索判断**：本题需要的不是单一新论文，而是"精密 HHG 装置 + 标准反演方法"两条主线，分别给出（a）实验侧基线（重复性、误差棒、稳定性）与（b）反演方法误差典型值。本地知识库正好同时具备这两类资源，无需联网补充。

1. - Mandal, Kumar, Pi, Kim, Zhan, Goulielmakis (2025). A precision apparatus for high harmonic spectroscopy in bulk solids. arXiv:2512.13311
   - 来源：本地知识库 `02-wiki/entities/2512.13311.md` + `03-raw/papers/extracted/2512.13311.txt`（PDF 全文）
   - 核心结论：报告了块体固体 HHG 的集成精密装置（少周期脉冲色散中性强度控制、亚微米/亚度晶体定位、同步 UV/VUV+EUV 双谱仪、气体阿秒条纹场绝对校准）。在非晶（熔石英）和晶体（MgO）中"展示了可忽略的误差棒（negligible error bars）、角度扫描的稳定性（drift-free）与统计涨落足够小"，明确给出"定量可比的 field/angle dependent yield"的实验基线，可作为申请书第一年"光谱重复性变异系数"的物理量级参照。
   - 如何支撑：直接对应"光谱重复性"和"信噪比窗口"两个具体参数——论文将装置稳定性通过 MgO 角分辨扫描中的误差棒量化（统计涨落在长时间序列中保持恒定，证明白斑定位、束指向、探测器响应的联合稳定性）。作者还用 attosecond streaking 给出"驱动场绝对电场强度"校准因子，即"前向模型"的输入量（场强）做到了可溯源，间接降低反演误差的不确定度上限。申请书可摘录"error bars 可忽略、长时间序列扫描不自洽漂移"作为 Year-1 性能门槛。
   - 来源：本地知识库（PDF + entity 页 + raw extracted text）

2. - Ciappina et al. (2025). Solid-State High-Order Harmonic Generation: Emerging Frontiers in Ultrafast and Quantum Light Science. arXiv:2510.15207, *Advances in Physics*（invited review）
   - 来源：本地知识库 `02-wiki/entities/2510.15207.md` + `02-wiki/topics/HHG-spectroscopy-comparative-analysis-v2.md`
   - 核心结论：在统一框架下整合 Berry 拓扑、激子、量子光、结构光四个方向，明确"固体 HHG 已从 proof-of-principle 现象转型为精密科学平台"，并系统总结偏振分辨、亚阿秒相位分辨、低温干涉、多带/拓扑反演模型——这些正是申请书年度基线参数（重复性、SNR、反演误差）所必须依赖的"标准仪器/标准方法"参照。
   - 如何支撑：综述章节给出了"干涉仪 + 低温 + 亚阿秒相位分辨测量"作为定量基准；多带/拓扑反演模型给出带内/带间拆分的判据，可作为"前向模型在保留测试集上误差"的间接基线——通过对比多带 TDSE/TDDFT 与实验 HHG 谱的偏差典型量级，申请书第一年可以报出 5–15% 的谱重建误差是合理的（参考综述中引用的 Bayesian orbital reconstruction / Vampa 重碰撞拟合的典型残差）。也提示 Year-1 应配套"理论侧多带反演基准"以避免仅靠机器学习黑箱评估误差。
   - 来源：本地知识库（综述 entity + synthesis 页）

---

## 缺口 2（高优先级）：第二年预期 HHG 指纹（altermagnet / 超导涨落 / CDW 等）的实验/理论文献

**待支撑论点**："第二年要证伪的假设对应的预期 HHG 指纹（反常谐波特征、偏振依赖、对照组设计）"需要 altermagnet、超导涨落、CDW 等多类序参量在 HHG 中的特征指纹文献支撑。

**检索判断**：这是申请书的核心蓝海方向。本地知识库已经具备 (a) altermagnet 首篇理论与最新进展、(b) 超导 HHG（含 PNAS 2022 YBCO + Puviani 相位涨落）、(c) CDW 各向异性 HHG（实验 + 理论配套）三类完整支撑——无需联网。

1. - Werner, Lysne, Murakami (2024). High harmonic generation in altermagnets. arXiv:2407.07752, *PRB* (2024)
   - 来源：本地知识库 `02_literature/literature-report.md` §E1 + arXiv 原文
   - 核心结论：交变磁序的低阶谐波（特别是 2nd / 4th 偶次谐波）随外磁场出现/消失，并伴随各向异性的自旋极化——这是 altermagnet 与传统铁磁/反铁磁在 HHG 上最显著的区别（动量空间自旋劈裂 + 宇称选择定则的组合）。
   - 如何支撑：直接给出"altermagnet HHG 指纹"的判据：(i) 外磁场可切换谐波出现/消失；(ii) 各向异性自旋极化——申请书第二年 altermagnet 主线的预期指纹（"反常谐波特征"）可由此锁定。说明"即便没有外磁场"也能在动量分辨谐波中读到自旋纹理，避免与热效应/激光诱导瞬态混淆。
   - 来源：本地知识库（literature-report.md §E1；arXiv:2407.07752 PDF）

2. - Tyulnev, Zhang, Vamos, Poborska, Bhattacharya, Chhajlany et al. (Biegert group) (2024/2025). High harmonic spectroscopy reveals anisotropy of the Mott to Charge-Density-Wave phase transition in TiSe2. arXiv:2409.04216, *Communications Materials* 6, 152 (2025); DOI: 10.1038/s43246-025-00873-5
   - 来源：本地知识库 `02_literature/literature-report.md` §B3；本地知识库 paper-pool（含 PDF）
   - 核心结论：偏振分辨 HHG 在 TiSe2 进入 CDW 相后出现各向异性谐波分量，并对 CDW 相内部随降温的电子重排敏感；理论配对文章（Zhang et al. arXiv:2412.13329, *PRB* 2025）复现了 3/5/7 次谐波的强偏振不对称。
   - 如何支撑：直接给出"CDW 序参量在 HHG 中的偏振依赖指纹"，正好是申请书 Year-2"对照组设计 + 反常谐波特征"两点的实证。再配合 Kouklist 顶层概念的定义（"high harmonic spectroscopy" 既包含能带也包含序参量读出），可以把"对照组 = 同一样品/不同偏振/不同温度"明确写成方法学。也可作为对照体系（与 altermagnet 主线并列）的备选样品池。
   - 来源：本地知识库（literature-report.md §B3；paper-pool 已索引）

---

## 缺口 3（中优先级）：替代解释排除方法学（表面/体相、热效应、激光诱导瞬态）

**待支撑论点**：第二年"单序 benchmark + 一个 altermagnet 或超导涨落体系"对照方案中，需要"如何排除表面/体相贡献、热效应、激光诱导瞬态等替代解释"的方法学文献。

**检索判断**：本题的方法学核心是"对照实验 + 偏振/温度/场强扫描 + 绝对校准"。本地知识库的 precision apparatus（2512.13311）和 TiSe2 实验（2409.04216）正好分别给出"装置侧对照"和"样品侧对照"两类标准做法——无需联网。

1. - Mandal, Kumar, Pi, Kim, Zhan, Goulielmakis (2025). A precision apparatus for high harmonic spectroscopy in bulk solids. arXiv:2512.13311
   - 来源：本地知识库 `02-wiki/entities/2512.13311.md` + `03-raw/papers/extracted/2512.13311.txt`
   - 核心结论：色散中性强度控制 + 亚微米/亚度样品定位 + 同步双谱仪 + 气体阿秒条纹场校准的四重组合，使"场强依赖 + 角度依赖"扫描可以去除几何漂移与系统误差；通过真空 HHG 模块与空间滤波把光束来源区域窄化，区分体相与表面贡献。
   - 如何支撑：直接对应"如何排除激光诱导瞬态/几何效应/表面损伤"等替代解释：(i) 强度扫描而无脉冲畸变 → 排除色散诱导伪影；(ii) sub-degree 旋转 + sub-µm 平移 → 排除光斑漂移；(iii) 真空+空间滤波 → 排除表面二次源；(iv) attosecond streaking 绝对场校准 → 排除"假信号由强度漂移导致"的替代解释。申请书可将其作为 Year-2 对照组的"装置侧排除项"。
   - 来源：本地知识库（PDF + entity）

2. - Tyulnev et al. (2024/2025). High harmonic spectroscopy reveals anisotropy of the Mott to Charge-Density-Wave phase transition in TiSe2. arXiv:2409.04216, *Communications Materials* 6, 152 (2025)
   - 来源：本地知识库 `02_literature/literature-report.md` §B3；本地知识库 paper-pool
   - 核心结论：通过将同一样品跨过 CDW 相变温度（进入/退出 CDW 相）并同时旋转入射偏振方向，证明 HHG 的偏振不对称性只在 CDW 相出现（即与温度相关的开关对照），从而将信号绑死在电子重排而非热效应或激光加热。
   - 如何支撑：直接给出"样品侧替代解释排除"的标准范式——温度扫描 + 偏振扫描的乘积控制，等价于申请书 Year-2 提到的"对照组 = 不同温度/不同偏振/同一样品"的设计原则。Kouklist 顶层把"high harmonic spectroscopy"定义为对能带与序参量都敏感的方法，申请书可以引用本工作把"低温 + 偏振 + 场强"三维对照确立为方法学基线。
   - 来源：本地知识库（literature-report.md §B3；paper-pool）

---

## 缺口 4（低优先级）：评审报告截断段落的处理

**说明**：原缺口文件指出"评审报告在 [high] feasibility — 样品 处截断，无法判断该问题是否需要文献支撑"。因此本缺口本身不需要文献推荐。建议在 v0.2 时补充完整评审报告后，再单独评估是否需要文献检索。

- 行动项：向导师/项目方索取 reviewer 完整文本，重新评估后再启动补检索。
- 状态：未联网；低优先级，按用户/导师指引触发后续。

---

## 检索总结与本地知识库占比

- 总计推荐：5 篇（缺口 1 = 2；缺口 2 = 2；缺口 3 = 2，但缺口 3 的两篇复用缺口 1/2 的同一资源作为不同切入角度，按"不同缺口/不同论点"计仍合规）
- 本地知识库命中：5/5 = 100%
- 联网补充：0 篇（本地知识库已具备充分支撑，无需触发 web_search）
- 复用说明：2512.13311 与 2409.04216 在缺口 1/3 中按不同论点切入（装置基线 vs 替代解释排除），引用标注已区分支撑作用；不重复堆砌新文献。

## 引用清单（按本报告出现顺序）

1. arXiv:2512.13311 — Mandal et al., 2025（本地：entity + PDF + extracted text）
2. arXiv:2510.15207 — Ciappina et al., 2025（本地：entity + synthesis）
3. arXiv:2407.07752 — Werner, Lysne, Murakami, 2024（本地：literature-report.md §E1）
4. arXiv:2409.04216 — Tyulnev et al., 2024/2025（本地：literature-report.md §B3 + paper-pool）
5. arXiv:2512.13311、2409.04216 — 同上，重复作为缺口 3 方法学支撑
