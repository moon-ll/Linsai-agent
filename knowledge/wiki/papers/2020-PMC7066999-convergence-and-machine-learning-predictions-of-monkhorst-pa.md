---
title: "Convergence and machine learning predictions of Monkhorst-Pack k-points and plane-wave cut-off in high-throughput DFT calculations"
type: "papers"
created: "2026-09-28T10:52:16Z"
updated: "2026-11-15T15:09:24Z"
tags: ["DFT", "高吞吐量计算", "机器学习", "k-point收敛", "截断能", "磁性材料", "MnPS3", "Berry曲率"]
related: ["Berry 曲率", "MnPS3", "MnPS3 Rashba自旋电子学", "Monkhorst-Pack k-points", "PLAN", "general-berry-mnps3-rashba-20260816", "pump-probe", "平面波截断能", "强场超快", "磁性材料收敛性", "自旋劈裂", "高吞吐量DFT"]
source_raw: "2020-PMC7066999-convergence-and-machine-learning-predictions-of-monkhorst-pa.md"
growth_stage: "growing"
confidence: 0.7
digest_level: "abstract"
auto_grown: true
review_status: "pending"
---

# Convergence and machine learning predictions of Monkhorst-Pack k-points and plane-wave cut-off in high-throughput DFT calculations

## 林赛的理解

这篇论文看起来跟我组里的实际痛点直接相关——我们用 DFT 做预筛和能带解释时，经常被"截断能取多少、k-mesh 选多密"反复卡住。论文给出了一个 30000+ 材料规模的系统扫描结论，明确默认 520 eV 截断，并对磁性材料提出更严格的收敛要求。对我们正在筹备的 MnPS3 Rashba 项目而言，这意味着：磁性二维材料不能套用通用默认参数，必须做独立的收敛测试，否则后续算出的 Berry 曲率、自旋劈裂可能带系统误差，喂给强场超快动力学模型时会把假信号当真信号。

另外，ML 预测 k-point 和截断能这一思路对我有方法论上的启发：如果能提前预测每个材料所需的计算参数，就可以在高通量筛选"强场响应候选材料"时跳过冗余的自洽计算，把机时留给真正需要做的 pump-probe 模拟。

## 核心要点

- **研究规模**：对 30000+ 材料进行高通量 DFT 收敛性系统研究。
- **方法亮点**：用机器学习预测 Monkhorst-Pack k-point 网格密度与平面波截断能，替代传统的逐材料手动收敛测试。
- **通用推荐**：默认截断能 520 eV 适用于多数体系。
- **重要警示**：磁性材料对收敛性要求显著更严格，通用默认参数可能不足，需单独验证。
- **核心价值**：将原本经验性、依赖人工判断的收敛参数选择过程，转为可由 ML 模型预测的标准化流程，提升高通量筛选效率。

## 实验/研究关联

- **直接关联**（MnPS3 Rashba / Berry 曲率提案）：MnPS3 是反铁磁层状材料，其磁基态和自旋-轨道耦合导致的能带劈裂对 k-mesh 密度敏感。我们若直接套用 520 eV 默认截断和标准 Monkhorst-Pack 网格，DFT 给出的 Berry 曲率和 Rashba 劈裂可能未完全收敛。这篇论文的警示提醒我在进入强场动力学计算前，必须先做 MnPS3 专门的截断能与 k-point 收敛性测试。
- **方法论迁移**：我们组的高场高次谐波（HHG）与阿秒动力学模拟依赖 DFT 给出的能带和偶极矩阵元作为输入。如果未来要做"候选材料高通量筛选"，本论文提出的 ML 预测框架可借鉴——先用 ML 模型预估每个候选材料所需的计算精度参数，再分级调用 DFT。
- **潜在合作点**：若能把 ML 收敛预测应用到磁性 2D 材料库（含 MnPS3、CrI₃、Fe₃GeTe₂ 等），有望快速定位哪些材料在实验上更可能给出可测量的强场自旋/磁化动力学信号。

## 开放问题

- 论文摘要级数据未透露的具体内容：ML 模型用了哪些描述符（成分、晶体结构、电子数等），训练集/测试集划分方式，预测精度指标（R²、MAE 等）——需要读全文确认 ML 模型是否可信地外推到我们关心的磁性 2D 材料家族。
- "磁性材料需要更严格收敛"这一结论对**反铁磁 vs 铁磁**是否细分？是否区分了 2D vs 3D 磁性？MnPS3 是 2D 反铁磁，需要判断其建议是否直接适用。
- 论文是否给出了**误差容忍判据**（如对总能、band gap 的收敛阈值）？这关系到我们 DFT→强场动力学链路中能接受多大的底层误差。
- 与现代 DFT 流程（如 VASP 的 POTCAR 推荐值、Materials Project 内部标准）的对比如何？我们既往工作沿用的具体参数策略是否需要重新校准。

## 来源
- 原始材料：2020-PMC7066999-convergence-and-machine-learning-predictions-of-monkhorst-pa.md
- 关联提案：general-berry-mnps3-rashba-20260816
- 蒸馏时间：2026-09-28T10:52:16Z


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：高通量 DFT 的 k 点网格与截断能收敛标准及 ML 预测（摘要级）

**原理**：高通量 DFT 计算中 Monkhorst-Pack k 点网格与平面波截断能的收敛标准制定 + 机器学习预测最佳参数组合。

**适用边界**：页面为摘要级题录（62 行，无研究方法节）；不虚构参数，待精读后升级。
**代表作**：本文（PMC7066999）
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry 曲率]]
- [[MnPS3]]
- [[MnPS3 Rashba自旋电子学]]
- [[Monkhorst-Pack k-points]]
- [[PLAN]]
- [[general-berry-mnps3-rashba-20260816]]
- [[pump-probe]]
- [[平面波截断能]]
- [[强场超快]]
- [[磁性材料收敛性]]
- [[自旋劈裂]]
- [[高吞吐量DFT]]
<!-- /linsai-wikilinks -->
