# -*- coding: utf-8 -*-
"""L0 基准模型：有隙各向异性 Dirac 模型（α-T₃ 价带-导带两带有效投影）。

模型定义（无量纲单位，ħ = 1，能量单位取 Δ₀ = E_g/2）：

    H(k,t) = d(k,t)·σ ，  d = (ħv·(k_x + A_x(t)),  ħv·α·(k_y + A_y(t)),  Δ_eff(t))

其中：
  - 最小耦合项  k → k + A(t)  承载驱动场的带内（轨道）耦合，A(t) 由 E(t) 积分给出；
  - 动态质量项  Δ_eff(t) = Δ₀ + m(t)  承载驱动场的带间（偶极）耦合，即"强场拓扑
    能带重整"的 L0 代理：m(t) = ℏΩ_R(t) 为场致带隙重整能量；
  - α ∈ (0,1] 为各向异性参数（α-T₃ 模型第三腿耦合比，α→1 为各向同性极限）。

解析结果（均在 verify_formulas.py 中与特征矢量数值对拍）：
  - 价带 Berry 曲率闭式：  Ω_v(k,t) = +Δ_eff·ħ²v²α / (2|d|³)
  - 瞬时陈数闭式（单锥）：  C_v(t) = (1/2π)∫Ω_v d²k = sgn(Δ_eff)/2
    （双谷格点模型中加倍为整数 ±1；带隙闭合 Δ_eff = 0 处 |ΔC| = 1 整数跃变）
  - 圆二色前向关系：        |v_+^cv|² − |v_−^cv|² = +2·(E_cv/ħ)²·Ω_v

本模块同时提供：
  - d·σ 两能级体系的闭式本征态与闭式精确幺正演化子（TDSE 引擎，任意步长精确）；
  - 批量化（numpy 向量）实现，供主模拟 l0_simulation.py 调用。

自检：python3 model.py --self-check
"""
import numpy as np

# ---- 物理常数（Bi₂Se₃ 锚定的无量纲单位制） ----
HBAR_V = 4.0          # ħ·v_F，能量·长度单位（Bi₂Se₃ 表面态 v_F ≈ 4 eV·Å）
DELTA0 = 0.15         # Δ₀ = E_g/2 = 0.15 eV（Bi₂Se₃ 体带隙 E_g = 0.3 eV）


def d_vec(kx, ky, Ax=0.0, Ay=0.0, mass=DELTA0, hv=HBAR_V, alpha=None):
    """瞬态 d 矢量（批量化）。alpha=None 时取模块默认 ALPHA。"""
    a = _alpha(alpha)
    kx, ky = np.broadcast_arrays(np.asarray(kx, dtype=float), np.asarray(ky, dtype=float))
    dx = hv * (kx + Ax)
    dy = hv * a * (ky + Ay)
    dz = np.broadcast_to(np.asarray(mass, dtype=float), dx.shape).copy()
    return dx, dy, dz


def _alpha(alpha):
    return 0.8 if alpha is None else alpha


def hamiltonian(kx, ky, Ax=0.0, Ay=0.0, mass=DELTA0, hv=HBAR_V, alpha=None):
    """H(k,t) = d·σ，形状 k.shape + (2,2)，厄米。"""
    dx, dy, dz = d_vec(kx, ky, Ax, Ay, mass, hv, alpha)
    H = np.empty(dx.shape + (2, 2), dtype=complex)
    H[..., 0, 0] = dz
    H[..., 1, 1] = -dz
    H[..., 0, 1] = dx - 1j * dy
    H[..., 1, 0] = dx + 1j * dy
    return H


