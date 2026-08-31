"""prob03 消融实验（ablation_v001）：硅片（附件3/4）厚度反演模型组件/约束必要性检验。

依据 `ablation/preregistration.md` + `ablation/experiment_matrix.yaml`，以**完整模型（F0）为内部对照**，
每次只改变一个目标项（数据 / 随机种子 / 其余配置一致）：
  F0 完整模型：基线-干涉分解 + 一维相位频率扫描（variable projection），N-SE 色散、p=3、q=1、两角共享 t。
  A1 色散项消融：N-SE → N-const（常数 n），检验色散项是否贡献 t̂。
  A2 多光束（Airy）高阶干涉项消融：两光束一阶 VP → 加 Airy 高阶谐波（cos2δ/sin2δ、cos3δ/sin3δ），
      检验多光束复杂度是否改变 t̂（L17 极值不变性，Q1 定量）。
  A3 基线多项式项消融：p=3 → p=0（仅常数 DC 基线），检验基线项是否贡献 t̂。
  A4 两角共享 t 约束消融：shared=True → False（每角独立 t），检验共享约束是否强加偏差。

本问为物理模型 + 可解性反演（非优化问题），主反演为精确/确定性一维扫描 + 每点线性 LS；
消融实验全部为**确定性计算**（实测谱固定，无随机噪声注入），seed 仅用于元数据/可复现性登记。

本模块**复用已审定 model.py**（不修改模型代码，保持 computation/robustness 既有 hash 追踪链稳定）；
Airy 高阶谐波列在_本模块内_局部构造。`compute.py` 为 CLI，`probe.py` 为秒级接口探针。

单位约定（与 formulation_v002 / parameters.yaml 一致）：t[um]、nu[cm^-1]、lambda[um]=1e4/nu、
theta[deg]（三角内转 rad）、delta[rad]、delta_nu[cm^-1]、Rbar 无量纲；R% → R/100 归一。
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

# ---- 预注册判据（运行前固定，不得事后修改；与 preregistration.md / experiment_matrix.yaml 一致） ----
ABLATION_VERSION = "ablation_v001"
REF_T_HAT_UM = 3.447668992836722  # F0 对审定公式实测（computation/robustness 阶段基准，仅供对照/容差）
F0_T_HAT_RANGE_UM = (3.40, 3.49)
DELTA_T_A1_MAX_PERCENT = 2.0  # A1 色散项消融 Δt 阈值
DELTA_T_A2_MAX_PERCENT = 1.0  # A2 多光束高阶项消融 Δt 阈值（L17 极值不变性）
DELTA_T_A3_MAX_PERCENT = 2.0  # A3 基线多项式项消融 Δt 阈值
DELTA_T_A4_MAX_PERCENT = 2.0  # A4 两角共享 t 约束消融 Δt 阈值
EPS12_A4_MAX_PERCENT = 2.0  # A4 每角独立 ε12 阈值
PREREGISTERED = {
    "version": ABLATION_VERSION,
    "F0": {"t_hat_range_um": list(F0_T_HAT_RANGE_UM), "model_in_unit_range": True},
    "A1": {"delta_t_percent_max": DELTA_T_A1_MAX_PERCENT, "ablate": "dispersion N-SE -> N-const"},
    "A2": {"delta_t_percent_max": DELTA_T_A2_MAX_PERCENT, "ablate": "airy high-order harmonics"},
    "A3": {"delta_t_percent_max": DELTA_T_A3_MAX_PERCENT, "ablate": "baseline poly p=3 -> p=0"},
    "A4": {
        "delta_t_percent_max": DELTA_T_A4_MAX_PERCENT,
        "eps12_percent_max": EPS12_A4_MAX_PERCENT,
        "ablate": "shared t -> independent",
    },
    "conclusion_rule": {"all_pass": "components_confirmed", "any_fail": "components_partially_confirmed"},
}

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
    "snell": "(3.1)",
    "phase": "(3.7)",
    "fresnel": "(3.2)-(3.4)",
    "two_beam": "(3.8)",
    "airy": "(3.5)/(3.6)",
    "sellmeier_si": "(6.1)",
    "n1_reflectivity": "(4.1)/(4.2)",
    "extremum_invariance": "(4.7)/(4.8), L17",
    "vp_decomposition": "(7.1)-(7.3)",
    "vp_scan": "(7.4)/(7.5)",
    "phase_freq_thickness": "(3.9)",
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


def load_attachment(path: str | Path) -> dict:
    return model.load_attachment(path)


def preprocess_attachment(att: dict, config: dict) -> dict:
    pp = model.preprocess_spectrum(
        att["nu"],
        att["r_obs"],
        exclude_band=tuple(float(v) for v in config.get("multiphonon_exclude_cm1")),
        weight_anomaly=float(config.get("weight_anomaly", 0.05)),
    )
    return {"nu": pp["nu"], "r_obs": pp["r_obs"], "weights": pp["weights"], "log": pp["log"]}


def band_data(atts: list[dict], thetas: list[float], config: dict, dispersion_model: str) -> dict:
    lo, hi = float(config["inv_band_lo"]), float(config["inv_band_hi"])
    nu_list, r_list, w_list, n_list = [], [], [], []
    for att, theta in zip(atts, thetas):
        mask = (att["nu"] >= lo) & (att["nu"] <= hi)
        n_nu = np.asarray(model.dispersion_epi_si(att["nu"], model=dispersion_model), dtype=float)
        nu_list.append(att["nu"][mask])
        r_list.append(att["r_obs"][mask])
        w_list.append(att["weights"][mask])
        n_list.append(n_nu[mask])
    return {"nu_list": nu_list, "r_list": r_list, "w_list": w_list, "n_list": n_list, "thetas": thetas}


def _scan_setup(config: dict) -> dict:
    return {
        "t_range": (float(config["t_scan_lo"]), float(config["t_scan_hi"])),
        "t_step": float(config["t_scan_step"]),
        "p": int(config["baseline_poly_deg"]),
        "q": int(config["envelope_poly_deg"]),
    }


def _scale_center(nu_list: list[np.ndarray]) -> tuple[float, float]:
    all_nu = np.concatenate([np.asarray(nu, dtype=float) for nu in nu_list])
    nu0 = float(np.mean(all_nu))
    half = max(float(np.max(all_nu) - nu0), float(nu0 - np.min(all_nu)), 1e-12)
    return nu0, half


# ---- Airy 高阶谐波设计矩阵与扫描（A2 消融；局部实现，不修改 model.py） ----
def vp_design_matrix_harm(
    nu_cm1: np.ndarray,
    n_nu: np.ndarray,
    theta_deg: float,
    t_um: float,
    p: int,
    q: int,
    nu0: float,
    half: float,
    extra_harmonics: list[int],
) -> np.ndarray:
    """基线-干涉分解设计矩阵 + Airy 高阶谐波列（cos(mδ)/sin(mδ)，m∈extra_harmonics）。

    基础列 = [B 多项式(0..p), C 多项式(0..q)*cosδ, S 多项式(0..q)*sinδ]（与 model.vp_design_matrix 一致）；
    额外列 = [cos(2δ), sin(2δ), cos(3δ), sin(3δ), ...]（单系数，表示多光束 Airy 高阶反射内容，
    高次反射幅值按 R̄^m 衰减，此处为对两光束一阶模型的复杂度扩充）。
    """
    g = np.asarray(model.phase_function(nu_cm1, n_nu, theta_deg), dtype=float)
    delta = 4.0 * np.pi * 1e-4 * float(t_um) * g
    b_poly = model.poly_basis_cheb(nu_cm1, p, nu0, half)
    c_poly = model.poly_basis_cheb(nu_cm1, q, nu0, half)
    s_poly = model.poly_basis_cheb(nu_cm1, q, nu0, half)
    cols = [b_poly, c_poly * np.cos(delta)[:, None], s_poly * np.sin(delta)[:, None]]
    for m in extra_harmonics:
        cols.append(np.cos(float(m) * delta)[:, None])
        cols.append(np.sin(float(m) * delta)[:, None])
    return np.concatenate(cols, axis=1)


def _linear_ls_harm(phi: np.ndarray, r_obs: np.ndarray, weights: np.ndarray) -> dict:
    w = np.clip(np.asarray(weights, dtype=float), 0.0, None)
    sq_w = np.sqrt(w)
    a = sq_w[:, None] * np.asarray(phi, dtype=float)
    b = sq_w * np.asarray(r_obs, dtype=float)
    beta, _, rank, sv = np.linalg.lstsq(a, b, rcond=None)
    residual = a @ beta - b
    rss = float(np.dot(residual, residual))
    cond = float(sv[0] / sv[-1]) if sv.size and sv[-1] > 0 else float("inf")
    return {"beta": beta, "rss": rss, "rank": int(rank), "cond": cond}


def vp_scan_harm(
    nu_list: list[np.ndarray],
    r_list: list[np.ndarray],
    theta_list: list[float],
    n_list: list[np.ndarray],
    weights_list: list[np.ndarray],
    *,
    t_range: tuple[float, float],
    t_step: float,
    p: int,
    q: int,
    extra_harmonics: list[int],
) -> dict:
    """两角共享 t 的一维相位频率扫描（含 Airy 高阶谐波列，A2）。

    与 model.variable_projection_scan(shared=True) 同构，仅设计矩阵增加 extra_harmonics 列。
    """
    nu0, half = _scale_center(nu_list)
    t_lo, t_hi = float(t_range[0]), float(t_range[1])
    n_points = int(np.floor((t_hi - t_lo) / t_step)) + 1
    t_grid = t_lo + np.arange(n_points) * t_step
    j_shared = np.zeros(n_points, dtype=float)
    per_angle_j = [np.zeros(n_points, dtype=float) for _ in nu_list]
    for i, t in enumerate(t_grid):
        for k in range(len(nu_list)):
            phi = vp_design_matrix_harm(
                nu_list[k], n_list[k], theta_list[k], float(t), p, q, nu0, half, extra_harmonics
            )
            rss = _linear_ls_harm(phi, r_list[k], weights_list[k])["rss"]
            per_angle_j[k][i] = rss
            j_shared[i] += rss
    idx = int(np.argmin(j_shared))
    t_hat = float(t_grid[idx])
    j_min = float(j_shared[idx])
    t_refined = t_hat
    if 0 < idx < n_points - 1:
        _, b, _ = t_grid[idx - 1], t_grid[idx], t_grid[idx + 1]
        ja, jb, jc = j_shared[idx - 1], j_shared[idx], j_shared[idx + 1]
        denom = ja - 2.0 * jb + jc
        if abs(denom) > 1e-15:
            t_refined = float(b + 0.5 * (ja - jc) / denom * t_step)
    angle_fits = []
    for k in range(len(nu_list)):
        phi = vp_design_matrix_harm(
            nu_list[k], n_list[k], theta_list[k], t_refined, p, q, nu0, half, extra_harmonics
        )
        fit = _linear_ls_harm(phi, r_list[k], weights_list[k])
        angle_fits.append({"theta_deg": theta_list[k], "rss": fit["rss"], "rank": fit["rank"], "cond": fit["cond"]})
    return {
        "mode": "shared_harm", "shared": True, "extra_harmonics": extra_harmonics,
        "nu_ref": nu0, "half_width": half, "p": p, "q": q,
        "t_hat": t_hat, "t_hat_refined": t_refined, "J_min_shared": j_min,
        "t_grid": t_grid, "J_shared": j_shared,
        "J_min_per_angle": [float(j[idx]) for j in per_angle_j],
        "angle_fits": angle_fits,
    }


def _weighted_rmse(scan: dict, data: dict) -> float:
    """按 PSD 权重计算最优拟合加权 RMSE（sqrt(sum(w r^2)/sum(w))）。"""
    t = float(scan["t_hat_refined"])
    nu0, half = scan["nu_ref"], scan["half_width"]
    p, q = int(scan["p"]), int(scan["q"])
    num, den = 0.0, 0.0
    for k in range(len(data["thetas"])):
        phi = model.vp_design_matrix(data["nu_list"][k], data["n_list"][k], data["thetas"][k], t, p, q, nu0, half)
        fit = model.vp_linear_ls(phi, data["r_list"][k], data["w_list"][k])
        w = np.asarray(data["w_list"][k], dtype=float)
        resid = np.asarray(data["r_list"][k], dtype=float) - (
            phi @ fit["beta"]
        )
        num += float(np.dot(w, resid * resid))
        den += float(np.sum(w))
    return float(np.sqrt(num / den)) if den > 0 else float("inf")


def _physical_r_range(scan: dict, data: dict, n_sub: float) -> dict:
    """以最佳 t̂ 计算两光束物理正模型反射率范围，检验能量守恒 R∈[0,1]。"""
    t = float(scan["t_hat_refined"])
    lo, hi = 1.0, 0.0
    for k in range(len(data["thetas"])):
        r = np.asarray(
            model.forward_reflectance(
                data["nu_list"][k], t, data["n_list"][k], n_sub, data["thetas"][k]
            ),
            dtype=float,
        )
        lo = min(lo, float(np.min(r)))
        hi = max(hi, float(np.max(r)))
    return {"R_min": lo, "R_max": hi, "in_unit_interval": bool(lo >= 0.0 and hi <= 1.0)}


def _delta_t(a: float, b: float) -> float:
    return abs(float(a) - float(b)) / max(abs(float(b)), 1e-12) * 100.0


def run_experiments(config: dict) -> dict:
    """执行 F0 + A1–A4 消融（每次只改变一个目标项）。"""
    thetas = [float(v) for v in config["theta_deg"]]
    att_si10 = Path(str(config["attachment_si10"])).resolve()
    att_si15 = Path(str(config["attachment_si15"])).resolve()
    att3 = preprocess_attachment(load_attachment(att_si10), config)
    att4 = preprocess_attachment(load_attachment(att_si15), config)
    atts = [att3, att4]
    seed = int(config.get("seed", 20260830))
    setup = _scan_setup(config)

    experiments: dict[str, dict] = {}
    f0_ref: float = REF_T_HAT_UM

    # ---- F0 完整模型（内部对照）: VP, N-SE, p=3, q=1, shared=True ----
    f0_data = band_data(atts, thetas, config, "N-SE")
    f0_scan = model.variable_projection_scan(
        f0_data["nu_list"], f0_data["r_list"], f0_data["thetas"], f0_data["n_list"], f0_data["w_list"],
        t_range=setup["t_range"], t_step=setup["t_step"], p=setup["p"], q=setup["q"], shared=True,
    )
    f0_t = float(f0_scan["t_hat_refined"])
    f0_ref = f0_t
    # n_sub：由幅值弱辨识，仅用于物理正模型 R∈[0,1] 检查，不影响 t̂ 消融
    nsub_est = _mean_nsub_est(atts, thetas, config, f0_scan)
    f0_rrange = _physical_r_range(f0_scan, f0_data, nsub_est)
    f0_rmse = _weighted_rmse(f0_scan, f0_data)
    f0_pass = bool(
        F0_T_HAT_RANGE_UM[0] <= f0_t <= F0_T_HAT_RANGE_UM[1] and f0_rrange["in_unit_interval"]
    )
    experiments["F0"] = {
        "ablate": "无（完整模型内部对照）",
        "t_hat_um": f0_t,
        "t_hat_per_angle_um": f0_scan.get("t_hat_per_angle", []),
        "J_min": f0_scan["J_min_shared"],
        "weighted_rmse": f0_rmse,
        "R_range": f0_rrange,
        "uniqueness_second_min_ratio": None,
        "n_sub_hat": nsub_est,
        "passed": f0_pass,
        "pass_detail": {"t_in_range": bool(F0_T_HAT_RANGE_UM[0] <= f0_t <= F0_T_HAT_RANGE_UM[1]),
                        "R_in_unit_interval": f0_rrange["in_unit_interval"]},
    }

    # ---- A1 色散项消融（N-SE → N-const） ----
    a1_data = band_data(atts, thetas, config, "N-const")
    a1_scan = model.variable_projection_scan(
        a1_data["nu_list"], a1_data["r_list"], a1_data["thetas"], a1_data["n_list"], a1_data["w_list"],
        t_range=setup["t_range"], t_step=setup["t_step"], p=setup["p"], q=setup["q"], shared=True,
    )
    a1_t = float(a1_scan["t_hat_refined"])
    experiments["A1"] = {
        "ablate": "色散模型 N-SE → N-const",
        "t_hat_um": a1_t,
        "delta_t_percent": _delta_t(a1_t, f0_ref),
        "criterion_max_percent": DELTA_T_A1_MAX_PERCENT,
        "passed": bool(_delta_t(a1_t, f0_ref) <= DELTA_T_A1_MAX_PERCENT),
        "weighted_rmse": _weighted_rmse(a1_scan, a1_data),
        "uniqueness_second_min_ratio": _uniqueness_ratio_from_scan(a1_scan),
    }

    # ---- A2 多光束（Airy）高阶干涉项消融（加 cos2δ/sin2δ、cos3δ/sin3δ） ----
    harm = [2, 3]
    a2_data = band_data(atts, thetas, config, "N-SE")
    a2_scan = vp_scan_harm(
        a2_data["nu_list"], a2_data["r_list"], a2_data["thetas"], a2_data["n_list"], a2_data["w_list"],
        t_range=setup["t_range"], t_step=setup["t_step"], p=setup["p"], q=setup["q"], extra_harmonics=harm,
    )
    a2_t = float(a2_scan["t_hat_refined"])
    experiments["A2"] = {
        "ablate": "加 Airy 高阶谐波列 cos2δ/sin2δ、cos3δ/sin3δ",
        "t_hat_um": a2_t,
        "delta_t_percent": _delta_t(a2_t, f0_ref),
        "criterion_max_percent": DELTA_T_A2_MAX_PERCENT,
        "passed": bool(_delta_t(a2_t, f0_ref) <= DELTA_T_A2_MAX_PERCENT),
        "weighted_rmse": _weighted_rmse_from_tuple_scan(a2_scan, a2_data),
        "J_min": a2_scan["J_min_shared"],
        "extra_harmonics": harm,
    }

    # ---- A3 基线多项式项消融（p=3 → p=0） ----
    a3_data = band_data(atts, thetas, config, "N-SE")
    a3_setup = dict(setup)
    a3_setup["p"] = 0
    a3_scan = model.variable_projection_scan(
        a3_data["nu_list"], a3_data["r_list"], a3_data["thetas"], a3_data["n_list"], a3_data["w_list"],
        t_range=a3_setup["t_range"], t_step=a3_setup["t_step"], p=a3_setup["p"], q=a3_setup["q"], shared=True,
    )
    a3_t = float(a3_scan["t_hat_refined"])
    experiments["A3"] = {
        "ablate": "基线多项式 p=3 → p=0（仅常数 DC 基线）",
        "t_hat_um": a3_t,
        "delta_t_percent": _delta_t(a3_t, f0_ref),
        "criterion_max_percent": DELTA_T_A3_MAX_PERCENT,
        "passed": bool(_delta_t(a3_t, f0_ref) <= DELTA_T_A3_MAX_PERCENT),
        "weighted_rmse": _weighted_rmse_from_pq(scan=a3_scan, data=a3_data, p=a3_setup["p"], q=a3_setup["q"]),
    }

    # ---- A4 两角共享 t 约束消融（shared=True → False） ----
    a4_data = band_data(atts, thetas, config, "N-SE")
    a4_scan = model.variable_projection_scan(
        a4_data["nu_list"], a4_data["r_list"], a4_data["thetas"], a4_data["n_list"], a4_data["w_list"],
        t_range=setup["t_range"], t_step=setup["t_step"], p=setup["p"], q=setup["q"], shared=False,
    )
    a4_t = a4_scan["t_hat_per_angle"]
    t1, t2 = float(a4_t[0]), float(a4_t[1])
    tbar = 0.5 * (t1 + t2)
    eps12 = abs(t1 - t2) / tbar * 100.0 if tbar > 0 else float("inf")
    max_dev = max(abs(t1 - f0_ref), abs(t2 - f0_ref)) / f0_ref * 100.0
    a4_pass = bool(max_dev <= DELTA_T_A4_MAX_PERCENT and eps12 <= EPS12_A4_MAX_PERCENT)
    experiments["A4"] = {
        "ablate": "两角共享 t 约束：shared=True → False（每角独立 t）",
        "t_hat_per_angle_um": [t1, t2],
        "t_hat_shared_ref_um": f0_ref,
        "delta_t_vs_shared_percent": max_dev,
        "eps12_percent": eps12,
        "criterion_max_percent": DELTA_T_A4_MAX_PERCENT,
        "eps12_max_percent": EPS12_A4_MAX_PERCENT,
        "passed": a4_pass,
    }

    summary = _build_summary(experiments)
    return {"experiments": experiments, "summary": summary, "thetas": thetas, "seed": seed}


def _mean_nsub_est(atts: list[dict], thetas: list[float], config: dict, f0_scan: dict) -> float:
    """由 F0 共享 t̂ 处干涉幅值弱辨识 n_sub（仅用于物理正模型 R∈[0,1] 检查，不影响 t̂ 消融）。"""
    data = band_data(atts, thetas, config, "N-SE")
    t = float(f0_scan["t_hat_refined"])
    nu0, half = f0_scan["nu_ref"], f0_scan["half_width"]
    p, q = int(f0_scan["p"]), int(f0_scan["q"])
    sub_vals = []
    for k in range(len(thetas)):
        phi = model.vp_design_matrix(data["nu_list"][k], data["n_list"][k], thetas[k], t, p, q, nu0, half)
        fit = model.vp_linear_ls(phi, data["r_list"][k], data["w_list"][k])
        beta = fit["beta"]
        b_cols = p + 1
        c_cols = q + 1
        c_beta = beta[b_cols : b_cols + c_cols]
        s_beta = beta[b_cols + c_cols : b_cols + 2 * c_cols]
        c_poly = model.poly_basis_cheb(np.asarray([model.AMP_REF_NU_CM1], dtype=float), q, nu0, half)
        s_poly = model.poly_basis_cheb(np.asarray([model.AMP_REF_NU_CM1], dtype=float), q, nu0, half)
        c_val = float((c_poly @ c_beta)[0])
        s_val = float((s_poly @ s_beta)[0])
        amp = float(np.hypot(c_val, s_val))
        n_c = float(np.interp(model.AMP_REF_NU_CM1, data["nu_list"][k], data["n_list"][k]))
        est = model.nsub_from_amplitude(amp, n_c, thetas[k])
        if est.get("n_sub") is not None:
            sub_vals.append(float(est["n_sub"]))
    return float(np.mean(sub_vals)) if sub_vals else float(model.N_SUB_SI_INIT)


def _uniqueness_ratio_from_scan(scan: dict) -> float | None:
    j = np.asarray(scan["J_shared"], dtype=float)
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


def _weighted_rmse_from_pq(scan: dict, data: dict, p: int, q: int) -> float:
    t = float(scan["t_hat_refined"])
    nu0, half = scan["nu_ref"], scan["half_width"]
    num, den = 0.0, 0.0
    for k in range(len(data["thetas"])):
        phi = model.vp_design_matrix(data["nu_list"][k], data["n_list"][k], data["thetas"][k], t, p, q, nu0, half)
        fit = model.vp_linear_ls(phi, data["r_list"][k], data["w_list"][k])
        w = np.asarray(data["w_list"][k], dtype=float)
        resid = np.asarray(data["r_list"][k], dtype=float) - phi @ fit["beta"]
        num += float(np.dot(w, resid * resid))
        den += float(np.sum(w))
    return float(np.sqrt(num / den)) if den > 0 else float("inf")


def _weighted_rmse_from_tuple_scan(scan: dict, data: dict) -> float:
    t = float(scan["t_hat_refined"])
    nu0, half = scan["nu_ref"], scan["half_width"]
    p, q = int(scan["p"]), int(scan["q"])
    harm = list(scan["extra_harmonics"])
    num, den = 0.0, 0.0
    for k in range(len(data["thetas"])):
        phi = vp_design_matrix_harm(
            data["nu_list"][k], data["n_list"][k], data["thetas"][k], t, p, q, nu0, half, harm
        )
        fit = _linear_ls_harm(phi, data["r_list"][k], data["w_list"][k])
        w = np.asarray(data["w_list"][k], dtype=float)
        resid = np.asarray(data["r_list"][k], dtype=float) - phi @ fit["beta"]
        num += float(np.dot(w, resid * resid))
        den += float(np.sum(w))
    return float(np.sqrt(num / den)) if den > 0 else float("inf")


def _build_summary(experiments: dict) -> list[dict]:
    rows = []
    for name in ("F0", "A1", "A2", "A3", "A4"):
        e = experiments.get(name)
        if e is None:
            continue
        row = {"experiment": name, "ablate": e.get("ablate", "")}
        row["t_hat_um"] = e.get("t_hat_um")
        row["t_hat_per_angle_um"] = e.get("t_hat_per_angle_um")
        row["delta_t_percent"] = e.get("delta_t_percent")
        row["eps12_percent"] = e.get("eps12_percent")
        row["weighted_rmse"] = e.get("weighted_rmse")
        row["R_in_unit_interval"] = e.get("R_range", {}).get("in_unit_interval")
        row["passed"] = e.get("passed")
        rows.append(row)
    return rows


def _sanitize(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "beta" and isinstance(v, np.ndarray):
                out[k] = v.tolist()
            elif k == "J_shared" and isinstance(v, np.ndarray):
                out[k] = v.tolist()
            elif k == "t_grid" and isinstance(v, np.ndarray):
                out[k] = v.tolist()
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
    parser = argparse.ArgumentParser(description="prob03 消融实验（ablation_v001）：硅片厚度模型组件/约束必要性检验")
    parser.add_argument("--config", help="ablation_config.yaml 路径（附件路径/反演设置）")
    parser.add_argument("--input", help="formulation parameters.yaml 路径（参数登记/追踪）")
    parser.add_argument("--output", help="输出目录（优先使用环境变量 AUTOMM_OUTPUT_DIR）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（优先使用环境变量 AUTOMM_SEED）")
    parser.add_argument("--self-check", action="store_true", help="仅运行秒级接口探针")
    args = parser.parse_args(argv)

    if args.self_check:
        checks = _self_check()
        for name, passed in sorted(checks.items()):
            print(f"{'PASS' if passed else 'FAIL'}  {name}")
        ok = all(checks.values())
        print(f"probe 汇总：{sum(checks.values())}/{len(checks)} 通过")
        return 0 if ok else 1

    if not args.config or not args.input:
        parser.error("--config 与 --input 为必填（--self-check 除外）")

    config = load_yaml(Path(args.config).resolve())
    scenario = config.get("scenario", config)
    input_path = Path(args.input).resolve()
    output_dir = resolve_output(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    seed = resolve_seed(args.seed, scenario)

    result = run_experiments(scenario)
    experiments = result["experiments"]
    summary = result["summary"]

    checks = []
    for name in ("F0", "A1", "A2", "A3", "A4"):
        e = experiments.get(name, {})
        checks.append(
            {
                "name": f"ablation_{name}",
                "passed": bool(e.get("passed", False)),
                "detail": json.dumps(_sanitize(e), ensure_ascii=False, default=str),
                "criterion": json.dumps(PREREGISTERED.get(name, {}), ensure_ascii=False, default=str),
            }
        )
    all_pass = all(c["passed"] for c in checks)
    rule = PREREGISTERED["conclusion_rule"]
    conclusion = rule["all_pass"] if all_pass else rule["any_fail"]

    result_payload = {
        "feasible_incumbent": all_pass,
        "task": "prob03-ablation-components",
        "passed": all_pass,
        "conclusion": conclusion,
        "ablation_version": ABLATION_VERSION,
        "ref_t_hat_f0_um": experiments["F0"]["t_hat_um"],
        "experiments": _sanitize(experiments),
        "notes": [
            "prob03 ablation_v001：完整模型内部对照（F0）+ A1 色散项 / A2 多光束（Airy）高阶项",
            "  / A3 基线多项式项 / A4 两角共享 t 约束",
            "每次只改变一个目标项，数据/随机种子/其余配置一致；主反演=基线-干涉分解",
            "  + 一维相位频率扫描（variable projection）",
            "A1/A3/A4 检验复杂度项对 t̂ 是否贡献；A2 检验多光束（Airy）高阶是否改变 t̂",
            "  （L17 极值不变性/Q1 定量）",
        ],
    }
    summary_payload = {
        "rows": [_sanitize(r) for r in summary],
        "conclusion": conclusion,
        "ref_t_hat_f0_um": experiments["F0"]["t_hat_um"],
    }
    verification_payload = {"passed": all_pass, "checks": checks, "method_reference": FORMULA_REFS}
    metadata_payload = {
        "problem_id": "2025-cumcm-b",
        "question_id": "prob03",
        "assumption_version": "assumption_v001",
        "formulation_version": "formulation_v002",
        "ablation_version": ABLATION_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "scenario": {
            "theta_deg": result["thetas"],
            "inv_band_cm1": [float(scenario["inv_band_lo"]), float(scenario["inv_band_hi"])],
            "attachment_si10": str(scenario["attachment_si10"]),
            "attachment_si15": str(scenario["attachment_si15"]),
            "baseline_poly_deg": int(scenario["baseline_poly_deg"]),
            "envelope_poly_deg": int(scenario["envelope_poly_deg"]),
            "t_scan_range": [float(scenario["t_scan_lo"]), float(scenario["t_scan_hi"])],
            "t_scan_step": float(scenario["t_scan_step"]),
        },
        "input_parameters_yaml_hash": sha256_file(input_path),
        "ablation_config_yaml_hash": sha256_file(Path(args.config).resolve()),
        "unit_conventions": UNIT_CONVENTIONS,
        "formula_refs": FORMULA_REFS,
        "python": sys.version.split()[0],
    }

    for name, payload in (
        ("result.json", result_payload),
        ("summary.json", summary_payload),
        ("checks.json", verification_payload),
        ("metadata.json", metadata_payload),
    ):
        text = json.dumps(_sanitize(payload), ensure_ascii=False, indent=2, default=str) + "\n"
        (output_dir / name).write_text(text, encoding="utf-8")

    n_ok = sum(c["passed"] for c in checks)
    print(f"prob03 ablation {'通过' if all_pass else '失败'}：conclusion={conclusion}, 判据 {n_ok}/{len(checks)}")
    print(f"F0 t̂={experiments['F0']['t_hat_um']:.4f} um")
    for name in ("A1", "A2", "A3", "A4"):
        e = experiments[name]
        print(f"{name} Δt%={e.get('delta_t_percent')} / eps12%={e.get('eps12_percent')} / passed={e.get('passed')}")
    if not all_pass:
        failed = [c["name"] for c in checks if not c["passed"]]
        print("未通过判据：" + "；".join(failed), file=sys.stderr)
    return 0


def _self_check() -> dict[str, bool]:
    """秒级接口探针：核验消融机制（确定性小计算，不运行完整数据集）。"""
    checks: dict[str, bool] = {}

    def _near(a: float, b: float, tol: float = 2e-3) -> bool:
        return abs(float(a) - float(b)) / max(abs(float(b)), 1e-12) < tol

    # 1. 硅 Sellmeier / 常数 n 色散模型可调用
    nu_band = np.linspace(2000.0, 4000.0, 40)
    n_se = np.asarray(model.dispersion_epi_si(nu_band, model="N-SE"), dtype=float)
    n_const = np.asarray(model.dispersion_epi_si(nu_band, model="N-const"), dtype=float)
    n_se_ref = np.asarray(model.sellmeier_si(1e4 / nu_band), dtype=float)
    checks["dispersion_nse_inv_band"] = bool(np.allclose(n_se, n_se_ref, rtol=1e-9))
    checks["dispersion_nconst_constant"] = bool(np.allclose(n_const, n_const[0], atol=1e-12))
    checks["dispersion_nconst_differs"] = bool(_near(n_const[0], 3.4221) or _near(n_const[0], 3.43, 5e-2))

    # 2. Airy 高阶谐波设计矩阵列数 = 基础列 + 2*len(harm)
    p, q, harm = 3, 1, [2, 3]
    base = model.vp_design_matrix(nu_band, n_se, 10.0, 3.4477, p, q, 2500.0, 750.0)
    harm_phi = vp_design_matrix_harm(nu_band, n_se, 10.0, 3.4477, p, q, 2500.0, 750.0, harm)
    checks["harm_matrix_cols"] = bool(harm_phi.shape[1] == base.shape[1] + 2 * len(harm))

    # 3. 合成谱上 F0（两光束一阶）与 A2（加高阶谐波）t̂ 应一致（验证 L17：高阶不放宽度）
    rng = np.random.default_rng(7)
    t_true, n_sub_true = 3.45, 3.05
    band_nu = np.linspace(2000.0, 4000.0, 300)
    band_n = np.asarray(model.dispersion_epi_si(band_nu, model="N-SE"), dtype=float)
    r_s = (
        np.asarray(model.forward_reflectance(band_nu, t_true, band_n, n_sub_true, 10.0), dtype=float)
        + 0.006
        + 0.0008 * (band_nu - 2000.0) / 2000.0
        + rng.normal(0.0, 1e-4, band_nu.shape)
    )
    w = np.ones(band_nu.shape)
    f0_scan = model.variable_projection_scan(
        [band_nu], [r_s], [10.0], [band_n], [w], t_range=(2.0, 12.0), t_step=0.05, p=3, q=1, shared=True
    )
    harm_scan = vp_scan_harm(
        [band_nu], [r_s], [10.0], [band_n], [w], t_range=(2.0, 12.0), t_step=0.05, p=3, q=1, extra_harmonics=[2, 3]
    )
    checks["f0_recovers_true_t"] = bool(abs(f0_scan["t_hat_refined"] - t_true) / t_true < 2e-2)
    checks["harm_recovers_same_t"] = bool(
        abs(harm_scan["t_hat_refined"] - f0_scan["t_hat_refined"]) / f0_scan["t_hat_refined"] < 2e-2
    )

    # 4. 基线 p=0 vs p=3 扫描均可运行
    p0_scan = model.variable_projection_scan(
        [band_nu], [r_s], [10.0], [band_n], [w], t_range=(2.0, 12.0), t_step=0.05, p=0, q=1, shared=True
    )
    checks["p0_scan_runs"] = bool(np.isfinite(p0_scan["t_hat_refined"]))

    # 5. 独立（shared=False）扫描可运行
    indep_scan = model.variable_projection_scan(
        [band_nu, band_nu], [r_s, r_s], [10.0, 15.0], [band_n, band_n], [w, w],
        t_range=(2.0, 12.0), t_step=0.05, p=3, q=1, shared=False,
    )
    t_hat_indep = indep_scan["t_hat_per_angle"]
    checks["indep_scan_runs"] = bool(len(t_hat_indep) == 2 and np.all(np.isfinite(t_hat_indep)))

    # 6. 预注册常量与实验矩阵一致（粗核验：A2 阈值 ≤ A1/A3/A4）
    checks["preregistered_thresholds_consistent"] = bool(
        DELTA_T_A2_MAX_PERCENT <= DELTA_T_A1_MAX_PERCENT and DELTA_T_A2_MAX_PERCENT <= DELTA_T_A3_MAX_PERCENT
    )

    return checks


if __name__ == "__main__":  # pragma: no cover - 仅用于手动/探针入口
    raise SystemExit(main())
