---
title: "Kubo公式/线性响应输运计算"
type: "methods"
created: "2026-09-25T23:22:46Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: ["Berry曲率", "Kubo公式", "量子几何"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.6
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Kubo公式在线性响应框架下由关联函数计算输运系数，其中反常霍尔电导率对应Berry曲率的布里渊区积分（TKNN关系）；新证据将其扩展到两个方向：一是计算磁振子介导的反常霍尔电导率并量化其对磁振子布居/温度的依赖，二是基于Zeeman量子几何（两能带模型、无需本征函数，可推广至多带）导出反常霍尔电导与磁光克尔/法拉第/磁圆二色的解析谱表达式。

## 参数表

**canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）：
Kubo 线性响应公式把输运系数写成微扰下电流-电流关联函数的积分：σ_{αβ} = (π e²/ℏ)Tr[V_α δ(ε_F−H) V_β δ(ε_F−H)]（Kubo-Greenwood 形式），是第一性原理输运计算的公共出发点。

| 要素 | 内容 | 出处 |
| --- | --- | --- |
| 公式 | σ_{αβ}(ε_F) = (πe²/ℏ)Σ_{nm}⟨ψ_n|v_α|ψ_m⟩⟨ψ_m|v_β|ψ_n⟩ δ(ε_F−ε_n)δ(ε_F−ε_m) | [1] |
| 输入 | 本征态/本征值（DFT 或 TB）+ 速度算符 | [1] |
| 数值要点 | δ 函数以高斯展宽替代，展宽收敛性必须检查 | [1] |

✅ 直流电导/光学电导/反常霍尔等线性响应。
❌ 强场非微输运超出线性响应（需 Boltzmann/量子轨道）；平带/局域态的展宽敏感区慎用。

- R. Kubo, "Statistical-mechanical theory of irreversible processes. Part I," Can. J. Phys. 34, 1274 (1956). https://doi.org/10.1139/p56-138

## 适用边界

仅在线性响应（弱场、小扰动）近似下成立，超出非线性区失效；紧凑解析公式基于两能带哈密顿量导出（多带系统需推广形式），Zeeman几何结果针对X波磁体（p/d/f/g/i波）且温度相关霍尔信号依赖磁振子布居的准确描述。

## 代表作

- paper:2026-2603.19737-magnon-driven-anomalous-hall-effect-in-altermagnets
- paper:2025-2512.05477-quantum-geometry-and-x-wave-magnets-with-xp-d-f-g-i

## 证据日志

- 2026-09-25｜r34｜回原文｜[paper:2026-2603.19737-magnon-driven-anomalous-hall-effect-in-altermagnets] Kubo公式/线性响应输运计算：计算磁振子介导的反常霍尔电导率，量化霍尔信号随磁振子布居/温度的依赖关系。
- 2026-09-25｜r34｜回原文｜[paper:2025-2512.05477-quantum-geometry-and-x-wave-magnets-with-xp-d-f-g-i] 久保公式线性响应计算：导出反常霍尔电导与磁光克尔/法拉第/磁圆二色的解析谱表达式。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[Berry曲率]]
- [[Kubo公式]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