def eig_vectors(kx, ky, Ax=0.0, Ay=0.0, mass=DELTA0, hv=HBAR_V, alpha=None):
    """d·σ 闭式本征态（批量化）。

    返回 (u_v, u_c, E_v, E_c)：u_v/u_c 形状 k.shape+(2,)，E_v < E_c。
    简并点（|dz| = |d|，即带隙闭合）处闭式退化，调用方须先做带隙掩膜。
    """
    a = _alpha(alpha)
    dx, dy, dz = d_vec(kx, ky, Ax, Ay, mass, hv, alpha)
    dn = np.sqrt(dx**2 + dy**2 + dz**2)
    s = dz + dn                       # 共同归一化因子 √(2|d|(|d|+dz))
    n = np.sqrt(2.0 * dn * s)
    u_v = np.empty(dx.shape + (2,), dtype=complex)
    u_c = np.empty(dx.shape + (2,), dtype=complex)
    u_v[..., 0] = -(dx - 1j * dy) / n
    u_v[..., 1] = s / n
    u_c[..., 0] = s / n
    u_c[..., 1] = (dx + 1j * dy) / n
    E_v, E_c = -dn, dn
    return u_v, u_c, E_v, E_c


def analytic_curvature(kx, ky, Ax=0.0, Ay=0.0, mass=DELTA0, hv=HBAR_V, alpha=None):
    """价带 Berry 曲率闭式：Ω_v = +Δ_eff·ħ²v²α / (2|d|³)。"""
    a = _alpha(alpha)
    dx, dy, dz = d_vec(kx, ky, Ax, Ay, mass, hv, alpha)
    d3 = (dx**2 + dy**2 + dz**2) ** 1.5
    return mass * hv**2 * a / (2.0 * d3)


def analytic_chern(mass=DELTA0):
    """瞬时陈数闭式（单锥）：C_v(t) = sgn(Δ_eff)/2；Δ_eff = 0 时未定义。"""
    m = float(mass)
    if m == 0.0:
        raise ValueError("带隙闭合处瞬时陈数未定义（Δ_eff = 0）")
    return 0.5 * np.sign(m)


def chern_by_quadrature(mass=DELTA0, Ax=0.0, Ay=0.0, hv=HBAR_V, alpha=None, R=80.0, nk=1601):
    """闭式曲率在方域 [−R,R]² 上的数值积分 + 方域外解析尾部（严格可对拍）。

    尾部推导（k_y 方向反导数，q = u² + (ħvα)²(ky+Ay)² + Δ²，u² = (ħv(kx+Ax))² + Δ²）：
        ∫ q^{-3/2} dky = [(ky+Ay)/√q] / u²，其在 ky→±∞ 的极限为 ±1/(ħvα)
    两条半无限条带求和后极限常数项相消为 2/(ħvα)，得每条 kx 线的尾部：
        T_ky(kx) = coef·[2/(ħvα) − b_R + b_{−R}] / u²
        b_R = (R+Ay)/√((ħvα(R+Ay))²+u²)，b_{−R} = (−R+Ay)/√((ħvα(Ay−R))²+u²)
    k_x 方向条带同型（ħv ↔ ħvα 角色互换）。
    """
    a = _alpha(alpha)
    xs = np.linspace(-R, R, nk)
    kx, ky = np.meshgrid(xs, xs, indexing="ij")
    om = analytic_curvature(kx, ky, Ax, Ay, mass, hv, alpha)
    core = np.trapezoid(np.trapezoid(om, xs, axis=1), xs)
    tail = _tail_square(mass, Ax, Ay, hv, a, R, nk)
    return (core + tail) / (2 * np.pi)


def chern_by_plaquette(mass=DELTA0, Ax=0.0, Ay=0.0, hv=HBAR_V, alpha=None, R=60.0, nk=801):
    """纯特征矢量途径的陈数：闭式本征态的 plaquette 通量求和 + 解析尾部。

    完全不使用 Ω 闭式，作为闭式陈数的独立对拍。
    """
    a = _alpha(alpha)
    xs = np.linspace(-R, R, nk)
    kx, ky = np.meshgrid(xs, xs, indexing="ij")
    # 每个格心（格点平均）的 plaquette 通量
    kc = 0.5 * (xs[:-1] + xs[1:])
    kxc, kyc = np.meshgrid(kc, kc, indexing="ij")
    u_v, _, _, _ = eig_vectors(kx, ky, Ax, Ay, mass, hv, alpha)
    flux = _plaquette_flux(u_v, xs)
    core = np.sum(flux)  # 每个 plaquette 通量已含 dk² 面积（弧度量），求和即 ∫Ω d²k
    tail = _tail_square(mass, Ax, Ay, hv, a, R, nk)
    return (core + tail) / (2 * np.pi)


