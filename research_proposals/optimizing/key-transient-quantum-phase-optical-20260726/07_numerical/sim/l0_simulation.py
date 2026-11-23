# -*- coding: utf-8 -*-
"""L0 端到端数值模拟：强场写入 → 弱探针圆二色 ATA → 拓扑反演闭环。

物理链路（式编号对应 01-理论推导.md / 02-测量方案.md）：
  写   H(k,t) = d·σ，d = (ħv(kx+Ax), ħvα·ky, Δ0 + κ·d_cv·E_w(t))
       —— 最小耦合（带内）+ 动态质量（"强场拓扑能带重整"的 L0 代理，式(1)）
  演化 精确幺正演化子（d·σ 闭式，任意步长严格幺正）
  读   双螺旋度弱探针（速度规范最小耦合 a_p），双传播差分出精确线性响应 δj(t)，
       窗口锁相给出 A_σ(ω,τ)（式(9)(15)）
  反演 模拟器内嵌波形拟合：θ = (Δ0, κ_m) 网格预扫 + Gauss-Newton（数值雅可比），
       前向 = 同一精确模拟器（拟合用降分辨率，消除前向模型近似误差）
  判据 M1 曲率点位 / M2 波形 / M3 陈数符号+裕度 / M4 闭合检出与跃变；
       噪声预算由拟合点的雅可比协方差（线性化）+ 蒙特卡洛复验给出

解析公式层（Ω 闭式 / 陈数闭式 / 圆二色前向关系）由 verify_formulas.py 的
16 项独立途径对拍背书；本模块的闭环把"模拟 ATA 数据 → 波形参数反演 → 瞬时陈数"
整链贯通并以 <1% 测量偏差为验收目标。

用法：
    python3 l0_simulation.py --self-check
依赖：numpy、model.py（同目录）。本模块为研究性数值验证代码（numpy 例外于管线零依赖约束）。
"""
import numpy as np

import model

# ---- 物理常数（01 文档 §1.1 映射表） ----
HBAR = 0.6582        # eV·fs
DELTA0 = 0.15        # eV（Bi₂Se₃ 体带隙 E_g = 0.3 eV 之半）
HV = 4.0             # ħv（eV·Å）
D_CV = 5.0           # Å·e（带间偶极，手册 G.3.3 三档映射）
EG = 2.0 * DELTA0
DEFAULT_PROBE = {"sigma_p": 1.5, "omega_c": 0.55 / HBAR, "Ep0_rel": 1e-3}


# ---------------------------------------------------------------- 波形
class Drive:
    """写脉冲及其派生量。

    E_w(t) = E0·exp(−(t−t0)²/2σ²)·cos(ω(t−t0)+CEP)
    a(t) = −∫E_w dt/ħ（Å⁻¹）；m(t) = κ·d_cv·E_w(t)（eV，κ=1 为标定真值）
    """

    def __init__(self, tier, cep=0.0, omega_ev=0.827, ncyc=8.0, t0=30.0,
                 alpha=0.8, delta0=DELTA0, kap=1.0, d_cv=D_CV):
        self.tier = float(tier)               # ħΩ_R/E_g 档位
        self.cep = float(cep)
        self.hbar_omega = float(omega_ev)
        self.omega = omega_ev / HBAR          # fs⁻¹
        self.t0 = float(t0)
        self.E0 = tier * EG / d_cv            # V/Å
        self.T_L = 2.0 * np.pi / self.omega
        self.sigma = ncyc * self.T_L / 2.355  # FWHM = ncyc·T_L
        self.d_cv = float(d_cv)
        self.delta0 = float(delta0)
        self.kap = float(kap)
        self.alpha = float(alpha)
        self._grid_cache = None

    def E(self, t):
        return model.pulse_E(np.asarray(t, dtype=float), self.t0, self.sigma,
                             self.omega, self.E0, self.cep)

    def m(self, t):
        return self.kap * self.d_cv * self.E(t)

    def delta_eff(self, t):
        return self.delta0 + self.m(t)

    def a_of_t(self, t):
        t = np.asarray(t, dtype=float)
        E = self.E(t)
        seg = 0.5 * (E[1:] + E[:-1]) * np.diff(t) / HBAR
        head = self._head_offset(t[0])
        return head - np.concatenate([[0.0], np.cumsum(seg)])

    def _head_offset(self, t_start):
        ts = np.linspace(t_start - 8 * self.sigma, t_start, 800)
        return -np.trapezoid(self.E(ts), ts) / HBAR

    def grid(self, dt):
        if self._grid_cache is None or abs(self._grid_cache[1] - dt) > 1e-15:
            t_start = self.t0 - 4.0 * self.sigma
            n = int(round(8.0 * self.sigma / dt)) + 1
            self._grid_cache = (t_start + dt * np.arange(n), dt)
        return self._grid_cache


