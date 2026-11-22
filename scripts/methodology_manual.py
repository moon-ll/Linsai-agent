#!/usr/bin/env python3
"""方法学手册生成器 — 研究管线"申请书撰写"阶段的参考文档模块。

为每个研究 proposal 生成详细的方法学手册。与申请书的"研究方案"章节（面向评审）
不同，方法学手册是**面向用户的研究参考文档**——详细阐述申请书中涉及的每种方法：
    - 理论背景（关键方程、物理原理）
    - 实现细节（参数选择、搭建考量）
    - 数据分析流程
    - 局限性与常见陷阱
    - 关键参考文献（含注释摘要）

位于研究管线"申请书撰写"阶段：
    ... → 03_question（科学问题构建） → 04_proposal（申请书撰写 + 方法学手册） → 05_review ...

产物存储：
    {proposal_dir}/04_proposal/methodology-handbook.json  — 结构化数据
    {proposal_dir}/04_proposal/methodology-handbook.md    — Markdown 导出
    使用 common.save_json 原子写入 + common.file_lock("methodology-{hash}") 跨进程锁。

核心流程：
    1. scan_methods()        扫描申请书各章节，检测涉及的方法关键词
    2. generate_method_entry()  为每个方法从内置数据库拉取模板并定制
    3. generate_handbook()   编排上述步骤，整合知识库链接与引文关联
    4. export_handbook()     导出为 Markdown 或 JSON

内置方法数据库覆盖强场超快光学与凝聚态物理的 18 种核心方法，涵盖理论、计算、
实验、分析四大类别。扫描到内置库以外的方法时，生成占位条目供用户后续补充。

用法:
    >>> from pathlib import Path
    >>> from methodology_manual import MethodologyManual
    >>> manual = MethodologyManual(Path("/data/proposals/T1"))
    >>> proposal_sections = {
    ...     "立项依据": {"content": "固体HHG中的TDDFT计算[1]表明..."},
    ...     "研究方案": {"content": "采用SBE和Floquet理论分析..."},
    ... }
    >>> handbook = manual.generate_handbook(proposal_sections)
    >>> print(manual.get_handbook_stats()["method_count"])
    >>> md = manual.export_handbook("markdown")

命令行自检:
    python3 scripts/methodology_manual.py --self-check

规范：仅 Python 标准库，pathlib.Path 路径处理，JSON ensure_ascii=False，时间戳 UTC ISO。
v6.2 研究管线模块，遵守 AGENTS.md §6 边界规范。
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, lazy_load

__all__ = [
    "MethodologyManual",
    "METHOD_CATEGORIES",
    "METHOD_STATUS_FLOW",
    "BUILTIN_METHOD_DATABASE",
]


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 方法类别
METHOD_CATEGORIES: Dict[str, str] = {
    "theoretical": "理论方法",
    "experimental": "实验方法",
    "computational": "计算方法",
    "analytical": "分析方法",
}

# 方法条目状态机
METHOD_STATUS_FLOW: Dict[str, set] = {
    "generated": {"reviewed", "enriched"},
    "reviewed": {"enriched"},
    "enriched": set(),  # 终态
}

# 引文标记正则：匹配 [1], [1,2], [1-3] 等
_CITATION_PATTERN = re.compile(r'\[(\d+(?:[,-]\d+)*)\]')


# ---------------------------------------------------------------------------
# 内置方法数据库（18 种核心方法）
# ---------------------------------------------------------------------------

BUILTIN_METHOD_DATABASE: Dict[str, Dict[str, Any]] = {
    # ── 理论方法 ──
    "TDDFT": {
        "name": "含时密度泛函理论",
        "name_en": "Time-Dependent Density Functional Theory",
        "category": "theoretical",
        "keywords": ["TDDFT", "含时密度泛函", "time-dependent density functional", "含时Kohn-Sham"],
        "related_methods": ["SBE", "密度泛函理论", "能带结构计算"],
        "expertise_level": "advanced",
        "estimated_learning_time": "4-6 周",
        "theoretical_background": (
            "含时密度泛函理论（TDDFT）是密度泛函理论（DFT）的时间推广，由 Runge 和 Gross 在 1984 年 "
            "建立[1]。其核心定理指出：对于任意含时外势，存在一一对应的含时电子密度映射，使得多体问题可以"
            "严格转化为单粒子问题。\n\n"
            "TDDFT 的基本方程是含时 Kohn-Sham 方程：\n"
            "$$i\\hbar\\frac{\\partial}{\\partial t}\\psi_k(\\mathbf{r},t) = "
            "\\hat{H}_{KS}(t)\\psi_k(\\mathbf{r},t)$$\n\n"
            "其中有效哈密顿量含外势、Hartree 势和交换关联势：\n"
            "$$\\hat{H}_{KS}(t) = -\\frac{\\hbar^2}{2m}\\nabla^2 + "
            "v_{ext}(\\mathbf{r},t) + v_H[n](\\mathbf{r},t) + v_{xc}[n](\\mathbf{r},t)$$\n\n"
            "在固体高次谐波产生（HHG）研究中，TDDFT 可直接模拟电子在强激光场下的非微扰动力学，"
            "捕获带间跃迁、带内加速以及复合辐射的完整过程[1]。相较于半经典模型，TDDFT 不依赖"
            "先验假设，能自然包含能带色散、多带耦合与拓扑效应。"
        ),
        "implementation_details": (
            "TDDFT 计算的关键参数选择：\n"
            "- **时间步长**：通常取 0.01-0.05 a.u.（原子单位），需满足 "
            "$\\Delta t \\ll T_{laser}/100$，以保证含时演化稳定。\n"
            "- **空间网格**：三维均匀网格间距 0.1-0.3 a.u.，过粗会丢失原子核附近"
            "的快速振荡，过细则计算量急剧上升。\n"
            "- **交换关联泛函**：常用 ALDA（绝热局域密度近似），计算效率高但缺乏记忆效应；"
            "对非线性响应需谨慎评估泛函选择的影响。\n"
            "- **k 点采样**：固体计算需充分采样布里渊区，典型使用 16x16x16 或更高密度 Monkhorst-Pack 网格。\n"
            "- **边界条件**：为避免边界反射，需引入吸收边界（如 mask function 或 CAP）。\n\n"
            "常用软件包：Octopus（实时 TDDFT）、YAMBO（线性响应 TDDFT）、"
            "TDAP（基于 ABINIT 的实时 TDDFT）。固体 HHG 模拟推荐 Octopus，"
            "支持周期性边界与规范不变实现。"
        ),
        "data_analysis": (
            "HHG 频谱提取流程：\n"
            "1. **收集含时偶极矩**：从 TDDFT 输出中提取宏观极化 P(t)，"
            "偶极矩 d(t) = P(t) * V_cell。\n"
            "2. **傅里叶变换**：对 d(t) 做快速傅里叶变换（FFT），"
            "获取谐波强度 |FFT[d(t)]|^2。\n"
            "3. **谐波阶次识别**：谐波阶次 q = omega_q / omega_0，"
            "其中 omega_0 为驱动光频率。\n"
            "4. **截止频率分析**：验证 q_cutoff 是否符合半经典三步模型预测 "
            "E_g / hbar + 3.17 Up。\n\n"
            "时间频率分析：使用 Gabor 变换或小波分析获取谐波发射的时间结构，"
            "区分带间与带内贡献。需注意窗函数选择对时间分辨的影响。\n\n"
            "收敛性检验：检查 k 点密度、网格间距、时间步长对谐波谱的影响，"
            "通常需在目标精度内（如 5%）确认参数收敛。"
        ),
        "limitations": (
            "主要局限：\n"
            "- **单粒子近似**：标准 TDDFT 采用独立 Kohn-Sham 粒子，"
            "无法描述强关联效应（如 Mott 绝缘体中的电子-电子散射）。\n"
            "- **交换关联泛函**：ALDA 等绝热泛函缺乏记忆效应，"
            "对超快动力学（< 1 fs）的描述可能不准确。\n"
            "- **计算成本**：三维固体的实时 TDDFT 计算量随体系增大急剧上升，"
            "典型超胞计算需数百至上千 CPU 核时。\n"
            "- **自相互作用误差**：常用 GGA/LDA 泛函存在自相互作用，"
            "导致能带带隙低估，影响带间跃迁阈值的准确性。\n"
            "- **退相干缺失**：标准 TDDFT 不含退相干机制，"
            "需人为引入退相干因子才能描述部分相干过程。"
        ),
    },
    "SBE": {
        "name": "半导体布洛赫方程",
        "name_en": "Semiconductor Bloch Equations",
        "category": "theoretical",
        "keywords": ["SBE", "semiconductor Bloch", "布洛赫方程", "半导体布洛赫", "光学布洛赫"],
        "related_methods": ["TDDFT", "Floquet理论", "密度泛函理论"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "2-3 周",
        "theoretical_background": (
            "半导体布洛赫方程（SBE）描述强场下固体中电子的相干动力学，"
            "是固体 HHG 理论分析的核心工具之一。其基础是密度矩阵形式下的"
            "光学布洛赫方程，将电子态用能带指标和 k 矢量标记。\n\n"
            "在两带近似下，SBE 的基本形式为：\n"
            "$$i\\hbar\\frac{\\partial}{\\partial t}\\rho_{cv}(\\mathbf{k},t) = "
            "\\epsilon_{cv}(\\mathbf{k},t)\\rho_{cv}(\\mathbf{k},t) - "
            "\\mathbf{E}(t)\\cdot\\mathbf{d}_{cv}(\\mathbf{k})[\\rho_{vv} - \\rho_{cc}]$$\n\n"
            "其中 $\\rho_{cv}$ 为带间相干（极化），$\\rho_{cc}$、$\\rho_{vv}$ 为布居数，"
            "$\\epsilon_{cv} = \\epsilon_c - \\epsilon_v$ 为带间能量差，"
            "$\\mathbf{d}_{cv}$ 为跃迁偶极矩。\n\n"
            "SBE 的优势在于物理图像清晰：带间极化对应 HHG 中的电子-空穴复合辐射，"
            "带内加速则通过 k 矢量的半经典运动方程 $\\hbar\\dot{\\mathbf{k}} = -e\\mathbf{E}(t)$ 描述。"
            "这使得 SBE 成为理解固体 HHG 机制的半经典三步模型的微观基础。"
        ),
        "implementation_details": (
            "SBE 数值求解的关键考量：\n"
            "- **能带输入**：需从 DFT 或紧束缚模型获取能带结构 $\\epsilon_{n}(\\mathbf{k})$ "
            "和跃迁偶极矩 $\\mathbf{d}_{nm}(\\mathbf{k})$，通常在布里渊区均匀采样。\n"
            "- **k 点采样**：1D 模型典型 1000-5000 个 k 点；"
            "3D 完整计算需 50^3 量级，计算量可观。\n"
            "- **时间步进**：采用四阶 Runge-Kutta 或分裂算符法，"
            "时间步长需满足 $\\Delta t < 0.1 T_{laser}$。\n"
            "- **退相干项**：引入唯象退相干时间 T2（带间）和 T1（带内），"
            "典型 T2 ~ 10-50 fs，T1 ~ 100-500 fs。\n"
            "- **规范选择**：长度规范（E·r）或速度规范（A·p），"
            "需确保跃迁偶极矩的规范一致性。\n\n"
            "多带扩展：两带近似适用于宽带隙绝缘体；"
            "对拓扑材料或简并体系需扩展至多带 SBE，计算复杂度显著增加。"
        ),
        "data_analysis": (
            "从 SBE 提取 HHG 谱：\n"
            "1. **宏观极化计算**：$P(t) = \\sum_{\\mathbf{k}} \\mathbf{d}_{cv}(\\mathbf{k})"
            "\\rho_{cv}(\\mathbf{k},t) + c.c.$，对所有 k 点求和。\n"
            "2. **频谱变换**：FFT[P(t)] 得到谐波谱。\n"
            "3. **机制分解**：将极化拆分为带间和带内分量，"
            "分析各阶谐波的来源。\n"
            "4. **k 空间分析**：追踪电子在 k 空间的轨迹，"
            "识别带间跃迁和带内加速事件。\n\n"
            "对称性分析：利用晶体对称性分析谐波偏振与晶体取向的关系，"
            "可提取 Berry 曲率等几何量的贡献。\n\n"
            "与 TDDFT 对比：SBE 结果可与 TDDFT 交叉验证，"
            "差异通常源于 SBE 中省略的多体效应和带间耦合细节。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **能带输入依赖**：SBE 结果高度依赖输入能带和偶极矩的质量，"
            "DFT 带隙低估会直接影响 HHG 截止频率预测。\n"
            "- **退相干唯象处理**：T1、T2 为可调参数，缺乏第一性原理依据，"
            "不同体系取值差异大。\n"
            "- **带数截断**：两带近似忽略远带贡献，"
            "对宽带激光或多光子过程可能不适用。\n"
            "- **偶极矩规范**：长度规范与速度规范的偶极矩不同，"
            "混用会导致非物理结果。\n"
            "- **电场强度上限**：极强场下布居数可能溢出 [0,1] 区间，"
            "需注意数值稳定性。\n"
            "- **无电子-电子散射**：标准 SBE 不含碰撞项，"
            "无法描述载流子热化和散射退相干。"
        ),
    },
    "Floquet理论": {
        "name": "Floquet 理论",
        "name_en": "Floquet Theory",
        "category": "theoretical",
        "keywords": ["Floquet", "弗洛凯", "quasi-energy", "准能量", "Floquet态"],
        "related_methods": ["SBE", "TDDFT", "能带结构计算"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "2-3 周",
        "theoretical_background": (
            "Floquet 理论是处理周期性含时哈密顿量的标准框架，类比 Bloch 定理在空间周期势中的应用。"
            "对于周期为 T = 2π/ω 的含时哈密顿量 H(t) = H(t+T)，Floquet 定理保证其解可写为：\n\n"
            "$$\\psi_\\alpha(\\mathbf{r},t) = e^{-i\\epsilon_\\alpha t/\\hbar} "
            "\\phi_\\alpha(\\mathbf{r},t)$$\n\n"
            "其中 $\\epsilon_\\alpha$ 为 Floquet 准能量（quasi-energy），"
            "$\\phi_\\alpha(\\mathbf{r},t) = \\phi_\\alpha(\\mathbf{r},t+T)$ 为周期函数。"
            "准能量定义在 Floquet Brillouin 区 $[-\\hbar\\omega/2, \\hbar\\omega/2)$ 内。\n\n"
            "在强场物理中，Floquet 理论提供了\u201c光子缀饰态\u201d（photon-dressed states）的图像："
            "驱动激光场将静态能带\u201c折叠\u201d为以 ℏω 为周期的 Floquet 能带。"
            "这种图像揭示了光诱导的带隙闭合、拓扑变化以及动态局域化等非平衡现象。\n\n"
            "Floquet 理论与 SBE 的关系：稳态 Floquet 态对应 SBE 的长时间极限解，"
            "准能量差即为缀饰带间的跃迁频率。"
        ),
        "implementation_details": (
            "Floquet 计算的实现路径：\n"
            "- **Floquet 矩阵构造**：将哈密顿量在 Floquet 基 $|n,\\alpha\\rangle$ "
            "（n 为光子副本指标，α 为静态能带指标）下展开，"
            "构造无穷维矩阵 H_F，其对角元为 $\\epsilon_\\alpha + n\\hbar\\omega$，"
            "非对角元为 V_±（光耦合矩阵元）。\n"
            "- **截断**：光子副本数 N_max 通常取 5-20，"
            "需检查准能量收敛性。\n"
            "- **对角化**：对截断后的 Floquet 矩阵对角化，"
            "得到准能量谱和 Floquet 态。\n"
            "- **电场参数化**：线偏振场 H_int = -eE_0 cos(ωt) x，"
            "圆偏振场需含两个分量。\n\n"
            "Sambe 空间-时间基：将 Floquet 态在空间和时间基上联合展开，"
            "可直接处理含时波函数。该方法精度高但矩阵维度大。\n\n"
            "常用工具：自研代码为主，部分 DFT 软件包（如 Wannier90 + 后处理）"
            "可构建 Floquet 哈密顿量。"
        ),
        "data_analysis": (
            "Floquet 准能量分析：\n"
            "1. **准能带绘制**：以 k 为横轴绘制准能量 $\\epsilon_\\alpha(\\mathbf{k})$，"
            "观察带隙闭合与 reopen 现象。\n"
            "2. **拓扑分析**：计算 Floquet 能带的 Chern 数，"
            "检测光诱导拓扑相变。\n"
            "3. **态密度**：Floquet 态密度 $D_F(\\epsilon) = "
            "\\sum_{\\alpha,\\mathbf{k}} \\delta(\\epsilon - \\epsilon_\\alpha(\\mathbf{k}))$，"
            "与实验 ARPES 对比。\n"
            "4. **吸收谱**：从 Floquet 极化率提取非线性吸收谱。\n\n"
            "收敛性检验：检查 N_max 对准能量的影响，"
            "通常准能量收敛速度 ~1/N_max^2。\n\n"
            "与实验对比：注意 Floquet 理论描述稳态（无限长脉冲），"
            "实际实验为有限脉冲，需引入瞬态 Floquet 分析。"
        ),
        "limitations": (
            "局限与注意事项：\n"
            "- **稳态假设**：标准 Floquet 理论假设无限长周期驱动，"
            "不适用于超短脉冲（< 10 周期）。\n"
            "- **退相干缺失**：不含耗散和退相干，"
            "预测的\u201c拓扑相变\u201d在实际体系中可能被退相干抹平。\n"
            "- **矩阵维度**：多带 + 多光子副本的 Floquet 矩阵维度"
            "可达数千，对角化成本高。\n"
            "- **共振发散**：在共振条件（$\\epsilon_c - \\epsilon_v \\approx n\\hbar\\omega$）"
            "附近，光子副本间强耦合可能导致数值困难。\n"
            "- **规范依赖**：长度规范与速度规范下的 Floquet 态不同，"
            "需确保一致使用。\n"
            "- **物理诠释**：Floquet 态为数学构造，"
            "其\u201c实在性\u201d在物理社区仍有争议。"
        ),
    },
    "Berry曲率计算": {
        "name": "贝里曲率计算",
        "name_en": "Berry Curvature Calculation",
        "category": "theoretical",
        "keywords": ["Berry曲率", "Berry curvature", "几何相位", "贝里曲率", "Berry phase"],
        "related_methods": ["量子度规计算", "拓扑不变量计算", "能带结构计算"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "1-2 周",
        "theoretical_background": (
            "Berry 曲率是量子几何张量的虚部，描述布洛赫态在参数空间中的\u201c几何相位曲率\u201d。"
            "对于能带 n，Berry 曲率定义为：\n\n"
            "$$\\Omega_n(\\mathbf{k}) = "
            "i\\left\\langle\\frac{\\partial u_{n\\mathbf{k}}}{\\partial k_x}\\right|"
            "\\frac{\\partial u_{n\\mathbf{k}}}{\\partial k_y}\\right\\rangle - (x \\leftrightarrow y)$$\n\n"
            "在紧束缚或 k·p 框架下，可表示为能带间求和：\n"
            "$$\\Omega_n(\\mathbf{k}) = -2\\text{Im}\\sum_{m\\neq n} "
            "\\frac{\\langle u_n|v_x|u_m\\rangle\\langle u_m|v_y|u_n\\rangle}"
            "{(\\epsilon_m - \\epsilon_n)^2}$$\n\n"
            "Berry 曲率是反常霍尔效应、轨道磁化和非线性光学响应的几何根源。"
            "在固体 HHG 中，Berry 曲率通过不对称载流子注入影响谐波偏振和效率，"
            "是连接量子几何与超快非线性光学的桥梁。"
        ),
        "implementation_details": (
            "Berry 曲率数值计算方法：\n"
            "- **波函数法**：从 DFT 获取布洛赫态 $|u_{n\\mathbf{k}}\\rangle$，"
            "用有限差分计算 k 空间导数。需充分采样 k 空间并在简并点附近特殊处理。\n"
            "- **能带求和法**：利用速度矩阵元公式直接求和，"
            "避免了波函数差分但需要完整能带和偶极矩阵元。\n"
            "- **Wannier 插值**：通过 Wannier90 获取紧束缚模型，"
            "在密集 k 网格上高效计算 Berry 曲率。推荐方法。\n"
            "- **k 空间网格**：典型 100x100 或更密，"
            "在简并点附近需自适应加密。\n"
            "- **规范处理**：Berry 曲率为规范不变量，"
            "但中间计算需固定规范。\n\n"
            "常用工具链：VASP/Quantum ESPRESSO → Wannier90 → "
            "自研后处理脚本（或 WannierBerri、WannierTools）。"
        ),
        "data_analysis": (
            "Berry 曲率的物理量提取：\n"
            "1. **Chern 数**：$C_n = \\frac{1}{2\\pi}\\int_{BZ} \\Omega_n(\\mathbf{k}) d^2k$，"
            "整数拓扑不变量。\n"
            "2. **反常霍尔电导**：$\\sigma_{xy} = "
            "-\\frac{e^2}{\\hbar}\\sum_n \\int \\frac{d^3k}{(2\\pi)^3} f_n \\Omega_n^z$。\n"
            "3. **轨道磁矩**：$m_n(\\mathbf{k}) = "
            "-\\frac{e}{2\\hbar}\\text{Im}\\langle\\nabla_{\\mathbf{k}}u_n|\\times"
            "(H(\\mathbf{k})-\\epsilon_n)|\\nabla_{\\mathbf{k}}u_n\\rangle$。\n"
            "4. **非线性光学响应**：从 Berry 曲率分布"
            "提取圆偏振光电流注入效率。\n\n"
            "可视化：k 空间 Berry 曲率分布图可揭示"
            "热点（hotspots）和奇点结构，"
            "对理解拓扑材料的反常响应至关重要。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **简并点困难**：在能带简并点（如 Dirac 点），"
            "分母 $(\\epsilon_m - \\epsilon_n)^2$ 发散，"
            "需使用非阿贝尔 Berry 曲率公式。\n"
            "- **规范依赖的中间量**：速度矩阵元"
            "$\\langle u_n|v_\\mu|u_m\\rangle$ 依赖波函数规范，"
            "需在计算中统一规范。\n"
            "- **k 空间分辨率**：粗糙网格会漏掉 Berry 曲率热点，"
            "导致积分结果偏差大。\n"
            "- **带数截断**：求和公式需包含所有能带，"
            "实践中常截断至导数带，"
            "可能引入系统误差。\n"
            "- **三维复杂性**：3D 体系 Berry 曲率为矢量"
            "$\\boldsymbol{\\Omega}_n$，"
            "分析比 2D 标量情形复杂。"
        ),
    },
    "量子度规计算": {
        "name": "量子度规计算",
        "name_en": "Quantum Metric Calculation",
        "category": "theoretical",
        "keywords": ["量子度规", "quantum metric", "Fubini-Study", "量子几何张量"],
        "related_methods": ["Berry曲率计算", "拓扑不变量计算", "能带结构计算"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "1-2 周",
        "theoretical_background": (
            "量子度规是量子几何张量的实部，衡量布洛赫态在 k 空间中的\u201c距离\u201d。"
            "量子几何张量定义为：\n\n"
            "$$Q^{\\mu\\nu}_n(\\mathbf{k}) = "
            "\\langle\\partial_\\mu u_{n\\mathbf{k}}|(1-|u_{n\\mathbf{k}}\\rangle"
            "\\langle u_{n\\mathbf{k}}|)|\\partial_\\nu u_{n\\mathbf{k}}\\rangle$$\n\n"
            "其实部为量子度规 $g^{\\mu\\nu}_n = \\text{Re}[Q^{\\mu\\nu}_n]$，"
            "虚部为 Berry 曲率 $\\Omega_n^{\\mu\\nu} = -2\\text{Im}[Q^{\\mu\\nu}_n]$。\n\n"
            "量子度规满足不等式 $\\det(g_n) \\geq \\Omega_n^2/4$，"
            "等号在量子自旋霍尔绝缘体等\u201c理想\u201d体系中成立。"
            "近年来研究表明，量子度规直接决定固体 HHG 的效率下限：\n"
            "$$I_{HHG} \\propto \\text{Tr}(g_n)$$\n\n"
            "这使得量子度规从纯几何量跃升为可观测的物理量，"
            "为通过 HHG 实验探测量子几何提供了理论依据。"
        ),
        "implementation_details": (
            "量子度规计算流程：\n"
            "- **波函数差分法**：从 DFT 获取相邻 k 点的布洛赫态，"
            "用重叠矩阵 $S_{\\mu} = \\langle u_{n,\\mathbf{k}}|u_{n,\\mathbf{k}+\\delta k_\\mu}\\rangle$ "
            "构造度规：\n"
            "$$g^{\\mu\\mu}_n \\approx \\frac{1}{\\delta k_\\mu^2}"
            "\\text{Re}[1 - S_\\mu]$$\n"
            "- **Wannier 插值**：在紧束缚模型上精确计算，"
            "推荐使用 WannierBerri 的 `quantum_metric` 模块。\n"
            "- **k 网格密度**：量子度规对 k 网格比 Berry 曲率更敏感，"
            "因不含发散分母但需精确差分，典型 200x200。\n"
            "- **简并处理**：简并能带需用非阿贝尔推广，"
            "度规矩阵在简并子空间内对角化。\n\n"
            "不等式检验：计算后检查 $\\det(g) \\geq \\Omega^2/4$，"
            "违反则提示 k 网格不足或规范问题。"
        ),
        "data_analysis": (
            "量子度规的物理分析：\n"
            "1. **积分量**：$\\text{Tr}(g)$ 的 BZ 积分"
            "与 HHG 效率相关，可用于材料筛选。\n"
            "2. **分布图**：k 空间量子度规分布揭示"
            "几何\u201c热点\u201d，与 Berry 曲率分布互补。\n"
            "3. **不等式饱和度**：$\\det(g)/\\Omega^2$ 比值"
            "反映体系偏离\u201c理想\u201d几何的程度。\n"
            "4. **与实验对比**：将度规积分量与 HHG 产额"
            "实验数据拟合，提取几何贡献。\n\n"
            "材料筛选：对候选材料（拓扑绝缘体、Weyl 半金属等）"
            "系统计算量子度规，筛选 HHG 增强候选体系。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **差分精度**：波函数差分法对 k 步长敏感，"
            "过大引入误差，过小受数值噪声主导，"
            "需系统扫描确定最优步长。\n"
            "- **规范依赖**：度规本身规范不变，"
            "但差分公式依赖重叠矩阵的规范选择。\n"
            "- **带简并**：简并能带的度规需非阿贝尔推广，"
            "标准公式不适用。\n"
            "- **物理诠释模糊**：与 Berry 曲率"
            "（直接联系反常霍尔效应）不同，"
            "量子度规的物理效应更隐蔽，"
            "主要通过不等式约束体现。\n"
            "- **实验间接性**：量子度规无直接可观测量，"
            "需通过 HHG 或非线性光学间接提取。"
        ),
    },
    "Kubo公式": {
        "name": "久保公式",
        "name_en": "Kubo Formula",
        "category": "theoretical",
        "keywords": ["Kubo", "久保", "线性响应", "Kubo公式", "Kubo-Greenwood"],
        "related_methods": ["Berry曲率计算", "能带结构计算", "傅里叶分析"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "1-2 周",
        "theoretical_background": (
            "Kubo 公式是线性响应理论的核心结果，描述系统对外部微扰的响应函数。"
            "对于电场微扰，光电导的 Kubo 公式为：\n\n"
            "$$\\sigma_{\\mu\\nu}(\\omega) = \\frac{ie^2}{\\omega}\\sum_{\\mathbf{k}}"
            "\\sum_{n,m}\\frac{f_{n\\mathbf{k}}-f_{m\\mathbf{k}}}"
            "{(\\epsilon_{m\\mathbf{k}}-\\epsilon_{n\\mathbf{k}}+\\hbar\\omega+i\\eta)}"
            "\\langle u_n|v_\\mu|u_m\\rangle\\langle u_m|v_\\nu|u_n\\rangle$$\n\n"
            "其中 $f_{n\\mathbf{k}}$ 为费米分布，$\\eta$ 为展宽参数。"
            "Kubo 公式将宏观响应（电导/吸收）与微观量（能带、速度矩阵元）"
            "直接联系，是计算光学性质的标准工具。\n\n"
            "非线性推广：Kubo 公式可推广至高阶响应（二阶、三阶），"
            "描述非线性光学过程如二次谐波产生（SHG）和 HHG。"
            "二阶 Kubo 公式含三能带求和与两个频率分母，"
            "计算复杂度显著增加。"
        ),
        "implementation_details": (
            "Kubo 公式数值实现要点：\n"
            "- **能带与矩阵元**：从 DFT/Wannier 获取 $\\epsilon_{n\\mathbf{k}}$ 和 "
            "$\\langle u_n|v_\\mu|u_m\\rangle$。\n"
            "- **k 点采样**：金属体系需密集 k 网格（100x100+），"
            "绝缘体可适当降低。\n"
            "- **展宽参数**：$\\eta$ 典型 0.01-0.1 eV，"
            "模拟有限温度和退相干效应。过小导致数值振荡，过大模糊特征。\n"
            "- **频率网格**：$\\omega$ 网格需覆盖目标频率范围，"
            "注意共振点附近的加密采样。\n"
            "- **带数截断**：导带数需足够以覆盖高频响应，"
            "典型 10-50 条导带。\n\n"
            "Kubo-Greenwood 变体：用于有限温度电导率计算，"
            "含温度依赖的费米分布。常用工具：WannierBerri、BoltzTraP、自研脚本。"
        ),
        "data_analysis": (
            "Kubo 公式输出分析：\n"
            "1. **光学电导谱**：$\\sigma(\\omega)$ 的实部对应吸收，"
            "虚部对应色散，满足 Kramers-Kronig 关系。\n"
            "2. **介电函数**：$\\epsilon(\\omega) = 1 + 4\\pi i\\sigma(\\omega)/\\omega$，"
            "与椭圆偏振实验对比。\n"
            "3. **带间/带内分解**：将电导拆分为带间（相干）"
            "和带内（Drude）分量。\n"
            "4. **求和规则检验**：验证 $\\int_0^\\infty \\text{Re}[\\sigma(\\omega)]d\\omega$ "
            "是否满足 f-求和规则，作为收敛性检验。\n\n"
            "非线性响应：二阶 Kubo 公式输出 $\\chi^{(2)}(\\omega)$，"
            "可直接与 SHG 实验对比。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **线性响应限制**：标准 Kubo 公式仅适用于弱场（线性）区域，"
            "强场需用非线性推广或非微扰方法（TDDFT/SBE）。\n"
            "- **退相干参数化**：$\\eta$ 为唯象参数，"
            "缺乏第一性原理依据。\n"
            "- **带隙低估**：DFT 带隙低估导致吸收边红移，"
            "需 scissor 修正或 GW 修正。\n"
            "- **k 点收敛慢**：金属体系费米面附近 k 收敛慢，"
            "可能需要 500x500 网格。\n"
            "- **带数收敛**：高频响应需大量导带，"
            "截断过早导致高频区误差。\n"
            "- **无场效应**：标准 Kubo 公式描述零场响应，"
            "强场修正需额外处理。"
        ),
    },
    "非线性光学理论": {
        "name": "非线性光学理论",
        "name_en": "Nonlinear Optics Theory",
        "category": "theoretical",
        "keywords": ["非线性光学", "nonlinear optics", "高阶极化", "非线性极化率", "chi(2)", "chi(3)"],
        "related_methods": ["Kubo公式", "TDDFT", "Floquet理论"],
        "expertise_level": "beginner",
        "estimated_learning_time": "1-2 周",
        "theoretical_background": (
            "非线性光学研究介质在强光场下极化对电场的非线性依赖。"
            "介质极化展开为：\n\n"
            "$$\\mathbf{P}(t) = \\chi^{(1)}\\mathbf{E}(t) + "
            "\\chi^{(2)}\\mathbf{E}^2(t) + \\chi^{(3)}\\mathbf{E}^3(t) + \\cdots$$\n\n"
            "其中 $\\chi^{(n)}$ 为 n 阶非线性极化率张量。"
            "在各向同性介质中，$\\chi^{(2)}$ 由反演对称性禁戒为零，"
            "最低非线性为 $\\chi^{(3)}$。\n\n"
            "固体 HHG 是极端非线性光学过程：在强场（~V/Å）下，"
            "微扰展开失效，需用非微扰理论描述。"
            "但弱场极限下，HHG 可与 $\\chi^{(n)}$ 的微扰值"
            "建立定量联系，为理解非线性来源提供桥梁。\n\n"
            "相位匹配条件：$\\Delta k = k_q - qk_0 = 0$，"
            "其中 $k_q$ 为 q 次谐波波矢，$k_0$ 为基频波矢。"
            "相位匹配决定谐波在介质中的相干增长效率。"
        ),
        "implementation_details": (
            "非线性光学分析的关键参数：\n"
            "- **极化率张量**：从 DFT/Kubo 公式计算 $\\chi^{(2)}_{\\mu\\nu\\lambda}$ 或 "
            "$\\chi^{(3)}_{\\mu\\nu\\lambda\\sigma}$，注意晶体对称性约化。\n"
            "- **相位匹配**：计算色散关系 $n(\\omega)$，"
            "确定相位匹配波长和角度。\n"
            "- **吸收长度**：$L_{abs} = 1/\\alpha(\\omega_q)$，"
            "谐波在介质中的吸收衰减。\n"
            "- **相干长度**：$L_c = \\pi/|\\Delta k|$，"
            "相位失配下的有效增长长度。\n"
            "- **损伤阈值**：介质可承受的最大光强，"
            "限制可用驱动强度。\n\n"
            "固体 HHG 相位匹配：与气体不同，固体色散强，"
            "相位匹配条件复杂。需考虑介电函数的频率依赖"
            "和各向异性，有时需利用结构双折射实现相位匹配。"
        ),
        "data_analysis": (
            "非线性光学测量分析：\n"
            "1. **谐波强度标度**：验证 $I_q \\propto I_0^q$（微扰区）"
            "或偏离幂律（非微扰区），区分机制。\n"
            "2. **偏振依赖**：旋转晶体取向或入射偏振，"
            "分析谐波偏振与对称性的关系。\n"
            "3. **相位匹配曲线**：改变介质厚度或相位匹配条件，"
            "拟合相干长度和吸收长度。\n"
            "4. **截止阶次分析**：与三步模型预测对比，"
            "提取有效带隙或电离势。\n\n"
            "非线性极化率提取：在弱场区，从谐波强度反推"
            "$|\\chi^{(n)}|^2$，需校准绝对强度。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **微扰展开失效**：强场下微扰级数不收敛，"
            "$\\chi^{(n)}$ 物理意义丧失，需非微扰方法。\n"
            "- **相位匹配复杂**：固体的强色散和各向异性"
            "使相位匹配分析远比气体复杂。\n"
            "- **多光子共振**：共振条件下的非线性增强"
            "可能伴随强烈吸收，需权衡。\n"
            "- **热效应**：高重复频率激光引起热透镜和热致双折射，"
            "影响测量稳定性。\n"
            "- **表面/界面贡献**：表面与体相的非线性响应不同，"
            "薄膜测量需区分贡献。\n"
            "- **时间分辨**：稳态测量无法区分瞬时和延迟响应，"
            "需泵浦-探测技术。"
        ),
    },

    # ── 计算方法 ──
    "HHG模拟": {
        "name": "高次谐波模拟",
        "name_en": "HHG Simulation",
        "category": "computational",
        "keywords": ["HHG模拟", "HHG simulation", "高次谐波模拟", "谐波计算", "harmonic generation"],
        "related_methods": ["TDDFT", "SBE", "Floquet理论"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "3-4 周",
        "theoretical_background": (
            "固体高次谐波模拟旨在数值重现或预测 HHG 谱，"
            "核心物理过程包括：\n"
            "1. 强场下电子从价带激发至导带（隧穿/多光子）；\n"
            "2. 电子在导带中被激光场加速（带内运动）；\n"
            "3. 电子与空穴复合，辐射高能光子（带间复合）。\n\n"
            "半经典三步模型的固体推广：\n"
            "- 步骤一：Zener 隧穿产生电子-空穴对，"
            "隧穿率 $W \\propto \\exp(-\\pi E_g^2/4e\\hbar v E_0)$；\n"
            "- 步骤二：电子在导带以 $\\hbar\\dot{k} = -eE(t)$ 运动，"
            "获得动能 $E_{kin}$；\n"
            "- 步骤三：复合时辐射 $\\hbar\\omega = E_g + E_{kin}$，"
            "截止频率 $\\hbar\\omega_{cutoff} \\approx E_g + 3.17 U_p$。\n\n"
            "固体与气体的关键差异：能带色散替代自由电子色散，"
            "带间复合替代连续态复合，"
            "使得固体 HHG 截止频率依赖带隙和能带曲率。"
        ),
        "implementation_details": (
            "HHG 模拟的实现层次（由简到繁）：\n"
            "- **半经典模型**：解析三步模型 + 能带色散，"
              "最快但忽略相干效应，适合参数扫描。\n"
            "- **SBE 模拟**：数值求解 SBE，"
              "含相干极化和布居动力学，平衡精度与效率。推荐入门。\n"
            "- **TDDFT 模拟**：第一性原理含时演化，"
              "最精确但计算量最大，适合基准验证。\n"
            "- **粒子模拟（PIC）**：经典轨迹 + 隧穿概率，"
              "适合大尺度或超快过程。\n\n"
            "通用参数设置：\n"
            "- 驱动波长：中红外（2-5 μm）最常用于固体 HHG，"
              "降低光子能量以避免样品损伤。\n"
            "- 光强：10^11 - 10^13 W/cm^2，"
              "低于损伤阈值。\n"
            "- 脉冲宽度：5-30 fs（少周期）或 50-100 fs（多周期）。\n"
            "- 时间窗口：需覆盖完整脉冲 + 余振荡衰减。"
        ),
        "data_analysis": (
            "HHG 模拟数据分析：\n"
            "1. **谐波谱提取**：FFT[偶极矩(t)] → |谱|^2，"
            "对数坐标展示。\n"
            "2. **截止频率验证**：对比 $\\omega_{cutoff}$ 与三步模型预测，"
            "提取有效带隙。\n"
            "3. **机制分解**：将极化拆分为带间/带内分量，"
            "分析各阶谐波来源。\n"
            "4. **椭圆率依赖**：改变驱动场椭圆率，"
            "分析再碰撞效率。\n"
            "5. **时间频率图**：Gabor 变换获取谐波发射时间，"
            "识别半周期发射峰。\n\n"
            "收敛性检验：k 点密度、时间步长、脉冲长度"
            "对谐波谱的影响，确保数值收敛。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **模型选择**：半经典模型忽略相干效应，"
            "TDDFT 计算昂贵，需根据目标选择合适层次。\n"
            "- **传播效应**：大多数模拟为单点（无传播），"
            "忽略相位匹配和吸收，需后处理修正。\n"
            "- **损伤未含**：模拟不含光损伤，"
            "高光强下实际样品可能已损伤。\n"
            "- **退相干参数化**：SBE 中 T1、T2 为可调参数，"
            "影响定量比较。\n"
            "- **温度效应**：多数模拟为零温，"
            "有限温度下声子散射和带隙变化未含。\n"
            "- **尺度限制**：TDDFT 限于数百原子，"
            "大尺度缺陷/界面需多尺度方法。"
        ),
    },
    "能带结构计算": {
        "name": "能带结构计算",
        "name_en": "Band Structure Calculation",
        "category": "computational",
        "keywords": ["能带结构", "band structure", "能带计算", "DFT能带", "电子结构"],
        "related_methods": ["TDDFT", "Berry曲率计算", "量子度规计算"],
        "expertise_level": "beginner",
        "estimated_learning_time": "1-2 周",
        "theoretical_background": (
            "能带结构计算是凝聚态物理计算的基础，描述电子能量"
            "在布里渊区中的色散关系 $\\epsilon_n(\\mathbf{k})$。"
            "主要基于密度泛函理论（DFT）求解 Kohn-Sham 方程：\n\n"
            "$$\\left[-\\frac{\\hbar^2}{2m}\\nabla^2 + V_{ion}(\\mathbf{r}) + "
            "V_H[n](\\mathbf{r}) + V_{xc}[n](\\mathbf{r})\\right]"
            "\\psi_{n\\mathbf{k}}(\\mathbf{r}) = "
            "\\epsilon_{n\\mathbf{k}}\\psi_{n\\mathbf{k}}(\\mathbf{r})$$\n\n"
            "DFT 将多体问题映射为等效单粒子问题，"
            "通过自洽迭代求解电子密度和能量。"
            "Kohn-Sham 本征值 $\\epsilon_{n\\mathbf{k}}$ 即为能带。\n\n"
            "在强场超快光学中，能带结构是所有后续计算（SBE、TDDFT、Berry 曲率等）"
            "的输入基础。能带带隙、有效质量、带间偶极矩等参数"
            "直接决定 HHG 截止频率、谐波效率和非线性响应。"
        ),
        "implementation_details": (
            "能带计算的标准流程：\n"
            "- **结构优化**：先对晶体结构做几何优化（原子位置+晶格常数），"
            "收敛力至 < 0.01 eV/Å。\n"
            "- **自洽计算（SCF）**：在密集 k 网格上自洽求解电荷密度，"
            "典型 Monkhorst-Pack 12x12x12。\n"
            "- **能带计算**：沿高对称路径（如 Γ-X-M-Γ）"
            "计算本征值，需非自洽计算或后处理插值。\n"
            "- **泛函选择**：PBE/GGA 为标准选择；"
            "带隙需 HSE06 杂化泛函或 GW 修正。\n"
            "- **投影分析**：将波函数投影到原子轨道，"
            "分析能带成分（s/p/d 贡献）。\n\n"
            "常用软件：VASP（商业）、Quantum ESPRESSO（开源）、"
            "ABINIT（开源）、CASTEP（商业）。"
            "后处理：Wannier90 用于紧束缚插值和拓扑分析。"
        ),
        "data_analysis": (
            "能带结构分析要点：\n"
            "1. **带隙确定**：识别 VBM 和 CBM 的 k 位置，"
            "判断直接/间接带隙。\n"
            "2. **有效质量**：在能带极值附近拟合曲率 "
            "$m^* = \\hbar^2/(\\partial^2\\epsilon/\\partial k^2)$，"
            "影响载流子动力学。\n"
            "3. **态密度（DOS）**：计算总 DOS 和投影 DOS（PDOS），"
            "分析元素贡献。\n"
            "4. **费米面**：金属体系绘制费米面，"
            "分析嵌套矢量和拓扑。\n"
            "5. **带隙修正**：对比 PBE 与 HSE06/GW 结果，"
            "确定 scissor 修正值。\n\n"
            "与其他计算衔接：将能带和波函数输出"
            "传递给 Wannier90（拓扑量）、SBE（HHG）或 TDDFT（含时模拟）。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **带隙低估**：标准 DFT（PBE/GGA）带隙低估 30-50%，"
            "需 HSE06 或 GW 修正。\n"
            "- **自相互作用**：LDA/GGA 的自相互作用误差"
            "导致 d/f 电子局域化不足。\n"
            "- **范德华力缺失**：标准 DFT 不含色散力，"
            "层状材料需 DFT-D 或 R-vdW 修正。\n"
            "- **强关联失效**：Mott 绝缘体、高温超导体等"
            "强关联体系需 DFT+U 或 DMFT。\n"
            "- **k 点收敛**：金属体系 k 收敛慢，"
            "需测试网格密度。\n"
            "- **赝势质量**：不同赝势（PAW/USPP/NC）"
            "结果可能有差异，需一致使用。"
        ),
    },
    "拓扑不变量计算": {
        "name": "拓扑不变量计算",
        "name_en": "Topological Invariant Computation",
        "category": "computational",
        "keywords": ["拓扑不变量", "topological invariant", "Chern数", "Z2不变量", "winding number"],
        "related_methods": ["Berry曲率计算", "量子度规计算", "能带结构计算"],
        "expertise_level": "advanced",
        "estimated_learning_time": "2-3 周",
        "theoretical_background": (
            "拓扑不变量是分类拓扑物相的核心量，"
            "包括 Chern 数、Z2 不变量、缠绕数等。\n\n"
            "**Chern 数**（2D）：\n"
            "$$C = \\frac{1}{2\\pi}\\int_{BZ} \\Omega(\\mathbf{k}) d^2k$$\n"
            "整数 Chern 数标记量子反常霍尔绝缘体。"
            "C=1 对应陈绝缘体，承载手性边缘态。\n\n"
            "**Z2 不变量**（2D 时间反演对称）：\n"
            "$$\\nu = \\frac{1}{2\\pi}\\left[\\oint_{\\partial BZ} \\mathbf{A}\\cdot d\\mathbf{k} "
            "- \\int_{BZ} \\mathbf{F} d^2k\\right] \\mod 2$$\n"
            "二值不变量（0/1）标记量子自旋霍尔绝缘体。\n\n"
            "**Wilson loop 方法**：通过 Wilson loop 计算"
            "Wannier 电荷中心演化，直接提取 Z2 不变量，"
            "避免了规范问题，是数值计算的首选方法。"
        ),
        "implementation_details": (
            "拓扑不变量计算方法：\n"
            "- **Berry 曲率积分法**：先计算 Berry 曲率，"
            "再在 BZ 积分得 Chern 数。需极密 k 网格（500x500+）。\n"
            "- **Wilson loop 法**：计算 Wannier 电荷中心"
            "沿 k_x 的演化 $\\theta(k_x)$，Z2 = [n_crossings] mod 2。"
            "推荐方法，规范无关。\n"
            "- **对称性指标法**：利用空间群对称性"
            "从能带不可约表示直接判定拓扑，"
            "无需 Berry 曲率计算（如 Topological Quantum Chemistry）。\n"
            "- **Wannier 插值**：通过 Wannier90 获取紧束缚模型，"
            "在任意密度的 k 网格上高效计算。\n\n"
            "常用工具：WannierTools、Z2Pack、WannierBerri、"
            "TopoTools、IRVSP。"
        ),
        "data_analysis": (
            "拓扑分析输出：\n"
            "1. **Chern 数**：整数结果，验证波函数收敛性。\n"
            "2. **Wilson loop 图**：Wannier 中心演化曲线，"
            "交叉次数判定 Z2。\n"
            "3. **边缘态**：从体态拓扑预测边缘态色散，"
            "可与 STM/ARPES 对比。\n"
            "4. **相图**：扫描参数（如应变、电场），"
            "绘制拓扑相变相图。\n"
            "5. **对称性指标**：列出高对称点"
            "的能带不可约表示，对照拓扑材料数据库。\n\n"
            "数据库交叉验证：与 Topological Materials Database "
            "（topologicalquantumchemistry.org）对比结果。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **k 网格密度**：Berry 曲率积分法"
            "对 k 网格极度敏感，不收敛结果完全错误。\n"
            "- **简并处理**：能带简并点处 Berry 曲率发散，"
            "需非阿贝尔推广或回避简并区。\n"
            "- **规范问题**：Berry 曲率法依赖波函数规范，"
            "Wilson loop 法更鲁棒。\n"
            "- **相互作用效应**：DFT 拓扑分类"
            "可能因电子-电子相互作用改变，"
            "需 DMFT 等方法验证。\n"
            "- **3D 复杂性**：3D Z2 需在 6 个时间反演不变面"
            "上分别计算，流程复杂。\n"
            "- **无序效应**：理想晶体拓扑"
            "在无序下可能改变（拓扑安德森绝缘体）。"
        ),
    },

    # ── 实验方法 ──
    "HHG光谱": {
        "name": "高次谐波光谱",
        "name_en": "HHG Spectroscopy",
        "category": "experimental",
        "keywords": ["HHG光谱", "HHG spectroscopy", "高次谐波光谱", "谐波光谱", "固体HHG实验"],
        "related_methods": ["HHG模拟", "偏振测量", "时间分辨泵浦-探测"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "3-4 周",
        "theoretical_background": (
            "高次谐波光谱（HHG Spectroscopy）通过测量固体产生的"
            "高次谐波谱来探测电子结构和超快动力学。"
            "谐波谱包含丰富的物理信息：\n\n"
            "- **截止频率**：反映有效带隙和电子最大动能，"
            "可用于测量能带参数。\n"
            "- **谐波效率**：依赖带间偶极矩和量子几何（Berry 曲率、量子度规），"
            "是探测量子几何的\u201c探针\u201d。\n"
            "- **谐波偏振**：受晶体对称性和 Berry 曲率调制，"
            "可提取拓扑信息。\n"
            "- **椭圆率依赖**：再碰撞效率对驱动场椭圆率的敏感度"
            "反映电子轨迹和能带色散。\n\n"
            "固体 HHG 光谱学与气体 HHG 的差异：固体的周期性结构"
            "使 HHG 不仅探测单原子响应，还编码能带结构、"
            "拓扑性质和相干电子动力学。"
        ),
        "implementation_details": (
            "固体 HHG 实验搭建要点：\n"
            "- **驱动激光**：中红外 OPA/OPCPA（2-5 μm），"
            "高峰值功率但光子能量低，避免样品损伤。\n"
            "- **样品环境**：薄晶（~100 μm）或薄膜，"
            "低温（77K）减少热损伤和声子散射。\n"
            "- **光路设计**：真空或充氮气路减少空气吸收，"
            "尤其对中红外驱动。\n"
            "- **光谱检测**：紫外-可见光谱仪（气相 HHG）"
            "或红外光谱仪（固体 HHG 截止较低）。\n"
            "- **强度校准**：绝对强度校准困难，"
            "常用相对标度（如功率的 n 次方）。\n"
            "- **偏振控制**：λ/2、λ/4 波片控制驱动场偏振，"
            "需注意中红外波片的色散。\n\n"
            "样品制备：单晶薄片需双面抛光，"
            "薄膜样品需透明基底。厚度需小于吸收长度"
            "以避免再吸收。"
        ),
        "data_analysis": (
            "HHG 光谱数据分析：\n"
            "1. **背景扣除**：扣除驱动光散射和探测器暗背景。\n"
            "2. **谐波阶次标定**：用已知波长校准光谱轴，"
            "识别奇次/偶次谐波。\n"
            "3. **强度标度分析**：拟合 $\\log I_q$ vs $\\log I_0$ 斜率，"
            "判断微扰/非微扰区。\n"
            "4. **截止频率提取**：识别谐波谱截止位置，"
            "与理论 $E_g + 3.17 U_p$ 对比。\n"
            "5. **偏振分析**：用偏振片扫描谐波偏振态，"
            "提取 Stokes 参数。\n"
            "6. **角度依赖**：旋转晶体取向，"
            "分析谐波强度/偏振与晶体对称性的关系。\n\n"
            "误差分析：光强涨落（~5-10%）、"
            "样品位置漂移、光谱仪响应"
            "是主要误差源。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **样品损伤**：高光强下样品易损伤，"
            "限制可探测的最大谐波阶次。\n"
            "- **相位匹配模糊**：实验测得的谐波谱"
            "受传播效应（相位匹配、吸收）调制，"
            "非本征单原子响应。\n"
            "- **热效应**：高重复频率激光引起热积累，"
            "改变样品温度和带隙。\n"
            "- **表面贡献**：表面与体相 HHG 机制不同，"
            "薄样品需区分。\n"
            "- **强度校准困难**：绝对强度校准误差大，"
            "定量对比理论困难。\n"
            "- **温度依赖**：室温下声子散射强烈，"
            "低温数据可能不代表室温行为。"
        ),
    },
    "偏振测量": {
        "name": "偏振测量",
        "name_en": "Polarimetry",
        "category": "experimental",
        "keywords": ["偏振测量", "polarimetry", "Stokes参数", "偏振态", "椭圆率测量"],
        "related_methods": ["HHG光谱", "时间分辨泵浦-探测", "傅里叶分析"],
        "expertise_level": "beginner",
        "estimated_learning_time": "1-2 周",
        "theoretical_background": (
            "偏振测量通过分析光波的偏振态来提取介质的光学性质。"
            "光波的偏振态由 Stokes 参数完整描述：\n\n"
            "$$S_0 = I, \\quad S_1 = I_H - I_V, \\quad "
            "S_2 = I_{+45} - I_{-45}, \\quad S_3 = I_R - I_L$$\n\n"
            "其中 $I_H, I_V$ 为水平/垂直偏振分量强度，"
            "$I_{+45}, I_{-45}$ 为 ±45° 线偏振分量，"
            "$I_R, I_L$ 为右旋/左旋圆偏振分量。"
            "偏振度 $P = \\sqrt{S_1^2+S_2^2+S_3^2}/S_0 \\leq 1$。\n\n"
            "在 HHG 研究中，谐波偏振态编码了晶体对称性和 Berry 曲率信息：\n"
            "- 线偏振驱动下，谐波偏振的旋转角"
            "与 Berry 曲率积分相关；\n"
            "- 圆偏振驱动下，谐波的手性"
            "反映材料的拓扑手性。\n\n"
            "偏振椭圆率 $\\epsilon = \\arctan(b/a)$（b 为短轴，a 为长轴）"
            "是区分线偏振和圆偏振的关键参数。"
        ),
        "implementation_details": (
            "偏振测量实验配置：\n"
            "- **旋转检偏器法**：旋转线偏振片，"
            "记录透射强度 $I(\\theta) = \\frac{S_0}{2} + "
            "\\frac{S_1}{2}\\cos 2\\theta + \\frac{S_2}{2}\\sin 2\\theta$。"
            "可提取 $S_0, S_1, S_2$，但无法获取 $S_3$。\n"
            "- **四分之一波片 + 检偏器**：先经 λ/4 波片"
            "将圆偏振转为线偏振，再旋转检偏器，"
            "可完整提取四个 Stokes 参数。\n"
            "- **分振幅偏振计**：用偏振分束器"
            "同时测量多个分量，速度快但校准复杂。\n"
            "- **光谱偏振测量**：结合光谱仪，"
            "获取每个谐波阶次的偏振态。\n\n"
            "校准：波片相位延迟、检偏器消光比、"
            "探测器响应均需校准。"
            "中红外波段需特殊波片（如 Fresnel rhomb）。"
        ),
        "data_analysis": (
            "偏振数据分析流程：\n"
            "1. **Stokes 参数计算**：从测量的强度数据"
            "拟合提取 $S_0, S_1, S_2, S_3$。\n"
            "2. **偏振椭圆参数**：方位角 "
            "$\\psi = \\frac{1}{2}\\arctan(S_2/S_1)$，"
            "椭圆率 $\\chi = \\frac{1}{2}\\arcsin(S_3/S_0)$。\n"
            "3. **偏振度**：$P = \\sqrt{S_1^2+S_2^2+S_3^2}/S_0$，"
            "P=1 为完全偏振，P<1 为部分偏振。\n"
            "4. **手性分析**：$S_3/S_0$ 的符号"
            "区分左旋/右旋圆偏振。\n"
            "5. **谐波阶次依赖**：绘制偏振参数 vs 谐波阶次，"
            "揭示对称性约束和几何贡献。\n\n"
            "与理论对比：将实验偏振角/椭圆率"
            "与 SBE/TDDFT 预测对比，验证模型。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **波片色散**：波片相位延迟依赖波长，"
            "宽谱测量需消色差波片或逐波长校准。\n"
            "- **检偏器消光比**：实际检偏器消光比有限（~1000:1），"
            "限制圆偏振测量精度。\n"
            "- **仪器偏振**：光路中的反射镜、光栅"
            "引入仪器偏振，需校准扣除。\n"
            "- **部分偏振**：若谐波为部分偏振，"
            "需额外测量 $S_0$ 获取偏振度。\n"
            "- **时间分辨率**：旋转检偏器法为时间积分，"
            "无法获取偏振的时间演化。\n"
            "- **低信噪比**：高次谐波强度弱，"
            "偏振测量的统计误差可能较大。"
        ),
    },
    "时间分辨泵浦-探测": {
        "name": "时间分辨泵浦-探测",
        "name_en": "Time-Resolved Pump-Probe",
        "category": "experimental",
        "keywords": ["泵浦-探测", "pump-probe", "时间分辨", "瞬态", "超快动力学"],
        "related_methods": ["HHG光谱", "傅里叶分析", "ARPES"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "2-3 周",
        "theoretical_background": (
            "时间分辨泵浦-探测技术是超快光学的核心实验方法，"
            "通过两束时间延迟可调的激光脉冲探测材料的瞬态响应：\n\n"
            "- **泵浦光**（pump）：激发样品，"
            "产生非平衡载流子或相干态。\n"
            "- **探测光**（probe）：在延迟时间 Δt 后"
            "探测样品的瞬态状态。\n\n"
            "通过扫描延迟时间 Δt，"
            "可重建激发态的时间演化。"
            "时间分辨率由脉冲宽度决定，"
            "飞秒脉冲可分辨 ~10 fs 的动力学。\n\n"
            "在固体 HHG 研究中，泵浦-探测可用于：\n"
            "- 测量载流子弛豫时间（T1）；\n"
            "- 探测退相干时间（T2）；\n"
            "- 研究光诱导相变；\n"
            "- 分离带间和带内 HHG 贡献（双色场方案）。\n\n"
            "信号形式：瞬态反射率 ΔR/R(t)、"
            "瞬态透射 ΔT/T(t)、"
            "瞬态谐波强度 ΔI_q(t) 等。"
        ),
        "implementation_details": (
            "泵浦-探测实验搭建要点：\n"
            "- **光源**：飞秒激光放大器（如 Ti:Sapphire，800 nm，35 fs，1 kHz），"
            "分束为泵浦和探测光。\n"
            "- **延迟线**：精密平移台（精度 ~100 nm）"
            "控制光程差，1 μm 对应 3.3 fs。\n"
            "- **泵浦/探测波长**：可用 OPA 改变波长，"
            "实现共振/非共振激发。\n"
            "- **锁相检测**：用斩波器调制泵浦光，"
            "锁相放大器提取 ΔR/R，提高信噪比。\n"
            "- **偏振控制**：泵浦与探测光的偏振"
            "（平行/垂直）影响信号物理含义。\n"
            "- **双色 HHG 泵浦-探测**：用基频 + 二倍频"
            "双色场驱动 HHG，"
            "通过相位延迟控制谐波发射。\n\n"
            "样品环境：低温恒温器（4-300K）"
            "研究温度依赖动力学。"
        ),
        "data_analysis": (
            "泵浦-探测数据分析：\n"
            "1. **瞬态曲线拟合**：$\\Delta R/R(t)$ 拟合"
            "多指数衰减 $\\sum A_i e^{-t/\\tau_i}$，"
            "提取弛豫时间常数。\n"
            "2. **相干振荡**：提取振荡分量频率，"
            "对应相干声子或电子量子拍频。\n"
            "3. **频率-时间分析**：对瞬态谱做"
            "Gabor 变换获取时间分辨光谱。\n"
            "4. **双色场 HHG 分析**：拟合谐波强度"
            "vs 两色场相位延迟，提取发射时间窗口。\n"
            "5. **温度依赖**：不同温度下的弛豫时间"
            "揭示散射机制（电子-声子、声子-声子）。\n\n"
            "误差分析：延迟线精度、"
            "脉冲到脉冲稳定性、"
            "热漂移是主要误差源。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **时间分辨率**：受脉冲宽度限制，"
            "无法分辨短于脉冲宽度的过程。\n"
            "- **时间-能量不确定性**：短脉冲带宽大，"
            "能量分辨率差，需权衡。\n"
            "- **热效应**：泵浦光加热样品，"
            "高重复频率下需散热。\n"
            "- **多光子激发**：强泵浦可能产生多光子"
            "或雪崩电离，偏离单光子图像。\n"
            "- **相干假象**：相干极化（如光子回波）"
            "可能被误认为载流子弛豫。\n"
            "- **空间平均**：聚焦光斑内强度不均，"
            "信号为空间平均，非本征响应。"
        ),
    },
    "ARPES": {
        "name": "角分辨光电子能谱",
        "name_en": "Angle-Resolved Photoemission Spectroscopy",
        "category": "experimental",
        "keywords": ["ARPES", "角分辨光电子", "photoemission", "光电子能谱"],
        "related_methods": ["能带结构计算", "时间分辨泵浦-探测", "Berry曲率计算"],
        "expertise_level": "advanced",
        "estimated_learning_time": "4-6 周",
        "theoretical_background": (
            "角分辨光电子能谱（ARPES）是直接测量固体电子结构的"
            "最强大实验技术之一。基于光电效应：\n\n"
            "$$E_{kin} = h\\nu - \\phi - |E_B|$$\n\n"
            "其中 $h\\nu$ 为光子能量，$\\phi$ 为功函数，"
            "$E_B$ 为结合能。通过测量光电子的动能和发射角度，"
            "可同时获取电子的能量和动量：\n"
            "$$k_{\\parallel} = \\frac{\\sqrt{2m_e E_{kin}}}{\\hbar}\\sin\\theta$$\n\n"
            "ARPES 直接测量占据态的能谱函数 $A(\\mathbf{k}, \\omega) f(\\omega)$，"
            "提供能带色散、费米面、自旋结构等信息。\n\n"
            "在超快光学研究中，trARPES（时间分辨 ARPES）"
            "可追踪非平衡电子分布的时间演化，"
            "直接观测 Floquet 态和光诱导能带变化。"
        ),
        "implementation_details": (
            "ARPES 实验配置：\n"
            "- **光源**：同步辐射或实验室激光（6-100 eV），"
            "高能量分辨率需单色器。\n"
            "- **真空**：超高真空（< 10^-10 mbar），"
            "避免表面污染。\n"
            "- **样品制备**：需解理或原位制备清洁表面，"
            "低温（10-100K）减少热展宽。\n"
            "- **电子分析器**：半球形电子能量分析器，"
            "同时测量能量和角度。\n"
            "- **自旋分辨**：Mott 探测器或 VLEED 自旋分析器"
            "实现自旋分辨 ARPES。\n"
            "- **trARPES**：飞秒激光 + 时间延迟扫描，"
            "时间分辨率 ~20-100 fs。\n\n"
            "常用设施：同步辐射光束线、"
            "实验室激光 ARPES（11 eV HHG 光源）。"
        ),
        "data_analysis": (
            "ARPES 数据分析：\n"
            "1. **能带绘制**：以 $E_B$ 和 $k_{\\parallel}$ 为轴"
            "绘制强度图 $I(k, \\omega)$，"
            "直接对应能带色散。\n"
            "2. **费米面**：在 $E_F$ 处的 $k_x$-$k_y$ 强度图，"
            "提取费米面拓扑。\n"
            "3. **谱函数提取**：从 ARPES 强度"
            "反卷积获取 $A(k, \\omega)$，"
            "需考虑矩阵元效应和背景。\n"
            "4. **自旋结构**：自旋分辨 ARPES "
            "绘制 $S(k, \\omega)$，验证拓扑物相。\n"
            "5. **trARPES 分析**：追踪非平衡分布"
            "$\\Delta n(k, t)$，拟合弛豫时间。\n"
            "6. **Floquet 态识别**：在驱动场下"
            "观察准能量复制带，验证 Floquet 理论。\n\n"
            "矩阵元效应：ARPES 强度"
            "$I \\propto |\\langle \\psi_f | \\mathbf{A}\\cdot\\mathbf{p} | "
            "\\psi_i \\rangle|^2 A(k,\\omega)$，"
            "矩阵元效应可改变表观强度。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **表面敏感**：ARPES 探测深度 ~5-10 Å，"
            "为表面敏感技术，体相性质需谨慎推断。\n"
            "- **仅占据态**：标准 ARPES 只能测量费米能以下"
            "的占据态，导带需反演或 trARPES。\n"
            "- **k_z 不确定**：光电子逃逸深度"
            "导致 k_z 分辨率差，3D 动量需光子能量扫描。\n"
            "- **矩阵元效应**：不同光子能量/偏振"
            "的选择定则不同，可能\u201c看不到\u201d某些能带。\n"
            "- **样品要求高**：需高质量单晶"
            "和清洁表面，层状材料更易测量。\n"
            "- **能量分辨率**：实验室 ARPES ~10 meV，"
            "同步辐射 ~1-5 meV，"
            "对窄带隙材料可能不足。"
        ),
    },

    # ── 分析方法 ──
    "贝叶斯反演": {
        "name": "贝叶斯反演",
        "name_en": "Bayesian Inversion",
        "category": "analytical",
        "keywords": ["贝叶斯", "Bayesian", "反演", "贝叶斯推断", "贝叶斯反演", "MCMC"],
        "related_methods": ["神经网络回归", "傅里叶分析"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "2-3 周",
        "theoretical_background": (
            "贝叶斯反演是将观测数据映射到模型参数的概率推断方法。"
            "核心是 Bayes 定理：\n\n"
            "$$P(\\theta|D) = \\frac{P(D|\\theta)P(\\theta)}{P(D)}$$\n\n"
            "其中 $\\theta$ 为模型参数，$D$ 为观测数据：\n"
            "- $P(\\theta|D)$：后验分布（推断目标）；\n"
            "- $P(D|\\theta)$：似然函数（数据与模型的匹配度）；\n"
            "- $P(\\theta)$：先验分布（参数的先验知识）；\n"
            "- $P(D)$：证据（归一化常数）。\n\n"
            "在强场光学中，贝叶斯反演可用于：\n"
            "- 从 HHG 谱反演能带结构；\n"
            "- 从偏振数据提取 Berry 曲率分布；\n"
            "- 从瞬态光谱拟合多参数动力学模型。\n\n"
            "优势：提供参数的不确定性量化（后验分布），"
            "而非点估计；可自然融入先验知识。"
        ),
        "implementation_details": (
            "贝叶斯反演实现要点：\n"
            "- **前向模型**：定义 $\\hat{y} = f(\\theta)$，"
            "将参数映射到可观测量。"
            "在 HHG 中即为 SBE/TDDFT 模拟器。\n"
            "- **似然函数**：假设观测噪声为高斯，"
            "$\\ln P(D|\\theta) = -\\frac{1}{2}\\sum_i "
            "\\frac{(y_i - \\hat{y}_i)^2}{\\sigma_i^2}$。\n"
            "- **先验选择**：均匀先验（无信息）"
            "或正态先验（含先验知识），"
            "需注意先验对后验的影响。\n"
            "- **采样方法**：MCMC（Metropolis-Hastings、"
            "Hamiltonian MC）或嵌套采样（MultiNest）。"
            "Python 标准库无直接支持，"
            "可自实现 Metropolis 算法。\n"
            "- **收敛诊断**：Gelman-Rubin R̂ 统计量、"
            "自相关时间、有效样本数。\n\n"
            "降维：参数空间高维时，"
            "用 PCA 或自动微分变分推断降维。"
        ),
        "data_analysis": (
            "贝叶斯反演结果分析：\n"
            "1. **后验分布**：MCMC 链的直方图"
            "给出各参数的边缘后验分布，"
            "报告均值 ± 标准差或置信区间。\n"
            "2. **参数相关性**：散点矩阵图"
            "揭示参数间的后验相关。\n"
            "3. **模型比较**：贝叶斯因子或信息准则"
            "（BIC/DIC）比较不同模型。\n"
            "4. **后验预测检验**：从后验采样参数，"
            "生成预测数据与观测对比，"
            "验证模型充分性。\n"
            "5. **不确定性传播**：将参数后验"
            "传播到预测量，获取预测区间。\n\n"
            "与点估计对比：贝叶斯结果"
            "含不确定性信息，"
            "比最小二乘拟合更完整。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **计算成本高**：MCMC 需大量前向模型评估，"
            "若前向模型为 TDDFT 则不可行，需代理模型。\n"
            "- **先验敏感**：数据稀疏时后验依赖先验，"
            "需做先验敏感性分析。\n"
            "- **收敛诊断困难**：MCMC 收敛判断"
            "无严格标准，"
            "需多种诊断工具联合使用。\n"
            "- **多峰后验**：后验分布多峰时"
            "MCMC 可能困于局部峰，"
            "需并行退火或嵌套采样。\n"
            "- **模型误设**：若前向模型本身有误，"
            "后验推断结果无意义，"
            "需后验预测检验。\n"
            "- **维数灾难**：参数维度 > 20 时"
            "MCMC 效率急剧下降。"
        ),
    },
    "神经网络回归": {
        "name": "神经网络回归",
        "name_en": "Neural Network Regression",
        "category": "analytical",
        "keywords": ["神经网络", "neural network", "深度学习", "deep learning", "NN回归", "机器学习"],
        "related_methods": ["贝叶斯反演", "傅里叶分析"],
        "expertise_level": "intermediate",
        "estimated_learning_time": "2-3 周",
        "theoretical_background": (
            "神经网络回归用神经网络拟合输入-输出映射 $y = f_\\theta(\\mathbf{x})$，"
            "通过反向传播优化参数 $\\theta$。"
            "全连接网络的前向传播：\n\n"
            "$$\\mathbf{h}^{(l+1)} = \\sigma(W^{(l)}\\mathbf{h}^{(l)} + \\mathbf{b}^{(l)})$$\n\n"
            "其中 $\\sigma$ 为激活函数（如 ReLU、tanh），"
            "$W^{(l)}$、$\\mathbf{b}^{(l)}$ 为第 l 层权重和偏置。\n\n"
            "损失函数（回归任务）：\n"
            "$$L = \\frac{1}{N}\\sum_{i=1}^N (y_i - \\hat{y}_i)^2 + \\lambda\\|\\theta\\|^2$$\n\n"
            "L2 正则化项 $\\lambda\\|\\theta\\|^2$ 防止过拟合。\n\n"
            "在强场光学中，神经网络回归可用于：\n"
            "- 从 HHG 谱预测材料参数（代理模型）；\n"
            "- 加速贝叶斯反演的前向模型评估；\n"
            "- 从实验数据学习非线性极化率映射；\n"
            "- 识别谐波谱中的物理特征模式。\n\n"
            "优势：可拟合任意非线性映射，"
            "无需显式物理模型假设。"
        ),
        "implementation_details": (
            "神经网络回归实现要点（纯标准库）：\n"
            "- **架构选择**：全连接网络 3-5 层，"
            "每层 64-256 神经元，ReLU 激活。\n"
            "- **数据预处理**：输入/输出标准化"
            "（零均值、单位方差），加速收敛。\n"
            "- **优化器**：Adam 或 SGD+动量，"
            "学习率 0.001-0.01，"
            "学习率衰减。\n"
            "- **批量训练**：mini-batch 32-256，"
            "epoch 100-1000，"
            "早停防过拟合。\n"
            "- **正则化**：Dropout（率 0.1-0.5）、"
            "L2 正则化、批归一化。\n"
            "- **纯 Python 实现**：标准库无神经网络框架，"
            "需自实现前向/反向传播（numpy 不可用），"
            "或调用外部 CLI（如 python3 -c 配合 hermes）。\n\n"
            "推荐：用框架训练模型，"
            "导出权重后在纯 Python 中做前向推理。"
        ),
        "data_analysis": (
            "神经网络回归结果分析：\n"
            "1. **训练/验证曲线**：监控训练/验证损失，"
            "检测过拟合（验证损失上升）。\n"
            "2. **R^2 分数**：$R^2 = 1 - "
            "\\frac{\\sum(y_i - \\hat{y}_i)^2}{\\sum(y_i - \\bar{y})^2}$，"
            "R^2 → 1 表示拟合良好。\n"
            "3. **残差分析**：残差 $y_i - \\hat{y}_i$ "
            "应无系统趋势，"
            "否则模型欠拟合。\n"
            "4. **特征重要性**：通过扰动分析"
            "或梯度归因识别关键输入特征。\n"
            "5. **外推检验**：在训练域外测试，"
            "评估泛化能力（通常较差）。\n"
            "6. **不确定性估计**：集成网络（dropout 推理）"
            "或贝叶斯神经网络提供预测不确定性。\n\n"
            "与物理模型对比：神经网络"
            "牺牲可解释性换取灵活性，"
            "需结合物理约束（PINN）提升可靠性。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **数据需求大**：需大量训练数据，"
            "实验数据通常不足，需数据增强或迁移学习。\n"
            "- **过拟合风险**：网络容量大时易过拟合，"
            "需严格正则化和验证。\n"
            "- **外推不可靠**：训练域外预测"
            "可能完全错误，需标注适用范围。\n"
            "- **缺乏可解释性**：黑箱模型"
            "难以提取物理洞察，"
            "需配合可解释性工具。\n"
            "- **超参数敏感**：层数、学习率、正则化等"
            "超参数影响大，调参耗时。\n"
            "- **物理约束缺失**：标准网络"
            "不保证物理守恒律，"
            "需物理信息神经网络（PINN）修正。"
        ),
    },
    "傅里叶分析": {
        "name": "傅里叶分析",
        "name_en": "Fourier Analysis",
        "category": "analytical",
        "keywords": ["傅里叶", "Fourier", "FFT", "频谱分析", "频域分析"],
        "related_methods": ["HHG模拟", "时间分辨泵浦-探测", "偏振测量"],
        "expertise_level": "beginner",
        "estimated_learning_time": "1 周",
        "theoretical_background": (
            "傅里叶分析将信号从时域转换到频域，"
            "是信号处理的基石。连续傅里叶变换：\n\n"
            "$$\\tilde{f}(\\omega) = \\int_{-\\infty}^{\\infty} f(t) e^{-i\\omega t} dt$$\n\n"
            "逆变换：\n"
            "$$f(t) = \\frac{1}{2\\pi}\\int_{-\\infty}^{\\infty} "
            "\\tilde{f}(\\omega) e^{i\\omega t} d\\omega$$\n\n"
            "离散傅里叶变换（DFT/FFT）：\n"
            "$$\\tilde{f}_k = \\sum_{n=0}^{N-1} f_n e^{-i2\\pi kn/N}$$\n\n"
            "在超快光学中，傅里叶分析用于：\n"
            "- 从含时偶极矩提取 HHG 频谱；\n"
            "- 从时间分辨信号提取振荡频率（声子、量子拍频）；\n"
            "- 滤波与降噪（低通/带通滤波）；\n"
            "- 短时傅里叶变换（STFT/Gabor 变换）"
            "获取时间-频率联合分布。\n\n"
            "关键定理：Parseval 定理保证"
            "时域和频域能量守恒；"
            "卷积定理将时域卷积转为频域乘积。"
        ),
        "implementation_details": (
            "傅里叶分析实现要点（纯标准库）：\n"
            "- **FFT 算法**：Python 标准库 `math` 含基础数学函数，"
            "但无 FFT。可用自实现 Cooley-Tukey FFT，"
            "或用 hermes CLI 调用 numpy。\n"
            "- **采样定理**：采样率 $f_s > 2 f_{max}$ "
            "避免混叠，需在采样前抗混叠滤波。\n"
            "- **窗函数**：有限长度信号需加窗"
            "（Hanning、Hamming、Blackman）"
            "减少频谱泄漏。\n"
            "- **零填充**：FFT 前零填充至 2 的幂次"
            "提高频率分辨率（插值，非真实分辨率提升）。\n"
            "- **STFT 实现**：滑动窗 FFT，"
            "窗长决定时间分辨率，"
            "与频率分辨率权衡。\n\n"
            "自实现 FFT（Cooley-Tukey）：\n"
            "对 N=2^m 点信号递归分解，"
            "复杂度 O(N log N)。"
            "标准库 `cmath` 提供复数运算支持。"
        ),
        "data_analysis": (
            "傅里叶分析输出解读：\n"
            "1. **幅度谱**：$|\\tilde{f}(\\omega)|$ vs 频率，"
            "识别主频率分量。\n"
            "2. **相位谱**：$\\arg[\\tilde{f}(\\omega)]$ vs 频率，"
            "含色散和延迟信息。\n"
            "3. **功率谱密度**：$|\\tilde{f}(\\omega)|^2$，"
            "与能量/强度直接相关。\n"
            "4. **STFT 时频图**：以时间和频率为轴"
            "的幅度热图，"
            "揭示频率分量的时间演化。\n"
            "5. **谐波识别**：在 HHG 谱中"
            "识别等间距的谐波峰，"
            "间距 = 驱动频率。\n"
            "6. **去噪**：频域滤波"
            "（保留目标频带，抑制噪声）"
            "后逆变换回时域。\n\n"
            "频率校准：用已知频率标准"
            "校准频轴，"
            "消除采样率误差。"
        ),
        "limitations": (
            "局限与陷阱：\n"
            "- **频谱泄漏**：有限窗导致"
            "频率分量\u201c泄漏\u201d到相邻频点，"
            "需加窗缓解。\n"
            "- **频率分辨率**：$\\Delta f = 1/T$，"
            "T 为信号长度，"
            "短信号频率分辨率差。\n"
            "- **时间-频率不确定性**：STFT 中"
            "时间分辨率与频率分辨率不可同时最优"
            "（Heisenberg 不确定性）。\n"
            "- **混叠**：采样率不足导致"
            "高频分量折叠到低频，"
            "需抗混叠滤波。\n"
            "- **边界效应**：有限信号"
            "FFT 假设周期延拓，"
            "边界不连续引入伪频谱。\n"
            "- **非平稳信号**：标准 FFT "
            "假设平稳信号，"
            "非平稳信号需 STFT 或小波分析。"
        ),
    },
}


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _count_words(text: str) -> int:
    """统计字数（中文字符按字计，英文按词计，标点不计）。"""
    if not text:
        return 0
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    no_chinese = re.sub(r'[\u4e00-\u9fff]', ' ', text)
    no_punct = re.sub(
        r'[#\*\-\[\]\(\)<>|`~!@#$%^&+=/\\.,;:\'"!?，。；：""''（）、…—\n\r\t ]',
        ' ', no_chinese,
    )
    english_words = len([w for w in no_punct.split() if len(w) > 1])
    return chinese_chars + english_words


def _parse_citation_numbers(match_str: str) -> List[int]:
    """解析引文标记中的数字，展开范围为完整列表。

    例如: "1" → [1], "1,3" → [1,3], "1-3" → [1,2,3], "1,2-4" → [1,2,3,4]
    """
    nums: List[int] = []
    for part in match_str.split(','):
        part = part.strip()
        if '-' in part:
            sub = part.split('-', 1)
            try:
                start, end = int(sub[0]), int(sub[1])
                if start <= end:
                    nums.extend(range(start, end + 1))
                else:
                    nums.append(start)
            except ValueError:
                continue
        else:
            try:
                nums.append(int(part))
            except ValueError:
                continue
    return nums


def _scan_citations_in_text(text: str) -> List[int]:
    """扫描文本中的 [N] 引文标记，返回引用编号列表（去重保序）。"""
    seen: List[int] = []
    for m in _CITATION_PATTERN.finditer(text):
        for n in _parse_citation_numbers(m.group(1)):
            if n not in seen:
                seen.append(n)
    return seen


# ---------------------------------------------------------------------------
# MethodologyManual 类
# ---------------------------------------------------------------------------

class MethodologyManual:
    """方法学手册生成器。

    为每个 proposal 生成详细方法学手册，扫描申请书章节中涉及的方法，
    从内置数据库拉取详细模板，整合知识库链接与引文关联。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护
    read-modify-write 临界区，锁键基于 proposal_dir 路径哈希，
    不同 proposal 互不阻塞。

    边界合规（AGENTS.md §6）：
    - 仅导入 common（共享基础设施）；
    - KB 访问只读（kb_index.search、kb_wiki.get_wiki_page）；
    - 文件写入仅限 research_proposals/{proposal_id}/ 目录；
    - 不导入 CoPilot 核心模块。
    """

    def __init__(self, proposal_dir: Path | str) -> None:
        """初始化方法学手册生成器。

        Args:
            proposal_dir: proposal 根目录（Path 或字符串），
                          手册保存于其下的 04_proposal/。
        """
        self.proposal_dir = Path(proposal_dir)
        self.proposal_content_dir = self.proposal_dir / "04_proposal"
        self.handbook_path = self.proposal_content_dir / "methodology-handbook.json"
        self.markdown_path = self.proposal_content_dir / "methodology-handbook.md"

        # 跨进程锁键：基于 proposal_dir 绝对路径哈希，避免不同 proposal 互相阻塞
        digest = hashlib.md5(
            str(self.proposal_dir.resolve()).encode("utf-8")
        ).hexdigest()[:12]
        self._lock_name = f"methodology-{digest}"

        # 确保目录结构存在
        self.proposal_content_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存
        self._handbook: Optional[Dict[str, Any]] = None

        # 懒加载的模块缓存（None = 尚未加载）
        self._kb_index = None
        self._kb_wiki = None

    # ------------------------------------------------------------------
    # 模块懒加载
    # ------------------------------------------------------------------

    def _load_kb_index(self):
        """懒加载 kb_index 模块，注入桩依赖，返回模块对象或 None。"""
        if self._kb_index is None:
            mod = lazy_load("kb_index")
            if mod is not None:
                # 门面 knowledge_base 未加载时，注入桩依赖使 search() 可正常调用
                if getattr(mod, "_load_aliases", None) is None:
                    mod._load_aliases = lambda: {}
                if getattr(mod, "_ensure_dirs", None) is None:
                    mod._ensure_dirs = lambda: None
                if getattr(mod, "log_growth", None) is None:
                    mod.log_growth = lambda *a, **kw: None
                if getattr(mod, "_log", None) is None:
                    mod._log = None
            self._kb_index = mod
        return self._kb_index

    def _load_kb_wiki(self):
        """懒加载 kb_wiki 模块，返回模块对象或 None。"""
        if self._kb_wiki is None:
            self._kb_wiki = lazy_load("kb_wiki")
        return self._kb_wiki

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------

    def _load_handbook(self) -> Dict[str, Any]:
        """加载手册状态（纯读，不加锁）。

        文件不存在或格式异常时返回空手册结构。
        """
        data = load_json(self.handbook_path, default=None)
        if not isinstance(data, dict) or "methods" not in data:
            return {
                "proposal_id": "",
                "proposal_title": "",
                "methods": {},
                "method_order": [],
                "created_at": now_utc(),
                "updated_at": now_utc(),
            }
        if not isinstance(data["methods"], dict):
            data["methods"] = {}
        if not isinstance(data.get("method_order"), list):
            data["method_order"] = []
        return data

    def _save_handbook(self, data: Dict[str, Any]) -> None:
        """保存手册状态（原子写入，应在锁内调用）。"""
        data["updated_at"] = now_utc()
        save_json(self.handbook_path, data)

    def _next_method_id(self, data: Dict[str, Any]) -> str:
        """生成下一个方法 ID（须在锁内调用）。"""
        existing = data.get("methods", {})
        max_num = 0
        for mid in existing:
            match = re.match(r'^method_(\d+)$', mid)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return f"method_{max_num + 1:03d}"

    # ------------------------------------------------------------------
    # 方法扫描
    # ------------------------------------------------------------------

    def scan_methods(self, text: str) -> List[Dict[str, Any]]:
        """扫描文本，检测涉及的方法关键词。

        匹配策略：
        - 中英文关键词子串匹配（大小写不敏感）；
        - 使用 BUILTIN_METHOD_DATABASE 的 keywords 列表；
        - 检测到的方法返回 [{'method_key': ..., 'name': ..., 'category': ...}]；
        - 去重，保持首次出现顺序。

        Args:
            text: 待扫描的文本（通常为申请书某章节内容）

        Returns:
            检测到的方法列表
        """
        if not text:
            return []

        text_lower = text.lower()
        # 归一化版本：去除所有空白字符，用于处理中英文混排时
        # "Berry 曲率"（带空格）与关键词 "Berry曲率"（无空格）的匹配
        text_nospc = re.sub(r"\s+", "", text_lower)
        detected: List[Dict[str, Any]] = []
        seen_keys: set = set()

        for method_key, info in BUILTIN_METHOD_DATABASE.items():
            keywords = info.get("keywords", [])
            matched = False
            for kw in keywords:
                kw_lower = kw.lower()
                # 1. 原始子串匹配（保留空格，处理多词关键词如 "Berry curvature"）
                if kw_lower in text_lower:
                    matched = True
                    break
                # 2. 去空格匹配（处理 "Berry 曲率" ↔ "Berry曲率" 的中英文间距差异）
                if re.sub(r"\s+", "", kw_lower) in text_nospc:
                    matched = True
                    break
            if matched and method_key not in seen_keys:
                seen_keys.add(method_key)
                detected.append({
                    "method_key": method_key,
                    "name": info["name"],
                    "name_en": info["name_en"],
                    "category": info["category"],
                })

        return detected

    def _scan_all_sections(
        self, proposal_sections: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """扫描所有申请书章节，返回各章节检测到的方法。

        Returns:
            {section_name: [detected_methods]}
        """
        result: Dict[str, List[Dict[str, Any]]] = {}
        for section_name, section_data in proposal_sections.items():
            if isinstance(section_data, dict):
                content = section_data.get("content", "")
            elif isinstance(section_data, str):
                content = section_data
            else:
                content = str(section_data)
            result[section_name] = self.scan_methods(content)
        return result

    # ------------------------------------------------------------------
    # 知识库集成
    # ------------------------------------------------------------------

    def _search_kb_for_method(self, method_name: str) -> List[str]:
        """搜索知识库中与方法相关的 wiki 页面（只读）。

        Args:
            method_name: 方法名称（中文或英文）

        Returns:
            相关 wiki 页面路径列表（可能为空）
        """
        kb_links: List[str] = []
        kb_index = self._load_kb_index()
        if kb_index is None:
            return kb_links

        try:
            # 用方法名和英文搜索
            for query in [method_name]:
                results = kb_index.search(query, top_k=3)
                if isinstance(results, dict):
                    for r in results.get("results", []):
                        path = r.get("path", "")
                        if path and path not in kb_links:
                            kb_links.append(path)
        except Exception:
            pass

        return kb_links

    # ------------------------------------------------------------------
    # 引文集成
    # ------------------------------------------------------------------

    def _link_citations(
        self,
        method_entry: Dict[str, Any],
        citation_manager: Any,
    ) -> Dict[str, Any]:
        """扫描方法条目中的 [N] 引文，关联到参考文献。

        Args:
            method_entry: 方法条目字典
            citation_manager: CitationManager 实例

        Returns:
            更新后的方法条目（含 key_references 和 missing_references 标记）
        """
        # 合并所有文本字段中的引文
        all_text = " ".join([
            method_entry.get("theoretical_background", ""),
            method_entry.get("implementation_details", ""),
            method_entry.get("data_analysis", ""),
            method_entry.get("limitations", ""),
        ])
        cited_numbers = _scan_citations_in_text(all_text)

        key_refs: List[Dict[str, str]] = []
        for num in cited_numbers:
            try:
                # 通过编号查找引用
                refs = citation_manager.list_references()
                for ref in refs:
                    if ref.get("cite_number") == num:
                        key_refs.append({
                            "cite_key": ref.get("cite_key", f"ref_{num:03d}"),
                            "cite_number": num,
                            "annotation": (
                                f"{ref.get('title', '')} — "
                                f"{ref.get('authors', [''])[0] if ref.get('authors') else ''} "
                                f"({ref.get('year', '')})"
                            ),
                        })
                        break
            except Exception:
                pass

        method_entry["key_references"] = key_refs
        method_entry["missing_references"] = len(key_refs) == 0

        return method_entry

    # ------------------------------------------------------------------
    # 核心接口
    # ------------------------------------------------------------------

    def generate_method_entry(
        self,
        method_name: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """生成单个方法条目。

        从内置数据库拉取模板，结合上下文定制。
        方法不在内置库中时生成占位条目。

        Args:
            method_name: 方法名称（可为内置库的 key、中文名或英文名）
            context: 可选上下文，可含：
                - section: 方法出现的申请书章节
                - proposal_text: 相关申请书文本
                - citation_manager: CitationManager 实例

        Returns:
            方法条目字典
        """
        if context is None:
            context = {}
        section = context.get("section", "未指定")

        # 查找内置库（按 key / 中文名 / 英文名 / 关键词匹配）
        template = self._find_builtin_template(method_name)

        timestamp = now_utc()
        if template is not None:
            entry: Dict[str, Any] = {
                "method_id": "",  # 由 generate_handbook 统一分配
                "name": template["name"],
                "name_en": template["name_en"],
                "category": template["category"],
                "section": section,
                "theoretical_background": template["theoretical_background"],
                "implementation_details": template["implementation_details"],
                "data_analysis": template["data_analysis"],
                "limitations": template["limitations"],
                "key_references": [],
                "kb_links": [],
                "related_methods": template.get("related_methods", []),
                "expertise_level": template.get("expertise_level", "intermediate"),
                "estimated_learning_time": template.get("estimated_learning_time", ""),
                "status": "generated",
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        else:
            # 占位条目（方法不在内置库中）
            entry = {
                "method_id": "",
                "name": method_name,
                "name_en": "",
                "category": "theoretical",  # 默认类别
                "section": section,
                "theoretical_background": (
                    f"> **待补充**：方法「{method_name}」不在内置方法数据库中。\n"
                    f"请补充该方法的理论背景、关键方程与物理原理。"
                ),
                "implementation_details": (
                    f"> **待补充**：请补充「{method_name}」的实现细节，"
                    f"包括参数选择、搭建考量与软件工具。"
                ),
                "data_analysis": (
                    f"> **待补充**：请补充「{method_name}」的数据分析流程。"
                ),
                "limitations": (
                    f"> **待补充**：请补充「{method_name}」的局限性与常见陷阱。"
                ),
                "key_references": [],
                "kb_links": [],
                "related_methods": [],
                "expertise_level": "intermediate",
                "estimated_learning_time": "",
                "status": "generated",
                "created_at": timestamp,
                "updated_at": timestamp,
            }

        # 知识库链接
        entry["kb_links"] = self._search_kb_for_method(entry["name"])

        # 引文关联
        citation_manager = context.get("citation_manager")
        if citation_manager is not None:
            entry = self._link_citations(entry, citation_manager)

        return entry

    def _find_builtin_template(self, method_name: str) -> Optional[Dict[str, Any]]:
        """在内置数据库中查找方法模板。

        匹配策略（按优先级）：
        1. 精确匹配 key
        2. 精确匹配中文名
        3. 精确匹配英文名（大小写不敏感）
        4. 关键词子串匹配
        """
        # 1. 精确匹配 key
        if method_name in BUILTIN_METHOD_DATABASE:
            return BUILTIN_METHOD_DATABASE[method_name]

        name_lower = method_name.lower()

        for key, info in BUILTIN_METHOD_DATABASE.items():
            # 2. 精确匹配中文名
            if method_name == info["name"]:
                return info
            # 3. 精确匹配英文名
            if name_lower == info["name_en"].lower():
                return info

        # 4. 关键词子串匹配
        for key, info in BUILTIN_METHOD_DATABASE.items():
            for kw in info.get("keywords", []):
                if kw.lower() in name_lower or name_lower in kw.lower():
                    return info

        return None

    def generate_handbook(
        self,
        proposal_sections: Dict[str, Any],
        gap_report: Optional[Dict[str, Any]] = None,
        citation_manager: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """从申请书章节生成完整方法学手册。

        流程：
        1. 扫描所有章节，检测涉及的方法；
        2. 为每个方法生成详细条目；
        3. 整合知识库链接与引文关联；
        4. 持久化手册。

        Args:
            proposal_sections: 申请书章节字典，
                {section_name: {"content": "..."}} 或 {section_name: "..."}
            gap_report: 可选缺口报告，用于补充方法缺口信息
            citation_manager: 可选 CitationManager 实例，用于引文关联

        Returns:
            完整手册字典
        """
        if not isinstance(proposal_sections, dict):
            raise ValueError("proposal_sections 必须为字典")

        # 扫描所有章节
        section_methods = self._scan_all_sections(proposal_sections)

        # 收集所有检测到的方法（去重，保持顺序）
        all_methods: List[Dict[str, Any]] = []
        seen_keys: set = set()
        for section_name, methods in section_methods.items():
            for m in methods:
                if m["method_key"] not in seen_keys:
                    seen_keys.add(m["method_key"])
                    m["section"] = section_name
                    all_methods.append(m)

        # 从 gap_report 补充方法缺口
        if gap_report and isinstance(gap_report, dict):
            for gap in gap_report.get("gaps", []):
                if gap.get("type") == "methodological":
                    gap_desc = gap.get("description", "")
                    # 尝试从缺口描述中提取方法名
                    for method_key, info in BUILTIN_METHOD_DATABASE.items():
                        if (
                            method_key not in seen_keys
                            and any(
                                kw.lower() in gap_desc.lower()
                                for kw in info.get("keywords", [])
                            )
                        ):
                            seen_keys.add(method_key)
                            all_methods.append({
                                "method_key": method_key,
                                "name": info["name"],
                                "name_en": info["name_en"],
                                "category": info["category"],
                                "section": "缺口补充",
                            })

        # 推导 proposal_title
        proposal_title = ""
        for section_data in proposal_sections.values():
            if isinstance(section_data, dict):
                content = section_data.get("content", "")
            else:
                content = str(section_data)
            if content:
                # 尝试从第一个标题行提取
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("#"):
                        proposal_title = line.lstrip("#").strip()
                        break
                if proposal_title:
                    break

        with file_lock(self._lock_name):
            # 重新加载已有数据（保留已审阅/已补充的条目）
            existing_data = self._load_handbook()
            existing_methods = existing_data.get("methods", {})

            new_methods: Dict[str, Dict[str, Any]] = {}
            method_order: List[str] = []

            for detected in all_methods:
                method_key = detected["method_key"]
                section = detected.get("section", "未指定")

                # 检查是否已有条目（保留 reviewed/enriched 状态）
                existing_entry = None
                for mid, m in existing_methods.items():
                    if m.get("name") == detected["name"]:
                        existing_entry = m
                        method_order.append(mid)
                        new_methods[mid] = m
                        break

                if existing_entry is None:
                    # 生成新条目
                    context = {
                        "section": section,
                        "citation_manager": citation_manager,
                    }
                    entry = self.generate_method_entry(method_key, context)
                    method_id = self._next_method_id(
                        {"methods": new_methods}
                    )
                    entry["method_id"] = method_id
                    new_methods[method_id] = entry
                    method_order.append(method_id)

            # 构建完整手册
            proposal_id = existing_data.get("proposal_id", "")
            if not proposal_id:
                proposal_id = (
                    f"prop_{hashlib.md5(now_utc().encode()).hexdigest()[:8]}"
                )

            handbook: Dict[str, Any] = {
                "proposal_id": proposal_id,
                "proposal_title": proposal_title,
                "methods": new_methods,
                "method_order": method_order,
                "created_at": existing_data.get(
                    "created_at", now_utc()
                ),
                "updated_at": now_utc(),
                "stats": {},
            }

            # 计算统计
            handbook["stats"] = self._compute_stats(handbook)

            self._save_handbook(handbook)

        self._handbook = handbook
        return handbook

    def get_handbook(self) -> Optional[Dict[str, Any]]:
        """获取当前手册；不存在返回 None。"""
        data = load_json(self.handbook_path, default=None)
        if not isinstance(data, dict) or "methods" not in data:
            return None
        return data

    def update_method_entry(
        self,
        method_name: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """更新特定方法条目。

        Args:
            method_name: 方法名称（中文名或英文名），用于定位条目
            updates: 更新字段字典，可含 theoretical_background、
                     implementation_details、data_analysis、limitations、
                     key_references、status 等

        Returns:
            更新后的方法条目

        Raises:
            KeyError: 方法条目不存在
        """
        with file_lock(self._lock_name):
            data = self._load_handbook()
            methods = data.get("methods", {})

            # 查找目标方法
            target_id = None
            for mid, m in methods.items():
                if (
                    m.get("name") == method_name
                    or m.get("name_en", "").lower() == method_name.lower()
                ):
                    target_id = mid
                    break

            if target_id is None:
                raise KeyError(f"方法条目不存在: {method_name}")

            # 应用更新
            target = methods[target_id]
            for key, value in updates.items():
                if key in ("method_id", "created_at"):
                    continue  # 不可更新字段
                target[key] = value

            target["updated_at"] = now_utc()

            # 如果状态更新，检查状态机合法性
            new_status = updates.get("status")
            if new_status and new_status not in METHOD_STATUS_FLOW:
                raise ValueError(
                    f"非法状态: {new_status}（支持: {list(METHOD_STATUS_FLOW)}）"
                )

            # 重新计算统计
            data["methods"][target_id] = target
            data["stats"] = self._compute_stats(data)

            self._save_handbook(data)

        self._handbook = data
        return dict(target)

    # ------------------------------------------------------------------
    # 导出与统计
    # ------------------------------------------------------------------

    def export_handbook(self, format: str = "markdown") -> str:
        """导出方法学手册。

        Args:
            format: "markdown" 或 "json"

        Returns:
            格式化的手册字符串
        """
        data = self.get_handbook()

        if data is None:
            if format == "json":
                return "{}"
            return "# 方法学手册\n\n（暂无手册，请先运行 generate_handbook()）\n"

        if format == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)

        if format != "markdown":
            raise ValueError(f"不支持的格式: {format}（支持 markdown / json）")

        # Markdown 格式
        lines: List[str] = []
        title = data.get("proposal_title", "（未命名）")
        lines.append(f"# 方法学手册：{title}\n")
        lines.append(
            "> 本手册为研究参考文档，详细阐述申请书涉及的核心理论方法与实验技术。\n"
        )

        method_order = data.get("method_order", [])
        methods = data.get("methods", {})

        chinese_numerals = ["一", "二", "三", "四", "五", "六", "七",
                            "八", "九", "十", "十一", "十二", "十三",
                            "十四", "十五", "十六", "十七", "十八"]

        for idx, method_id in enumerate(method_order):
            method = methods.get(method_id, {})
            if not method:
                continue

            numeral = (
                chinese_numerals[idx] if idx < len(chinese_numerals)
                else str(idx + 1)
            )
            name = method.get("name", "未知方法")
            name_en = method.get("name_en", "")
            category = METHOD_CATEGORIES.get(
                method.get("category", ""), method.get("category", "")
            )

            # 标题行
            header = f"## 方法{numeral}：{name}"
            if name_en:
                header += f"（{name_en}）"
            # 生成锚点 ID
            anchor_id = self._make_anchor(name_en or name)
            header += f" {{#{anchor_id}}}"
            lines.append(header + "\n")

            if category:
                lines.append(f"**类别**：{category}")
            expertise = method.get("expertise_level", "")
            if expertise:
                level_map = {
                    "beginner": "入门",
                    "intermediate": "中级",
                    "advanced": "高级",
                }
                lines.append(
                    f"**难度**：{level_map.get(expertise, expertise)}"
                )
            learn_time = method.get("estimated_learning_time", "")
            if learn_time:
                lines.append(f"**预计学习时间**：{learn_time}")
            section = method.get("section", "")
            if section:
                lines.append(f"**出现章节**：{section}")
            status = method.get("status", "")
            if status:
                status_map = {
                    "generated": "已生成",
                    "reviewed": "已审阅",
                    "enriched": "已补充",
                }
                lines.append(f"**状态**：{status_map.get(status, status)}")
            lines.append("")

            # 理论基础
            bg = method.get("theoretical_background", "")
            if bg:
                lines.append("### 理论基础\n")
                lines.append(bg + "\n")

            # 实现细节
            impl = method.get("implementation_details", "")
            if impl:
                lines.append("### 实现细节\n")
                lines.append(impl + "\n")

            # 数据分析
            analysis = method.get("data_analysis", "")
            if analysis:
                lines.append("### 数据分析\n")
                lines.append(analysis + "\n")

            # 局限性
            limits = method.get("limitations", "")
            if limits:
                lines.append("### 局限性\n")
                lines.append(limits + "\n")

            # 参考文献
            refs = method.get("key_references", [])
            if refs:
                lines.append("### 参考文献\n")
                for ref in refs:
                    cite_key = ref.get("cite_key", "")
                    annotation = ref.get("annotation", "")
                    # 提取编号
                    cite_num = ref.get("cite_number", "")
                    if cite_num:
                        lines.append(f"- [{cite_num}] {annotation}")
                    else:
                        lines.append(f"- [{cite_key}] {annotation}")
                lines.append("")
            elif method.get("missing_references"):
                lines.append("### 参考文献\n")
                lines.append("> **待补充**：该方法暂无关联参考文献。\n")

            # 知识库链接
            kb_links = method.get("kb_links", [])
            if kb_links:
                lines.append("### 知识库链接\n")
                for link in kb_links:
                    link_name = Path(link).stem if link else ""
                    lines.append(f"- [{link_name}]({link})")
                lines.append("")
            else:
                lines.append("### 知识库链接\n")
                lines.append(
                    "> **认知边界**：知识库中暂无该方法的条目，"
                    "可作为知识库增长点。\n"
                )

            # 相关方法
            related = method.get("related_methods", [])
            if related:
                lines.append("### 相关方法\n")
                lines.append("、".join(related) + "\n")

            lines.append("---\n")

        markdown_text = "\n".join(lines)

        # 同时写入 Markdown 文件
        try:
            self.markdown_path.write_text(markdown_text, encoding="utf-8")
        except Exception:
            pass

        return markdown_text

    @staticmethod
    def _make_anchor(name: str) -> str:
        """生成 Markdown 锚点 ID。"""
        # 转小写，空格转连字符，保留中英文
        anchor = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', name.lower())
        anchor = re.sub(r'-+', '-', anchor).strip('-')
        return f"method-{anchor}" if anchor else "method"

    def _compute_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算手册统计信息。"""
        methods = data.get("methods", {})
        method_order = data.get("method_order", [])

        total_words = 0
        total_refs = 0
        category_counts: Dict[str, int] = {}
        status_counts: Dict[str, int] = {}

        for mid in method_order:
            m = methods.get(mid, {})
            if not m:
                continue
            for field in (
                "theoretical_background",
                "implementation_details",
                "data_analysis",
                "limitations",
            ):
                total_words += _count_words(m.get(field, ""))
            total_refs += len(m.get("key_references", []))

            cat = m.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

            status = m.get("status", "generated")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "method_count": len(method_order),
            "total_words": total_words,
            "reference_count": total_refs,
            "category_distribution": category_counts,
            "status_distribution": status_counts,
            "kb_linked_count": sum(
                1 for mid in method_order
                if methods.get(mid, {}).get("kb_links")
            ),
        }

    def get_handbook_stats(self) -> Dict[str, Any]:
        """获取手册统计信息。

        Returns:
            统计字典，含：
            - method_count: 方法总数
            - total_words: 总字数
            - reference_count: 参考文献总数
            - category_distribution: 按类别分布
            - status_distribution: 按状态分布
            - kb_linked_count: 关联知识库的方法数
        """
        data = self.get_handbook()
        if data is None:
            return {
                "method_count": 0,
                "total_words": 0,
                "reference_count": 0,
                "category_distribution": {},
                "status_distribution": {},
                "kb_linked_count": 0,
            }
        # 如果已缓存 stats 则返回，否则重新计算
        stats = data.get("stats")
        if stats and isinstance(stats, dict) and "method_count" in stats:
            return stats
        return self._compute_stats(data)


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """自检：15 个检查点，使用临时目录与 mock 数据隔离测试。

    覆盖：
      1.  MethodologyManual 初始化
      2.  完整手册生成（从 mock 章节）
      3.  单个方法条目生成
      4.  方法扫描（从文本检测方法）
      5.  内置数据库覆盖（18 种方法完整）
      6.  手册获取
      7.  方法条目更新
      8.  Markdown 导出（结构验证）
      9.  JSON 导出
      10. 手册统计
      11. 知识库集成（mock 搜索结果）
      12. 空申请书处理
      13. 原子写入 + 文件锁
      14. 引文集成（mock citation_manager）
      15. 占位条目（非内置库方法）
    """
    import shutil
    import tempfile

    print("=" * 50)
    print("◐ methodology_manual 自检")
    print("=" * 50)

    tmp = Path(tempfile.mkdtemp(prefix="methodology_test_"))
    try:
        proposal_dir = tmp / "T1_proposal"

        # ── [1/15] 初始化 ──
        print("\n[1/15] 初始化...")
        manual = MethodologyManual(proposal_dir)
        assert manual.proposal_dir == proposal_dir
        assert manual.proposal_content_dir == proposal_dir / "04_proposal"
        assert (
            manual.handbook_path
            == proposal_dir / "04_proposal" / "methodology-handbook.json"
        )
        assert (
            manual.markdown_path
            == proposal_dir / "04_proposal" / "methodology-handbook.md"
        )
        assert manual._lock_name.startswith("methodology-")
        assert manual.proposal_content_dir.exists()
        print(f"  proposal_dir: {manual.proposal_dir}")
        print(f"  handbook_path: {manual.handbook_path}")
        print(f"  lock_name: {manual._lock_name}")
        print("  ✓ 初始化字段完整，目录已创建")

        # ── [2/15] 完整手册生成 ──
        print("\n[2/15] 完整手册生成...")
        mock_sections = {
            "立项依据": {
                "content": (
                    "# 量子度规对固体HHG光谱的调制机制研究\n\n"
                    "固体高次谐波产生（HHG）是强场超快光学的前沿方向。"
                    "TDDFT 计算[1]表明固体 HHG 编码了量子几何信息。"
                    "Berry 曲率[2]和量子度规[3]对谐波效率有显著调制作用。\n"
                )
            },
            "研究方案": {
                "content": (
                    "## 研究方法\n\n"
                    "本项目采用 SBE（半导体布洛赫方程）和 Floquet 理论"
                    "进行理论分析。计算方法包括能带结构计算和"
                    "拓扑不变量计算[4]。"
                    "实验上采用 HHG 光谱和偏振测量技术。"
                    "数据分析使用贝叶斯反演和傅里叶分析。\n"
                )
            },
        }
        handbook = manual.generate_handbook(mock_sections)
        assert "methods" in handbook
        assert "method_order" in handbook
        assert len(handbook["method_order"]) > 0
        method_count = len(handbook["method_order"])
        print(f"  检测到 {method_count} 种方法")
        print(f"  方法列表: {[handbook['methods'][mid]['name'] for mid in handbook['method_order']]}")
        # 应至少检测到 TDDFT、SBE、Floquet、Berry曲率、量子度规等
        detected_names = {
            handbook["methods"][mid]["name"]
            for mid in handbook["method_order"]
        }
        assert "含时密度泛函理论" in detected_names, "应检测到 TDDFT"
        assert "半导体布洛赫方程" in detected_names, "应检测到 SBE"
        assert "Floquet 理论" in detected_names, "应检测到 Floquet"
        assert "贝里曲率计算" in detected_names, "应检测到 Berry 曲率"
        assert "量子度规计算" in detected_names, "应检测到量子度规"
        print(f"  proposal_title: {handbook['proposal_title']}")
        assert "量子度规" in handbook["proposal_title"]
        print("  ✓ 手册生成正确，方法检测完整")

        # ── [3/15] 单个方法条目生成 ──
        print("\n[3/15] 单个方法条目生成...")
        entry = manual.generate_method_entry(
            "TDDFT",
            context={"section": "研究方案"},
        )
        assert entry["name"] == "含时密度泛函理论"
        assert entry["name_en"] == "Time-Dependent Density Functional Theory"
        assert entry["category"] == "theoretical"
        assert entry["section"] == "研究方案"
        assert len(entry["theoretical_background"]) > 100
        assert len(entry["implementation_details"]) > 100
        assert len(entry["data_analysis"]) > 100
        assert len(entry["limitations"]) > 100
        assert entry["status"] == "generated"
        assert "TDDFT" in entry["related_methods"] or "SBE" in entry["related_methods"]
        print(f"  名称: {entry['name']}")
        print(f"  类别: {entry['category']}")
        print(f"  理论背景长度: {len(entry['theoretical_background'])} 字符")
        print(f"  相关方法: {entry['related_methods']}")
        print("  ✓ 单个条目字段完整")

        # ── [4/15] 方法扫描 ──
        print("\n[4/15] 方法扫描...")
        test_text = (
            "我们使用 TDDFT 和 SBE 进行模拟，"
            "并结合 ARPES 实验验证。"
            "数据采用神经网络回归分析。"
        )
        detected = manual.scan_methods(test_text)
        detected_keys = {d["method_key"] for d in detected}
        print(f"  检测到 {len(detected)} 种方法: {detected_keys}")
        assert "TDDFT" in detected_keys
        assert "SBE" in detected_keys
        assert "ARPES" in detected_keys
        assert "神经网络回归" in detected_keys
        # 空文本
        assert manual.scan_methods("") == []
        # 无方法文本
        assert manual.scan_methods("这是一段普通文字，没有方法。") == []
        print("  ✓ 方法扫描正确（含空文本降级）")

        # ── [5/15] 内置数据库覆盖 ──
        print("\n[5/15] 内置数据库覆盖...")
        assert len(BUILTIN_METHOD_DATABASE) >= 15, (
            f"内置库应至少 15 种方法，实际 {len(BUILTIN_METHOD_DATABASE)}"
        )
        required_categories = {
            "theoretical", "experimental", "computational", "analytical"
        }
        actual_categories = {
            info["category"] for info in BUILTIN_METHOD_DATABASE.values()
        }
        assert required_categories == actual_categories, (
            f"类别覆盖不完整: {actual_categories}"
        )
        # 每个方法应有完整字段
        for key, info in BUILTIN_METHOD_DATABASE.items():
            assert "name" in info, f"{key} 缺少 name"
            assert "name_en" in info, f"{key} 缺少 name_en"
            assert "category" in info, f"{key} 缺少 category"
            assert "keywords" in info and len(info["keywords"]) > 0, (
                f"{key} 缺少 keywords"
            )
            assert "theoretical_background" in info and len(info["theoretical_background"]) > 100, (
                f"{key} theoretical_background 过短"
            )
            assert "implementation_details" in info and len(info["implementation_details"]) > 100, (
                f"{key} implementation_details 过短"
            )
            assert "data_analysis" in info and len(info["data_analysis"]) > 100, (
                f"{key} data_analysis 过短"
            )
            assert "limitations" in info and len(info["limitations"]) > 100, (
                f"{key} limitations 过短"
            )
        print(f"  内置方法数: {len(BUILTIN_METHOD_DATABASE)}")
        print(f"  类别覆盖: {actual_categories}")
        # 验证具体方法存在
        expected_methods = [
            "TDDFT", "SBE", "Floquet理论", "Berry曲率计算",
            "量子度规计算", "Kubo公式", "非线性光学理论",
            "HHG模拟", "能带结构计算", "拓扑不变量计算",
            "HHG光谱", "偏振测量", "时间分辨泵浦-探测", "ARPES",
            "贝叶斯反演", "神经网络回归", "傅里叶分析",
        ]
        for m in expected_methods:
            assert m in BUILTIN_METHOD_DATABASE, f"缺少方法: {m}"
        print(f"  全部 {len(expected_methods)} 种必需方法均存在")
        print("  ✓ 内置数据库完整，字段齐全")

        # ── [6/15] 手册获取 ──
        print("\n[6/15] 手册获取...")
        loaded = manual.get_handbook()
        assert loaded is not None
        assert len(loaded["method_order"]) == method_count
        assert loaded["proposal_title"] == handbook["proposal_title"]
        # 获取不存在的手册
        empty_manual = MethodologyManual(tmp / "nonexistent_proposal")
        assert empty_manual.get_handbook() is None
        print(f"  已加载手册方法数: {len(loaded['method_order'])}")
        print("  ✓ 手册获取正确（含不存在降级）")

        # ── [7/15] 方法条目更新 ──
        print("\n[7/15] 方法条目更新...")
        updated = manual.update_method_entry(
            "含时密度泛函理论",
            {
                "status": "reviewed",
                "theoretical_background": (
                    "更新后的理论背景：TDDFT 是 DFT 的时间推广...\n"
                    "（用户审阅补充内容）"
                ),
            },
        )
        assert updated["status"] == "reviewed"
        assert "用户审阅补充内容" in updated["theoretical_background"]
        assert updated["updated_at"] >= updated["created_at"]
        # 验证持久化
        reloaded = manual.get_handbook()
        target = None
        for mid in reloaded["method_order"]:
            if reloaded["methods"][mid]["name"] == "含时密度泛函理论":
                target = reloaded["methods"][mid]
                break
        assert target is not None
        assert target["status"] == "reviewed"
        print(f"  更新后状态: {updated['status']}")
        print("  ✓ 条目更新 + 持久化正确")

        # ── [8/15] Markdown 导出 ──
        print("\n[8/15] Markdown 导出...")
        md = manual.export_handbook("markdown")
        assert "# 方法学手册" in md
        assert "量子度规" in md  # proposal_title
        assert "理论基础" in md
        assert "实现细节" in md
        assert "数据分析" in md
        assert "局限性" in md
        assert "知识库链接" in md
        assert "---" in md
        # Markdown 文件应已写入
        assert manual.markdown_path.exists()
        md_file_content = manual.markdown_path.read_text(encoding="utf-8")
        assert "# 方法学手册" in md_file_content
        print(f"  Markdown 长度: {len(md)} 字符")
        print(f"  Markdown 文件已写入: {manual.markdown_path.exists()}")
        print("  ✓ Markdown 结构完整")

        # ── [9/15] JSON 导出 ──
        print("\n[9/15] JSON 导出...")
        json_str = manual.export_handbook("json")
        parsed = json.loads(json_str)
        assert "methods" in parsed
        assert "method_order" in parsed
        assert len(parsed["method_order"]) == method_count
        assert "stats" in parsed
        print(f"  JSON 长度: {len(json_str)} 字符")
        print(f"  方法数: {len(parsed['method_order'])}")
        print("  ✓ JSON 格式正确，可正常解析")

        # ── [10/15] 手册统计 ──
        print("\n[10/15] 手册统计...")
        stats = manual.get_handbook_stats()
        assert stats["method_count"] == method_count
        assert stats["total_words"] > 0
        assert "category_distribution" in stats
        assert "status_distribution" in stats
        assert "theoretical" in stats["category_distribution"]
        # 至少有一个 reviewed（刚才更新的）
        assert stats["status_distribution"].get("reviewed", 0) >= 1
        print(f"  方法总数: {stats['method_count']}")
        print(f"  总字数: {stats['total_words']}")
        print(f"  类别分布: {stats['category_distribution']}")
        print(f"  状态分布: {stats['status_distribution']}")
        print(f"  KB 关联数: {stats['kb_linked_count']}")
        print("  ✓ 统计信息正确")

        # ── [11/15] 知识库集成 ──
        print("\n[11/15] 知识库集成...")
        # Mock kb_index
        class _MockKbIndex:
            def search(self, query, top_k=3):
                if "TDDFT" in query or "密度泛函" in query:
                    return {
                        "results": [
                            {"path": "wiki/methods/TDDFT.md", "title": "TDDFT",
                             "score": 0.95},
                        ],
                        "total": 1,
                    }
                return {"results": [], "total": 0}

        manual2 = MethodologyManual(tmp / "kb_test_proposal")
        manual2._kb_index = _MockKbIndex()
        entry_with_kb = manual2.generate_method_entry(
            "TDDFT", context={"section": "研究方案"}
        )
        assert len(entry_with_kb["kb_links"]) > 0, "应有 KB 链接"
        assert "wiki/methods/TDDFT.md" in entry_with_kb["kb_links"]
        print(f"  KB 链接: {entry_with_kb['kb_links']}")
        # 无 KB 匹配的方法
        entry_no_kb = manual2.generate_method_entry(
            "偏振测量", context={"section": "实验方案"}
        )
        assert entry_no_kb["kb_links"] == [], "偏振测量应无 KB 匹配"
        print("  ✓ KB 集成正确（含无匹配降级）")

        # ── [12/15] 空申请书处理 ──
        print("\n[12/15] 空申请书处理...")
        empty_sections: Dict[str, Any] = {}
        empty_handbook = manual.generate_handbook(empty_sections)
        assert empty_handbook["method_order"] == []
        assert empty_handbook["methods"] == {}
        assert empty_handbook["stats"]["method_count"] == 0
        print(f"  方法数: {empty_handbook['stats']['method_count']}")
        md_empty = manual.export_handbook("markdown")
        assert "# 方法学手册" in md_empty
        print("  ✓ 空申请书优雅降级")

        # ── [13/15] 原子写入 + 文件锁 ──
        print("\n[13/15] 原子写入 + 文件锁...")
        # 重新生成以确保文件存在
        handbook = manual.generate_handbook(mock_sections)
        # 验证文件是有效 JSON
        raw_content = manual.handbook_path.read_text(encoding="utf-8")
        parsed_again = json.loads(raw_content)
        assert parsed_again["stats"]["method_count"] > 0
        # 验证锁名唯一性
        manual_a = MethodologyManual(tmp / "proposal_A")
        manual_b = MethodologyManual(tmp / "proposal_B")
        assert manual_a._lock_name != manual_b._lock_name, (
            "不同 proposal 应有不同锁名"
        )
        print(f"  锁名 A: {manual_a._lock_name}")
        print(f"  锁名 B: {manual_b._lock_name}")
        # 多次写入不损坏
        handbook2 = manual.generate_handbook(mock_sections)
        raw2 = manual.handbook_path.read_text(encoding="utf-8")
        parsed2 = json.loads(raw2)
        assert parsed2["stats"]["method_count"] == handbook2["stats"]["method_count"]
        print("  ✓ 原子写入有效，锁按 proposal 隔离，多次写入不损坏")

        # ── [14/15] 引文集成 ──
        print("\n[14/15] 引文集成...")
        # Mock citation_manager
        class _MockCitationManager:
            def list_references(self):
                return [
                    {
                        "cite_key": "ref_001",
                        "cite_number": 1,
                        "title": "TDDFT for HHG in solids",
                        "authors": ["Zhang, Y.", "Li, X."],
                        "year": 2024,
                    },
                    {
                        "cite_key": "ref_002",
                        "cite_number": 2,
                        "title": "Berry curvature in topological materials",
                        "authors": ["Wang, J."],
                        "year": 2023,
                    },
                ]

        mock_cm = _MockCitationManager()
        entry_with_cite = manual.generate_method_entry(
            "TDDFT",
            context={
                "section": "立项依据",
                "citation_manager": mock_cm,
            },
        )
        # TDDFT 模板含 [1] 引文标记
        assert len(entry_with_cite["key_references"]) > 0, (
            "应关联到引文"
        )
        ref = entry_with_cite["key_references"][0]
        assert ref["cite_number"] == 1
        assert "TDDFT" in ref["annotation"] or "Zhang" in ref["annotation"]
        assert entry_with_cite["missing_references"] is False
        print(f"  关联引文数: {len(entry_with_cite['key_references'])}")
        print(f"  首条引文: {ref['annotation']}")
        # 无引文方法
        entry_no_cite = manual.generate_method_entry(
            "偏振测量",
            context={
                "section": "实验方案",
                "citation_manager": mock_cm,
            },
        )
        # 偏振测量模板不含 [N] 标记
        assert entry_no_cite["missing_references"] is True
        print("  ✓ 引文集成正确（含无引文标记）")

        # ── [15/15] 占位条目（非内置库方法） ──
        print("\n[15/15] 占位条目...")
        stub_entry = manual.generate_method_entry(
            "量子蒙特卡洛",
            context={"section": "研究方案"},
        )
        assert stub_entry["name"] == "量子蒙特卡洛"
        assert stub_entry["name_en"] == ""
        assert "待补充" in stub_entry["theoretical_background"]
        assert "待补充" in stub_entry["implementation_details"]
        assert "待补充" in stub_entry["data_analysis"]
        assert "待补充" in stub_entry["limitations"]
        assert stub_entry["status"] == "generated"
        print(f"  占位方法名: {stub_entry['name']}")
        print(f"  理论背景含待补充: {'待补充' in stub_entry['theoretical_background']}")
        print("  ✓ 非内置库方法生成占位条目")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("\n(已清理临时目录)")

    print("\n" + "=" * 50)
    print("✓ methodology_manual 自检全部通过（15/15）")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="方法学手册生成器")
    parser.add_argument(
        "--self-check", action="store_true", help="运行自检"
    )
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()