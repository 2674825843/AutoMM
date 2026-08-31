"""prob01 合成验证计算 CLI（computation 阶段由 supervised worker 执行）。

prob01 为纯解析建模（无附件实测数据），本任务用正模型生成合成反射率谱，数值验证：

- 正模型物理边界（R in [0, 1]，formula_validation §4）；
- 同型相邻极值间隔与理论 Delta_nu 一致（(3.8)/(3.10)）；
- 方法 A 极值间隔反演 t（(3.9)/(3.10)）与方法 B 全谱 NLS 反演 t（§3.6）；
- 色散化相位函数法 t（(3.13)）与弱色散一致性；
- 两入射角（10°/15°）反演厚度一致性（A10 可观测验证）。

用法：
    python compute.py --config CONFIG --input INPUT --output OUTPUT [--seed SEED]
    python compute.py --self-check          # 仅运行秒级接口探针

输入：
    --config  configs/task_config.yaml         场景与执行设置（t_true、入射角、n_sub、容差等）
    --input   formulations/formulation_v001/parameters.yaml  （参数登记，n_air/nu_range/reststrahlen 等）
输出目录（--output 或环境变量 AUTOMM_OUTPUT_DIR）：
    result.json           可行解标记 + 厚度估计汇总（worker 读取 feasible_incumbent）
    solver_status.json    各 NLS 拟合的求解器状态（scipy.optimize.least_squares）
    verification.json     验证检查明细（checks 列表）
    metadata.json         场景、种子、输入/配置 hash、单位约定（可追溯性）
    synthetic_spectrum_theta*.csv   合成谱（nu, R_clean, R_noisy），供可视化/归档
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
    "delta": "rad",
    "delta_nu": "cm^-1",
}
FORMULA_REFS = {
    "forward_model": "(3.5)/(3.6)",
    "snell": "(2.1)-(2.3)",
    "optical_path": "(2.5)/(2.6)",
    "phase": "(2.7)/(2.8)",
    "fresnel": "(3.1)-(3.3)",
    "extremum": "(3.7)",
    "spacing": "(3.8)",
    "thickness": "(3.10)",
    "phase_method": "(3.11)-(3.13)",
    "sellmeier": "(4.1)",
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


def verify_scenario(
    nu: np.ndarray,
    t_true: float,
    n_sub: float,
    theta: float,
    params: dict,
    rng: np.random.Generator,
) -> dict[str, float]:
    """生成合成谱并做单角度数值验证，返回该角度的估计、检查结果与谱数据。"""
    n_nu = model.dispersion_from_nu(nu)
    r_clean = model.gen_synthetic_spectrum(nu, t_true, n_sub, theta)
    r_obs = model.add_gaussian_noise(r_clean, scenario_noise(params), rng)

    weak_nu, weak_mask = model.restrict_band(nu, *model.WEAK_DISPERSION_BAND_CM1)
    weak_r = r_obs[weak_mask]
    weak_n = n_nu[weak_mask]

    checks: dict[str, dict] = {}
    tol_a = float(inv_conf(params).get("method_a_tol_rel", 0.10))
    tol_b = float(inv_conf(params).get("method_b_tol_rel", 0.01))
    tol_cons = float(inv_conf(params).get("nls_band_consistency_tol_rel", 0.01))

    # 物理边界：模型反射率 R in [0, 1]（formula_validation §4）
    checks["forward_model_R_in_unit"] = {
        "passed": bool(np.all(r_clean >= 0.0) and np.all(r_clean <= 1.0)),
        "detail": f"R_clean ∈ [{np.min(r_clean):.6f}, {np.max(r_clean):.6f}]（theta={theta}°）",
        "tolerance": "0 <= R <= 1",
    }

    # 方法 A：极值间隔（弱色散谱段，n_eff 均值）——(3.8)/(3.9) 常数 n 近似基线
    # 2000-4000 cm^-1 谱段色散效应显著（nu*dn/dnu 约 9%），(3.8) 忽略色散引入系统偏差
    # （A3 文档化偏差方向），故方法 A 作为基线/初值，容忍 10%；色散修正见相位法与 NLS。
    spacing = model.invert_from_spacing(weak_nu, weak_r, theta, weak_n, kind="max")
    n_eff = spacing["n_eff"]
    delta_nu_theory = model.evaluate_spacing_theory(t_true, n_eff, theta)
    rel_spacing = abs(spacing["delta_nu_median"] - delta_nu_theory) / delta_nu_theory
    checks["spacing_constant_n_approx"] = {
        "passed": bool(rel_spacing < tol_a),
        "detail": (
            f"Δν_obs={spacing['delta_nu_median']:.4f} vs "
            f"Δν_theory(常数 n)={delta_nu_theory:.4f} cm^-1（rel={rel_spacing:.2e}，"
            "A3 文档化色散偏差）"
        ),
        "tolerance": f"rel < {tol_a}（基线）",
    }
    rel_a = abs(spacing["t_spacing_um"] - t_true) / t_true
    checks["method_a_t_error"] = {
        "passed": bool(rel_a < tol_a),
        "detail": (
            f"t_A={spacing['t_spacing_um']:.6f} um vs t_true={t_true} um"
            f"（rel={rel_a:.2e}，极值数={spacing['extrema_count']}，n_eff={n_eff:.5f}）"
        ),
        "tolerance": f"rel < {tol_a}（基线）",
    }

    # 色散化相位间隔律（(3.11)-(3.13)）：同型相邻极值 delta_g = 1/(2*1e-4*t_true)
    phase = model.invert_phase_method(weak_nu, weak_r, theta, weak_n, kind="max")
    delta_g_theory = 1.0 / (2.0 * 1e-4 * t_true)
    rel_gap = abs(phase["delta_g_median"] - delta_g_theory) / delta_g_theory
    checks["phase_gap_law_match"] = {
        "passed": bool(rel_gap < tol_b),
        "detail": (
            f"Δg_obs={phase['delta_g_median']:.4f} vs Δg_theory={delta_g_theory:.4f} cm^-1"
            f"（rel={rel_gap:.2e}）"
        ),
        "tolerance": f"rel < {tol_b}（(3.13) 间隔律）",
    }
    rel_phase = abs(phase["t_phase_um"] - t_true) / t_true
    checks["phase_method_t_error"] = {
        "passed": bool(rel_phase < tol_b),
        "detail": (
            f"t_phase={phase['t_phase_um']:.6f} um vs t_true={t_true} um"
            f"（rel={rel_phase:.2e}，pairs={phase['g_pairs']}）"
        ),
        "tolerance": f"rel < {tol_b}",
    }
    checks["phase_g_monotonic"] = {
        "passed": bool(phase["g_monotonic"]),
        "detail": f"g(nu) 在弱色散谱段单调递增：{phase['g_monotonic']}",
        "tolerance": "g' > 0（(3.13) 成立前提）",
    }

    # 方法 B：全谱/弱色散 NLS（相位法解析初值 + 多初值，规避周期歧义局部极小）
    nls_full = model.invert_nls_multistart(
        nu, r_obs, theta, n_nu, n_sub, t0_um=spacing["t_spacing_um"], alt_t0_um=phase["t_phase_um"]
    )
    nls_weak = model.invert_nls_multistart(
        weak_nu, weak_r, theta, weak_n, n_sub, t0_um=spacing["t_spacing_um"], alt_t0_um=phase["t_phase_um"]
    )
    best_full = nls_full["best"]
    best_weak = nls_weak["best"]
    rel_b = abs(best_full["t_um"] - t_true) / t_true
    checks["nls_full_success"] = {
        "passed": bool(best_full["success"]),
        "detail": f"NLS status={best_full['status']}，nfev={best_full['nfev']}，rmse={best_full['rmse']:.3e}",
        "tolerance": "success=True",
    }
    checks["nls_full_t_error"] = {
        "passed": bool(rel_b < tol_b),
        "detail": f"t_NLS={best_full['t_um']:.6f} um vs t_true={t_true} um（rel={rel_b:.2e}）",
        "tolerance": f"rel < {tol_b}",
    }
    rel_cons = abs(best_full["t_um"] - best_weak["t_um"]) / max(abs(best_weak["t_um"]), 1e-12)
    checks["nls_band_consistency"] = {
        "passed": bool(rel_cons < tol_cons),
        "detail": (
            f"t_NLS(full)={best_full['t_um']:.6f} vs t_NLS(weak)={best_weak['t_um']:.6f} um"
            f"（rel={rel_cons:.2e}）"
        ),
        "tolerance": f"rel < {tol_cons}",
    }

    return {
        "theta_deg": float(theta),
        "nu": nu,
        "r_clean": r_clean,
        "r_obs": r_obs,
        "spacing": spacing,
        "phase": phase,
        "nls_full": nls_full,
        "nls_weak": nls_weak,
        "checks": checks,
        "passed": bool(all(item["passed"] for item in checks.values())),
    }


def scenario_noise(params: dict) -> float:
    return float(params.get("noise_sigma_percent", 0.0))


def inv_conf(params: dict) -> dict:
    value = params.get("inversion", {})
    return value if isinstance(value, dict) else {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="prob01 两光束干涉测厚模型合成验证（formulation_v001）")
    parser.add_argument("--config", help="task_config.yaml 路径（场景与执行设置）")
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
    param_map = {
        str(entry["name"]): entry
        for entry in input_params.get("parameters", [])
        if isinstance(entry, dict) and entry.get("name")
    }
    output_dir = resolve_output(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    seed = resolve_seed(args.seed, config)
    rng = np.random.default_rng(seed)

    scenario = config.get("scenario", {})
    t_true = float(scenario["t_true_um"])
    n_sub = float(scenario["n_sub"])
    thetas = [float(theta) for theta in scenario["theta_deg"]]
    registered_nu_range = [float(item) for item in param_map.get("nu_range", {}).get("value", [400.0, 4000.0])]
    nu_min = float(scenario.get("nu_min_cm1", registered_nu_range[0]))
    nu_max = float(scenario.get("nu_max_cm1", registered_nu_range[1]))
    nu_points = int(scenario.get("nu_points", 3601))
    sigma_percent = scenario_noise(scenario)

    # 输入参数登记值与代码常量一致性（parameters.yaml 是参数权威来源）
    n_air = float(param_map.get("n_air", {}).get("value", model.N_AIR))
    reststrahlen_registered = param_map.get("reststrahlen_exclude", {}).get("value", model.RESTSTRAHLEN_EXCLUDE_CM1)
    reststrahlen = [float(item) for item in reststrahlen_registered]
    sellmeier_boundary = float(param_map.get("sellmeier_boundary", {}).get("value", model.SELLMEIER_BOUNDARY_UM))
    if abs(n_air - model.N_AIR) > 1e-9:
        print(f"警告：parameters.yaml n_air={n_air} 与代码常量 {model.N_AIR} 不一致", file=sys.stderr)

    nu = np.linspace(nu_min, nu_max, nu_points)
    per_theta: dict[str, dict] = {}
    all_checks: list[dict] = []
    for theta in thetas:
        result = verify_scenario(nu, t_true, n_sub, theta, scenario, rng)
        per_theta[f"theta_{theta:g}".replace(".", "p")] = result
        for name, item in result["checks"].items():
            all_checks.append(
                {
                    "name": f"{name}[theta={theta:g}°]",
                    "passed": item["passed"],
                    "detail": item["detail"],
                    "tolerance": item["tolerance"],
                }
            )
        # 合成谱归档（供可视化与复核；与反演使用同一 rng 序列保证可复现）
        theta_tag = f"{theta:g}".replace(".", "p")
        csv_path = output_dir / f"synthetic_spectrum_theta{theta_tag}.csv"
        np.savetxt(
            csv_path,
            np.column_stack([result["nu"], result["r_clean"], result["r_obs"]]),
            header="nu_cm1,R_clean,R_noisy",
            delimiter=",",
            fmt="%.8f",
            comments="",
        )

    # 两入射角一致性（A10：厚度与入射角无关）
    tol_angle = float(inv_conf(scenario).get("two_angle_consistency_tol_rel", 0.02))
    t_by_theta = {
        theta: per_theta[f"theta_{theta:g}".replace(".", "p")]["nls_full"]["best"]["t_um"] for theta in thetas
    }
    two_angle_passed = True
    two_angle_detail = "仅单入射角场景，跳过"
    if len(thetas) >= 2:
        mean_t = float(np.mean(list(t_by_theta.values())))
        rel_diff = abs(t_by_theta[thetas[0]] - t_by_theta[thetas[1]]) / mean_t
        two_angle_passed = rel_diff < tol_angle
        two_angle_detail = (
            f"t(10°)={t_by_theta[thetas[0]]:.6f} vs t(15°)={t_by_theta[thetas[1]]:.6f} um"
            f"（rel={rel_diff:.2e}）"
        )
    all_checks.append(
        {
            "name": "two_angle_consistency",
            "passed": two_angle_passed,
            "detail": two_angle_detail,
            "tolerance": f"rel < {tol_angle}",
        }
    )

    passed = bool(all(item["passed"] for item in all_checks))
    failed_names = [item["name"] for item in all_checks if not item["passed"]]

    # 序列化友好的估计汇总（去掉 nu/r_clean/r_obs 数组，谱数据已落 CSV）
    estimates_summary: dict[str, dict] = {}
    for theta_label, fit in per_theta.items():
        estimates_summary[theta_label] = {
            "theta_deg": fit["theta_deg"],
            "spacing": fit["spacing"],
            "phase": fit["phase"],
            "nls_full": {
                "best": fit["nls_full"]["best"],
                "period_um_estimate": fit["nls_full"]["period_um_estimate"],
                "n_starts": len(fit["nls_full"]["starts"]),
            },
            "nls_weak": {
                "best": fit["nls_weak"]["best"],
                "period_um_estimate": fit["nls_weak"]["period_um_estimate"],
                "n_starts": len(fit["nls_weak"]["starts"]),
            },
            "checks": fit["checks"],
            "passed": fit["passed"],
        }

    result_payload = {
        "feasible_incumbent": passed,
        "task": "prob01-synthetic-verification",
        "passed": passed,
        "t_true_um": t_true,
        "n_sub": n_sub,
        "theta_deg": thetas,
        "seed": seed,
        "estimates": estimates_summary,
        "checks_failed": failed_names,
        "notes": [
            "prob01 无实测数据；本任务为公式/算法数值验证（合成数据，正模型自洽）",
            f"色散延伸策略 constant：lambda>{sellmeier_boundary} um 用 n(boundary) 常数延续（prob02 数据反演确定）",
            f"Reststrahlen 区 {reststrahlen} cm^-1 本问无吸收模型不适用，已排除在方法 A 谱段之外",
            "方法 A (3.9) 常数 n 近似在 2000-4000 cm^-1 引入约 4% 色散偏差（A3 文档化），作为基线/初值；"
            "相位法 (3.13) 与全谱 NLS 为色散修正主方法",
        ],
    }
    solver_payload = {
        "solver": "scipy.optimize.least_squares",
        "fits": {
            theta_label: {
                "full_band": {
                    "best": fit["nls_full"]["best"],
                    "starts": fit["nls_full"]["starts"],
                    "period_um_estimate": fit["nls_full"]["period_um_estimate"],
                },
                "weak_band": {
                    "best": fit["nls_weak"]["best"],
                    "starts": fit["nls_weak"]["starts"],
                    "period_um_estimate": fit["nls_weak"]["period_um_estimate"],
                },
            }
            for theta_label, fit in per_theta.items()
        },
        "bounds": (1e-4, 1e4),
        "tolerances": {
            "ftol": inv_conf(scenario).get("nls_ftol", 1e-10),
            "xtol": inv_conf(scenario).get("nls_xtol", 1e-10),
            "gtol": inv_conf(scenario).get("nls_gtol", 1e-10),
            "max_nfev": inv_conf(scenario).get("nls_max_nfev", 200),
        },
    }
    verification_payload = {
        "passed": passed,
        "checks": all_checks,
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
            "nu_range_cm1": [nu_min, nu_max],
            "nu_points": nu_points,
            "noise_sigma_percent": sigma_percent,
            "dispersion_extension": "constant",
            "sellmeier_boundary_um": sellmeier_boundary,
            "reststrahlen_exclude_cm1": reststrahlen,
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
    ):
        (output_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    passed_count = sum(1 for c in all_checks if c["passed"])
    print(f"合成验证 {'通过' if passed else '失败'}：{passed_count}/{len(all_checks)} 检查通过")
    if failed_names:
        print("未通过检查：" + "；".join(failed_names), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