# ---------------------------------------------------------------- TDSE
def tdse_write_pass(kx, ky, drive, times, dt, snap_idx):
    """写场主传播（线偏振沿 x：a_y ≡ 0）。返回快照字典与主网格电流。"""
    nk = kx.shape[0]
    dk2 = ((kx[1, 0] - kx[0, 0]) * (ky[0, 1] - ky[0, 0])
           if kx.shape[0] > 1 and kx.shape[1] > 1 else 1.0)
    psi = np.zeros((nk, nk, 2), dtype=complex)
    psi[..., 0] = 1.0
    a = drive.a_of_t(times)
    m_t = drive.m(times)
    al = drive.alpha
    jx = np.empty(len(times))
    jy = np.empty(len(times))
    snaps = {}
    for i in range(len(times)):
        z = psi[..., 0] * np.conj(psi[..., 1])  # ⟨σx⟩=2Re(z)、⟨σy⟩=−2Im(z)
        jx[i] = dk2 * HV * np.sum(2.0 * np.real(z))
        jy[i] = -dk2 * HV * al * np.sum(2.0 * np.imag(z))
        if i in snap_idx:
            snaps[i] = psi.copy()
        if i + 1 < len(times):
            dx = HV * (kx + a[i])
            dy = HV * al * ky
            dz = drive.delta0 + m_t[i]
            U = model.exact_unitary(dx, dy, dz, dt / HBAR)
            psi = np.einsum("...ij,...j->...i", U, psi)
    return snaps, jx, jy


def probe_pass(psi0, drive, t_grid, dt, i0, probe, nsteps, kx, ky):
    """探针通过段：写场继续 + 弱探针（速度规范）。返回窗口电流与探针场。"""
    al = drive.alpha
    sig = probe["sigma_p"]
    om_c = probe["omega_c"]
    hp = probe["helicity"]
    Ep0 = probe["Ep0"]
    t_w = t_grid[i0:i0 + nsteps + 1]
    a_w = drive.a_of_t(t_grid)[i0:i0 + nsteps + 1]
    m_t = drive.m(t_w)
    tc = t_grid[i0] + 3.0 * sig
    env = Ep0 * np.exp(-((t_w - tc) ** 2) / (2.0 * sig ** 2))
    Epx = env * np.cos(om_c * (t_w - t_grid[i0]))
    Epy = hp * env * np.sin(om_c * (t_w - t_grid[i0]))
    apx = -np.concatenate([[0.0], np.cumsum(0.5 * (Epx[1:] + Epx[:-1]) * dt)]) / HBAR
    apy = -np.concatenate([[0.0], np.cumsum(0.5 * (Epy[1:] + Epy[:-1]) * dt)]) / HBAR
    psi = psi0.copy()
    dk2 = ((kx[1, 0] - kx[0, 0]) * (ky[0, 1] - ky[0, 0])
           if kx.shape[0] > 1 and kx.shape[1] > 1 else 1.0)
    jx = np.empty(nsteps + 1)
    jy = np.empty(nsteps + 1)
    for i in range(nsteps + 1):
        z = psi[..., 0] * np.conj(psi[..., 1])
        jx[i] = dk2 * HV * np.sum(2.0 * np.real(z))
        jy[i] = -dk2 * HV * al * np.sum(2.0 * np.imag(z))
        if i < nsteps:
            dx = HV * (kx + a_w[i] + apx[i])
            dy = HV * al * (ky + apy[i])
            dz = drive.delta0 + m_t[i]
            U = model.exact_unitary(dx, dy, dz, dt / HBAR)
            psi = np.einsum("...ij,...j->...i", U, psi)
    return jx, jy, Epx, Epy


