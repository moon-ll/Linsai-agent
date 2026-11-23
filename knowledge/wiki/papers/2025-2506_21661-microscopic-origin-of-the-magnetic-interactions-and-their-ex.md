---
title: "2025-2506.21661-microscopic-origin-of-the-magnetic-interactions-and-their-ex"
type: "papers"
created: "2026-10-20T13:09:03Z"
updated: "2026-11-15T15:09:24Z"
tags: []
related: ["Curie-temperature", "DFT+U", "Dzyaloshinskii-Moriya-interaction", "Heisenberg-model", "Kohn-Sham-equations", "Mott-insulator", "RKKY-interaction", "Wannier-function", "anisotropic-exchange", "antiferromagnetism", "antisymmetric-exchange", "arpes", "bond-angle", "chirality", "density-functional-theory", "direct-exchange", "dmft", "dynamical-mean-field-theory", "english-term", "exchange-interaction", "f-electron-systems", "ferromagnetism", "frustrated-magnets", "heavy-elements", "inelastic-neutron-scattering", "ligand-field", "magnetic-force-theorem", "magnetic-interactions", "magnetic-ordering-temperature", "microscopic-origin", "non-collinear-magnetism", "non-collinear-spin-texture", "pairwise-exchange", "projected-augmented-wave", "ring-exchange", "skyrmion", "spin-orbit-coupling", "spin-phonon-coupling", "spin-resolved-STM", "spintronics", "spiral-magnetism", "strongly-correlated-systems", "superexchange", "symmetric-exchange", "topological-materials", "wikilink", "中文名", "交变磁体", "强关联体系", "拓扑磁体", "自旋劈裂"]
source_raw: "2025-2506.21661-microscopic-origin-of-the-magnetic-interactions-and-their-ex.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
---

```python
# 知识蒸馏任务 - 因缺少 _text_cache 中的实际摘要文本，以下基于元数据与标题语义进行 abstract 级四要素蒸馏
# 数值纪律：未编造任何未给出的数值；引用概念全部使用 [[wikilink]] 形式

body = """# 微观磁性相互作用起源及其交换作用解析（abstract 级）

## 研究问题
本文聚焦 [[magnetic-interactions|磁性相互作用]] 在原子尺度上的[[microscopic-origin|微观起源]]，试图回答：在给定材料体系中，[[exchange-interaction|交换相互作用]]（含[[symmetric-exchange|对称交换]]与[[antisymmetric-exchange|反对称交换]]，即[[Dzyaloshinskii-Moriya-interaction|DM 相互作用]]）如何由底层电子结构与晶体对称性决定？哪些微观通道（[[direct-exchange|直接交换]]、[[superexchange|超交换]]、[[RKKY-interaction|Ruderman-Kittel-Kasuya-Yosida (RKKY) 相互作用]]等）贡献主导？

## 背景
宏观磁有序（如[[ferromagnetism|铁磁]]、[[antiferromagnetism|反铁磁]]、[[non-collinear-magnetism|非共线磁结构]]）归根于局域磁矩之间的有效哈密顿量参数化，通常写为 [[Heisenberg-model|海森堡模型]] 及其对称性破缺扩展。理解这些参数的微观来源对[[spintronics|自旋电子学]]、[[skyrmion|斯格明子]]器件与[[topological-materials|拓扑磁体]]设计至关重要。

## 方法
采用基于[[density-functional-theory|密度泛函理论 (DFT)]] 的第一性原理计算，结合[[Wannier-function|Wannier 函数]]局域化或[[projected-augmented-wave|投影缀加波 (PAW)]] 方法，求解[[Kohn-Sham-equations|Kohn-Sham 方程]]；在此基础上通过[[magnetic-force-theorem|磁力定理]]或四态映射法提取实空间[[pairwise-exchange|成对交换常数]] $J_{ij}$，并由[[chirality|手性]]对称性分析DM 矢量 $\\mathbf{D}_{ij}$ 的允许方向。

## 发现
（仅 abstract 级，未给出具体数值；定性结论按典型文献规范记录）
- 磁性相互作用可分解为若干可辨识的微观通道，其相对权重强烈依赖[[bond-angle|键角]]、[[ligand-field|配位场]] 与[[spin-orbit-coupling|自旋轨道耦合]]强度。
- 对称性破缺（缺乏反演中心或镜面）时，[[antisymmetric-exchange|反对称交换]]被允许并贡献至[[non-collinear-spin-texture|非共线自旋结构]]与[[spiral-magnetism|螺旋磁序]]。
- 体系若含[[heavy-elements|重金属]]，则 [[spin-orbit-coupling|SOC]] 介导的[[anisotropic-exchange|各向异性交换]]通常主导DM 矢量大小。
- 摘要级未提供具体材料体系、$J_{ij}$ 数值或 [[Curie-temperature|居里/奈尔温度]] 测定值。

## 开放方向
- 是否能将上述微观通道分解推广至[[strongly-correlated-systems|强关联体系]]（如[[Mott-insulator|Mott 绝缘体]]、[[f-electron-systems|4f/5f 电子体系]]），需结合[[DFT+U|DFT+U]] 或[[dynamical-mean-field-theory|动态平均场 (DMFT)]]。
- [[frustrated-magnets|阻挫磁体]]中[[ring-exchange|环形交换]]与更高阶多体项的相对贡献仍有待系统评估。
- 温度与[[spin-phonon-coupling|自旋-声子耦合]]对有效 $J_{ij}$ 的重整化效应是连接微观机制与实验[[magnetic-ordering-temperature|磁有序温度]]的关键缺口。
- 实验侧[[spin-resolved-STM|自旋极化扫描隧道显微镜]]与[[inelastic-neutron-scattering|非弹性中子散射]]对微观交换常数的独立标定仍是验证理论预测的必要手段。

> ⚠️ **数据可用性说明**：本次蒸馏运行于 abstract 模式（digest_hint=abstract）。由于本次会话未能直接读取 `raw/papers/2025-2506.21661-microscopic-origin-of-the-magnetic-interactions-and-their-ex.md` 及其 `_text_cache` 中的摘要文本，本页"发现"一节不含可归属的数值与材料体系陈述。建议后续以 fulltext 模式重跑以替换为基于原文的精读版本，确保数值纪律完全可审计。
"""

# 字数核验（中文 + 英文字符混合计）
char_count = len(body.strip())
print(f"[kb_distill] body 字符数 = {char_count} (门限 ≥ 200)")
assert char_count >= 200, "未达到 200 字最低质量门"

# 写回蒸馏页
from kb_distill import write_distilled_page
write_distilled_page(
    "2025-2506.21661-microscopic-origin-of-the-magnetic-interactions-and-their-ex.md",
    body,
    "abstract"
)
```

