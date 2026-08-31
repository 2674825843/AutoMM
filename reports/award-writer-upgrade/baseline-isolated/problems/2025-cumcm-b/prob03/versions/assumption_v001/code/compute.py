"""prob03 硅/碳化硅外延层多光束判定与厚度反演 CLI（computation 阶段由 supervised worker 执行）。

任务：依据 formulation_v002，交付本问三个子问题：
  Q1 多光束干涉必要条件推导 → 以 N1–N4 数值判据落地（Rbar/相干/平行度/吸收 + 极值不变性 L17）；
  Q2 硅片（附件3=10°/附件4=15°）是否出现显著多光束 → 判定（Rbar≤θ_mb、η_mb≤τ_mb）；
     以及硅厚度主反演（baseline-robust variable projection，两角共享 t）；
  Q3 SiC（附件1/2）重新判定（prob02 对照）→ 是否需多光束修正。

主方法（S1）：基线-干涉分解 + 一维相位频率扫描（variable projection），两角共享 t；t 由干涉相位频率
唯一确定、与 n_sub 解耦。多光束判定（S2）：两光束 (2.8) vs Airy (2.6) 全谱残差改善率 η_mb。

用法：
    python compute.py --config CONFIG --input INPUT --output OUTPUT [--seed SEED]
    python compute.py --self-check          # 仅运行秒级接口探针

输出目录（--output 或环境变量 AUTOMM_OUTPUT_DIR）：
    result.json         硅厚度（共享+每角）、n_sub 弱辨识、多光束判定（Si/SiC）、可靠性判据汇总
    solver_status.json  主 variable projection 扫描状态
    verification.json   检查明细（checks 列表）
    metadata.json       场景、种子、输入/配置 hash、单位约定、公式引用
    preprocessing.json  预处理日志（硅透明谱段截断、异常点、SiC 对照日志）
    dispersion_ref.json 色散模型 n(lambda) 对照（硅/碳化硅 Sellmeier）
    mb_conditions.json  多光束必要条件 N1–N4 数值 + η_mb + SiC 重新判定
    reflectance_theta*.csv 反演带内谱（nu, R_obs, R_model_best, weight）
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import model
import numpy as np
import yaml

# ---- 单位与公式来源登记（与 formulation_v002 / parameters.yaml 一致） ----
UNIT_CONVENTIONS = {
    "t": "um",
    "nu": "cm^-1",
    "lambda": "um = 1e4 / nu",
    "theta": "degree（三角函数内部转 rad）",
    "delta": "rad",
    "delta_nu": "cm^-1",
    "r": "dimensionless（R% / 100 归一）",
    "g": "cm^-1（相位函数 g=n*nu*cos(theta')）",
    "Rbar": "dimensionless（sqrt(R01*R12)，多光束显著性主控量）",
}
FORMULA_REFS = {
    "snell": "(2.1)",
    "phase": "(2.7)",
    "fresnel": "(2.2)-(2.4)",
    "two_beam": "(2.8)",
    "airy": "(2.5)/(2.6)",
    "sellmeier_si": "(5.1)",
    "sellmeier_sic": "prob02 (4.1)",
    "n1_reflectivity": "(3.1)/(3.2)",
    "n2_coherence": "(3.3)/(3.4)",
    "n3_parallelism": "(3.5)",
    "n4_absorption": "(3.6)",
    "extremum_invariance": "(3.7)/(3.8)",
    "vp_decomposition": "(6.1)-(6.3)",
    "vp_scan": "(6.4)/(6.5)",
    "phase_freq_thickness": "(2.9)",
    "mb_improvement": "(7.1)/(7.2)",
    "ftest": "§7.2",
    "disp_sensitivity": "§7.2",
    "ci_profile": "§7.5",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"配置文件必须是映射：{path}")
    return value


def resolve_output(output_arg: str | None) -> Path:
    env_dir = os.environ.get("AUTOMM_OUTPUT_DIR")
    if env_dir and output_arg:
        env_path = Path(env_dir).resolve()
        arg_path = Path(output_arg).resolve()
        if env_path != arg_path:
            raise ValueError(f"环境变量 AUTOMM_OUTPUT_DIR 与 --output 不一致：{env_dir} vs {output_arg}")
        return env_path
    chosen = env_dir or output_arg
    if not chosen:
        raise ValueError("缺少输出目录：请提供 --output 或 AUTOMM_OUTPUT_DIR")
    return Path(chosen).resolve()


def resolve_seed(cli_seed: int | None, config: dict) -> int:
    env_seed = os.environ.get("AUTOMM_SEED")
    if env_seed is not None:
        return int(env_seed)
    if cli_seed is not None:
        return int(cli_seed)
    return int(config.get("seed", 20260830))


def inv_conf(config: dict) -> dict:
    value = config.get("inversion", {})
    return value if isinstance(value, dict) else {}


def rel_conf(config: dict) -> dict:
    value = config.get("reliability", {})
    return value if isinstance(value, dict) else {}


def band_conf(config: dict) -> tuple[float, float]:
    inv = inv_conf(config)
    lo = inv.get("inv_band_lo")
    hi = inv.get("inv_band_hi")
    if lo is not None and hi is not None:
        return float(lo), float(hi)
    return float(model.SI_INV_BAND_CM1[0]), float(model.SI_INV_BAND_CM1[1])


def _check_registered(param_map: dict, band_lo: float, band_hi: float) -> None:
    n_air_reg = param_map.get("n_air", {}).get("value")
    if n_air_reg is not None and abs(float(n_air_reg) - model.N_AIR) > 1e-9:
        print(f"警告：parameters.yaml n_air={n_air_reg} 与代码常量 {model.N_AIR} 不一致", file=sys.stderr)
    nu_inv_reg = param_map.get("nu_inv_si", {}).get("value")
    if nu_inv_reg is not None:
        nv = [float(v) for v in nu_inv_reg]
        if abs(nv[0] - band_lo) > 1e-9 or abs(nv[1] - band_hi) > 1e-9:
            print(f"警告：parameters.yaml nu_inv_si={nv} 与反演谱段 {[band_lo, band_hi]} 不一致", file=sys.stderr)
    p_reg = param_map.get("baseline_poly_deg", {}).get("value")
    q_reg = param_map.get("envelope_poly_deg", {}).get("value")
    if p_reg is not None and int(p_reg) != model.BASELINE_POLY_DEG:
        print(
            f"警告：parameters.yaml baseline_poly_deg={p_reg} 与代码常量 {model.BASELINE_POLY_DEG} 不一致",
            file=sys.stderr,
        )
    if q_reg is not None and int(q_reg) != model.ENVELOPE_POLY_DEG:
        print(
            f"警告：parameters.yaml envelope_poly_deg={q_reg} 与代码常量 {model.ENVELOPE_POLY_DEG} 不一致",
            file=sys.stderr,
        )


def load_attachment(path: str | Path) -> dict:
    return model.load_attachment(path)


def preprocess_attachment(att: dict, config: dict, *, exclude_band: tuple[float, float] | None) -> dict:
    pp = model.preprocess_spectrum(
        att["nu"],
        att["r_obs"],
        exclude_band=exclude_band,
        weight_anomaly=float(inv_conf(config).get("weight_anomaly", 0.05)),
    )
    return {"nu": pp["nu"], "r_obs": pp["r_obs"], "weights": pp["weights"], "log": pp["log"]}


def dispersion_for_angle(att: dict, config: dict, dispersion_model: str, c_disp: float = 1.0) -> np.ndarray:
    return np.asarray(model.dispersion_epi_si(att["nu"], model=dispersion_model, c_disp=c_disp), dtype=float)


def inv_band_data(atts: list[dict], thetas: list[float], config: dict, dispersion_model: str, c_disp=1.0) -> dict:
    lo, hi = band_conf(config)
    nu_list, r_list, w_list, n_list = [], [], [], []
    for att, theta in zip(atts, thetas):
        mask = (att["nu"] >= lo) & (att["nu"] <= hi)
        n_nu = dispersion_for_angle(att, config, dispersion_model, c_disp)
        nu_list.append(att["nu"][mask])
        r_list.append(att["r_obs"][mask])
        w_list.append(att["weights"][mask])
        n_list.append(n_nu[mask])
    return {"nu_list": nu_list, "r_list": r_list, "w_list": w_list, "n_list": n_list, "thetas": thetas}


def vp_scan_setup(config: dict) -> dict:
    inv = inv_conf(config)
    t_lo = float(inv.get("t_scan_lo", model.T_SCAN_RANGE_SI[0]))
    t_hi = float(inv.get("t_scan_hi", model.T_SCAN_RANGE_SI[1]))
    t_step = float(inv.get("t_scan_step", model.T_SCAN_STEP))
    p = int(inv.get("baseline_poly_deg", model.BASELINE_POLY_DEG))
    q = int(inv.get("envelope_poly_deg", model.ENVELOPE_POLY_DEG))
    return {"t_range": (t_lo, t_hi), "t_step": t_step, "p": p, "q": q}


def main_variable_projection(atts, thetas, config, dispersion_model) -> dict:
    data = inv_band_data(atts, thetas, config, dispersion_model)
    setup = vp_scan_setup(config)
    shared = model.variable_projection_scan(
        data["nu_list"], data["r_list"], data["thetas"], data["n_list"], data["w_list"],
        t_range=setup["t_range"], t_step=setup["t_step"], p=setup["p"], q=setup["q"], shared=True,
    )
    indep = model.variable_projection_scan(
        data["nu_list"], data["r_list"], data["thetas"], data["n_list"], data["w_list"],
        t_range=setup["t_range"], t_step=setup["t_step"], p=setup["p"], q=setup["q"], shared=False,
    )
    nsub_estimates = []
    for k in range(len(thetas)):
        amp = shared["angle_fits"][k]["amplitude"]
        nu_k = data["nu_list"][k]
        n_k = data["n_list"][k]
        n_c = float(np.interp(model.AMP_REF_NU_CM1, nu_k, n_k)) if nu_k.size else None
        if n_c is not None:
            est = model.nsub_from_amplitude(amp, n_c, thetas[k], n_sub_max=model.SI_N_SUB_BOUNDS[1])
        else:
            est = {"n_sub": None}
        nsub_estimates.append(
            {"theta_deg": thetas[k], "amplitude": amp, "n_sub": est["n_sub"], "R1": est["R1"], "R2": est["R2"]}
        )
    return {"shared": shared, "indep": indep, "nsub_estimates": nsub_estimates, "setup": setup}


def _mean_nsub(estimates: list[dict]) -> float:
    vals = [float(e["n_sub"]) for e in estimates if e.get("n_sub") is not None]
    return float(np.mean(vals)) if vals else float(model.N_SUB_SI_INIT)


def necessary_conditions_si(atts, thetas, config, dispersion_model, main_fit: dict, n_sub_hat: float) -> dict:
    """N1–N4 必要条件（Q1）＋ 由幅值反演 R12 / Rbar / finesse（§7.2）。"""
    data = inv_band_data(atts, thetas, config, dispersion_model)
    t_hat = float(main_fit["shared"]["t_hat_refined"])
    amplitude = float(np.mean([e["amplitude"] for e in main_fit["nsub_estimates"]]))
    ref_nu = model.AMP_REF_NU_CM1
    n_ref = float(np.mean([np.interp(ref_nu, nu, n_nu) for nu, n_nu in zip(data["nu_list"], data["n_list"])]))
    nc = model.necessary_conditions(
        n_ref, n_sub_hat, thetas[0], t_hat,
        amplitude=amplitude, nu_cm1=ref_nu, lambda_um=4.0,
    )
    return {"t_um": t_hat, "amplitude": amplitude, "n_ref": n_ref, "n_sub_hat": n_sub_hat, "conditions": nc}


def multibeam_improvement_si(atts, thetas, config, dispersion_model, main_fit: dict, n_sub_hat: float) -> dict:
    """η_mb（Q1/Q2 主判据）：两光束 (2.8) vs Airy (2.6) 全谱残差改善率（§7.2）。"""
    data = inv_band_data(atts, thetas, config, dispersion_model)
    t_hat = float(main_fit["shared"]["t_hat_refined"])
    per_angle = []
    for k, theta in enumerate(thetas):
        res = model.multibeam_improvement(
            data["nu_list"][k], data["r_list"][k], t_hat, data["n_list"][k], n_sub_hat, theta
        )
        per_angle.append({"theta_deg": theta, **res})
    best = max(r["improvement_percent"] for r in per_angle)
    threshold = float(rel_conf(config).get("tau_mb", model.TAU_MB_PERCENT))
    return {
        "per_angle": per_angle,
        "improvement_percent": best,
        "threshold_percent": threshold,
        "needs_multibeam_correction": bool(best > threshold),
        "decision": "two_beam_negligible" if best <= threshold else "multibeam_significant",
    }


def sic_multibeam_recheck(atts_sic, thetas, config, sic_t_ref_um: float) -> dict:
    """Q3：SiC 重新判定（§7.3/§13.5）。

    以只读方式在 prob02 的 t̂（sic_t_ref_um）处对附件1/2 做固定 t 的基线-干涉分解，
    取干涉幅值 A=√(C²+S²) 反演 R12 → Rbar=√(R01·R12)，确认 ≤θ_mb（prob02 实测 R12≈3.2e-5）。
    不重新求解厚度（仅量级核实），不发起新反演。
    """
    lo, hi = band_conf(config)
    per_angle = []
    for att, theta in zip(atts_sic, thetas):
        mask = (att["nu"] >= lo) & (att["nu"] <= hi)
        nu = att["nu"][mask]
        r = att["r_obs"][mask]
        w = att["weights"][mask]
        n_nu = np.asarray(model.dispersion_epi_sic(nu), dtype=float)
        nu0 = float(np.mean(nu))
        half = max(float(np.max(nu) - nu0), float(nu0 - np.min(nu)), 1e-12)
        p = model.BASELINE_POLY_DEG
        q = model.ENVELOPE_POLY_DEG
        phi = model.vp_design_matrix(nu, n_nu, theta, sic_t_ref_um, p, q, nu0, half)
        fit = model.vp_linear_ls(phi, r, w)
        beta = fit["beta"]
        b_cols = p + 1
        c_cols = q + 1
        c_beta = beta[b_cols : b_cols + c_cols]
        s_beta = beta[b_cols + c_cols : b_cols + 2 * c_cols]
        c_poly = np.polynomial.chebyshev.chebvander((np.asarray([model.AMP_REF_NU_CM1]) - nu0) / half, q)
        s_poly = np.polynomial.chebyshev.chebvander((np.asarray([model.AMP_REF_NU_CM1]) - nu0) / half, q)
        c_val = float((c_poly @ c_beta)[0])
        s_val = float((s_poly @ s_beta)[0])
        amplitude = float(np.hypot(c_val, s_val))
        n_c = float(np.interp(model.AMP_REF_NU_CM1, nu, n_nu))
        r01 = float(model._r1_pol_avg(n_c, theta))
        r12 = model.r12_from_amplitude(amplitude, r01)
        rbar = float(np.sqrt(max(r01, 0.0) * (r12 if r12 is not None else model.SIC_R12_REF)))
        per_angle.append(
            {
                "theta_deg": theta,
                "amplitude": amplitude,
                "R01": r01,
                "R12_from_amplitude": r12,
                "R12_used": r12 if r12 is not None else model.SIC_R12_REF,
                "Rbar": rbar,
                "theta_mb": model.THETA_MB,
                "criterion_met": bool(rbar <= model.THETA_MB),
            }
        )
    all_met = all(a["criterion_met"] for a in per_angle)
    theta_mb = float(rel_conf(config).get("theta_mb", model.THETA_MB))
    return {
        "per_angle": per_angle,
        "Rbar_max": max(a["Rbar"] for a in per_angle),
        "theta_mb": theta_mb,
        "sic_mb_verdict": "no_correction_needed" if all_met else "corrected_t",
        "prob02_reference": {
            "t_sic_um": model.SIC_T_REF_UM,
            "R01_ref": model.SIC_R01_REF,
            "R12_ref": model.SIC_R12_REF,
            "Rbar_ref": float(np.sqrt(model.SIC_R01_REF * model.SIC_R12_REF)),
            "content_hash": "27b0ce86…a12ea（prob02-conclusion-v1）",
        },
        "note": "SiC 在 prob02 t̂ 处只读量级核实（不重新求解厚度）；Rbar<=θ_mb → 无显著多光束、无需修正",
    }


def two_angle_ftest(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    data = inv_band_data(atts, thetas, config, dispersion_model)
    n_tot = int(sum(np.count_nonzero(np.asarray(w, dtype=float) > 0.0) for w in data["w_list"]))
    alpha = float(rel_conf(config).get("alpha_ftest", 0.05))
    ft = model.two_angle_ftest_vp(main_fit["shared"], main_fit["indep"], n_tot=n_tot, alpha=alpha)
    ft["n_tot"] = n_tot
    ft["eps12_threshold_percent"] = float(rel_conf(config).get("tau_12", 2.0))
    return ft


def dispersion_sensitivity(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    """§7.2：带内合法候选 {N-SE, N-SE-δ} 的 Δt_disp（硅无 λ>5µm 缺口，故无 Δt_inv_band）。"""
    t_base = float(main_fit["shared"]["t_hat_refined"])
    delta = float(rel_conf(config).get("delta_c_disp", model.DELTA_C_DISP))
    setup = vp_scan_setup(config)
    results = {"N-SE": t_base}
    max_dev = 0.0
    for sign in (+1.0, -1.0):
        c = 1.0 + sign * delta
        d = inv_band_data(atts, thetas, config, "N-SE-delta", c_disp=c)
        sc = model.variable_projection_scan(
            d["nu_list"], d["r_list"], d["thetas"], d["n_list"], d["w_list"],
            t_range=setup["t_range"], t_step=setup["t_step"], p=setup["p"], q=setup["q"], shared=True,
        )
        label = f"N-SE-delta{'+' if sign > 0 else '-'}"
        results[label] = float(sc["t_hat_refined"])
        max_dev = max(max_dev, abs(float(sc["t_hat_refined"]) - t_base))
    dt_disp = max_dev / t_base * 100.0 if t_base > 0 else float("inf")
    tau_d = float(rel_conf(config).get("tau_disp", 2.0))
    return {
        "status": "PASS" if dt_disp <= tau_d else "FAIL",
        "dispersion_models_t": results,
        "delta_t_disp_percent": dt_disp,
        "threshold_percent": tau_d,
        "delta_c_disp": delta,
        "note": "硅色散弱（Δn/n≈0.51%），Δt_disp 预期<1%；硅 Sellmeier 在主反演带全程有效（无 λ>5µm 缺口）",
    }


def ci_profile_likelihood(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    shared_scan = main_fit["shared"]
    data = inv_band_data(atts, thetas, config, dispersion_model)
    n_tot = int(sum(np.count_nonzero(np.asarray(w, dtype=float) > 0.0) for w in data["w_list"]))
    p = int(shared_scan["p"])
    q = int(shared_scan["q"])
    n_angles = int(shared_scan.get("n_angles", len(thetas)))
    coef_per_angle = (p + 1) + 2 * (q + 1)
    n_params = n_angles * coef_per_angle + 1
    ci = model.profile_ci_from_Jcurve(
        shared_scan["t_grid"], shared_scan["J_shared"], shared_scan["t_hat_refined"],
        n_tot=n_tot, n_params=n_params,
    )
    tau_ci = float(rel_conf(config).get("tau_ci", 2.0))
    if ci is None:
        return {
            "status": "INSUFFICIENT",
            "t_hat_um": float(shared_scan["t_hat_refined"]),
            "threshold_percent": tau_ci,
            "method": "profile_likelihood_Jcurve",
        }
    half_rel = ci["halfwidth_percent"]
    out = dict(ci)
    out["status"] = "PASS" if half_rel <= tau_ci else "FAIL"
    out["threshold_percent"] = tau_ci
    out["t_hat_um"] = float(shared_scan["t_hat_refined"])
    out["method"] = "profile_likelihood_Jcurve（SSE(t) 曲率/夹逼区间）"
    return out


def anomaly_impact(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    t_base = float(main_fit["shared"]["t_hat_refined"])
    setup = vp_scan_setup(config)
    t_dict: dict[str, float | None] = {}
    for label, weight_anom in (("downweight", 0.05), ("drop", 0.0), ("keep", 1.0)):
        atts_mod = []
        for a in atts:
            pp = model.preprocess_spectrum(
                a["nu"], a["r_obs"], weight_anomaly=weight_anom, exclude_band=model.SI_MULTIPHONON_EXCLUDE_CM1
            )
            atts_mod.append({"nu": a["nu"], "r_obs": a["r_obs"], "weights": pp["weights"]})
        data = inv_band_data(atts_mod, thetas, config, dispersion_model)
        try:
            sc = model.variable_projection_scan(
                data["nu_list"], data["r_list"], data["thetas"], data["n_list"], data["w_list"],
                t_range=setup["t_range"], t_step=setup["t_step"] * 2.0, p=setup["p"], q=setup["q"], shared=True,
            )
            t_dict[label] = float(sc["t_hat_refined"])
        except (ValueError, FloatingPointError):
            t_dict[label] = None
    valid = {k: v for k, v in t_dict.items() if v is not None}
    base = valid.get("downweight", t_base)
    spread = (
        (max(valid.values()) - min(valid.values())) / base * 100.0
        if len(valid) >= 2 and base > 0
        else float("inf")
    )
    tau_a = float(rel_conf(config).get("tau_anom", 1.0))
    return {
        "status": "PASS" if spread <= tau_a else "FAIL",
        "strategy_t": t_dict,
        "delta_t_anom_percent": spread,
        "threshold_percent": tau_a,
        "note": "硅片附件 3/4 无 R%>100 异常；异常点按 weight_anomaly 降权（不改原始数据），B2 策略沿用为鲁棒",
    }


def _uniqueness_ratio(shared_scan: dict) -> float | None:
    j = np.asarray(shared_scan["J_shared"], dtype=float)
    idx = int(np.argmin(j))
    if idx == 0 or idx == j.size - 1:
        return None
    lo = max(0, idx - 3)
    hi = min(j.size, idx + 4)
    region = np.concatenate([j[:lo], j[hi:]])
    if region.size == 0:
        return None
    second = float(np.min(region))
    return float(second / j[idx]) if j[idx] > 0 else None


def _j_curve_sample(shared_scan: dict, max_points: int = 200) -> dict:
    t = np.asarray(shared_scan["t_grid"], dtype=float)
    j = np.asarray(shared_scan["J_shared"], dtype=float)
    if t.size <= max_points:
        return {"t": t.tolist(), "J": j.tolist()}
    idxs = np.linspace(0, t.size - 1, max_points).astype(int)
    return {"t": t[idxs].tolist(), "J": j[idxs].tolist()}


def _sanitize(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "jac" and isinstance(v, np.ndarray):
                out[k] = {"shape": list(v.shape), "frobenius_norm": float(np.linalg.norm(v))}
            elif k == "beta" and isinstance(v, np.ndarray):
                out[k] = v.tolist()
            elif k in ("t_grid", "J_shared", "angle_scan") and isinstance(v, np.ndarray):
                out[k] = _sanitize(v)
            else:
                out[k] = _sanitize(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [_sanitize(x) for x in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    return str(obj)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="prob03 硅/碳化硅外延层多光束判定与厚度反演（formulation_v002）")
    parser.add_argument("--config", help="task_config.yaml 路径（附件路径/反演/可靠性设置）")
    parser.add_argument("--input", help="formulation parameters.yaml 路径（参数登记）")
    parser.add_argument("--output", help="输出目录（优先使用环境变量 AUTOMM_OUTPUT_DIR）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（优先使用环境变量 AUTOMM_SEED）")
    parser.add_argument("--self-check", action="store_true", help="仅运行接口探针（秒级）")
    args = parser.parse_args(argv)

    if args.self_check:
        results = model.run_probes()
        for name, passed in sorted(results.items()):
            print(f"{'PASS' if passed else 'FAIL'}  {name}")
        ok = all(results.values())
        print(f"probe 汇总：{sum(results.values())}/{len(results)} 通过")
        return 0 if ok else 1

    if not args.config or not args.input:
        parser.error("--config 与 --input 为必填（--self-check 除外）")

    config = load_yaml(Path(args.config).resolve())
    input_params = load_yaml(Path(args.input).resolve())
    output_dir = resolve_output(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    seed = resolve_seed(args.seed, config)

    scenario = config.get("scenario", {})
    dispersion_model = str(scenario.get("dispersion_model", "N-SE"))
    band_lo, band_hi = band_conf(config)
    att_si10 = Path(str(scenario.get("attachment_si10", "data/2025_cumcm_B/附件3.xlsx"))).resolve()
    att_si15 = Path(str(scenario.get("attachment_si15", "data/2025_cumcm_B/附件4.xlsx"))).resolve()
    att_sic10 = Path(str(scenario.get("attachment_sic10", "data/2025_cumcm_B/附件1.xlsx"))).resolve()
    att_sic15 = Path(str(scenario.get("attachment_sic15", "data/2025_cumcm_B/附件2.xlsx"))).resolve()
    sic_t_ref = float(scenario.get("sic_t_ref_um", model.SIC_T_REF_UM))

    param_map = {str(e["name"]): e for e in input_params.get("parameters", []) if isinstance(e, dict) and e.get("name")}
    _check_registered(param_map, band_lo, band_hi)

    # ---- 硅片（附件3/4）预处理：透明谱段 [2000,4000]；多声子带/异常点降权 ----
    att3 = preprocess_attachment(load_attachment(att_si10), config, exclude_band=model.SI_MULTIPHONON_EXCLUDE_CM1)
    att4 = preprocess_attachment(load_attachment(att_si15), config, exclude_band=model.SI_MULTIPHONON_EXCLUDE_CM1)
    atts_si = [att3, att4]
    thetas = [10.0, 15.0]

    # ---- 主反演（S1：基线-干涉分解 + 一维相位频率扫描，两角共享 t） ----
    main_fit = main_variable_projection(atts_si, thetas, config, dispersion_model)
    t_hat_shared = float(main_fit["shared"]["t_hat_refined"])
    n_sub_hat = _mean_nsub(main_fit["nsub_estimates"])

    # ---- 多光束必要条件 N1–N4（Q1）与 η_mb（Q2 主判据） ----
    nc_si = necessary_conditions_si(atts_si, thetas, config, dispersion_model, main_fit, n_sub_hat)
    mb_si = multibeam_improvement_si(atts_si, thetas, config, dispersion_model, main_fit, n_sub_hat)
    n1_ok = bool(nc_si["conditions"]["N1"]["criterion_met"])
    mb_decision_si = (
        "two_beam_negligible"
        if (n1_ok and not mb_si["needs_multibeam_correction"])
        else "multibeam_significant"
    )

    # ---- SiC 重新判定（Q3） ----
    att1sic = preprocess_attachment(load_attachment(att_sic10), config, exclude_band=model.SIC_RESTSTRAHLEN_EXCLUDE_CM1)
    att2sic = preprocess_attachment(load_attachment(att_sic15), config, exclude_band=model.SIC_RESTSTRAHLEN_EXCLUDE_CM1)
    sic_recheck = sic_multibeam_recheck([att1sic, att2sic], thetas, config, sic_t_ref)

    # ---- 可靠性 ----
    two_angle = two_angle_ftest(atts_si, thetas, config, dispersion_model, main_fit)
    disp_sens = dispersion_sensitivity(atts_si, thetas, config, dispersion_model, main_fit)
    ci_payload = ci_profile_likelihood(atts_si, thetas, config, dispersion_model, main_fit)
    anom = anomaly_impact(atts_si, thetas, config, dispersion_model, main_fit)

    # ---- 预处理日志（硅 + SiC 对照） ----
    band_data = inv_band_data(atts_si, thetas, config, dispersion_model)
    n_points_band = int(sum(np.count_nonzero(np.asarray(w, dtype=float) > 0.0) for w in band_data["w_list"]))
    preprocess_payload = {
        "attachment_si10": {"path": str(att_si10), "sha256": sha256_file(att_si10), "log": att3["log"]},
        "attachment_si15": {"path": str(att_si15), "sha256": sha256_file(att_si15), "log": att4["log"]},
        "attachment_sic10": {"path": str(att_sic10), "sha256": sha256_file(att_sic10), "log": att1sic["log"]},
        "attachment_sic15": {"path": str(att_sic15), "sha256": sha256_file(att_sic15), "log": att2sic["log"]},
        "inv_band_cm1": [band_lo, band_hi],
        "n_points_inv_band_si_all_angles": n_points_band,
        "si_multiphonon_exclude_cm1": list(model.SI_MULTIPHONON_EXCLUDE_CM1),
        "sic_reststrahlen_exclude_cm1": list(model.SIC_RESTSTRAHLEN_EXCLUDE_CM1),
        "truncation_rule": (
            f"硅主反演谱段截断至 ν∈[{band_lo},{band_hi}]（透明窗，C8）；"
            "ν<2000（多声子带边缘）不进入主反演；异常点降权 w=weight_anomaly；原始数据只读"
        ),
    }
    # ---- 色散核验（硅 + SiC） ----
    lam_check = np.array([2.5, 3.0, 5.0])
    n_si = np.asarray(model.dispersion_epi_si(model.lambda_to_nu(lam_check), model="N-SE"), dtype=float)
    n_si_const = np.asarray(model.dispersion_epi_si(model.lambda_to_nu(lam_check), model="N-const"), dtype=float)
    n_sic = np.asarray(model.dispersion_epi_sic(model.lambda_to_nu(lam_check)), dtype=float)
    dispersion_payload = {
        "model_si": dispersion_model,
        "anchor_checks": {
            "lambda_um": lam_check.tolist(),
            "n_si_NSE": n_si.tolist(),
            "n_si_Nconst": n_si_const.tolist(),
            "n_sic_sellmeier": n_sic.tolist(),
        },
        "inv_band_cm1": [float(band_lo), float(band_hi)],
        "si_sellmeier_boundary_um": model.SI_SELLMEIER_BOUNDARY_UM,
        "sic_sellmeier_boundary_um": model.SIC_SELLMEIER_BOUNDARY_UM,
        "p_baseline_deg": main_fit["setup"]["p"],
        "q_envelope_deg": main_fit["setup"]["q"],
        "note": (
            "硅主反演带用 Sellmeier（L12/L13，N-SE；λ≤11µm 全程有效，无 λ>5µm 缺口）；"
            "SiC 用 prob02 4H-SiC Sellmeier（L09）仅作 §7.3 重新判定；基线/包络用中心化正交化（Chebyshev）多项式基"
        ),
    }

    # ---- 评估汇总 ----
    checks = []
    for name, item, passed in (
        ("reliability_two_angle_ftest", two_angle, two_angle["status"] != "FAIL"),
        ("reliability_dispersion", disp_sens, disp_sens["status"] != "FAIL"),
        ("reliability_ci", ci_payload, ci_payload["status"] == "PASS"),
        ("reliability_anomaly", anom, anom["status"] != "FAIL"),
        ("multibeam_si", mb_si, mb_si["decision"] == "two_beam_negligible"),
        ("multibeam_sic", sic_recheck, sic_recheck["sic_mb_verdict"] == "no_correction_needed"),
    ):
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "detail": json.dumps(item, ensure_ascii=False, default=str),
                "tolerance": str(item.get("threshold_percent", item.get("theta_mb", ""))),
            }
        )
    nsub_check = {
        "name": "reliability_nsub_diag",
        "passed": True,  # 诊断项（非硬门禁）：主方法 t 与 n_sub 解耦
        "detail": json.dumps(
            {"n_sub_hat_amplitude": n_sub_hat, "main_t_decoupled": True}, ensure_ascii=False, default=str
        ),
        "tolerance": str(rel_conf(config).get("tau_nsub_diag", 3.0)),
    }
    checks.append(nsub_check)

    passed_all = bool(all(c["passed"] for c in checks))
    feasible = passed_all

    result_payload = {
        "feasible_incumbent": feasible,
        "task": "prob03-silicon-multibeam-thickness",
        "passed": passed_all,
        "theta_deg": thetas,
        "material": "silicon（附件3/4）",
        "n_sub_hat_amplitude": n_sub_hat,
        "dispersion_model": dispersion_model,
        "inv_band_cm1": [float(band_lo), float(band_hi)],
        "main_variable_projection": {
            "mode": "baseline_interference_decoupled_1d_scan",
            "t_hat_shared_um": t_hat_shared,
            "t_hat_per_angle_um": main_fit["indep"]["t_hat_per_angle"],
            "J_min_shared": main_fit["shared"]["J_min_shared"],
            "J_min_per_angle": main_fit["shared"]["J_min_per_angle"],
            "uniqueness_second_min_ratio": _uniqueness_ratio(main_fit["shared"]),
            "p_baseline_deg": main_fit["setup"]["p"],
            "q_envelope_deg": main_fit["setup"]["q"],
            "polynomial_basis": "centered_orthogonalized_chebyshev",
            "nsub_estimates": main_fit["nsub_estimates"],
        },
        "multibeam_conditions_si": nc_si,
        "multibeam_improvement_si": mb_si,
        "multibeam_decision_si": mb_decision_si,
        "sic_multibeam_recheck": sic_recheck,
        "two_angle_consistency": two_angle,
        "dispersion_sensitivity": disp_sens,
        "ci_profile_likelihood": ci_payload,
        "anomaly_impact": anom,
        "checks_failed": [c["name"] for c in checks if not c["passed"]],
        "notes": [
            "prob03：硅片（附件3/4）多光束判定 + 厚度反演（formulation_v002）",
            "Q1 多光束必要条件 N1-N4：Rbar=sqrt(R01*R12)<=theta_mb、相干长度、界面平行度、吸收限制",
            "Q2 硅片：主反演=基线-干涉分解 + 一维相位频率扫描（variable projection，两角共享 t），"
            "t 由相位频率唯一确定、与 n_sub 解耦",
            "Q3 SiC 重新判定：prob02 对照（Rbar<=theta_mb → 无显著多光束、无需修正）",
        ],
    }
    solver_payload = {
        "method": "variable_projection_1d_scan（S1 主）+ 两光束 vs Airy 正模型残差改善率（S2 判定）",
        "main_variable_projection": {
            "t_range": main_fit["setup"]["t_range"],
            "t_step": main_fit["setup"]["t_step"],
            "p_baseline_deg": main_fit["setup"]["p"],
            "q_envelope_deg": main_fit["setup"]["q"],
            "shared": {
                "t_hat": main_fit["shared"]["t_hat"],
                "t_hat_refined": main_fit["shared"]["t_hat_refined"],
                "J_min_shared": main_fit["shared"]["J_min_shared"],
            },
            "independent_per_angle": main_fit["indep"]["t_hat_per_angle"],
            "sample_J_curve": _j_curve_sample(main_fit["shared"]),
        },
    }
    verification_payload = {"passed": passed_all, "checks": checks, "method_reference": FORMULA_REFS}
    metadata_payload = {
        "problem_id": "2025-cumcm-b",
        "question_id": "prob03",
        "assumption_version": "assumption_v001",
        "formulation_version": "formulation_v002",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "scenario": {
            "theta_deg": thetas,
            "dispersion_model": dispersion_model,
            "inv_band_cm1": [float(band_lo), float(band_hi)],
            "attachment_si10": str(att_si10),
            "attachment_si15": str(att_si15),
            "attachment_sic10": str(att_sic10),
            "attachment_sic15": str(att_sic15),
            "sic_t_ref_um": sic_t_ref,
            "baseline_poly_deg": main_fit["setup"]["p"],
            "envelope_poly_deg": main_fit["setup"]["q"],
        },
        "input_parameters_yaml_hash": sha256_file(Path(args.input).resolve()),
        "task_config_yaml_hash": sha256_file(Path(args.config).resolve()),
        "unit_conventions": UNIT_CONVENTIONS,
        "formula_refs": FORMULA_REFS,
        "python": sys.version.split()[0],
    }
    mb_conditions_payload = {
        "N1-N4": nc_si["conditions"],
        "si_eta_mb": mb_si,
        "si_mb_decision": mb_decision_si,
        "sic_mb_verdict": sic_recheck,
        "theta_mb": float(rel_conf(config).get("theta_mb", model.THETA_MB)),
        "tau_mb_percent": float(rel_conf(config).get("tau_mb", model.TAU_MB_PERCENT)),
    }

    for name, payload in (
        ("result.json", result_payload),
        ("solver_status.json", solver_payload),
        ("verification.json", verification_payload),
        ("metadata.json", metadata_payload),
        ("preprocessing.json", preprocess_payload),
        ("dispersion_ref.json", dispersion_payload),
        ("mb_conditions.json", mb_conditions_payload),
    ):
        text = json.dumps(_sanitize(payload), ensure_ascii=False, indent=2, default=str) + "\n"
        (output_dir / name).write_text(text, encoding="utf-8")

    # 归档硅反演带内谱（供可视化/复核）
    for idx, att in enumerate(atts_si, start=1):
        theta_tag = f"theta{'10' if idx == 1 else '15'}"
        mask = (att["nu"] >= band_lo) & (att["nu"] <= band_hi)
        nu_band = att["nu"][mask]
        r_band = att["r_obs"][mask]
        w_band = att["weights"][mask]
        n_band = np.asarray(dispersion_for_angle(att, config, dispersion_model), dtype=float)[mask]
        best_model = np.asarray(
            model.forward_reflectance(nu_band, t_hat_shared, n_band, n_sub_hat, thetas[idx - 1]), dtype=float
        )
        np.savetxt(
            output_dir / f"reflectance_{theta_tag}.csv",
            np.column_stack([nu_band, r_band, best_model, w_band]),
            header="nu_cm1,R_obs,R_model_best,weight",
            delimiter=",",
            fmt="%.8f",
            comments="",
        )

    failed_names = [c["name"] for c in checks if not c["passed"]]
    n_passed = sum(1 for c in checks if c["passed"])
    print(f"prob03 反演 {'通过' if passed_all else '失败'}：{n_passed}/{len(checks)} 判据通过")
    print(f"t(硅, variable projection, shared) = {t_hat_shared:.4f} um")
    print(
        f"t(硅, per-angle) = {[round(v, 4) for v in main_fit['indep']['t_hat_per_angle']]} um, "
        f"n_sub(amp) = {n_sub_hat:.4f}"
    )
    print(f"多光束判定（硅）：{mb_decision_si}；η_mb = {mb_si['improvement_percent']:.4f}%")
    print(f"多光束判定（SiC）：{sic_recheck['sic_mb_verdict']}；Rbar_max = {sic_recheck['Rbar_max']:.4e}")
    if failed_names:
        print("未通过判据：" + "；".join(failed_names), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
