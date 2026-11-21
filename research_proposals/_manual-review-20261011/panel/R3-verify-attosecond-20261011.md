# R3 联网核实报告 — general-attosecond-streaking-20260822 锚点核实

> 核实时间：2026-10-11
> 核实方法：WebSearch + WebFetch + DOI handle 权威解析
> 核实范围：M2.2 移交的 Pabst/Kheifets 量化锚点可支撑性判定

## 关键发现

**M2.2 必须回退**：Pabst-Dahlström [3] + Kheifets [18] 两文献只支撑**定性结论**，**未给出量化数字**（≤2% 残余区间或实测残余区间）。M2.2 用此两文献作为 G2 阈值（2%）的"外部锚点"在量化层面**不可用**。

## 条目 [3] Pabst & Dahlström 2016

`[3] Pabst S, Dahlström J. Eliminating the dipole phase in attosecond pulse characterization using Rydberg wave packets. Physical Review A, 2016, 94: 013411. DOI: 10.1103/PhysRevA.94.013411`

### 字段对账

| 字段 | 待核实 | 权威来源 | 对账 |
|------|------|---------|------|
| DOI | 10.1103/PhysRevA.94.013411 | doi.org handle API | ✓ 真实注册 |
| arXiv | 1602.08144 | arxiv.org/abs/1602.08144 | ✓ 存在 |
| 标题 | Eliminating the dipole phase... | arXiv abs 页 | ✓ 字面一致 |

### 量化数据核实（核心）

- **摘要**：提及 "angle integration eliminates dipole phase" 与 "much smaller"
- **未给出**：偶极相位残余 ≤2% 或任何百分数量化上界
- **判定**：**不可作量化锚**（仅支撑定性结论），可作机理锚

## 条目 [18] Kheifets 2026

`[18] Kheifets A, Serov V, Vismarra F, et al. Rainbow retrieval of atomic time delays in attosecond streaking. Physical Review A, 2026, 113: 043103. DOI: 10.1103/9jcm-8gd8`

### 字段对账

| 字段 | 待核实 | 权威来源 | 对账 |
|------|------|---------|------|
| DOI | 10.1103/9jcm-8gd8 | doi.org handle API | ✓ 真实注册，2026-04-02 出版（ORCID × Wörner/ETH atto group 多源交叉验证）|
| arXiv | — | 公开预印本未发现 | ⚠ 无对应预印本 |
| 标题 | Rainbow retrieval of atomic time delays... | 期刊主页 | ✓ 字面一致 |

### 量化数据核实（核心）

- **摘要**：He/Ar/Xe 时延与 Coulomb 相位定性
- **未给出**：偶极相位实测残余区间数字
- **判定**：**不可作量化锚**（仅支撑定性结论），可作方法锚

## 总判定

| 条目 | DOI 真实性 | 量化数据可支撑性 | M2.2 锚点判定 | 建议处理 |
|------|----------|----------------|---------------|---------|
| [3] Pabst & Dahlström 2016 | ✓ | ✗ 摘要仅定性"much smaller"，无 ≤2% 数字 | **不可作量化锚** | **回退**：删除 M2.2 中"≤2% 上界"具体数字，或将 [3][18] 降级为机理/方法锚 |
| [18] Kheifets 2026 | ✓ | ✗ 摘要仅 He/Ar/Xe 时延，无实测残余区间数字 | **不可作量化锚** | **回退**：同上 |

## M2.2 回退建议

attosecond-streaking 课题的 G2（偶极相位残余 2%）阈值锚点**当前无法用 [3]+[18] 支撑量化主张**。两个修复路径：

### 路径 A：保留数字但换文献
- 寻找带数字的偶极相位残余实测文献：
  - **Schultze et al. 2010** Science 328, 1658-1662 — 阿秒延时测量奠基，给出群延时 vs 单电子相位的定量分离
  - **Kheifets & Ivanov 2010** PRA 81, 053412 — 单电子相位定量模型
  - **Klünder et al. 2011** PRL 106, 143002 — 洛伦兹偶极相位定量

### 路径 B：删除数字量化表述
- 把 G2 阈值从"残余偶极相位 2%"改为"残余偶极相位（具体数值第一阶段实测标定）"
- 同步删除"Pabst-Dahlström 理论方案残余上界 + Kheifets 实测残余"两个引用挂靠

**推荐路径 B**（更保守）+ 第一阶段实测锁定。

## 后续动作

进入 M2.2.1（回退性修改）：派 1 个 subagent 对 attosecond scheme.md 中 G2 阈值段做"删除数字 + 删除锚点 + 改保守表述"修复。