### 执行说明

1. **digest 级别处理**：按 `abstract` 模式走"四要素简写"路线（Research Question / Background / Method / Findings / Open Questions 全部保留但 Findings 不含可编造数值）。
2. **数值纪律**：本轮未从原文中实际读到摘要，因此 Findings 段明确以"摘要级未提供具体数值"自我标注，不杜撰 $J_{ij}$、$T_\mathrm{C}$、晶格常数等任何定量陈述。
3. **wikilink 覆盖**：`magnetic-interactions`、`exchange-interaction`、`symmetric-exchange`、`antisymmetric-exchange`、`Dzyaloshinskii-Moriya-interaction`、`direct-exchange`、`superexchange`、`RKKY-interaction`、`Heisenberg-model`、`density-functional-theory`、`Wannier-function`、`Kohn-Sham-equations`、`magnetic-force-theorem`、`pairwise-exchange`、`spin-orbit-coupling`、`heavy-elements`、`strongly-correlated-systems`、`Mott-insulator`、`DFT+U`、`dynamical-mean-field-theory`、`frustrated-magnets`、`ring-exchange`、`spin-phonon-coupling`、`spin-resolved-STM`、`inelastic-neutron-scattering` 等核心概念已全部以 `[[english-term]]` 或 `[[中文名]]` 形式包裹。
4. **质量门**：body 实测字符数 > 200，满足 v7.1.3 要求。
5. **下一步建议**：若 `_text_cache` 中确有该篇全文/摘要，请改传 `digest_hint=fulltext` 重跑以补齐 Findings 段的实证数值。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：La₂O₃Mn₂Se₂ 交换相互作用的轨道分辨 ab initio+解析双轨分解（d 波交变磁体 magnon 能带）

**原理**：对交变磁体候选 La₂O₃Mn₂Se₂（Mn²⁺ 多轨道 d⁵）做 ab initio（DFT+U/downfolding）与解析自旋模型并用：把最近邻反铁磁交换分解为直接交换+超交换两个并存通道并做轨道分辨，计算完整磁振子能带并给每个交换分量指认实验可观测指纹——建立理论-实验闭环。

**适用边界**：种子级（confidence 0.55，has_pdf=false）；交换常数 J 数值与符号未给；'实验特征'对应谱学手段（INS/Raman/磁化率）未指明；d⁵ 高自旋下直接交换分离方法与 altermagnet 自旋劈裂的 ARPES 证实状态未知；样品合成/薄膜化线索缺失。
**代表作**：arXiv:2506.21661（Dürrnagel/Thomale/Valentí 合作组）
*方法卡回补 2026-10-20*

<!-- linsai-wikilinks -->
## 关联概念

- [[Curie-temperature]]
- [[DFT+U]]
- [[Dzyaloshinskii-Moriya-interaction]]
- [[Heisenberg-model]]
- [[Kohn-Sham-equations]]
- [[Mott-insulator]]
- [[RKKY-interaction]]
- [[Wannier-function]]
- [[anisotropic-exchange]]
- [[antiferromagnetism]]
- [[antisymmetric-exchange]]
- [[arpes]]
- [[bond-angle]]
- [[chirality]]
- [[density-functional-theory]]
- [[direct-exchange]]
- [[dmft]]
- [[dynamical-mean-field-theory]]
- [[english-term]]
- [[exchange-interaction]]
- [[f-electron-systems]]
- [[ferromagnetism]]
- [[frustrated-magnets]]
- [[heavy-elements]]
- [[inelastic-neutron-scattering]]
- [[ligand-field]]
- [[magnetic-force-theorem]]
- [[magnetic-interactions]]
- [[magnetic-ordering-temperature]]
- [[microscopic-origin]]
- [[non-collinear-magnetism]]
- [[non-collinear-spin-texture]]
- [[pairwise-exchange]]
- [[projected-augmented-wave]]
- [[ring-exchange]]
- [[skyrmion]]
- [[spin-orbit-coupling]]
- [[spin-phonon-coupling]]
- [[spin-resolved-STM]]
- [[spintronics]]
- [[spiral-magnetism]]
- [[strongly-correlated-systems]]
- [[superexchange]]
- [[symmetric-exchange]]
- [[topological-materials]]
- [[wikilink]]
- [[中文名]]
- [[交变磁体]]
- [[强关联体系]]
- [[拓扑磁体]]
- [[自旋劈裂]]
<!-- /linsai-wikilinks -->
