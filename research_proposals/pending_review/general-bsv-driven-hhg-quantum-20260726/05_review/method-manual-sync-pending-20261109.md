# 方法学手册待同步项（writer 提交，供轮末 update_method_manual 步骤处理）

课题：general-bsv-driven-hhg-quantum-20260726
提交日期：2026-11-09
来源：第 1 轮对抗评审（critic-round-1-scheme.md）问题 1（critical，formula 错转录）

## 待修正条目

**文件**：`03_method/method-manual.md`
**位置**：§2.9 固体截止律与截止判据（另见文件头部参数溯源表第 20 行）

**现值（错误）**：

```
$$E_s=E_B+1.6\hbar\Omega_r^6\quad\text{（交流 Zener 隧穿）},\qquad E_s=3.6\hbar\Omega_I^6\quad\text{（半导体半金属化）}$$
```

**应改为（按 PRL 116, 016601 原文，arXiv:1701.02869 全文核对）**：

```
$$E_s=E_B'+1.6\hbar\Omega_{R,0}\quad\text{（交流 Zener 隧穿）},\qquad E_s=3.6\hbar\Omega_{I,0}\quad\text{（半导体半金属化）}$$
```

配套定义（须同时写入 §2.9）：

- $\Omega_{R,0}$、$\Omega_{I,0}$：对应驱动场强下的**峰值 Rabi 频率**（原文记 $\Omega_I(t)=\Omega_{I0}\exp[-(t-t_0)^2/\tau^2]\cos(\omega_0 t)$，场强重整化在 $\Omega_{I0}$ 中）
- $E_B' = E_g - 2\hbar\Omega_{R,0}$：**带内跃迁重整化后**的带隙（原文 $\overline{E_B}=E_B-2\hbar\Omega_r$）
- 两式对 Rabi 频率呈**线性标度**（一次幂），非六次幂
- 推导链：交流 Zener 区 $E_s = E_B' + 2\times3.2\,U_w$，$U_w = \hbar\Omega_{R,0}/4$；半金属化区 $E_s = 2\hbar\Omega_{R,0} + 3.2\,U_w$
- 以裸带隙表述的等价形式（交流 Zener 区）：$E_s = E_g - 0.4\hbar\Omega_{R,0}$

## 错误成因

原文提取时把下标 R/I 误作上标（六次幂），并把重整化带隙 $E_B'$ 与裸带隙 $E_B$ 混用。

## 已同步位置（本轮 writer 已完成）

- `04_proposal/sections/scheme.md` §3.3 截止判据段（正文）
- `04_proposal/sections/references.md` [29] 条目
- `02_literature/reading-notes.md` 新增 1701.02869 全文核验笔记（含 GaSe 工作点数值自洽核对）

## 数值自洽核对记录

以论文自述工作点（GaSe、30 THz 场、$E_B\approx16\hbar\omega_0$、$\Omega_{I0}\approx0.5\omega_0$）代入线性形式：
$E_B'\approx1.86$ eV、$E_s\approx1.96$ eV，与论文结论句 "the cutoff energy is roughly determined by the band-gap energy" 一致。

## 未处置项（需 update_method_manual 判断）

手册 §2.9 尾部的自检清单条目「固体截止律核对：$E_s$ 两式与 ZnO 对标 [35] 的截止阶差 ≤1 阶（§2.9）」中，
公式引用需同步更新；该清单条目的判据本身（截止阶差 ≤1 阶）不依赖被修正的幂次形式，无需改动判据。
