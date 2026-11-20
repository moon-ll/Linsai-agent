# -*- coding: utf-8 -*-
"""端到端验证驱动：三阶段闭环验证，结果写 results/validation-results.json。

阶段1 闭环矩阵：12 个驱动点（数据全分辨率生成 / 拟合降分辨率前向——前向失配
       构成真实模型误差），输出 M1–M4 指标；验收：无噪 M2/M1 < 1%。
阶段2 噪声预算：雅可比协方差线性化给 σ_θ(η) 与 M2(η)，η_c 为 M2<1% 的噪声容限；
       蒙特卡洛复验（注入高斯相对噪声后重拟合）。
阶段3 分辨率收敛性：拟合前向分辨率递增时 M2 的收敛趋势。

用法：
    python3 run_validation.py                # 全部阶段
    python3 run_validation.py --phase 1      # 仅阶段1
    python3 run_validation.py --phase 2      # 仅阶段2（需阶段1的点4结果）
    python3 run_validation.py --phase 3      # 仅阶段3
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np

import l0_simulation as L

RESULTS = Path(__file__).resolve().parent.parent / "results"
RESULTS.mkdir(exist_ok=True)

# 分辨率：闭环矩阵与噪声预算用匹配分辨率（噪声极限检验）；
# 前向保真度极限（模型误差）由 phase3 的失配收敛表单独量化。
DATA_RES = {"nk": 64, "k_max": 0.45, "dt_rel": 100.0}
FIT_RES = {"nk": 64, "k_max": 0.45, "dt_rel": 100.0}


def drive_matrix():
    """≥10 个代表性驱动点（覆盖三档强度 × CEP × 各向异性 × 波长 × 脉宽）。"""
    return [
        {"tier": 0.3, "cep": 0.0, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T0.3"},
        {"tier": 0.6, "cep": 0.0, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T0.6"},
        {"tier": 1.0, "cep": 0.0, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T1.0"},
        {"tier": 1.5, "cep": 0.0, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T1.5"},
        {"tier": 2.0, "cep": 0.0, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T2.0"},
        {"tier": 0.3, "cep": np.pi / 2, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T0.3-CEP"},
        {"tier": 1.0, "cep": np.pi / 2, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T1.0-CEP"},
        {"tier": 2.0, "cep": np.pi / 2, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T2.0-CEP"},
        {"tier": 1.0, "cep": 0.0, "alpha": 1.0, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T1.0-iso"},
        {"tier": 2.0, "cep": 0.0, "alpha": 1.0, "omega_ev": 0.827, "ncyc": 8.0, "tag": "T2.0-iso"},
        {"tier": 1.0, "cep": 0.0, "alpha": 0.8, "omega_ev": 0.620, "ncyc": 8.0, "tag": "T1.0-2um"},
        {"tier": 0.3, "cep": 0.0, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 6.0, "tag": "T0.3-6cyc"},
    ]


def make_drive(spec):
    return L.Drive(spec["tier"], cep=spec["cep"], alpha=spec["alpha"],
                   omega_ev=spec["omega_ev"], ncyc=spec["ncyc"])


def phase1(out):
    """闭环矩阵：匹配分辨率 + 实验级噪声（η=1%）蒙特卡洛。"""
    matrix = drive_matrix()
    results = []
    t_start = time.time()
    for k, spec in enumerate(matrix):
        drv = make_drive(spec)
        probe = dict(L.DEFAULT_PROBE)
        dt_data = drv.T_L / DATA_RES["dt_rel"]
        delays = drv.t0 + np.linspace(-20.0, 20.0, 17)
        omega = np.linspace(0.10 / L.HBAR, 0.95 / L.HBAR, 32)
        A, diag = L.simulate_ATA(drv, delays, omega, probe,
                                 nk=DATA_RES["nk"], k_max=DATA_RES["k_max"],
                                 dt=dt_data)
        Eg_min = 2.0 * np.min(np.abs(drv.delta_eff(delays)))
        band = omega * L.HBAR > max(Eg_min - 0.03, 0.09)
        fit_res = {"nk": FIT_RES["nk"], "k_max": FIT_RES["k_max"],
                   "dt": drv.T_L / FIT_RES["dt_rel"]}
        fit = L.fit_sim(A, drv, delays, omega, probe, band, fit_res=fit_res)
        th0 = np.array(fit["theta_hat"])
        mask = L.mask_from_gap(drv.delta_eff(delays))
        met0 = L.compute_metrics(tuple(th0), drv, delays, mask)
        # 实验级噪声（η=1%，每延迟点 10⁴ 发平均的相对噪声设计值）MC ×3
        mc = []
        for r in range(3):
            rng = np.random.default_rng(100 + r)
            An = A * (1.0 + 0.01 * rng.standard_normal(A.shape))
            fitn = L.fit_sim(An, drv, delays, omega, probe, band,
                             d0_grid=[th0[0]], kap_grid=[th0[1]],
                             n_gn=5, fit_res=fit_res)
            metn = L.compute_metrics(fitn["theta_hat"], drv, delays, mask)
            mc.append({"rep": r,
                       "theta_hat": list(fitn["theta_hat"]),
                       "m2": metn["m2"], "m1": metn["m1"],
                       "m3_agree": metn["m3_agree"]})
        rec = {"tag": spec["tag"], "spec": spec,
               "theta_hat_noiseless": list(th0),
               "resid_rms": fit["resid_rms"],
               "cov": None if fit["cov"] is None else fit["cov"].tolist(),
               "sigma_A": fit["sigma_A"],
               "metrics_noiseless": {k2: met0[k2] for k2 in ("m1", "m2", "m3_agree", "m3_margin", "m4")},
               "mc_eta_1pct": mc,
               "m2_mc_max": max(m["m2"] for m in mc),
               "pc_max": diag["pc_max"],
               "delta_true": met0["delta_true"].tolist(),
               "delta_hat": met0["delta_hat"].tolist(),
               "mask": met0["mask"].tolist(),
               "delays": delays.tolist()}
        results.append(rec)
        out["phase1"] = results
        _save(out)
        print(f"[{k+1}/{len(matrix)}] {spec['tag']}: "
              f"无噪 M2={met0['m2']:.4%} | η=1% MC M2 max={rec['m2_mc_max']:.4%} "
              f"M3={mc[0]['m3_agree']} ({time.time()-t_start:.0f}s)")
    return results


def phase2(out):
    """噪声预算：线性化协方差 + 蒙特卡洛复验。"""
    matrix = drive_matrix()
    eta_list = [0.001, 0.002, 0.005, 0.01]
    budget = []
    rng = np.random.default_rng(7)
    for spec in matrix:
        if spec["tag"] not in ("T0.3", "T1.0", "T2.0"):
            continue
        drv = make_drive(spec)
        probe = dict(L.DEFAULT_PROBE)
        dt_data = drv.T_L / DATA_RES["dt_rel"]
        delays = drv.t0 + np.linspace(-20.0, 20.0, 17)
        omega = np.linspace(0.10 / L.HBAR, 0.95 / L.HBAR, 32)
        A, _ = L.simulate_ATA(drv, delays, omega, probe,
                              nk=DATA_RES["nk"], k_max=DATA_RES["k_max"],
                              dt=dt_data)
        Eg_min = 2.0 * np.min(np.abs(drv.delta_eff(delays)))
        band = omega * L.HBAR > max(Eg_min - 0.03, 0.09)
        fit_res = {"nk": FIT_RES["nk"], "k_max": FIT_RES["k_max"],
                   "dt": drv.T_L / FIT_RES["dt_rel"]}
        fit = L.fit_sim(A, drv, delays, omega, probe, band,
                        d0_grid=np.linspace(0.12, 0.18, 4),
                        kap_grid=np.linspace(0.85, 1.15, 4), fit_res=fit_res)
        J = fit["J"]
        if J is None:
            continue
        jtj_inv = np.linalg.inv(J.T @ J)
        a_rms = float(np.sqrt(np.mean(np.abs(A[:, band, :]) ** 2)))
        # 波形偏差对 θ 的敏度：δd(τ) = δΔ0 + δκ·m(τ)
        m_pk = float(np.max(np.abs(drv.m(delays))))
        rec = {"tag": spec["tag"], "theta_hat": list(fit["theta_hat"]),
               "sigma_theta_unit": np.sqrt(np.diag(jtj_inv)).tolist(),
               "a_rms": a_rms, "m_pk": m_pk,
               "eta_table": []}
        for eta in eta_list:
            sig_th = np.sqrt(np.diag(jtj_inv)) * eta * a_rms
            m2_1s = float((sig_th[0] + sig_th[1] * m_pk) / L.DELTA0)
            rec["eta_table"].append({"eta": eta, "sigma_d0": float(sig_th[0]),
                                     "sigma_kap": float(sig_th[1]),
                                     "m2_1sigma": m2_1s,
                                     "pass_1pct_1s": bool(m2_1s < 0.01)})
        # 蒙特卡洛复验（仅 T1.0，两个 η 档 × 3 次）
        if spec["tag"] == "T1.0":
            mc = []
            for eta in (0.002, 0.01):
                errs = []
                for r in range(3):
                    rng_r = np.random.default_rng(100 + r)
                    An = A * (1.0 + eta * rng_r.standard_normal(A.shape))
                    fitn = L.fit_sim(An, drv, delays, omega, probe, band,
                                     d0_grid=[fit["theta_hat"][0]],
                                     kap_grid=[fit["theta_hat"][1]],
                                     n_gn=3, fit_res=fit_res)
                    thn = np.array(fitn["theta_hat"])
                    d_hn = thn[0] + thn[1] * drv.m(delays)
                    d_t = drv.delta_eff(delays)
                    msk = L.mask_from_gap(d_t)
                    m2n = float(np.max(np.abs((d_hn - d_t)[~msk])) / L.DELTA0)
                    errs.append(m2n)
                mc.append({"eta": eta, "m2_realizations": errs,
                           "m2_mean": float(np.mean(errs))})
            rec["monte_carlo"] = mc
        budget.append(rec)
        out["phase2"] = budget
        _save(out)
        print(f"[phase2] {spec['tag']}: σ_θ(unit-noise) = "
              f"{rec['sigma_theta_unit']}")
    return budget


def phase3(out):
    """分辨率收敛性：拟合前向分辨率递增时 M2 的趋势。"""
    spec = {"tier": 1.0, "cep": 0.0, "alpha": 0.8, "omega_ev": 0.827, "ncyc": 8.0}
    drv = make_drive(spec)
    probe = dict(L.DEFAULT_PROBE)
    dt_data = drv.T_L / DATA_RES["dt_rel"]
    delays = drv.t0 + np.linspace(-20.0, 20.0, 17)
    omega = np.linspace(0.10 / L.HBAR, 0.95 / L.HBAR, 32)
    A, _ = L.simulate_ATA(drv, delays, omega, probe,
                          nk=DATA_RES["nk"], k_max=DATA_RES["k_max"],
                          dt=dt_data)
    Eg_min = 2.0 * np.min(np.abs(drv.delta_eff(delays)))
    band = omega * L.HBAR > max(Eg_min - 0.03, 0.09)
    conv = []
    for nk_f, dt_rel_f in ((36, 60.0), (44, 80.0), (52, 90.0), (60, 95.0), (64, 100.0)):
        fit_res = {"nk": nk_f, "k_max": 0.45, "dt": drv.T_L / dt_rel_f}
        fit = L.fit_sim(A, drv, delays, omega, probe, band, fit_res=fit_res)
        mask = L.mask_from_gap(drv.delta_eff(delays))
        met = L.compute_metrics(fit["theta_hat"], drv, delays, mask)
        conv.append({"fit_nk": nk_f, "fit_dt_rel": dt_rel_f,
                     "theta_hat": list(fit["theta_hat"]),
                     "m1": met["m1"], "m2": met["m2"]})
        out["phase3"] = conv
        _save(out)
        print(f"[phase3] fit_res nk={nk_f} dt=T/{dt_rel_f:.0f}: "
              f"M2={met['m2']:.4%} M1={met['m1']:.4%}")
    return conv


def _save(out):
    with open(RESULTS / "validation-results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, default=0)
    args = ap.parse_args()
    out = {}
    t0 = time.time()
    if args.phase in (0, 1):
        phase1(out)
    if args.phase in (0, 2):
        phase2(out)
    if args.phase in (0, 3):
        phase3(out)
    out["wall_time_s"] = time.time() - t0
    _save(out)
    print(f"完成，总时长 {out['wall_time_s']:.0f}s，结果已写入 "
          f"{RESULTS / 'validation-results.json'}")


if __name__ == "__main__":
    main()