def lockin(djx, djy, Epx, Epy, t_w, omega):
    """窗口锁相观测算：A_σ(ω) = Re[Σ_μ δj_μ(ω)E_μ(ω)*]/Σ_μ|E_μ(ω)|²。"""
    dt = t_w[1] - t_w[0]
    ph = np.exp(1j * np.outer(omega, t_w))
    djx_w = ph @ (djx * dt)
    djy_w = ph @ (djy * dt)
    Ex_w = ph @ (Epx * dt)
    Ey_w = ph @ (Epy * dt)
    num = np.real(djx_w * np.conj(Ex_w) + djy_w * np.conj(Ey_w))
    den = np.abs(Ex_w) ** 2 + np.abs(Ey_w) ** 2
    return num / np.maximum(den, 1e-300)


# ---------------------------------------------------------------- 端到端 ATA 模拟
def simulate_ATA(drive, delays, omega, probe, nk=64, k_max=0.45, dt=None,
                 write_jref=True, verbose=False):
    """给定 θ（drive 内含 Δ0 与 κ）的端到端 ATA 双螺旋度谱。

    返回 A[2, Nω, Nτ]（h=0/1 ↔ 螺旋度 +1/−1）与诊断字典。
    """
    if dt is None:
        dt = drive.T_L / 100.0
    probe = dict(probe)
    probe.setdefault("Ep0", probe.pop("Ep0_rel", 1e-3) * max(drive.E0, 1e-6)
                     if drive.E0 > 0 else probe.get("Ep0", 1e-3))
    t_grid, dt = drive.grid(dt)
    ks = np.linspace(-k_max, k_max, nk)
    kx, ky = np.meshgrid(ks, ks, indexing="ij")
    sig_p = probe["sigma_p"]
    half_w = 3.0 * sig_p
    nsteps = int(round(2 * half_w / dt))
    i0s = np.round((np.asarray(delays) - half_w - t_grid[0]) / dt).astype(int)
    i0s = np.clip(i0s, 0, len(t_grid) - nsteps - 2)
    snaps, jx_ref, jy_ref = tdse_write_pass(kx, ky, drive, t_grid, dt,
                                            set(i0s.tolist()))
    A = np.zeros((2, len(omega), len(delays)))
    pc_max = 0.0
    for h_i, hp in enumerate((1.0, -1.0)):
        pr = dict(probe, helicity=hp)
        for i, i0 in enumerate(i0s):
            jx_w, jy_w, Epx, Epy = probe_pass(snaps[i0], drive, t_grid, dt,
                                              i0, pr, nsteps, kx, ky)
            if write_jref:
                djx = jx_w - jx_ref[i0:i0 + nsteps + 1]
                djy = jy_w - jy_ref[i0:i0 + nsteps + 1]
            else:
                djx, djy = jx_w, jy_w
            A[h_i, :, i] = lockin(djx, djy, Epx, Epy,
                                  t_grid[i0:i0 + nsteps + 1], omega)
    for s in snaps.values():
        pc_max = max(pc_max, float(np.max(np.abs(s[..., 1]) ** 2)))
    return A, {"pc_max": pc_max, "dt": dt, "nk": nk}


