# Training-set-free 两阶段深度学习光谱去噪（主成分追踪先验）

- 课题 ID: general-tdse-tddft-20261115
- 五维笔记（literature-reading skill 标准）
- 出处：arXiv:2402.18830（2024-02），摘要级蒸馏（KB 蒸馏页 digest_level: abstract）
- 与本课题的关系：**「无干净参考」场景的去噪方案**——物理先验替代标注数据。

## 研究问题（Research Question）

ARPES 等光谱数据测量时间受限、原始信号被噪声主导、且监督式去噪所需的「干净-含噪」配对数据在物理实验中几乎不可能获得——能否用数据自身结构构造先验、彻底绕开训练集？

## 研究背景（Background）

强场超快实验中 beamtime 极其宝贵、采集窗口短；光谱数据的低秩性是被普遍接受但很少被显式用作去噪先验的事实。

## 研究方法（Methods）

两阶段框架：①主成分追踪（Principal Component Tracking）——从含噪数据本身估计自适应先验（挖掘低维子空间结构）；②基于该先验的光谱重建/去噪（无外部训练集）。瞄准 ARPES 等角度分辨类光谱；推广到 TR-ARPES/瞬态吸收需看正文。

## 主要发现与核心结论（Main Results）

1. Training-set-free 两阶段去噪框架成立——「无监督」落到 ARPES 类结构化光谱上。
2. 方法学贡献：用数据低秩结构（PCA 追踪）构造自适应先验，替代大量标注数据。

## 潜在研究方向（Future Directions）

向 TR-ARPES/瞬态吸收光谱的推广验证；先验构造对信号秩结构假设的依赖；去噪伪影对定量分析的传递。

## 对本课题的意义

①本课题实验数据的去噪工具候选：强场泵浦-探测数据同样面临「短窗口+无干净参考」——两阶段框架可直接迁移；②「物理先验替代标注数据」的思路与「可解释反演」主线一致（先验=物理结构约束）；③去噪伪影纪律：去噪后数据用于定量反演前须验证伪影不污染序参量提取。

source: knowledge/wiki/papers/2024-2402_18830-training-set-free-two-stage-deep-learning-for-spectroscopic.md（KB 蒸馏页，摘要级）
