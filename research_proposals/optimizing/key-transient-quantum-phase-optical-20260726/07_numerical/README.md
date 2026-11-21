# 07_numerical — 瞬态量子相全光读写：理论推导、测量方案与数值验证

> 课题 `key-transient-quantum-phase-optical-20260726` 的用户指定任务交付目录（2026-11-05）。
> 任务：针对课题内容完成理论推导、提出测量方案，并通过数值模拟验证测量方案的可行性，
> 要求测量偏差小于 1%。

## 文档与代码清单

| 文件 | 内容 |
|------|------|
| `01-理论推导.md` | L0 基准模型、瞬时 Berry 曲率/陈数闭式推导、CD-ATA 前向关系、误差传递与 1% 目标预算 |
| `02-测量方案.md` | 写-读-反演可执行协议、参数表（与手册 G.3.3 三档表对齐）、判据门 |
| `03-数值验证报告.md` | 端到端闭环数值验证结果：M1–M4 指标、噪声预算 η_c、收敛性 |
| `sim/model.py` | 基准模型与解析公式（闭式本征态/曲率/陈数/精确演化子），`--self-check` 可跑 |
| `sim/verify_formulas.py` | 16 项解析公式对拍（闭式 vs Kubo 途径 / 规范不变 plaquette / 径向积分） |
| `sim/l0_simulation.py` | 端到端闭环（写 TDSE → 双螺旋度 ATA → 模拟器内嵌波形拟合 → M1–M4），`--self-check` 可跑 |
| `sim/run_validation.py` | 三阶段验证驱动（闭环矩阵 / 噪声预算 / 分辨率收敛） |
| `results/validation-results.json` | 验证原始结果（JSON，含全部偏差数值） |

## 复现

```bash
cd research_proposals/optimizing/key-transient-quantum-phase-optical-20260726/07_numerical/sim
python3 model.py --self-check           # 闭式本征态残差 < 2e-15
python3 verify_formulas.py              # 16 项解析对拍全部 PASS
python3 l0_simulation.py --self-check   # 守恒律 + 迷你闭环反演
python3 run_validation.py               # 端到端三阶段验证（约 30-50 分钟）
```

依赖：numpy（研究性数值验证代码；管线其余脚本仍为零第三方依赖）。

## 核心结论速览

1. **解析层**：瞬时 Berry 曲率闭式 Ω_v = Δ_eff(ħv)²α/(2|d|³)、瞬时陈数闭式
   C_v(t) = sgn[Δ_eff(t)]/2（带隙闭合处 |ΔC| = 1 整数跃变）、圆二色前向关系
   |v̄_σ^cv|² = S + σE_cv²Ω_v，全部经 16 项独立途径对拍（最优 1e-16）。
2. **测量方案**：双螺旋度弱探针 CD-ATA 通道给出 Berry 曲率的严格螺旋度奇宇称
   载体；比值信号 D = (A₊−A₋)/(A₊+A₋) 中占据/相干权重相消，反演无需解卷积权重。
3. **数值闭环**：以精确模拟器为前向模型的波形参数反演（Δ0, κ_m），数据分辨率与
   拟合分辨率有意失配构成真实模型误差；无噪闭环与含噪预算（η_c）见 03 报告。