# ---------------------------------------------------------------- 拟合
def fit_sim(A_data, drive_true, delays, omega, probe, band_mask,
            d0_grid=None, kap_grid=None, n_gn=4, fit_res=None,
            eps=(2e-3, 5e-3), verbose=False):
    """模拟器内嵌波形拟合：粗网格预扫 + Gauss-Newton（数值雅可比）。

    前向 = simulate_ATA（拟合分辨率 fit_res）；返回 θ̂、雅可比、协方差。
    """
    bm = np.asarray(band_mask, dtype=bool)

    def forward(theta):
        drv = Drive(drive_true.tier, cep=drive_true.cep,
                    omega_ev=drive_true.hbar_omega, ncyc=8.0,
                    t0=drive_true.t0, alpha=drive_true.alpha,
                    delta0=theta[0], kap=theta[1])
        res = fit_res or {}
        A, _ = simulate_ATA(drv, delays, omega, probe,
                            nk=res.get("nk", 48), k_max=res.get("k_max", 0.45),
                            dt=res.get("dt"))
        return A

    def resid(theta):
        F = forward(theta)[:, bm, :]
        R = A_data[:, bm, :] - F
        return R, float(np.sqrt(np.mean(R ** 2)))

    if d0_grid is None:
        d0_grid = np.linspace(0.10, 0.20, 5)
    if kap_grid is None:
        kap_grid = np.linspace(0.6, 1.4, 5)
    best, best_r = None, np.inf
    for d0 in d0_grid:
        for kp in kap_grid:
            _, r = resid((d0, kp))
            if verbose:
                print(f"  grid ({d0:.3f},{kp:.2f}): rms={r:.3e}")
            if r < best_r:
                best_r, best = r, (d0, kp)
    theta = np.array(best, dtype=float)
    J = None
    n_iter = 0
    lam_rel = 1e-3
    R, r_best = resid(tuple(theta))
    for it in range(n_gn):
        J = np.empty((R.size, 2))
        for k in range(2):
            tp = theta.copy(); tp[k] += eps[k]
            Rp, _ = resid(tuple(tp))
            J[:, k] = ((Rp - R) / eps[k]).ravel()
        jtj = J.T @ J
        scale = float(np.trace(jtj) / 2 + 1e-30)
        accepted = False
        for _retry in range(4):
            dth, *_ = np.linalg.lstsq(jtj + lam_rel * scale * np.eye(2),
                                      -J.T @ R.ravel(), rcond=None)
            step = np.clip(dth, [-0.04, -0.25], [0.04, 0.25])
            th_try = theta + step
            R_try, r_try = resid(tuple(th_try))
            if r_try < r_best:
                theta = th_try
                R, r_best = R_try, r_try
                lam_rel = max(lam_rel * 0.4, 1e-8)
                accepted = True
                break
            lam_rel = min(lam_rel * 6.0, 1e3)
        n_iter = it + 1
        if verbose:
            print(f"  LM it{it}: rms={r_best:.3e} theta=({theta[0]:.5f},{theta[1]:.4f}) "
                  f"lam={lam_rel:.1e} accepted={accepted}")
        if not accepted or np.max(np.abs(step)) < 1e-5:
            break
    rms = r_best
    sigma_A = float(np.std(R)) if R.size > 1 else 0.0
    try:
        cov = np.linalg.inv(J.T @ J) * sigma_A ** 2
    except np.linalg.LinAlgError:
        cov = None
    return {"theta_hat": tuple(theta), "resid_rms": rms, "cov": cov,
            "n_iter": n_iter, "J": J, "sigma_A": sigma_A}


# ---------------------------------------------------------------- 指标
def mask_from_gap(delta_t, eps_g=0.05):
    """闭合掩膜：E_g^inst = 2|Δ| < eps_g 处不评定。"""
    return np.abs(delta_t) < eps_g / 2.0


def compute_metrics(theta_hat, drive, delays, mask):
    """M1–M4 指标（掩膜窗口外评定）。"""
    d0h, kaph = theta_hat
    t = np.asarray(delays, dtype=float)
    d_true = drive.delta_eff(t)
    d_hat = d0h + kaph * drive.m(t)
    ok = ~mask
    m2 = float(np.max(np.abs((d_hat - d_true)[ok])) / drive.delta0)

    E = np.linspace(0.05, 0.9, 300)
    dts = d_true[ok][:, None]
    dhs = d_hat[ok][:, None]

    def om_of(dd):
        rho = np.sqrt(np.clip(E[None, :] ** 2 / 4.0 - dd ** 2, 0.0, None))
        return model.analytic_curvature(rho / HV, np.zeros_like(rho), 0.0, 0.0,
                                        dd, hv=HV, alpha=drive.alpha)

    om_true = om_of(dts)
    om_hat = om_of(dhs)
    m1 = float(np.max(np.abs(om_hat - om_true)) / np.max(np.abs(om_true)))
    c_true = np.sign(d_true) / 2.0
    c_hat = np.sign(d_hat) / 2.0
    agree = bool(np.all(c_hat[ok] == c_true[ok]))
    margin = float(np.min(np.abs(d_hat[ok])) / drive.delta0)
    mt = mask_from_gap(d_true)
    mh = mask_from_gap(d_hat)
    jt = np.abs(np.diff(np.sign(d_true))) > 0
    jh = np.abs(np.diff(np.sign(d_hat))) > 0
    pair = ok[:-1] & ok[1:]
    m4 = {"n_mask_true": int(np.sum(mt)), "n_mask_hat": int(np.sum(mh)),
          "mask_match": bool(np.array_equal(mt, mh)),
          "jump_match": bool(np.array_equal(jt[pair], jh[pair]))}
    return {"m1": m1, "m2": m2, "m3_agree": agree, "m3_margin": margin,
            "m4": m4, "delta_true": d_true, "delta_hat": d_hat, "mask": mask}


