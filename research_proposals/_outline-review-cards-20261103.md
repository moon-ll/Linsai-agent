# 大纲过目卡 · 8 课题批量审阅（ZCode 整理 2026-11-03）

> 用途：outline_review 队列 15 分钟批量过目。共同背景：8 课题均于 11-02 16:02 按用户裁决（v7.3.0 手册维度上线）整体退回，退回原因同构（major_revision + 手册八要素结构化意见），非内容性否决。

## 汇总表

| # | 课题 | pass | 章节 r/c/s | 手册分/L | 核心命题一句话 | 主要风险 |
|---|---|---|---|---|---|---|
| 1 | [ssh-weyl](../general-ssh-weyl-20260920/) | 2 | 0.81/0.81/0.79 | 0.70/L2 | 三类拓扑物态 HHG 统一判别标尺（Weyl 三因素闭合≥95%） | 守卫缺 2 章 |
| 2 | [attosecond](../general-attosecond-streaking-20260822/) | 4 | **0.88**/0.79/0.83 | 0.68/L2 | 水窗多通道失效修正+跨能区标定 | content 0.79 短板 |
| 3 | [berry-mnps3](../general-berry-mnps3-rashba-20260816/) | 4 | **0.79**/0.81/0.80 | 0.65/L2 | 滑移切换+i-wave HHG 指纹反演 | rationale 两轮均未过线 |
| 4 | [moire](../general-moire-strong-field-probe-20260726/) | 7 | 0.81/0.83/0.83 | 0.66/L2 | 莫尔态读出+光 Floquet 改写闭环 | 7 遍；I_c 余量 2.3-9× |
| 5 | [order-parameter](../general-order-parameter-ultrafast-readout-20260727/) | 5 | 0.81/0.83/0.80 | **0.76/L3** | 交错磁序参量 HHG 唯一归因（FIM κ<10²） | CrSb 波型争议未定 |
| 6 | [key-transient](../key-transient-quantum-phase-optical-20260726/) | 7 | 0.83/0.83/**0.77** | 0.63/L2 | 瞬态量子相全光写-读-反演 | 7 遍；scheme 最低 |
| 7 | [houston](../general-houston-kronig-penney-landau-zener-20261004/) | 2 | 0.79/0.81/0.79 | **0.38/L2** | 三通道分解+四象限标度律 | **手册自查出 LZ 阈值错 10⁴ 倍待回改** |
| 8 | [bsv-hhg](../general-bsv-driven-hhg-quantum-20260726/) | 7 | 0.81/0.82/0.83 | 0.59/L2 | BSV 量子光多体态探针 | 7 遍；自带三级降级出口 |

## 关键判据速览（Go/No-Go）

1. **ssh-weyl**：Weyl 三因素闭合 X+Y+Z≥95%、σ_dec≤5pp、R²≥0.9；ΔI_gap≥2 或 CD 符号翻转偏离 ZnO 参照。
2. **attosecond**：多通道贡献区重构误差 >20%→<5%（≥4×改善）；角积分残余 <2%；解析修正 vs 全耦合 <5%。
3. **berry**：指纹基准 ≥4/5 偏差≤20%；d′≥2.1 单量通过，否则多量融合 √J<1.81 否则 R3 转向。
4. **moire**：SNR=50 下莫尔势误差≤15%、扭转角 ±0.02°；SNR=30 误差≥30% 即 No-Go；TA 抑制>50% + 恢复时间超复合一个量级。
5. **order-parameter**：FIM 条件数 κ<10² 可辨识、>10⁴ 直接 No-Go；磁场反转差分偶次谐波 ≥σ×1.5-2.0 且 SNR>5；后验宽度<先验 50%。
6. **key-transient**：ħω/E_g≥2 用瞬时陈数、≤1 用 Wilson 圈、[1,2] 双轨；写窗口 ħΩ_R/E_g≤0.3；体带隙不得全程闭合。
7. **houston**：三通道交叉项闭合；反常谐波三角甄别；LZ 阈值 5.8×10⁴ TW/cm² vs 驱动 2 TW/cm²（⚠ 手册版本量级错 10⁴ 待修）。
8. **bsv**：QEF 四体系无统计差异→降级分类工具；Q_F 经典极限偏差>5%→降级特征化；mapping R²≥0.7 且 AIC 降≥10。

## 分层与建议批阅顺序

- **优先过目（4 个 7 遍老课题）**：moire / order-parameter / key-transient / bsv——判断是否人工干预或定向补强
- **手册短板组**：houston 0.38（有实锤错误）、bsv 0.59——ZCode 已列入定向重建批次
- **单点亮点**：attosecond rationale 0.88 全队列最高；order-parameter 手册 0.76/L3 冲刺过线在即
- **统一口径确认**：KB 引用守卫根因已修（v7.3.4，原为扫错文件），各课题下轮 writer 将按新纪律⑤补 wikilink——此项不再需要逐课题人工处理

---
*生成：ZCode，2026-11-03T15:23:08Z；逐卡详版见各课题 03_question/question-framework.md。*
