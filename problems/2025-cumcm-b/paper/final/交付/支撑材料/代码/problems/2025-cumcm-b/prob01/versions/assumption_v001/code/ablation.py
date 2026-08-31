"""prob01 ablation 消融实验 CLI（ablation 阶段，由 supervised worker 执行）。

在合成基准场景（assumption_v001 / formulation_v001：t_true=10um、n_sub=3.0、
theta=10/15°、full 谱段 [400,4000] cm^-1、弱色散反演段 [2000,4000] cm^-1、
Reststrahlen 区 [700,1000] cm^-1 排除）下，以完整模型为内部对照，对公式项与
算法模块执行预注册的四组消融（完整方案见 ablation/preregistration.md，
判据运行前固定，不能事后修改）：

F0 完整模型对照：M1 色散化两光束 Fresnel 模型 (3.5)/(3.6) + 全谱 NLS 多初值
A1 干涉叠加项消融：移除 (3.5) 的 2(1-R1)sqrt(R1R2)cos(delta) 项 -> 非相干模型
   （A11 相干性失效极限）——检验干涉项是否承载全部厚度信息（预期：不可辨识）
A2 衬底界面反射消融：R2 -> 0（无衬底模型）——检验第二界面反射是否为条纹必要
   条件（预期：不可辨识）
A3 偏振平均消融：s/p 平均 (3.6) 替换为单 s / 单 p 反演——检验偏振平均是否为
   安全简化（预期：不敏感）
A4 多初值模块消融：移除 NLS ±period 布点，仅方法 A 解析初值单次 NLS——检验
   多初值模块是否必要（预期：单初值落入周期歧义局部极小）

prob01 无附件实测数据，本任务基于正模型合成谱检验模型组件与算法模块必要性，
与 robustness（输入/情景不确定性）互补，直接支撑 prob02 反演方法选择的证据链。

用法：
    python ablation.py --config CONFIG --input INPUT --output OUTPUT [--seed SEED]
    python ablation.py --self-check          # 秒级接口探针（静态检查用）

输出（--output 目录，即 results/ablation/）：
    result.json            实验级汇总：各消融判定、conclusion、feasible_incumbent
    summary.json           汇总表：F0 + A1-A4 的 t、rmse、平坦度/深度比、判定
    checks.json            预注册判据逐条检查（预期 vs 实测）
    metadata.json          场景、种子、输入/配置 hash、单位约定、公式引用
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

# ---- 单位与公式来源登记（与 formulation.md / parameters.yaml 一致） ----
UNIT_CONVENTIONS = {
    "t": "um",
    "nu": "cm^-1",
    "lambda": "um = 1e4 / nu",
    "theta": "degree（三角函数内部转 rad）",
    "n_sub": "dimensionless",
    "R": "dimensionless（0-1，能量守恒）",
}
FORMULA_REFS = {
    "forward_model": "(3.5)/(3.6)",
    "snell": "(2.1)-(2.3)",
    "fresnel": "(3.1)-(3.3)",
    "extremum": "(3.7)",
    "spacing": "(3.8)-(3.10)",
    "phase_method": "(3.11)-(3.13)",
    "sellmeier": "(4.1)",
    "period_ambiguity": "formula_validation §6",
}

# ---- 预注册方案（ablation/preregistration.md 的机器可读镜像；运行前固定） ----
# 消融判据：F0/A1-A4 各自的判定条件（预期方向在 preregistration.md §2 固定）。
PREREGISTERED = {
    "version": "ablation_v001",
    "base_scenario": {
        "t_true_um": 10.0,
        "n_sub": 3.0,
        "theta_deg": [10.0, 15.0],
        "nu_range_cm1": [400.0, 4000.0],
        "weak_band_cm1": [2000.0, 4000.0],
        "reststrahlen_exclude_cm1": [700.0, 1000.0],
    },
    "identifiability": {
        "t_lo_um": 1.0,
        "t_hi_um": 25.0,
        "n_grid": 200,
        "flatness_threshold": 0.05,
        "eps": 1e-12,
    },
    "criteria": {
        "f0": {
            "rel_err_threshold": 0.01,
            "rmse_depth_ratio": 100.0,
            "note": "F0 对照：NLS 厚度相对真值最大误差 <= 1% 且 rmse(t) 深度比 >= 100（t_true 处全局极小）",
        },
        "a1": {
            "flatness_threshold": 0.05,
            "note": "A1 干涉项消融：rmse(t) 网格平坦度 <= 5% -> 厚度不可辨识 -> 干涉项必要",
        },
        "a2": {
            "flatness_threshold": 0.05,
            "note": "A2 衬底界面反射消融：rmse(t) 网格平坦度 <= 5% -> 厚度不可辨识 -> 衬底反射项必要",
        },
        "a3": {
            "pol_pairwise_tol": 0.01,
            "note": "A3 偏振平均消融：s/p/avg 三种反演厚度最大相对差 <= 1% -> 偏振平均为非关键简化",
        },
        "a4": {
            "single_init_err_threshold": 0.02,
            "multi_init_err_threshold": 0.01,
            "note": "A4 多初值模块消融：单初值误差 > 2%（落入周期歧义局部极小）且多初值 <= 1% -> 多初值模块必要",
        },
    },
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


def exp_config(config: dict) -> dict:
    value = config.get("ablation", {})
    return value if isinstance(value, dict) else {}


def base_nu(config: dict) -> np.ndarray:
    scenario = config.get("scenario", {})
    registered = exp_config(config).get("nu_range_cm1", PREREGISTERED["base_scenario"]["nu_range_cm1"])
    lo = float(scenario.get("nu_min_cm1", registered[0]))
    hi = float(scenario.get("nu_max_cm1", registered[1]))
    points = int(scenario.get("nu_points", 3601))
    return np.linspace(lo, hi, points)


def ident_config(config: dict) -> dict:
    value = exp_config(config).get("identifiability", {})
    merged = dict(PREREGISTERED["identifiability"])
    if isinstance(value, dict):
        merged.update(value)
    return merged


def interface_avg_reflectivities(
    n_nu: np.ndarray, n_sub: float, theta_deg: float, n_air: float = model.N_AIR
) -> tuple[np.ndarray, np.ndarray]:
    """逐点计算 s/p 平均界面强度反射率 (R1_avg, R2_avg)（(3.1)-(3.3) + (3.6) 平均）。

    供 A1/A2 消融模型使用；n_nu 为色散折射率数组（逐点计算 Snell 折射角与 Fresnel 系数）。
    """
    n_arr = np.asarray(n_nu, dtype=float)
    r1_list: list[float] = []
    r2_list: list[float] = []
    for n_val in n_arr:
        tp = model.theta_prime(theta_deg, float(n_val), n_air)
        tpp = model.theta_double_prime(tp, float(n_val), n_sub)
        r1s, r1p = model.fresnel_interface(n_air, float(n_val), theta_deg, tp)
        r2s, r2p = model.fresnel_interface(float(n_val), n_sub, tp, tpp)
        r1_list.append(0.5 * (r1s * r1s + r1p * r1p))
        r2_list.append(0.5 * (r2s * r2s + r2p * r2p))
    return np.asarray(r1_list, dtype=float), np.asarray(r2_list, dtype=float)


def forward_incoherent(
    nu_cm1: np.ndarray,
    t_um: float,
    n_nu: np.ndarray,
    n_sub: float,
    theta_deg: float,
    n_air: float = model.N_AIR,
) -> np.ndarray:
    """A1 消融模型：非相干叠加 R = R1 + (1-R1)^2 * R2（(3.5) 去除 cos(delta) 干涉项）。

    模型不含 t（R1、R2 仅依赖 n(nu)、theta、n_sub）——模拟 A11 相干性失效的极限；
    物理边界：0 <= R <= 1（能量守恒）。
    """
    r1, r2 = interface_avg_reflectivities(n_nu, n_sub, theta_deg, n_air)
    return r1 + (1.0 - r1) ** 2 * r2


def forward_no_substrate(
    nu_cm1: np.ndarray,
    t_um: float,
    n_nu: np.ndarray,
    n_sub: float,
    theta_deg: float,
    n_air: float = model.N_AIR,
) -> np.ndarray:
    """A2 消融模型：无衬底界面反射 R = R1（R2 -> 0，去掉 (1-R1)^2*R2 与干涉幅度 sqrt(R2)）。

    模型不含 t；模拟衬底/外延层折射率差消失（A6 物理前提失效）的极限。
    """
    r1, _ = interface_avg_reflectivities(n_nu, n_sub, theta_deg, n_air)
    return r1


def rmse_profile(
    nu_cm1: np.ndarray,
    r_obs: np.ndarray,
    theta_deg: float,
    n_nu: np.ndarray,
    n_sub: float,
    forward_fn,
    t_lo_um: float,
    t_hi_um: float,
    n_grid: int,
    include_t_true_um: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """rmse(t) 网格剖面：在 [t_lo, t_hi] um 均匀扫描 forward_fn 的拟合 rmse。

    用于可辨识性度量（A1/A2 预期平坦；F0 预期 t_true 处尖锐极小）。
    若提供 include_t_true_um，将其并入网格——完整模型 F0 在真值处应完美拟合
    （rmse~0），网格若不含真值会低估 rmse 深度比（网格点距真值最近可达半格）。
    """
    t_grid = np.linspace(float(t_lo_um), float(t_hi_um), int(n_grid))
    if include_t_true_um is not None:
        t_grid = np.unique(np.append(t_grid, float(include_t_true_um)))
    rmses = np.empty(t_grid.shape, dtype=float)
    for index, t in enumerate(t_grid):
        r_model = np.asarray(forward_fn(nu_cm1, float(t), n_nu, n_sub, theta_deg), dtype=float)
        rmses[index] = float(np.sqrt(np.mean((np.asarray(r_obs, dtype=float) - r_model) ** 2)))
    return t_grid, rmses


def profile_flatness(rmses: np.ndarray, eps: float = PREREGISTERED["identifiability"]["eps"]) -> float:
    """rmse 剖面平坦度 = (max - min) / (min + eps)。越小越平坦（厚度不可辨识）。"""
    return float((float(np.max(rmses)) - float(np.min(rmses))) / (float(np.min(rmses)) + eps))


def profile_depth_ratio(rmses: np.ndarray, eps: float = PREREGISTERED["identifiability"]["eps"]) -> float:
    """rmse 剖面深度比 = max / (min + eps)。越大表示 t_true 处极小越尖锐（可辨识）。

    min 在完美拟合点（t_true）处可精确为 0，故加 eps 防除零；F0 对照预期 >> 100。
    """
    return float(float(np.max(rmses)) / (float(np.min(rmses)) + eps))


def grid_scan_t(
    nu: np.ndarray,
    r_obs: np.ndarray,
    theta_deg: float,
    n_nu: np.ndarray,
    n_sub: float,
    pol: str = "avg",
    t_lo_um: float = 1.0,
    t_hi_um: float = 25.0,
    n_grid: int = 200,
) -> float:
    """网格扫描初值：在 [t_lo, t_hi] um 均匀扫描正模型 rmse，返回最小 rmse 的 t。

    与 robustness 阶段一致（噪声/极值定位失真下稳健的初值策略）。
    """
    t_grid = np.linspace(float(t_lo_um), float(t_hi_um), int(n_grid))
    best_t, best_rmse = float(t_grid[0]), float("inf")
    for t in t_grid:
        r_model = np.asarray(model.forward_reflectance(nu, float(t), n_nu, n_sub, theta_deg, pol=pol), dtype=float)
        rmse = float(np.sqrt(np.mean((np.asarray(r_obs, dtype=float) - r_model) ** 2)))
        if rmse < best_rmse:
            best_t, best_rmse = float(t), rmse
    return best_t


def run_nls(
    nu: np.ndarray, r_obs: np.ndarray, theta_deg: float, n_nu: np.ndarray, n_sub: float, pol: str = "avg"
) -> dict:
    """全谱 NLS 反演（formulation_v001 §3.6 方法 B，多初值），返回 best 与周期信息。

    初值策略：网格扫描给出全局最优附近初值，再以 ±period 平移布点规避 cos(delta)
    周期歧义（formula_validation §6）。
    """
    grid_t0 = grid_scan_t(nu, r_obs, theta_deg, n_nu, n_sub, pol=pol)
    period = model.phase_period_estimate(nu, n_nu, theta_deg)
    starts: list[float] = []
    for candidate in (grid_t0, grid_t0 - period, grid_t0 + period):
        if not any(abs(candidate - existing) < 1e-6 for existing in starts):
            starts.append(float(candidate))
    fits = [model.invert_nls(nu, r_obs, theta_deg, n_nu, n_sub, t0, pol=pol) for t0 in starts]
    best = min(fits, key=lambda item: item["rmse"] if item["rmse"] is not None else float("inf"))
    return {
        "t_um": float(best["t_um"]),
        "success": bool(best["success"]),
        "rmse": float(best["rmse"]) if best["rmse"] is not None else None,
        "status": int(best["status"]),
        "period_um_estimate": float(period),
        "n_starts": int(len(starts)),
        "grid_t0_um": float(grid_t0),
    }


def run_nls_single_init(
    nu: np.ndarray,
    r_obs: np.ndarray,
    theta_deg: float,
    n_nu: np.ndarray,
    n_sub: float,
    pol: str = "avg",
) -> dict:
    """A4 单初值分支：仅方法 A 解析初值（弱色散段峰定位 -> (3.10)），单次 NLS。

    不移除方法 A 初值本身（那是基线），而是移除「网格扫描 + ±period 多初值布点」模块，
    模拟 prob02 若仅依赖解析初值的退化情景（implementation §6.1 预警周期歧义）。
    """
    weak_band = PREREGISTERED["base_scenario"]["weak_band_cm1"]
    sub_nu, mask = model.restrict_band(nu, *weak_band)
    spacing = model.invert_from_spacing(sub_nu, r_obs[mask], theta_deg, n_nu[mask], kind="max")
    t0 = float(spacing["t_spacing_um"])
    fit = model.invert_nls(nu, r_obs, theta_deg, n_nu, n_sub, t0, pol=pol)
    return {
        "t_um": float(fit["t_um"]),
        "t0_um": t0,
        "success": bool(fit["success"]),
        "rmse": float(fit["rmse"]) if fit["rmse"] is not None else None,
        "status": int(fit["status"]),
        "spacing_delta_nu_median": float(spacing["delta_nu_median"]),
        "spacing_extrema_count": int(spacing["extrema_count"]),
    }


def experiment_f0(nu: np.ndarray, n_sub: float, thetas: list[float], cfg: dict) -> dict:
    """F0 完整模型对照：NLS 精确恢复 + rmse 深度比。"""
    t_true = PREREGISTERED["base_scenario"]["t_true_um"]
    n_nu = np.asarray(model.dispersion_from_nu(nu), dtype=float)
    ident = ident_config(cfg)
    rows: list[dict] = []
    for theta in thetas:
        r_obs = model.gen_synthetic_spectrum(nu, t_true, n_sub, theta)
        fit = run_nls(nu, r_obs, theta, n_nu, n_sub)
        _, rmses = rmse_profile(
            nu, r_obs, theta, n_nu, n_sub, model.forward_reflectance,
            ident["t_lo_um"], ident["t_hi_um"], ident["n_grid"],
            include_t_true_um=t_true,
        )
        rows.append(
            {
                "theta_deg": float(theta),
                "t_nls_um": fit["t_um"],
                "rel_err_vs_true": float(abs(fit["t_um"] - t_true) / t_true),
                "rmse_min": float(np.min(rmses)),
                "rmse_depth_ratio": profile_depth_ratio(rmses),
                "success": fit["success"],
            }
        )
    max_err = max((row["rel_err_vs_true"] for row in rows), default=0.0)
    min_depth = min((row["rmse_depth_ratio"] for row in rows), default=0.0)
    crit = PREREGISTERED["criteria"]["f0"]
    passed = bool(
        max_err <= crit["rel_err_threshold"]
        and min_depth >= crit["rmse_depth_ratio"]
        and all(row["success"] for row in rows)
    )
    return {
        "experiment": "f0",
        "rows": rows,
        "max_rel_err": float(max_err),
        "min_depth_ratio": float(min_depth),
        "rel_err_threshold": crit["rel_err_threshold"],
        "rmse_depth_ratio_threshold": crit["rmse_depth_ratio"],
        "passed": passed,
    }


def experiment_a1(nu: np.ndarray, n_sub: float, thetas: list[float], cfg: dict) -> dict:
    """A1 干涉叠加项消融：非相干模型拟合相干谱 -> rmse 平坦度（厚度不可辨识）。"""
    t_true = PREREGISTERED["base_scenario"]["t_true_um"]
    n_nu = np.asarray(model.dispersion_from_nu(nu), dtype=float)
    ident = ident_config(cfg)
    rows: list[dict] = []
    for theta in thetas:
        r_obs = model.gen_synthetic_spectrum(nu, t_true, n_sub, theta)
        _, rmses = rmse_profile(
            nu, r_obs, theta, n_nu, n_sub, forward_incoherent,
            ident["t_lo_um"], ident["t_hi_um"], ident["n_grid"],
        )
        r_model = forward_incoherent(nu, t_true, n_nu, n_sub, theta)
        rows.append(
            {
                "theta_deg": float(theta),
                "rmse_flatness": profile_flatness(rmses, ident["eps"]),
                "rmse_constant": float(np.mean(rmses)),
                "model_R_min": float(np.min(r_model)),
                "model_R_max": float(np.max(r_model)),
                "R_in_unit": bool(np.all(r_model >= 0.0) and np.all(r_model <= 1.0)),
            }
        )
    max_flat = max((row["rmse_flatness"] for row in rows), default=0.0)
    threshold = PREREGISTERED["criteria"]["a1"]["flatness_threshold"]
    passed = bool(max_flat <= threshold and all(row["R_in_unit"] for row in rows))
    return {
        "experiment": "a1",
        "rows": rows,
        "max_flatness": float(max_flat),
        "flatness_threshold": threshold,
        "passed": passed,
        "interpretation": "rmse(t) 平坦 -> 厚度不可辨识 -> 干涉叠加项是厚度信息的必要条件",
    }


def experiment_a2(nu: np.ndarray, n_sub: float, thetas: list[float], cfg: dict) -> dict:
    """A2 衬底界面反射消融：无衬底模型拟合相干谱 -> rmse 平坦度（厚度不可辨识）。"""
    t_true = PREREGISTERED["base_scenario"]["t_true_um"]
    n_nu = np.asarray(model.dispersion_from_nu(nu), dtype=float)
    ident = ident_config(cfg)
    rows: list[dict] = []
    for theta in thetas:
        r_obs = model.gen_synthetic_spectrum(nu, t_true, n_sub, theta)
        _, rmses = rmse_profile(
            nu, r_obs, theta, n_nu, n_sub, forward_no_substrate,
            ident["t_lo_um"], ident["t_hi_um"], ident["n_grid"],
        )
        r_model = forward_no_substrate(nu, t_true, n_nu, n_sub, theta)
        rows.append(
            {
                "theta_deg": float(theta),
                "rmse_flatness": profile_flatness(rmses, ident["eps"]),
                "rmse_constant": float(np.mean(rmses)),
                "model_R_min": float(np.min(r_model)),
                "model_R_max": float(np.max(r_model)),
                "R_in_unit": bool(np.all(r_model >= 0.0) and np.all(r_model <= 1.0)),
            }
        )
    max_flat = max((row["rmse_flatness"] for row in rows), default=0.0)
    threshold = PREREGISTERED["criteria"]["a2"]["flatness_threshold"]
    passed = bool(max_flat <= threshold and all(row["R_in_unit"] for row in rows))
    return {
        "experiment": "a2",
        "rows": rows,
        "max_flatness": float(max_flat),
        "flatness_threshold": threshold,
        "passed": passed,
        "interpretation": "rmse(t) 平坦 -> 厚度不可辨识 -> 衬底界面反射项是干涉条纹的必要条件",
    }


def experiment_a3(nu: np.ndarray, n_sub: float, thetas: list[float], cfg: dict) -> dict:
    """A3 偏振平均消融：avg / s / p 三种偏振模型反演同一 avg 观测谱，比较厚度一致性。"""
    t_true = PREREGISTERED["base_scenario"]["t_true_um"]
    n_nu = np.asarray(model.dispersion_from_nu(nu), dtype=float)
    rows: list[dict] = []
    for theta in thetas:
        r_obs = model.gen_synthetic_spectrum(nu, t_true, n_sub, theta)
        results: dict[str, float] = {}
        for pol in ("avg", "s", "p"):
            fit = run_nls(nu, r_obs, theta, n_nu, n_sub, pol=pol)
            results[pol] = fit["t_um"]
            rows.append(
                {
                    "theta_deg": float(theta),
                    "pol": pol,
                    "t_nls_um": fit["t_um"],
                    "rel_err_vs_true": float(abs(fit["t_um"] - t_true) / t_true),
                    "success": fit["success"],
                }
            )
        pairwise = max(
            abs(results[a] - results[b]) / t_true
            for a in results for b in results if a < b
        )
        rows.append(
            {
                "theta_deg": float(theta),
                "pol": "pairwise_max_rel_diff",
                "t_nls_um": None,
                "rel_err_vs_true": None,
                "success": bool(pairwise == pairwise),
                "pairwise_max_rel_diff": float(pairwise),
            }
        )
    pairwise_rows = [row for row in rows if row.get("pol") == "pairwise_max_rel_diff"]
    max_pairwise = max((row["pairwise_max_rel_diff"] for row in pairwise_rows), default=0.0)
    tol = PREREGISTERED["criteria"]["a3"]["pol_pairwise_tol"]
    passed = bool(max_pairwise <= tol and all(row["success"] for row in rows if "pairwise" not in str(row["pol"])))
    return {
        "experiment": "a3",
        "rows": rows,
        "max_pairwise_rel_diff": float(max_pairwise),
        "pol_pairwise_tol": tol,
        "passed": passed,
        "interpretation": "s/p/avg 厚度一致 -> 相位 delta 与偏振无关（A4）-> 偏振平均是非关键简化",
    }


def experiment_a4(nu: np.ndarray, n_sub: float, thetas: list[float], cfg: dict) -> dict:
    """A4 多初值模块消融：单初值（方法 A 解析初值）vs 多初值（网格 +- period）。"""
    t_true = PREREGISTERED["base_scenario"]["t_true_um"]
    n_nu = np.asarray(model.dispersion_from_nu(nu), dtype=float)
    rows: list[dict] = []
    for theta in thetas:
        r_obs = model.gen_synthetic_spectrum(nu, t_true, n_sub, theta)
        single = run_nls_single_init(nu, r_obs, theta, n_nu, n_sub)
        multi = run_nls(nu, r_obs, theta, n_nu, n_sub)
        rows.append(
            {
                "theta_deg": float(theta),
                "single_t0_um": single["t0_um"],
                "single_t_nls_um": single["t_um"],
                "single_rel_err_vs_true": float(abs(single["t_um"] - t_true) / t_true),
                "single_rmse": single["rmse"],
                "single_success": single["success"],
                "multi_t_nls_um": multi["t_um"],
                "multi_rel_err_vs_true": float(abs(multi["t_um"] - t_true) / t_true),
                "multi_rmse": multi["rmse"],
                "multi_success": multi["success"],
            }
        )
    max_single_err = max((row["single_rel_err_vs_true"] for row in rows), default=0.0)
    max_multi_err = max((row["multi_rel_err_vs_true"] for row in rows), default=0.0)
    crit = PREREGISTERED["criteria"]["a4"]
    passed = bool(
        max_single_err > crit["single_init_err_threshold"]
        and max_multi_err <= crit["multi_init_err_threshold"]
        and all(row["multi_success"] for row in rows)
    )
    return {
        "experiment": "a4",
        "rows": rows,
        "max_single_init_rel_err": float(max_single_err),
        "max_multi_init_rel_err": float(max_multi_err),
        "single_init_err_threshold": crit["single_init_err_threshold"],
        "multi_init_err_threshold": crit["multi_init_err_threshold"],
        "passed": passed,
        "interpretation": "单初值落入周期歧义局部极小 -> 多初值模块必要（formula_validation §6）",
    }


def _serialize(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): _serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, np.ndarray):
        return _serialize(value.tolist())
    return value


def run_self_check() -> dict[str, bool]:
    """秒级接口探针（静态检查 / --self-check）：验证脚本可运行、消融模型与判据定义完整。"""
    checks: dict[str, bool] = {}
    checks["preregistered_criteria_complete"] = all(
        name in PREREGISTERED["criteria"] for name in ("f0", "a1", "a2", "a3", "a4")
    )
    nu = base_nu({"scenario": {"nu_min_cm1": 400.0, "nu_max_cm1": 4000.0, "nu_points": 601}})
    n_nu = np.asarray(model.dispersion_from_nu(nu), dtype=float)
    r_obs = model.gen_synthetic_spectrum(nu, 10.0, 3.0, 10.0)
    fit = run_nls(nu, r_obs, 10.0, n_nu, 3.0)
    checks["f0_single_nls_recovers_t"] = bool(fit["success"] and abs(fit["t_um"] - 10.0) / 10.0 < 1e-2)
    r_incoh = forward_incoherent(nu, 10.0, n_nu, 3.0, 10.0)
    checks["a1_incoherent_shapes_and_unit"] = bool(
        r_incoh.shape == nu.shape and np.all(r_incoh >= 0.0) and np.all(r_incoh <= 1.0)
    )
    r_nosub = forward_no_substrate(nu, 10.0, n_nu, 3.0, 10.0)
    checks["a2_no_substrate_shapes_and_unit"] = bool(
        r_nosub.shape == nu.shape and np.all(r_nosub >= 0.0) and np.all(r_nosub <= 1.0)
    )
    t_grid, rmses = rmse_profile(nu, r_obs, 10.0, n_nu, 3.0, forward_incoherent, 1.0, 25.0, 51)
    checks["a1_profile_flat"] = bool(t_grid.size == 51 and profile_flatness(rmses) <= 0.05)
    fit_single = run_nls_single_init(nu, r_obs, 10.0, n_nu, 3.0)
    checks["a4_single_init_runs"] = bool(fit_single["success"] and fit_single["t0_um"] > 0.0)
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="prob01 ablation 消融实验（formulation_v001）")
    parser.add_argument("--config", help="ablation_config.yaml 路径（实验与执行设置）")
    parser.add_argument("--input", help="formulation parameters.yaml 路径（参数登记）")
    parser.add_argument("--output", help="输出目录（优先使用环境变量 AUTOMM_OUTPUT_DIR）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（优先使用环境变量 AUTOMM_SEED）")
    parser.add_argument("--self-check", action="store_true", help="仅运行秒级接口探针")
    args = parser.parse_args(argv)

    if args.self_check:
        results = run_self_check()
        for name, passed in sorted(results.items()):
            print(f"{'PASS' if passed else 'FAIL'}  {name}")
        ok = all(results.values())
        print(f"probe 汇总：{sum(results.values())}/{len(results)} 通过")
        return 0 if ok else 1

    if not args.config or not args.input:
        parser.error("--config 与 --input 为必填（--self-check 除外）")

    config = load_yaml(Path(args.config).resolve())
    input_params = load_yaml(Path(args.input).resolve())
    param_map = {
        str(entry["name"]): entry
        for entry in input_params.get("parameters", [])
        if isinstance(entry, dict) and entry.get("name")
    }
    output_dir = resolve_output(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    seed = resolve_seed(args.seed, config)
    scenario = config.get("scenario", {})
    t_true = float(scenario["t_true_um"])
    n_sub = float(scenario["n_sub"])
    thetas = [float(theta) for theta in scenario["theta_deg"]]

    # 输入参数登记值与代码常量一致性（parameters.yaml 是参数权威来源）
    n_air = float(param_map.get("n_air", {}).get("value", model.N_AIR))
    if abs(n_air - model.N_AIR) > 1e-9:
        print(f"警告：parameters.yaml n_air={n_air} 与代码常量 {model.N_AIR} 不一致", file=sys.stderr)

    nu = base_nu(config)
    cfg = exp_config(config)

    f0 = experiment_f0(nu, n_sub, thetas, cfg)
    a1 = experiment_a1(nu, n_sub, thetas, cfg)
    a2 = experiment_a2(nu, n_sub, thetas, cfg)
    a3 = experiment_a3(nu, n_sub, thetas, cfg)
    a4 = experiment_a4(nu, n_sub, thetas, cfg)

    criteria_passed = {
        "f0": f0["passed"],
        "a1": a1["passed"],
        "a2": a2["passed"],
        "a3": a3["passed"],
        "a4": a4["passed"],
    }
    failed = [name for name, passed in criteria_passed.items() if not passed]
    if not failed:
        conclusion = "components_confirmed"
    else:
        conclusion = "components_partially_confirmed"
    feasible = True  # 实验执行完成且判据评估完整；判据与预期不一致是部分确认结论而非任务失败

    result_payload = {
        "feasible_incumbent": feasible,
        "task": "prob01-ablation-components",
        "preregistration_version": PREREGISTERED["version"],
        "t_true_um": t_true,
        "n_sub": n_sub,
        "theta_deg": thetas,
        "seed": seed,
        "criteria_passed": criteria_passed,
        "conclusion": conclusion,
        "failed_checks": failed,
        "notes": [
            "prob01 无实测数据；本实验基于正模型合成谱检验模型公式项与算法模块的必要性",
            "观测谱始终用完整模型 (3.5) avg 生成；各消融只改变反演模型/初值策略（每次只改变一个目标项）",
            "判据在运行前固定（ablation_v001，见 ablation/preregistration.md），实测与预期不一致记"
            "为 components_partially_confirmed，如实报告反证项",
            "A1/A2 的「厚度不可辨识」是预期结论（组件必要性的正向证据），不是实验失败",
        ],
    }
    summary_payload = {
        "experiments": {
            "f0": {
                "rows": f0["rows"],
                "max_rel_err": f0["max_rel_err"],
                "min_depth_ratio": f0["min_depth_ratio"],
                "thresholds": {
                    "rel_err": f0["rel_err_threshold"],
                    "rmse_depth_ratio": f0["rmse_depth_ratio_threshold"],
                },
                "passed": f0["passed"],
            },
            "a1": {
                "rows": a1["rows"],
                "max_flatness": a1["max_flatness"],
                "flatness_threshold": a1["flatness_threshold"],
                "interpretation": a1["interpretation"],
                "passed": a1["passed"],
            },
            "a2": {
                "rows": a2["rows"],
                "max_flatness": a2["max_flatness"],
                "flatness_threshold": a2["flatness_threshold"],
                "interpretation": a2["interpretation"],
                "passed": a2["passed"],
            },
            "a3": {
                "rows": a3["rows"],
                "max_pairwise_rel_diff": a3["max_pairwise_rel_diff"],
                "pol_pairwise_tol": a3["pol_pairwise_tol"],
                "interpretation": a3["interpretation"],
                "passed": a3["passed"],
            },
            "a4": {
                "rows": a4["rows"],
                "max_single_init_rel_err": a4["max_single_init_rel_err"],
                "max_multi_init_rel_err": a4["max_multi_init_rel_err"],
                "thresholds": {
                    "single_init_err": a4["single_init_err_threshold"],
                    "multi_init_err": a4["multi_init_err_threshold"],
                },
                "interpretation": a4["interpretation"],
                "passed": a4["passed"],
            },
        }
    }
    checks_payload = {
        "passed": bool(all(criteria_passed.values())),
        "criteria": [
            {
                "name": "f0",
                "passed": f0["passed"],
                "metric": "max_rel_err / min_depth_ratio",
                "measured": [f0["max_rel_err"], f0["min_depth_ratio"]],
                "threshold": [f0["rel_err_threshold"], f0["rmse_depth_ratio_threshold"]],
                "note": PREREGISTERED["criteria"]["f0"]["note"],
            },
            {
                "name": "a1",
                "passed": a1["passed"],
                "metric": "max_flatness",
                "measured": a1["max_flatness"],
                "threshold": a1["flatness_threshold"],
                "note": PREREGISTERED["criteria"]["a1"]["note"],
            },
            {
                "name": "a2",
                "passed": a2["passed"],
                "metric": "max_flatness",
                "measured": a2["max_flatness"],
                "threshold": a2["flatness_threshold"],
                "note": PREREGISTERED["criteria"]["a2"]["note"],
            },
            {
                "name": "a3",
                "passed": a3["passed"],
                "metric": "max_pairwise_rel_diff",
                "measured": a3["max_pairwise_rel_diff"],
                "threshold": a3["pol_pairwise_tol"],
                "note": PREREGISTERED["criteria"]["a3"]["note"],
            },
            {
                "name": "a4",
                "passed": a4["passed"],
                "metric": "max_single_init_rel_err / max_multi_init_rel_err",
                "measured": [a4["max_single_init_rel_err"], a4["max_multi_init_rel_err"]],
                "threshold": [a4["single_init_err_threshold"], a4["multi_init_err_threshold"]],
                "note": PREREGISTERED["criteria"]["a4"]["note"],
            },
        ],
        "method_reference": FORMULA_REFS,
    }
    metadata_payload = {
        "problem_id": "2025-cumcm-b",
        "question_id": "prob01",
        "assumption_version": "assumption_v001",
        "formulation_version": "formulation_v001",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "scenario": {
            "t_true_um": t_true,
            "n_sub": n_sub,
            "theta_deg": thetas,
            "nu_range_cm1": [float(nu.min()), float(nu.max())],
            "nu_points": int(nu.size),
            "weak_band_cm1": PREREGISTERED["base_scenario"]["weak_band_cm1"],
            "reststrahlen_exclude_cm1": PREREGISTERED["base_scenario"]["reststrahlen_exclude_cm1"],
            "identifiability": ident_config(cfg),
            "dispersion_extension": "constant",
        },
        "input_parameters_yaml_hash": sha256_file(Path(args.input).resolve()),
        "ablation_config_yaml_hash": sha256_file(Path(args.config).resolve()),
        "unit_conventions": UNIT_CONVENTIONS,
        "formula_refs": FORMULA_REFS,
        "python": sys.version.split()[0],
    }

    for name, payload in (
        ("result.json", result_payload),
        ("summary.json", summary_payload),
        ("checks.json", checks_payload),
        ("metadata.json", metadata_payload),
    ):
        (output_dir / name).write_text(
            json.dumps(_serialize(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(f"ablation 实验完成：conclusion={conclusion}，判据通过 {sum(criteria_passed.values())}/5")
    if failed:
        print("与预期不一致的判据：" + "；".join(failed), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