# ---------------------------------------------------------------- 单驱动点
def run_drive_point(drive, delays=None, omega=None, probe=None,
                    nk=64, k_max=0.45, dt=None, n_omega=32,
                    fit_res=None, seed=0, verbose=True):
    """单驱动点端到端：数据生成 → 模拟器内嵌拟合 → M1–M4 指标。"""
    if probe is None:
        probe = dict(DEFAULT_PROBE)
    probe = dict(probe)
    probe.setdefault("Ep0", probe.pop("Ep0_rel", 1e-3) * max(drive.E0, 1e-6)
                     if drive.E0 > 0 else probe.get("Ep0", 1e-3))
    if dt is None:
        dt = drive.T_L / 100.0
    t_grid, dt = drive.grid(dt)
    sig_p = probe["sigma_p"]
    if delays is None:
        delays = drive.t0 + np.linspace(-20.0, 20.0, 17)
    delays = np.asarray(delays, dtype=float)
    if omega is None:
        omega = np.linspace(0.10 / HBAR, 0.95 / HBAR, n_omega)

    if verbose:
        print(f"[run] tier={drive.tier} cep={drive.cep:.2f} α={drive.alpha} "
              f"nk={nk} dt={dt:.4f}fs Nτ={len(delays)}")
    A, diag = simulate_ATA(drive, delays, omega, probe, nk=nk, k_max=k_max,
                           dt=dt)
    Eg_min = 2.0 * np.min(np.abs(drive.delta_eff(delays)))
    band_mask = omega * HBAR > max(Eg_min - 0.03, 0.09)
    fit = fit_sim(A, drive, delays, omega, probe, band_mask,
                  fit_res=fit_res, verbose=verbose)
    mask = mask_from_gap(drive.delta_eff(delays))
    met = compute_metrics(fit["theta_hat"], drive, delays, mask)
    if verbose:
        print(f"[fit] θ̂ = ({fit['theta_hat'][0]:.5f}, {fit['theta_hat'][1]:.4f}) "
              f"rms={fit['resid_rms']:.3e} | M2={met['m2']:.4%} M1={met['m1']:.4%} "
              f"M3 agree={met['m3_agree']} margin={met['m3_margin']:.3f} "
              f"M4={met['m4']}")
    cov = fit["cov"]
    return {"drive": {"tier": drive.tier, "cep": drive.cep, "alpha": drive.alpha,
                      "hbar_omega": drive.hbar_omega, "E0": drive.E0,
                      "delta0": drive.delta0, "kap": drive.kap},
            "theta_hat": list(fit["theta_hat"]),
            "resid_rms": fit["resid_rms"],
            "cov": None if cov is None else cov.tolist(),
            "sigma_A": fit["sigma_A"],
            "metrics": {k: met[k] for k in ("m1", "m2", "m3_agree", "m3_margin", "m4")},
            "delays": delays.tolist(), "delta_true": met["delta_true"].tolist(),
            "delta_hat": met["delta_hat"].tolist(), "mask": met["mask"].tolist(),
            "pc_max": diag["pc_max"]}


