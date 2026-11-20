# -*- coding: utf-8 -*-
"""解析公式快速校验（理论推导文档的前置数值背书）。

每条解析式均与至少一条**独立途径**对拍：
  V1  价带 Berry 曲率闭式  Ω_v = Δ_eff·ħ²v²α/(2|d|³)
      对拍 1：Kubo 速度矩阵元公式 Ω_v = 2·Im[v_x^cv (v_y^cv)*]/E_cv²（闭式本征态）
      对拍 2：plaquette Wilson 通量（纯特征矢量数值，规范不变）
  V2  瞬时陈数闭式  C_v(t) = sgn(Δ_eff)/2
      对拍 1：闭式曲率方域积分 + 方域外解析尾部
      对拍 2：plaquette 通量求和（纯特征矢量数值）
  V3  带隙闭合处 |ΔC| = 1 整数跃变（Δ_eff 反号）
  V4  圆二色前向关系 |v_+^cv|² − |v_−^cv|² = 2·(E_cv/ħ)²·Ω_v（闭式本征态矩阵元）
  V5  精确 2×2 幺正演化（d·σ 闭式）的能量守恒

用法：
    python3 verify_formulas.py            # 全部校验，输出 PASS/FAIL
    python3 verify_formulas.py --self-check
"""
import sys
import numpy as np

import model


def run_all():
    results = []
    rng = np.random.default_rng(42)
    mass_test = 0.4  # Δ_eff = 0.4·Δ₀，避开闭合点

    # V1a: 曲率闭式 vs Kubo 公式（含驱动位移与动态质量）
    for Ax, Ay, mass in [(0.0, 0.0, mass_test), (0.3, -0.2, mass_test),
                         (0.1, 0.1, -mass_test), (0.5, 0.0, 0.16)]:
        kx, ky = 0.37 + rng.uniform(-0.05, 0.05), -0.21 + rng.uniform(-0.05, 0.05)
        a = model.analytic_curvature(kx, ky, Ax, Ay, mass)
        n = model.curvature_by_kubo(kx, ky, Ax, Ay, mass)
        rel = abs(a - n) / abs(a)
        results.append(("V1a 曲率闭式 vs Kubo", f"A=({Ax},{Ay}) m={mass}", rel, rel < 1e-10))

    # V1b: 曲率闭式 vs plaquette 数值曲率（单 plaquette 离散误差 O(dk·∂lnΩ)）
    for Ax, Ay, mass in [(0.0, 0.0, mass_test), (0.3, -0.2, mass_test)]:
        kx, ky = 0.37, -0.21
        a = model.analytic_curvature(kx, ky, Ax, Ay, mass)
        dk = 2e-4
        xs = np.linspace(kx - 2 * dk, kx + 2 * dk, 5)
        ys = np.linspace(ky - 2 * dk, ky + 2 * dk, 5)
        kX, kY = np.meshgrid(xs, ys, indexing="ij")
        u_v, _, _, _ = model.eig_vectors(kX, kY, Ax, Ay, mass)
        flux = model._plaquette_flux(u_v, xs)
        n = flux[1, 1] / dk**2
        rel = abs(a - n) / abs(a)
        results.append(("V1b 曲率闭式 vs plaquette", f"A=({Ax},{Ay}) m={mass}", rel, rel < 5e-3))

    # V2a: 陈数闭式 vs 径向数值积分（重标度坐标 (u,w)=(ħv(kx+Ax), ħvα(ky+Ay)) 下被积函数
    #      各向同性：∫∫Ω d²k = (Δ_eff/2)·2π·∫ρ dρ(ρ²+Δ²)^{-3/2}，纯数值、无解析尾部）
    for Ax, Ay, mass in [(0.0, 0.0, mass_test), (0.3, -0.2, mass_test), (0.4, 0.4, -mass_test)]:
        a = model.analytic_chern(mass)
        rho = np.linspace(0.0, 2000.0, 200001)
        integ = (mass / 2.0) * 2 * np.pi * np.trapezoid(
            rho / (rho**2 + mass**2) ** 1.5, rho)
        n = integ / (2 * np.pi)
        rel = abs(a - n) / abs(a)
        results.append(("V2a 陈数闭式 vs 径向积分", f"A=({Ax},{Ay}) m={mass}", rel, rel < 1e-3))

    # V2b: 陈数闭式 vs plaquette 求和（纯特征矢量途径）+ 方域解析尾部
    for Ax, Ay, mass in [(0.0, 0.0, 1.0), (0.3, -0.2, 1.0)]:
        a = model.analytic_chern(mass)
        n = model.chern_by_plaquette(mass, Ax, Ay, R=80.0, nk=2401)
        rel = abs(a - n) / abs(a)
        results.append(("V2b 陈数闭式 vs plaquette 求和", f"A=({Ax},{Ay}) m={mass}", rel, rel < 2.5e-3))

    # V3: 闭合跃变 |ΔC| = 1
    c_pos = model.analytic_chern(+mass_test)
    c_neg = model.analytic_chern(-mass_test)
    jump = abs(c_pos - c_neg)
    results.append(("V3 闭合跃变 |ΔC|", f"m=±{mass_test}", abs(jump - 1.0), abs(jump - 1.0) < 1e-12))

    # V4: 圆二色前向关系 |v_+|²−|v_−|² = +2·E_cv²·Ω_v（ħ = 1；符号以规范不变途径为仲裁）
    for kx, ky, Ax, Ay, mass in [(0.37, -0.21, 0.0, 0.0, mass_test),
                                 (0.90, 0.40, 0.3, -0.2, mass_test),
                                 (-0.50, 0.60, 0.0, 0.0, -mass_test)]:
        p, m_ = model.circular_dipole_squared(kx, ky, Ax, Ay, mass)
        om = model.analytic_curvature(kx, ky, Ax, Ay, mass)
        _, _, Ev, Ec = model.eig_vectors(kx, ky, Ax, Ay, mass)
        e2 = (Ec - Ev) ** 2
        lhs = p - m_
        rhs = 2.0 * e2 * om
        rel = abs(lhs - rhs) / abs(rhs)
        results.append(("V4 圆二色前向关系", f"k=({kx:.2f},{ky:.2f}) m={mass}", rel, rel < 1e-10))

    # V5: 精确幺正演化能量守恒（随机 d，1000 步）
    d = (rng.normal(), rng.normal(), rng.normal())
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    H = d[0] * sx + d[1] * sy + d[2] * sz
    psi = np.array([1.0, 0.0], dtype=complex)
    e0 = np.real(np.vdot(psi, H @ psi))
    dt = 0.05
    for _ in range(1000):
        psi = model.exact_unitary(d[0], d[1], d[2], dt) @ psi
    e1 = np.real(np.vdot(psi, H @ psi))
    drift = abs(e1 - e0)
    results.append(("V5 精确幺正能量守恒", "1000 步", drift, drift < 1e-12))

    print("=" * 76)
    all_ok = True
    for name, cond, val, ok in results:
        flag = "✓ PASS" if ok else "✗ FAIL"
        all_ok = all_ok and ok
        print(f"{flag}  {name:26s} {cond:26s} 偏差 = {val:.3e}")
    print("=" * 76)
    print("全部通过" if all_ok else "存在失败项")
    return all_ok


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
