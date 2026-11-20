---
name: literature-reading
description: "Structured literature reading method: five-dimension notes (research question / background / methods / main results / future directions), KB distillation five-elements, and weekend-input deep-digest fields. Use when reading papers for a proposal, distilling raw notes into wiki, or digesting new sources."
version: 1.0.0
author: LinSai-CoPilot
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [literature, reading, notes, distill, 文献阅读, 结构化笔记]
---

# 结构化文献阅读法（literature-reading）

课题文献深读、知识库蒸馏、周末输入消化三条链路统一的结构化阅读方法。核心原则：每篇文献的笔记必须能脱离原文独立回答"这篇文献对课题有什么用"。

## 一、五维笔记（课题文献深读标准）

每篇论文按五个维度整理笔记，每维度 2-3 句实质内容（不是标题复述）：

1. **研究问题（Research Question）**：论文的核心研究问题、目标或中心论点
2. **研究背景（Background）**：学术背景、前人工作、领域现状及研究动机
3. **研究方法（Methods）**：数据来源、实验方法、理论框架或技术路线
4. **主要发现与核心结论（Main Results）**：关键结果、定量发现、核心结论——数字必须保留原值
5. **潜在研究方向（Future Directions）**：研究局限性、注意事项及未解决的开放问题

每篇以"## arXiv ID"行开头独立成节；多篇合并单会话时顺序与清单一致；单篇有效笔记门槛 120 字符，低于视为截断/缺失，降级单篇直读。

## 二、五要素蒸馏（raw→wiki 知识库蒸馏）

整篇文献入库蒸馏（kb_distill，全文级）时每篇笔记必须完整覆盖五要素、每要素一节各有实质内容（v7.0.4 与 kb_distill 实际契约对齐）：

1. **研究问题**（Research Question）：论文要回答的核心问题、目标或中心论点
2. **研究背景**（Background）：学术脉络、前人工作、研究动机
3. **研究方法**（Data & Method）：数据来源、实验/理论/计算方法、材料体系、关键技术
4. **主要发现与核心结论**（Main Results & Findings）：关键结果与定量发现——全文中出现的数值必须原样保留（含单位），不得凭记忆改写或省略
5. **潜在研究方向**（Limitations & Open Questions）：局限性、注意事项、未解决的问题

摘要级来源（无全文）只做摘要级蒸馏，不虚构全文级要素。
方法密度高的论文，"研究方法"节按五节方法卡格式详述（装置/序列/参数表，数值原样）——蒸馏页同时是课题方案写作的方法素材库。

## 三、深读五字段（周末输入新料消化）

单篇新料结构化深读：core（一句话核心发现）、mechanism（物理机制）、method_leads（可借鉴方法线索）、proposal_links（与现有课题的关联点）、keywords（检索关键词）。tier>2 的次级来源不做深读，只留索引。

## 四、通用纪律

1. 数值忠实：转述实验数字与文献原数量级一致，禁止升格（"至少 5-15 倍"不得写成"两个量级"）
2. 挂靠准确：转述特定文献的具体结论时，引用编号与作者名必须匹配，严禁 A 论文的结论挂到 B 条目
3. 无法核实的元数据保持原样并标注，绝不填充
4. 笔记服务于课题：每个维度写完后自问"这对我的课题意味着什么"，无关联的维度可从简
## 五、方法学整理（方法卡提取——可实施方案素材的来源）

文献阅读不止于理解知识，还承担方法学资产沉淀：方案写作的操作性五问（装置/序列/参数/判据/时间预算）能否答上，取决于阅读时有没有把文献里的方法整理成可复用素材。

**方法卡四要素**（与 knowledge/wiki/methods/ 方法页结构化专区字段一一对应）：

1. **原理**：方法测什么/算什么、核心机制两三句（不是教科书式展开）
2. **参数表**：装置配置（光源参数/光路元件/探测器及指标）、测量序列（时序/扫描网格/积分参数）、计算设置（模型/泛函/k 网格/体系规模）——**数值原样保留含单位与出处**，一行一参数
3. **适用边界**：该方法成立的前提、失效条件、统计/分辨率限制
4. **代表作**：方法的关键文献 1-2 篇（作者+年份+核心指标）

**两个采集场景**：

- **深读五字段的 method_leads**（executor lit_read / weekend deep_digest）：method_leads 不是一句话占位，按方法卡要素写实——方法名 + 关键参数或配置特征，供 methods_settle 融合进方法页
- **全文蒸馏的研究方法节**（kb_distill）：方法密度高的论文（核心贡献是方法创新，或实验/计算细节详尽），"研究方法"节按方法卡格式详述装置/序列/参数表；方法密度低的论文该节从简，不为凑格式虚构参数

**纪律**：方法卡的参数必须来自原文（数值忠实，见四节），无出处的参数不写；方法页的融合与维护由 methods_settle 专职步骤执行，阅读侧只负责把素材整理实。