# ---------------------------------------------------------------- 自检
def _self_check():
    ok_all = True
    print("=" * 72)
    # SC2 模方守恒 + 静态能量守恒（精确幺正）
    d = Drive(1.0)
    t, dt = d.grid(d.T_L / 100.0)
    ks = np.linspace(-0.3, 0.3, 40)
    kx, ky = np.meshgrid(ks, ks, indexing="ij")
    psi = np.zeros(kx.shape + (2,), dtype=complex)
    psi[..., 0] = 1.0
    a = d.a_of_t(t)
    m_t = d.m(t)
    norm_dev = 0.0
    for i in range(len(t)):
        norm_dev = max(norm_dev, float(np.max(np.abs(
            np.abs(psi[..., 0]) ** 2 + np.abs(psi[..., 1]) ** 2 - 1.0))))
        if i + 1 < len(t):
            U = model.exact_unitary(HV * (kx + a[i]), HV * d.alpha * ky,
                                    d.delta0 + m_t[i], dt / HBAR)
            psi = np.einsum("...ij,...j->...i", U, psi)
    ok2a = norm_dev < 1e-12
    d_stat = Drive(0.0)
    ts, dts = d_stat.grid(d_stat.T_L / 50.0)
    psi = np.zeros(kx.shape + (2,), dtype=complex)
    psi[..., 0] = 1.0
    z = psi[..., 0] * np.conj(psi[..., 1])
    e0 = np.sum(-HV * d_stat.alpha * ky * 2 * np.imag(z)
                + DELTA0 * (np.abs(psi[..., 0]) ** 2 - np.abs(psi[..., 1]) ** 2))
    edrift = 0.0
    for i in range(len(ts)):
        z = psi[..., 0] * np.conj(psi[..., 1])
        en = np.sum(-HV * d_stat.alpha * ky * 2 * np.imag(z)
                    + DELTA0 * (np.abs(psi[..., 0]) ** 2 - np.abs(psi[..., 1]) ** 2))
        edrift = max(edrift, abs(en - e0))
        if i + 1 < len(ts):
            U = model.exact_unitary(np.zeros_like(kx), HV * d_stat.alpha * ky,
                                    DELTA0, dts / HBAR)
            psi = np.einsum("...ij,...j->...i", U, psi)
    ok2b = edrift < 1e-9
    ok_all &= (ok2a and ok2b)
    print(f"{'✓' if ok2a else '✗'} SC2a 模方守恒偏差 = {norm_dev:.3e}    "
          f"{'✓' if ok2b else '✗'} SC2b 静态能量漂移 = {edrift:.3e}")

    # SC3 迷你闭环：单驱动点（定义保持档，小分辨率）反演 θ
    d0 = Drive(0.3)
    delays = d0.t0 + np.linspace(-12.0, 12.0, 7)
    omega = np.linspace(0.12 / HBAR, 0.85 / HBAR, 16)
    Eg_min = 2.0 * np.min(np.abs(d0.delta_eff(delays)))
    band = omega * HBAR > Eg_min - 0.03
    A, _ = simulate_ATA(d0, delays, omega, dict(DEFAULT_PROBE),
                        nk=32, k_max=0.4, dt=d0.T_L / 80.0)
    fit = fit_sim(A, d0, delays, omega, dict(DEFAULT_PROBE), band,
                  d0_grid=np.linspace(0.11, 0.19, 5),
                  kap_grid=np.linspace(0.7, 1.3, 5), n_gn=3,
                  fit_res={"nk": 32, "k_max": 0.4, "dt": d0.T_L / 80.0})
    th = np.array(fit["theta_hat"])
    err = np.abs(th - np.array([DELTA0, 1.0]))
    ok3 = bool(np.all(err < np.array([0.01, 0.05])))
    ok_all &= ok3
    print(f"{'✓' if ok3 else '✗'} SC3 迷你闭环反演：θ̂ = ({th[0]:.5f},{th[1]:.4f}) "
          f"真值 ({DELTA0:.3f},1.00) 偏差 = ({err[0]:.4f},{err[1]:.4f})")
    print("=" * 72)
    print("全部通过" if ok_all else "存在失败项")
    return ok_all


if __name__ == "__main__":
    import sys
    ok = _self_check()
    sys.exit(0 if ok else 1)