def _plaquette_flux(u, xs):
    """给定格点上的本征态场 u（shape nk×nk×2），返回每个格心的 plaquette 通量。"""
    # 相邻格点态的重叠（规范不变 Wilson 回路：∏ ⟨u_i|u_{i+1}⟩）
    o_x = np.sum(np.conj(u[:-1, :, :]) * u[1:, :, :], axis=-1)   # 向 +x
    o_xb = np.sum(np.conj(u[1:, :, :]) * u[:-1, :, :], axis=-1)  # 向 −x
    o_y = np.sum(np.conj(u[:, :-1, :]) * u[:, 1:, :], axis=-1)
    o_yb = np.sum(np.conj(u[:, 1:, :]) * u[:, :-1, :], axis=-1)
    # 每个格心回路 A(i,j)→B(i+1,j)→C(i+1,j+1)→D(i,j+1)→A（回路闭合使规范相位抵消）
    link = np.angle(o_x[:, :-1]) + np.angle(o_y[1:, :]) \
        + np.angle(o_xb[:, 1:]) + np.angle(o_yb[:-1, :])
    return -link  # 价带符号约定（与闭式 Ω_v 的正负号一致，由 verify V1 对拍确认）


def _tail_square(mass, Ax, Ay, hv, a, R, nk):
    """方域外解析尾部（推导见 chern_by_quadrature docstring）。"""
    xs = np.linspace(-R, R, nk)
    coef = mass * hv**2 * a / 2.0
    # 上下条带：|ky| > R，kx ∈ [−R,R]
    u2 = (hv * (xs + Ax)) ** 2 + mass**2
    b_p = (R + Ay) / np.sqrt((hv * a * (R + Ay)) ** 2 + u2)
    b_m = (-R + Ay) / np.sqrt((hv * a * (Ay - R)) ** 2 + u2)
    vals_ky = coef * (2.0 / (hv * a) - b_p + b_m) / u2
    # 左右条带：|kx| > R，ky ∈ [−R,R]
    u2y = (hv * a * (xs + Ay)) ** 2 + mass**2
    c_p = (R + Ax) / np.sqrt((hv * (R + Ax)) ** 2 + u2y)
    c_m = (-R + Ax) / np.sqrt((hv * (Ax - R)) ** 2 + u2y)
    vals_kx = coef * (2.0 / hv - c_p + c_m) / u2y
    return np.trapezoid(vals_ky, xs) + np.trapezoid(vals_kx, xs)


def curvature_by_kubo(kx, ky, Ax=0.0, Ay=0.0, mass=DELTA0, hv=HBAR_V, alpha=None):
    """Kubo 公式独立途径：Ω_v = +2·Im[v_x^cv (v_y^cv)*] / E_cv²（ħ = 1）。

    符号约定以规范不变 plaquette 通量（A = i⟨u|∇u⟩，Ω = ∇×A）为仲裁，
    已由 verify_formulas.py V1a/V1b 对拍确认。
    """
    a = _alpha(alpha)
    _, _, E_v, E_c = eig_vectors(kx, ky, Ax, Ay, mass, hv, alpha)
    vx_cv, vy_cv = velocity_matrix_elements(kx, ky, Ax, Ay, mass, hv, alpha)
    E_cv = E_c - E_v
    return 2.0 * np.imag(vx_cv * np.conj(vy_cv)) / E_cv**2


