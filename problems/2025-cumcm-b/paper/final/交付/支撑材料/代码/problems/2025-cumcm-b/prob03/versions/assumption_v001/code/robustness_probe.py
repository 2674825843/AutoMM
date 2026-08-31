"""prob03 robustness 只读探针：补登 formulation §8.5 预注册的 R7（硅谱段窗口敏感性）。

复用 computation 阶段已审定的 model.py 模块（formulation_v002），对硅片附件 3/4 在
不同反演带下界（[1600,1800,2000,2200] × 4000）运行 variable_projection_scan（shared t），
量化 t 对谱段窗口的敏感性 Δt_win = max|t_win - t_base|/t_base×100%。

本探针为只读、确定性、秒级小计算：不修改原始数据、不修改 model.py/compute.py、
不创建新模型，仅补登预注册但未在 computation 阶段执行的 R7 判据（formulation §8.5 标记为
登记/报告项，robustness 阶段补齐实测值）。输出到 robustness/（独立目录）。

用法：
  python robustness_probe.py [--out DIR]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import model

WINDOWS = [(2000.0, 4000.0), (1600.0, 4000.0), (1800.0, 4000.0), (2200.0, 4000.0)]
THETAS = [10.0, 15.0]
P = model.BASELINE_POLY_DEG
Q = model.ENVELOPE_POLY_DEG
T_RANGE = (2.0, 12.0)
T_STEP = 0.01


def load_and_preprocess(path: Path) -> dict:
    att = model.load_attachment(path)
    pp = model.preprocess_spectrum(
        att["nu"], att["r_obs"], exclude_band=model.SI_MULTIPHONON_EXCLUDE_CM1, weight_anomaly=0.05
    )
    return {"nu": att["nu"], "r_obs": att["r_obs"], "weights": pp["weights"]}


def inv_band_data(att, lo: float, hi: float) -> dict:
    mask = (att["nu"] >= lo) & (att["nu"] <= hi)
    n_nu = np.asarray(model.dispersion_epi_si(att["nu"], model="N-SE"), dtype=float)
    return {
        "nu": att["nu"][mask],
        "r": att["r_obs"][mask],
        "w": att["weights"][mask],
        "n": n_nu[mask],
    }


def run_window(att10: dict, att15: dict, lo: float, hi: float) -> dict:
    d10 = inv_band_data(att10, lo, hi)
    d15 = inv_band_data(att15, lo, hi)
    scan = model.variable_projection_scan(
        [d10["nu"], d15["nu"]], [d10["r"], d15["r"]], THETAS, [d10["n"], d15["n"]], [d10["w"], d15["w"]],
        t_range=T_RANGE, t_step=T_STEP, p=P, q=Q, shared=True,
    )
    n_pts = sum(int(np.count_nonzero(w > 0.0)) for w in (d10["w"], d15["w"]))
    rmse = float(np.sqrt(scan["J_min_shared"] / n_pts)) if n_pts > 0 else float("inf")
    return {
        "band_cm1": [lo, hi],
        "t_hat_shared_um": float(scan["t_hat_refined"]),
        "J_min": float(scan["J_min_shared"]),
        "n_points": n_pts,
        "weighted_rmse": rmse,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="prob03 robustness R7 谱段窗口敏感性只读探针")
    parser.add_argument("--out", default=None, help="输出 JSON 路径（默认打印）")
    parser.add_argument("--att10", default="data/2025_cumcm_B/附件3.xlsx")
    parser.add_argument("--att15", default="data/2025_cumcm_B/附件4.xlsx")
    args = parser.parse_args()

    att10 = load_and_preprocess(Path(args.att10))
    att15 = load_and_preprocess(Path(args.att15))

    rows = []
    for lo, hi in WINDOWS:
        rows.append(run_window(att10, att15, lo, hi))

    base = next(r["t_hat_shared_um"] for r in rows if r["band_cm1"][0] == 2000.0)
    deltas = []
    for r in rows:
        r["delta_t_percent_from_base"] = (r["t_hat_shared_um"] - base) / base * 100.0
        deltas.append(abs(r["delta_t_percent_from_base"]))
    dt_win = float(max(deltas))
    tau = 2.0  # 与 formulation §8.5 窗口稳健阈值一致（Δt_disp 同量级，弱色散下窗口影响预期接近 0）

    payload = {
        "problem_id": "2025-cumcm-b",
        "question_id": "prob03",
        "assumption_version": "assumption_v001",
        "formulation_version": "formulation_v002",
        "robustness_criterion": "R7_window_sensitivity",
        "method": "baseline_interference_decoupled_1d_scan(variable_projection, shared_t)",
        "baseline_band_cm1": [2000.0, 4000.0],
        "baseline_t_hat_shared_um": base,
        "windows": rows,
        "delta_t_win_percent": dt_win,
        "threshold_percent": tau,
        "status": "PASS" if dt_win <= tau else "FAIL",
        "note": (
            "只读探针补登 formulation §8.5 R7（预注册但 computation 未单独执行）；"
            "主反演带取 [2000,4000]，另对 [1600,4000]/[1800,4000]/[2200,4000] 做敏感性；"
            "弱色散（Δn/n≈0.51%）下窗口边界变化对 t 影响应与 Δt_disp≈0.503% 同量级；"
            "不修改原始数据，未改动 model.py/compute.py（read-only probe）"
        ),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"written: {args.out}")
    else:
        print(text)
    print(f"R7 窗口敏感性 Δt_win = {dt_win:.3f}% (阈值 {tau}%) -> {payload['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
