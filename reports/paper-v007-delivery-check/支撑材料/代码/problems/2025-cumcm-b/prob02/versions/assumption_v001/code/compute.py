"""prob02 实测反射率谱厚度反演 CLI（computation 阶段由 supervised worker 执行）。

任务：对附件 1（入射角 10°）与附件 2（入射角 15°）的 SiC 晶圆片实测红外反射率谱，
执行 formulation_v003 的厚度反演算法：
  * 主反演谱段截断 ν∈[2000,4000] cm⁻¹（Sellmeier 色散已知区，B6/v003 保留）；
  * **M1（主）= 基线-干涉分解 + 一维相位频率扫描（baseline-robust variable projection）**，
    两角共享 t；t 由干涉相位频率唯一确定，与 n_sub 解耦；
  * M1-ind = 每角独立 t（一致性检验，§7.1）；M1-P1 = 物理正模型 NLS（交叉校验/诊断）；
  * M2 色散相位法、M3 常数 n 基线（初值/交叉验证）；M4 多光束（Airy）诊断（B13）；
  * n_sub 由干涉幅值 A=√(C²+S²) 事后弱辨识（B7）。
  * 可靠性（§7.1–§7.6）：两角一致性嵌套 F 检验、色散敏感性（带内 N-SE/N-SE-δ）+ 谱段截断 Δt_inv_band、
    n_sub 解耦灵敏度诊断、噪声 95% CI（轮廓似然，由 J(t) 曲线）、异常点影响、多光束诊断。

用法：
    python compute.py --config CONFIG --input INPUT --output OUTPUT [--seed SEED]
    python compute.py --self-check          # 仅运行秒级接口探针

输入：
    --config  configs/task_config.yaml  反演场景/附件路径/容差/求解器设置
    --input   formulations/formulation_v003/parameters.yaml （参数登记）
输出目录（--output 或环境变量 AUTOMM_OUTPUT_DIR）：
    result.json        厚度（共享 + 每角）、n_sub 幅度弱辨识、两角度一致性、可靠性判据汇总
    solver_status.json 主 variable projection 扫描状态 + 物理正模型 NLS 交叉校验
    verification.json  检查明细（checks 列表）
    metadata.json      场景、种子、输入/配置 hash、单位约定、公式引用
    preprocessing.json 预处理日志（异常点/剔除/谱段截断/归一化）
    dispersion_ref.json 所用色散模型 n(lam) 对照与锚点核验
    reflectance_theta*.csv  反演带内谱（nu, R_obs, R_model_best, weights）
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

# ---- 单位与公式来源登记（与 formulation_v003 / parameters.yaml 一致） ----
UNIT_CONVENTIONS = {
    "t": "um",
    "nu": "cm^-1",
    "lambda": "um = 1e4 / nu",
    "theta": "degree（三角函数内部转 rad）",
    "delta": "rad",
    "delta_nu": "cm^-1",
    "r": "dimensionless（R% / 100 归一）",
    "g": "cm^-1（相位函数 g=n*nu*cos(theta')）",
}
FORMULA_REFS = {
    "forward_model": "(2.3)/(2.4)",
    "snell": "(2.1)",
    "phase": "(2.2)",
    "fresnel": "(2.3) 内 Fresnel s/p",
    "extremum": "(6.1)",
    "spacing": "(6.1) 方法 A",
    "phase_method": "(6.1)/(6.2)",
    "vp_decomposition": "(5.1)-(5.3)",
    "vp_design_matrix": "(5.4)",
    "vp_linear_ls": "(5.5)",
    "vp_scan": "(5.6)/(5.7)",
    "phase_freq_thickness": "(5.8)/(5.9)",
    "sellmeier": "(4.1)",
    "disp_band_trunc": "(3.1)/(3.2)",
    "ftest": "(7.1)",
    "disp_sensitivity": "(7.2)/(7.3)",
    "nsub_amplitude": "§7.3",
    "ci_profile": "§7.4",
    "reliability": "(7.1)-(7.6)",
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
    return int(config.get("seed", 20260829))


def inv_conf(config: dict) -> dict:
    value = config.get("inversion", {})
    return value if isinstance(value, dict) else {}


def rel_conf(config: dict) -> dict:
    value = config.get("reliability", {})
    return value if isinstance(value, dict) else {}


def band_conf(config: dict) -> tuple[float, float]:
    """主反演谱段 ν_inv（v003 (3.1)）。优先取 config，缺省取 model.INV_BAND_CM1。"""
    inv = inv_conf(config)
    lo = inv.get("inv_band_lo")
    hi = inv.get("inv_band_hi")
    if lo is not None and hi is not None:
        return float(lo), float(hi)
    return float(model.INV_BAND_CM1[0]), float(model.INV_BAND_CM1[1])


def _check_registered(param_map: dict, dispersion_model: str, band_lo: float, band_hi: float) -> None:
    """核验 parameters.yaml 登记值与代码常量一致（不一致只警告，不阻断）。"""
    n_air_reg = param_map.get("n_air", {}).get("value")
    if n_air_reg is not None and abs(float(n_air_reg) - model.N_AIR) > 1e-9:
        print(f"警告：parameters.yaml n_air={n_air_reg} 与代码常量 {model.N_AIR} 不一致", file=sys.stderr)
    nu_c_reg = param_map.get("nu_c", {}).get("value")
    if nu_c_reg is not None and abs(float(nu_c_reg) - model.VC_CM1) > 1e-9:
        print(f"警告：parameters.yaml nu_c={nu_c_reg} 与代码常量 {model.VC_CM1} 不一致", file=sys.stderr)
    nu_inv_reg = param_map.get("nu_inv", {}).get("value")
    if nu_inv_reg is not None:
        nv = [float(v) for v in nu_inv_reg]
        if abs(nv[0] - band_lo) > 1e-9 or abs(nv[1] - band_hi) > 1e-9:
            print(f"警告：parameters.yaml nu_inv={nv} 与反演谱段 {[band_lo, band_hi]} 不一致", file=sys.stderr)
    rest_reg = param_map.get("reststrahlen_exclude", {}).get("value")
    if rest_reg is not None:
        rest = [float(v) for v in rest_reg]
        if (
            abs(rest[0] - model.RESTSTRAHLEN_EXCLUDE_CM1[0]) > 1e-9
            or abs(rest[1] - model.RESTSTRAHLEN_EXCLUDE_CM1[1]) > 1e-9
        ):
            print(
                f"警告：parameters.yaml reststrahlen={rest} 与代码常量 {list(model.RESTSTRAHLEN_EXCLUDE_CM1)} 不一致",
                file=sys.stderr,
            )
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
    if dispersion_model not in {"N-SE", "N-SE-delta", "N-const"}:
        print(f"警告：未知色散模型 {dispersion_model}，按 N-SE 处理", file=sys.stderr)


def load_attachment(path: str | Path) -> dict:
    return model.load_attachment(path)


def dispersion_for_angle(att: dict, config: dict, dispersion_model: str, c_disp: float = 1.0) -> np.ndarray:
    return np.asarray(model.dispersion_epi(att["nu"], model=dispersion_model, c_disp=c_disp), dtype=float)


def inv_band_data(
    atts: list[dict],
    thetas: list[float],
    config: dict,
    dispersion_model: str,
    c_disp: float = 1.0,
) -> dict:
    """将各角度的预处理结果按主反演谱段 ν_inv 截断，返回反演向量集（都在带内）。"""
    lo, hi = band_conf(config)
    nu_list: list[np.ndarray] = []
    r_list: list[np.ndarray] = []
    w_list: list[np.ndarray] = []
    n_list: list[np.ndarray] = []
    for att, theta in zip(atts, thetas):
        mask = (att["nu"] >= lo) & (att["nu"] <= hi)
        n_nu = dispersion_for_angle(att, config, dispersion_model, c_disp)
        nu_list.append(att["nu"][mask])
        r_list.append(att["r_obs"][mask])
        w_list.append(att["weights"][mask])
        n_list.append(n_nu[mask])
    return {"nu_list": nu_list, "r_list": r_list, "w_list": w_list, "n_list": n_list, "thetas": thetas}


def full_band_data(
    atts: list[dict],
    thetas: list[float],
    config: dict,
    dispersion_model: str,
    c_disp: float = 1.0,
) -> dict:
    """全谱数据（用于 Δt_inv_band 报告：ν<2000 采用 λ>5µm 代理色散，不截断）。"""
    r_list = [a["r_obs"] for a in atts]
    w_list = [a["weights"] for a in atts]
    n_list = [dispersion_for_angle(att, config, dispersion_model, c_disp) for att in atts]
    nu_list = [a["nu"] for a in atts]
    return {"nu_list": nu_list, "r_list": r_list, "w_list": w_list, "n_list": n_list, "thetas": thetas}


def per_angle_m2_m3(
    atts: list[dict],
    thetas: list[float],
    config: dict,
    dispersion_model: str,
    n_sub: float,
    c_disp: float = 1.0,
) -> dict:
    """单个角度的 M3（常数 n 间隔法）与 M2（色散化相位法）——都在反演带内，作初值/交叉验证。"""
    data = inv_band_data(atts, thetas, config, dispersion_model, c_disp)
    prom = float(inv_conf(config).get("prominence_rel", 5e-4))
    out: list[dict] = []
    for k, theta in enumerate(thetas):
        nu = data["nu_list"][k]
        r = data["r_list"][k]
        n = data["n_list"][k]
        spacing = None
        try:
            spacing = model.invert_from_spacing(nu, r, theta, n, kind="max", prominence=prom)
        except ValueError:
            spacing = {"t_spacing_um": None, "delta_nu_median": None, "n_eff": None, "extrema_count": 0}
        phase = None
        try:
            phase = model.invert_phase_method(nu, r, theta, n, kind="max", prominence=prom)
        except ValueError:
            phase = {"t_phase_um": None, "delta_g_median": None, "g_pairs": 0, "g_monotonic": False}
        out.append({"theta_deg": theta, "spacing": spacing, "phase": phase})
    return {"angles": out}


def _mean_nsub(estimates: list[dict]) -> float:
    """n_sub 幅度弱辨识估计的平均（过滤 None），无有效值时回退登记初值。"""
    vals = [float(e["n_sub"]) for e in estimates if e.get("n_sub") is not None]
    return float(np.mean(vals)) if vals else float(model.N_SUB_AMP_INIT)


def vp_scan_setup(config: dict) -> dict:
    """主反演扫描配置（t_range/t_step/p/q），与 parameters.yaml 登记值一致（计算前固定）。"""
    inv = inv_conf(config)
    t_lo = float(inv.get("t_scan_lo", model.T_SCAN_RANGE[0]))
    t_hi = float(inv.get("t_scan_hi", model.T_SCAN_RANGE[1]))
    t_step = float(inv.get("t_scan_step", model.T_SCAN_STEP))
    p = int(inv.get("baseline_poly_deg", model.BASELINE_POLY_DEG))
    q = int(inv.get("envelope_poly_deg", model.ENVELOPE_POLY_DEG))
    return {"t_range": (t_lo, t_hi), "t_step": t_step, "p": p, "q": q}


def main_variable_projection(atts, thetas, config, dispersion_model) -> dict:
    """主反演：基线-干涉分解 + 一维相位频率扫描（v003 §5/§6），两角共享 t。

    返回 shared 扫描结果 + 每角独立扫描 + 由幅值 A=√(C²+S²) 弱辨识的 n̂_sub。
    """
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
    # n_sub 幅度弱辨识（B7）：取各角度在共享 t̂ 处的干涉幅值，用带内参考色散反演 R₂→n̂_sub
    nsub_estimates = []
    for k in range(len(thetas)):
        amp = shared["angle_fits"][k]["amplitude"]
        nu_k = data["nu_list"][k]
        n_k = data["n_list"][k]
        n_c = float(np.interp(model.AMP_REF_NU_CM1, nu_k, n_k)) if nu_k.size else None
        est = model.nsub_from_amplitude(amp, n_c, thetas[k]) if n_c is not None else {"n_sub": None}
        nsub_estimates.append(
            {"theta_deg": thetas[k], "amplitude": amp, "n_sub": est["n_sub"], "R1": est["R1"], "R2": est["R2"]}
        )
    return {"shared": shared, "indep": indep, "nsub_estimates": nsub_estimates, "setup": setup}


def two_angle_ftest(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    """§7.1：两角一致性嵌套 F 检验（对相位-频率拟合；M_shared vs M_indep）。"""
    # 统计反演带内有效点数（w>0）作为 n_tot
    data = inv_band_data(atts, thetas, config, dispersion_model)
    n_tot = int(sum(np.count_nonzero(np.asarray(w, dtype=float) > 0.0) for w in data["w_list"]))
    shared_scan = main_fit["shared"]
    indep_scan = main_fit["indep"]
    alpha = float(rel_conf(config).get("alpha_ftest", 0.05))
    ft = model.two_angle_ftest_vp(shared_scan, indep_scan, n_tot=n_tot, alpha=alpha)
    ft["n_tot"] = n_tot
    ft["eps12_threshold_percent"] = float(rel_conf(config).get("tau_12", 2.0))
    return ft


def dispersion_sensitivity(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    """§7.2：带内合法候选 {N-SE, N-SE-δ} 的 Δt_disp；另报告 Δt_inv_band（谱段截断影响）。"""
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
    # Δt_inv_band：全谱（含 ν<2000 色散缺口代理）vp 反演 vs 截断反演
    full_data = full_band_data(atts, thetas, config, dispersion_model)
    t_full = None
    try:
        sc_full = model.variable_projection_scan(
            full_data["nu_list"], full_data["r_list"], full_data["thetas"], full_data["n_list"], full_data["w_list"],
            t_range=setup["t_range"], t_step=setup["t_step"] * 4.0, p=setup["p"], q=setup["q"], shared=True,
        )
        t_full = float(sc_full["t_hat_refined"])
    except (ValueError, FloatingPointError):
        t_full = None
    dt_inv_band = abs(t_base - t_full) / t_base * 100.0 if (t_full is not None and t_base > 0) else None
    return {
        "status": "PASS" if dt_disp <= tau_d else "FAIL",
        "dispersion_models_t": results,
        "delta_t_disp_percent": dt_disp,
        "threshold_percent": tau_d,
        "delta_c_disp": delta,
        "t_truncated_um": t_base,
        "t_full_um": t_full,
        "delta_t_inv_band_percent": dt_inv_band,
        "note": "Δt_inv_band 为谱段截断合理性证据（v002 在错误盆地约 117%），不作主判据",
    }


def nsub_sensitivity_diag(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    """§7.3：t 与 n_sub 解耦灵敏度诊断。

    主反演 t 由相位频率确定、不依赖 n_sub（解耦，Δt_nsub ≈ 0 by construction）；
    另给出物理正模型 NLS（M1-P1，起点 t̂）在不同 n_sub 下 t 的交叉校验灵敏度。
    诊断项（非硬门禁）。
    """
    t_hat = float(main_fit["shared"]["t_hat_refined"])
    data = inv_band_data(atts, thetas, config, dispersion_model)
    amp_est = [e for e in main_fit["nsub_estimates"]]
    n_sub_ref = _mean_nsub(amp_est)
    # 物理正模型 NLS 交叉校验：不同 n_sub 下 t 的灵敏度（探针，非主方法）
    t_at_nsub: dict[str, float | None] = {}
    for label, nsub in (
        ("nsub_amp", n_sub_ref),
        ("nsub_amp_plus", n_sub_ref + 0.10),
        ("nsub_amp_minus", n_sub_ref - 0.10),
    ):
        try:
            fit = model.invert_nls(
                data["nu_list"], data["r_list"], data["thetas"], data["n_list"], data["w_list"],
                t_hat, fit_nsub=False, n_sub_init=float(nsub),
            )
            t_at_nsub[label] = float(fit["t_um"])
        except (ValueError, FloatingPointError):
            t_at_nsub[label] = None
    valid = {k: v for k, v in t_at_nsub.items() if v is not None}
    t_nsub_sens = ((max(valid.values()) - min(valid.values())) / t_hat * 100.0) if valid and t_hat > 0 else None
    tau_diag = float(rel_conf(config).get("tau_nsub_diag", 3.0))
    return {
        "status": "DIAGNOSTIC",
        "main_t_decoupled": True,  # 主方法 t 由相位频率确定、不依赖 n_sub（B7，结构解耦）
        "main_t_nsub_delta_percent": 0.0,  # 主方法 t 与 n_sub 结构解耦（by construction）
        "physical_nls_t_by_nsub": t_at_nsub,
        "physical_nls_t_sensitivity_percent": t_nsub_sens,
        "t_hat_um": t_hat,
        "n_sub_hat_amp": n_sub_ref,
        "threshold_percent": tau_diag,
        "note": "主方法 t 由相位频率确定、与 n_sub 解耦（B7）；物理正模型 NLS 仅作交叉校验灵敏度报告",
    }


def ci_profile_likelihood(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    """§7.4：轮廓似然 95% CI（由 J(t) 曲线，无 bootstrap 之需）。"""
    shared_scan = main_fit["shared"]
    data = inv_band_data(atts, thetas, config, dispersion_model)
    n_tot = int(sum(np.count_nonzero(np.asarray(w, dtype=float) > 0.0) for w in data["w_list"]))
    p = int(shared_scan["p"])
    q = int(shared_scan["q"])
    n_angles = int(shared_scan["n_angles"]) if "n_angles" in shared_scan else len(thetas)
    coef_per_angle = (p + 1) + 2 * (q + 1)
    n_params = n_angles * coef_per_angle + 1  # 共享 t
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
    status = "PASS" if half_rel <= tau_ci else "FAIL"
    out = dict(ci)
    out["status"] = status
    out["threshold_percent"] = tau_ci
    out["t_hat_um"] = float(shared_scan["t_hat_refined"])
    out["method"] = "profile_likelihood_Jcurve（SSE(t) 曲率/夹逼区间；bootstrap 留 computation 备选）"
    return out


def anomaly_impact(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    """§7.5：异常点 剔除 vs 降权 vs 保留 对 t 的影响（重跑主 vp 扫描）。"""
    t_base = float(main_fit["shared"]["t_hat_refined"])
    setup = vp_scan_setup(config)
    t_dict: dict[str, float | None] = {}
    for label, weight_anom in (("downweight", 0.05), ("drop", 0.0), ("keep", 1.0)):
        atts_mod = []
        for att in atts:
            pp = model.preprocess_spectrum(att["nu"], att["r_obs"], weight_anomaly=weight_anom)
            atts_mod.append({"nu": pp["nu"], "r_obs": pp["r_obs"], "weights": pp["weights"]})
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
        "note": "异常点按 weight_anomaly 降权（默认 0.05），原始数据不修改（B2）",
    }


def multibeam_diagnostic(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    """§7.6/B13：两光束 vs 多光束（Airy）模型残差比较（反演带内），诊断是否显著多光束。"""
    t_opt = float(main_fit["shared"]["t_hat_refined"])
    n_sub_hat = _mean_nsub(main_fit["nsub_estimates"])
    data = inv_band_data(atts, thetas, config, dispersion_model)
    best_improve = 0.0
    two_rmse_list = []
    airy_rmse_list = []
    for k, theta in enumerate(thetas):
        nu = data["nu_list"][k]
        r_obs = data["r_list"][k]
        n = data["n_list"][k]
        r_2beam = np.asarray(model.forward_reflectance(nu, t_opt, n, n_sub_hat, theta), dtype=float)
        rmse_2 = float(np.sqrt(np.mean((r_obs - r_2beam) ** 2)))
        r_airy = np.asarray(_airy_reflectance(nu, t_opt, n, n_sub_hat, theta), dtype=float)
        rmse_a = float(np.sqrt(np.mean((r_obs - r_airy) ** 2)))
        if rmse_2 > 0:
            best_improve = max(best_improve, (rmse_2 - rmse_a) / rmse_2 * 100.0)
        two_rmse_list.append(rmse_2)
        airy_rmse_list.append(rmse_a)
    threshold = float(rel_conf(config).get("multibeam_improve_threshold", 10.0))
    needs = best_improve > threshold
    return {
        "two_beam_rmse": two_rmse_list,
        "airy_rmse": airy_rmse_list,
        "improvement_percent": best_improve,
        "needs_multibeam_correction": bool(needs),
        "threshold_percent": threshold,
        "t_used_um": t_opt,
        "n_sub_used": n_sub_hat,
        "note": "prob03 深究 Airy 修正；prob02 仅诊断并记录",
    }


def physical_nls_crosscheck(atts, thetas, config, dispersion_model, main_fit: dict) -> dict:
    """M1-P1：物理正模型 NLS（含基线 + Fresnel 幅度），起点 t̂（v003 §6.4）。"""
    t_hat = float(main_fit["shared"]["t_hat_refined"])
    n_sub_hat = _mean_nsub(main_fit["nsub_estimates"])
    data = inv_band_data(atts, thetas, config, dispersion_model)
    try:
        fit_p1 = model.invert_nls(
            data["nu_list"], data["r_list"], data["thetas"], data["n_list"], data["w_list"],
            t_hat, fit_nsub=False, n_sub_init=n_sub_hat,
        )
        fit_p2 = model.invert_nls(
            data["nu_list"], data["r_list"], data["thetas"], data["n_list"], data["w_list"],
            t_hat, fit_nsub=True, n_sub_init=n_sub_hat,
        )
        ok = bool(abs(fit_p1["t_um"] - t_hat) / t_hat < 5e-2) if t_hat > 0 else False
    except (ValueError, FloatingPointError):
        fit_p1 = fit_p2 = None
        ok = False
    return {
        "t_vp_main_um": t_hat,
        "P1": fit_p1,
        "P2": fit_p2,
        "consistent_with_main": ok,
        "note": "物理正模型 NLS 从主 t̂ 起点局部拟合（不从此远处启动），作交叉校验/诊断（v003 §6.4）",
    }


def _sanitize(obj):
    """递归对输出 payload 做 JSON 可序列化处理。"""
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


def _airy_reflectance(nu: np.ndarray, t_um: float, n_nu: np.ndarray, n_sub: float, theta_deg: float) -> np.ndarray:
    """多光束（Airy）反射率（s/p 平均，含多次反射），用于 §7.6 诊断。"""
    sin_tp = 1.0 * np.sin(np.deg2rad(theta_deg)) / n_nu
    cos_tp = np.sqrt(1 - sin_tp**2)
    sin_tpp = n_nu * sin_tp / n_sub
    cos_tpp = np.sqrt(1 - sin_tpp**2)
    cos_th = np.cos(np.deg2rad(theta_deg))
    r1s = (1.0 * cos_th - n_nu * cos_tp) / (1.0 * cos_th + n_nu * cos_tp)
    r1p = (n_nu * cos_th - 1.0 * cos_tp) / (n_nu * cos_th + 1.0 * cos_tp)
    r2s = (n_nu * cos_tp - n_sub * cos_tpp) / (n_nu * cos_tp + n_sub * cos_tpp)
    r2p = (n_sub * cos_tp - n_nu * cos_tpp) / (n_sub * cos_tp + n_nu * cos_tpp)
    delta = np.asarray(model.phase_delta(nu, t_um, n_nu, theta_deg), dtype=float)
    e = np.exp(1j * delta)

    def airy(r1, r2):
        rt = (r1 + r2 * e) / (1.0 + r1 * r2 * e)
        return np.abs(rt) ** 2

    r_s = airy(r1s, r2s)
    r_p = airy(r1p, r2p)
    return 0.5 * (r_s + r_p)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="prob02 实测反射率谱厚度反演（formulation_v003）")
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
    attachment1 = Path(str(scenario.get("attachment1", "data/2025_cumcm_B/附件1.xlsx"))).resolve()
    attachment2 = Path(str(scenario.get("attachment2", "data/2025_cumcm_B/附件2.xlsx"))).resolve()

    # 参数登记核验（parameters.yaml 是参数权威来源）
    param_map = {str(e["name"]): e for e in input_params.get("parameters", []) if isinstance(e, dict) and e.get("name")}
    _check_registered(param_map, dispersion_model, band_lo, band_hi)

    att1 = load_attachment(attachment1)
    att2 = load_attachment(attachment2)
    pp1 = model.preprocess_spectrum(
        att1["nu"], att1["r_obs"], weight_anomaly=float(inv_conf(config).get("weight_anomaly", 0.05))
    )
    pp2 = model.preprocess_spectrum(
        att2["nu"], att2["r_obs"], weight_anomaly=float(inv_conf(config).get("weight_anomaly", 0.05))
    )
    att1 = {"nu": pp1["nu"], "r_obs": pp1["r_obs"], "weights": pp1["weights"]}
    att2 = {"nu": pp2["nu"], "r_obs": pp2["r_obs"], "weights": pp2["weights"]}
    atts = [att1, att2]
    thetas = [10.0, 15.0]

    # ---- 主反演（M1 = 基线-干涉分解 + 一维相位频率扫描，两角共享 t） ----
    main_fit = main_variable_projection(atts, thetas, config, dispersion_model)
    t_hat_shared = float(main_fit["shared"]["t_hat_refined"])
    n_sub_hat = _mean_nsub(main_fit["nsub_estimates"])
    # ---- 物理正模型 NLS 交叉校验（M1-P1/P2） ----
    cross_check = physical_nls_crosscheck(atts, thetas, config, dispersion_model, main_fit)
    # ---- 方法 M2/M3 交叉验证（带内） ----
    per_angle = per_angle_m2_m3(atts, thetas, config, dispersion_model, n_sub_hat)

    # ---- 可靠性 ----
    two_angle = two_angle_ftest(atts, thetas, config, dispersion_model, main_fit)
    disp_sens = dispersion_sensitivity(atts, thetas, config, dispersion_model, main_fit)
    nsub_sens = nsub_sensitivity_diag(atts, thetas, config, dispersion_model, main_fit)
    ci_payload = ci_profile_likelihood(atts, thetas, config, dispersion_model, main_fit)
    anom = anomaly_impact(atts, thetas, config, dispersion_model, main_fit)
    mbeam = multibeam_diagnostic(atts, thetas, config, dispersion_model, main_fit)

    # ---- 预处理日志 ----
    band_data = inv_band_data(atts, thetas, config, dispersion_model)
    n_points_band = int(sum(np.count_nonzero(np.asarray(w, dtype=float) > 0.0) for w in band_data["w_list"]))
    preprocess_payload = {
        "attachment1": {"path": str(attachment1), "sha256": sha256_file(attachment1), "log": pp1["log"]},
        "attachment2": {"path": str(attachment2), "sha256": sha256_file(attachment2), "log": pp2["log"]},
        "inv_band_cm1": [band_lo, band_hi],
        "n_points_inv_band_all_angles": n_points_band,
        "truncation_rule": (
            f"主反演谱段截断至 ν∈[{band_lo},{band_hi}]（Sellmeier 已知区）；"
            "ν<2000 与 Reststrahlen 不进入主反演；异常点降权 w=weight_anomaly"
        ),
    }
    # ---- 色散核验 ----
    lam_check = np.array([2.5, 3.0, 5.0, 17.0, 20.0, 25.0])
    n_sell = [
        float(np.asarray(model.sellmeier_n4hsi(lam), dtype=float)) if lam <= model.SELLMEIER_BOUNDARY_UM else None
        for lam in lam_check
    ]
    n_se = np.asarray(model.dispersion_epi(model.lambda_to_nu(lam_check), model="N-SE"), dtype=float)
    n_const = np.asarray(model.dispersion_epi(model.lambda_to_nu(lam_check), model="N-const"), dtype=float)
    dispersion_payload = {
        "model": dispersion_model,
        "anchor_checks": {
            "lambda_um": lam_check.tolist(),
            "n_sellmeier": n_sell,
            "n_NSE": n_se.tolist(),
            "n_Nconst": n_const.tolist(),
        },
        "inv_band_cm1": [float(band_lo), float(band_hi)],
        "boundary_vc_cm1": model.VC_CM1,
        "reststrahlen_exclude_cm1": list(model.RESTSTRAHLEN_EXCLUDE_CM1),
        "p_baseline_deg": main_fit["setup"]["p"],
        "q_envelope_deg": main_fit["setup"]["q"],
        "note": (
            "主反演带内 N-SE 退化为纯 Sellmeier（L09）；λ>5µm（ν<2000）仅作 Δt_inv_band 背景"
            "（5-17µm 缺口代理），不进入主反演；基线/包络用中心化正交化（Chebyshev）多项式基"
        ),
    }

    # ---- 评估汇总 ----
    checks = []
    for name, item, passed in (
        ("reliability_two_angle_ftest", two_angle, two_angle["status"] != "FAIL"),
        ("reliability_dispersion", disp_sens, disp_sens["status"] != "FAIL"),
        ("reliability_ci", ci_payload, ci_payload["status"] == "PASS"),
        ("reliability_anomaly", anom, anom["status"] != "FAIL"),
    ):
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "detail": json.dumps(item, ensure_ascii=False),
                "tolerance": str(item.get("threshold_percent")),
            }
        )
    nsub_check = {
        "name": "reliability_nsub_diag",
        "passed": True,  # 诊断项（非硬门禁）：主方法 t 与 n_sub 解耦
        "detail": json.dumps(nsub_sens, ensure_ascii=False),
        "tolerance": str(nsub_sens.get("threshold_percent")),
    }
    checks.append(nsub_check)
    mbeam_check = {
        "name": "reliability_multibeam",
        "passed": bool(not mbeam["needs_multibeam_correction"]),
        "detail": json.dumps(mbeam, ensure_ascii=False),
        "tolerance": str(mbeam.get("threshold_percent")),
    }
    checks.append(mbeam_check)

    passed_all = bool(all(c["passed"] for c in checks))
    feasible = passed_all

    result_payload = {
        "feasible_incumbent": feasible,
        "task": "prob02-epitaxy-thickness",
        "passed": passed_all,
        "theta_deg": thetas,
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
        "physical_nls_crosscheck": cross_check,
        "per_angle_m2_m3": per_angle,
        "two_angle_consistency": two_angle,
        "dispersion_sensitivity": disp_sens,
        "nsub_decoupled_sensitivity": nsub_sens,
        "ci_profile_likelihood": ci_payload,
        "anomaly_impact": anom,
        "multibeam_diagnostic": mbeam,
        "checks_failed": [c["name"] for c in checks if not c["passed"]],
        "notes": [
            "prob02 实测数据反演（formulation_v003）：主反演 = 基线-干涉分解 + 一维相位频率扫描"
            "（variable projection，两角共享 t），t 由干涉相位频率唯一确定、与 n_sub 解耦",
            "多相位频率（g 空间）测厚：t = 1/(2×1e-4·Δg)（B10）；基线/包络用中心化正交化多项式基（p=3/q=1）",
            "色散模型 N-SE（带内纯 Sellmeier，L09）；λ>5µm 仅作 Δt_inv_band 背景（5-17µm 缺口代理，L26 待取数）",
            "Reststrahlen [700,1000] 剔除（w=0）；附件2 反射率 >100% 异常点降权（w=weight_anomaly），不修改原始数据",
            "可靠性判据 §7.1-§7.6（两角一致性嵌套 F 检验/带内色散敏感性+Δt_inv_band/n_sub 解耦诊断/"
            "噪声轮廓似然 CI/异常点影响/多光束诊断），阈值见 parameters.yaml",
        ],
    }
    solver_payload = {
        "method": "variable_projection_1d_scan + scipy.optimize.least_squares (physical cross-check)",
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
        "physical_nls_crosscheck": {
            "P1": cross_check["P1"],
            "P2": cross_check["P2"],
            "tolerances": {
                "ftol": inv_conf(config).get("nls_ftol", 1e-10),
                "xtol": inv_conf(config).get("nls_xtol", 1e-10),
                "gtol": inv_conf(config).get("nls_gtol", 1e-10),
                "max_nfev": inv_conf(config).get("nls_max_nfev", 400),
            },
        },
    }
    verification_payload = {"passed": passed_all, "checks": checks, "method_reference": FORMULA_REFS}
    metadata_payload = {
        "problem_id": "2025-cumcm-b",
        "question_id": "prob02",
        "assumption_version": "assumption_v001",
        "formulation_version": "formulation_v003",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "scenario": {
            "theta_deg": thetas,
            "dispersion_model": dispersion_model,
            "inv_band_cm1": [float(band_lo), float(band_hi)],
            "attachment1": str(attachment1),
            "attachment2": str(attachment2),
            "baseline_poly_deg": main_fit["setup"]["p"],
            "envelope_poly_deg": main_fit["setup"]["q"],
        },
        "input_parameters_yaml_hash": sha256_file(Path(args.input).resolve()),
        "task_config_yaml_hash": sha256_file(Path(args.config).resolve()),
        "unit_conventions": UNIT_CONVENTIONS,
        "formula_refs": FORMULA_REFS,
        "python": sys.version.split()[0],
    }

    for name, payload in (
        ("result.json", result_payload),
        ("solver_status.json", solver_payload),
        ("verification.json", verification_payload),
        ("metadata.json", metadata_payload),
        ("preprocessing.json", preprocess_payload),
        ("dispersion_ref.json", dispersion_payload),
    ):
        text = json.dumps(_sanitize(payload), ensure_ascii=False, indent=2) + "\n"
        (output_dir / name).write_text(text, encoding="utf-8")

    # 归档反演带内谱（供可视化/复核）
    for idx, att in enumerate(atts, start=1):
        theta_tag = f"theta{'10' if idx == 1 else '15'}"
        mask = (att["nu"] >= band_lo) & (att["nu"] <= band_hi)
        nu_band = att["nu"][mask]
        r_band = att["r_obs"][mask]
        w_band = att["weights"][mask]
        n_band = np.asarray(dispersion_for_angle(att, config, dispersion_model), dtype=float)[mask]
        best_model = np.asarray(
            model.forward_reflectance(nu_band, t_hat_shared, n_band, n_sub_hat, thetas[idx - 1]),
            dtype=float,
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
    print(f"prob02 反演 {'通过' if passed_all else '失败'}：{n_passed}/{len(checks)} 判据通过")
    print(f"t(variable projection, shared) = {t_hat_shared:.4f} um")
    print(
        f"t(per-angle) = {[round(v, 4) for v in main_fit['indep']['t_hat_per_angle']]} um, "
        f"n_sub(amp) = {n_sub_hat:.4f}"
    )
    if failed_names:
        print("未通过判据：" + "；".join(failed_names), file=sys.stderr)
    return 0


def _uniqueness_ratio(shared_scan: dict) -> float | None:
    """全局极小与次小"独立候选"的相对残差比（唯一性证据；作报告项）。"""
    j = np.asarray(shared_scan["J_shared"], dtype=float)
    idx = int(np.argmin(j))
    if idx == 0 or idx == j.size - 1:
        return None
    # 排除 t̂ 邻近 ±（三步）的候选，取其余最小值
    lo = max(0, idx - 3)
    hi = min(j.size, idx + 4)
    region = np.concatenate([j[:lo], j[hi:]])
    if region.size == 0:
        return None
    second = float(np.min(region))
    return float(second / j[idx]) if j[idx] > 0 else None


def _j_curve_sample(shared_scan: dict, max_points: int = 200) -> dict:
    """对 J(t) 曲线做等距抽样（避免结果文件过大）。"""
    t = np.asarray(shared_scan["t_grid"], dtype=float)
    j = np.asarray(shared_scan["J_shared"], dtype=float)
    if t.size <= max_points:
        return {"t": t.tolist(), "J": j.tolist()}
    idxs = np.linspace(0, t.size - 1, max_points).astype(int)
    return {"t": t[idxs].tolist(), "J": j[idxs].tolist()}


if __name__ == "__main__":
    raise SystemExit(main())