def velocity_matrix_elements(kx, ky, Ax=0.0, Ay=0.0, mass=DELTA0, hv=HBAR_V, alpha=None):
    """带间速度矩阵元 v_x^cv = ⟨u_c|∂H/∂k_x|u_v⟩，v_y 同理（闭式本征态，批量化）。

    约定：σ_y 矩阵元为 ⟨u_c|σ_y|u_v⟩ = i·(⟨u_c| 的第二分量 × u_v 第一分量
    − 第一分量 × u_v 第二分量），与 σ_y = [[0,−i],[i,0]] 的标准定义一致。
    """
    a = _alpha(alpha)
    u_v, u_c, _, _ = eig_vectors(kx, ky, Ax, Ay, mass, hv, alpha)
    uv0, uv1 = u_v[..., 0], u_v[..., 1]
    uc0, uc1 = u_c[..., 0], u_c[..., 1]
    sx_cv = np.conj(uc0) * uv1 + np.conj(uc1) * uv0
    sy_cv = 1j * (np.conj(uc1) * uv0 - np.conj(uc0) * uv1)
    return hv * sx_cv, hv * a * sy_cv


def circular_dipole_squared(kx, ky, Ax=0.0, Ay=0.0, mass=DELTA0, hv=HBAR_V, alpha=None):
    """|v_±^cv|²（螺旋度 ± 的带间圆偏振偶极平方），批量化。"""
    vx, vy = velocity_matrix_elements(kx, ky, Ax, Ay, mass, hv, alpha)
    return np.abs(vx + 1j * vy) ** 2, np.abs(vx - 1j * vy) ** 2


def exact_unitary(dx, dy, dz, dt):
    """H = d·σ 的精确演化子 U = cos(|d|dt)·I − i·sin(|d|dt)/|d|·(d·σ)（闭式，批量化）。"""
    dx, dy, dz = np.broadcast_arrays(np.asarray(dx, dtype=float),
                                     np.asarray(dy, dtype=float),
                                     np.asarray(dz, dtype=float))
    dn = np.sqrt(dx**2 + dy**2 + dz**2)
    c = np.cos(dn * dt)
    s = np.sin(dn * dt) / dn
    U = np.empty(dx.shape + (2, 2), dtype=complex)
    U[..., 0, 0] = c - 1j * s * dz
    U[..., 1, 1] = c + 1j * s * dz
    U[..., 0, 1] = -1j * s * (dx - 1j * dy)
    U[..., 1, 0] = -1j * s * (dx + 1j * dy)
    return U


def pulse_E(t, t0, sigma, omega, E0, cep):
    """高斯包络线偏振驱动场 E(t) = E0·exp(−(t−t0)²/(2σ²))·cos(ω(t−t0)+CEP)。"""
    return E0 * np.exp(-((t - t0) ** 2) / (2 * sigma**2)) * np.cos(omega * (t - t0) + cep)


def self_check():
    """模块级自检：闭式本征态满足本征方程与正交归一。"""
    rng = np.random.default_rng(7)
    kx, ky = rng.uniform(-2, 2, 200), rng.uniform(-2, 2, 200)
    mass = 0.4
    u_v, u_c, E_v, E_c = eig_vectors(kx, ky, mass=mass)
    H = hamiltonian(kx, ky, mass=mass)
    res_v = np.max(np.abs(np.einsum("...ij,...j->...i", H, u_v) - E_v[..., None] * u_v))
    res_c = np.max(np.abs(np.einsum("...ij,...j->...i", H, u_c) - E_c[..., None] * u_c))
    orth = np.max(np.abs(np.sum(np.conj(u_v) * u_c, axis=-1)))
    norm = max(np.max(np.abs(np.sum(np.conj(u_v) * u_v, axis=-1) - 1)),
               np.max(np.abs(np.sum(np.conj(u_c) * u_c, axis=-1) - 1)))
    ok = res_v < 1e-10 and res_c < 1e-10 and orth < 1e-10 and norm < 1e-10
    print(f"✓ 本征方程残差 v: {res_v:.2e}  c: {res_c:.2e}  正交: {orth:.2e}  归一: {norm:.2e}")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(self_check())
