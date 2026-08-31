"""prob01（assumption_v001 / formulation_v001）出版级图表生成脚本。

数据源（只读，不修改）：
- results/synthetic_verify/synthetic_spectrum_theta10.csv、theta15.csv（合成反射率谱）
- results/synthetic_verify/result.json（三方法反演结果与检查明细）
- results/synthetic_verify/solver_status.json（NLS 多初值收敛轨迹）
- model.py（正模型 (3.5)、色散 (4.1)、相位函数 (3.11)、极值定位 (3.7)）

输出（figures/ 目录）：
- prob01_fig_<slug>_<short_hash>.png 共 7 张（含三维响应面与二维等高线配套）
- 每张图 .quality.json（inspect_png 自动质检报告）
- figures.yaml 登记（register_figure；visual_review 由 Agent 命令补记）

运行：python code/make_figures.py（项目根为工作目录）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[6]  # E:\项目\AutoMM
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # 同目录 import model

import matplotlib

matplotlib.use("Agg")

from matplotlib import font_manager, pyplot as plt
from matplotlib.ticker import MultipleLocator

import model
from automm.common import config_section, hash_path, relative, utc_now
from automm.visualization import inspect_png, register_figure, stable_figure_id

PROBLEM_ID = "2025-cumcm-b"
QUESTION_ID = "prob01"
ASSUMPTION_VERSION = "assumption_v001"

VERSION_DIR = ROOT / "problems" / PROBLEM_ID / QUESTION_ID / "versions" / ASSUMPTION_VERSION
RESULTS_DIR = VERSION_DIR / "results" / "synthetic_verify"
FIGURES_DIR = VERSION_DIR / "figures"
SCRIPT_PATH = Path(__file__).resolve()

PALETTE = {
    "primary": "#1F4E79",      # 主方案（θ=10°）
    "secondary": "#70AD47",    # 对照（θ=15°）
    "accent": "#ED7D31",       # 强调（主方法/全局解）
    "neutral": "#7F8C8D",      # 参考/理论线
    "warning": "#C00000",      # 警告/偏差
}


def probe_font(cfg: dict) -> str:
    """按配置探测中文字体：preferred_font 优先，fallback_fonts 依次；全部不可用则失败并列出环境字体。"""
    candidates = [cfg.get("preferred_font", "Microsoft YaHei")] + [
        item for item in cfg.get("fallback_fonts", []) if item
    ]
    available = {font.name for font in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            return name
    env_fonts = sorted(available)
    raise RuntimeError(
        f"未找到可用中文字体（preferred/fallback 均缺失）。环境字体：{env_fonts}"
    )


def setup_style(cfg: dict) -> tuple[dict, str]:
    font_name = probe_font(cfg)
    theme = cfg.get("theme", "publication")
    size = float(cfg.get("font_size", 11))
    title_size = float(cfg.get("title_size", 14))
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [font_name, "DejaVu Sans"],
            "axes.unicode_minus": False,
            "axes.titlesize": title_size,
            "axes.titleweight": "bold",
            "axes.labelsize": size,
            "xtick.labelsize": size - 1,
            "ytick.labelsize": size - 1,
            "legend.fontsize": size - 1,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )
    return {"theme": theme, "font": font_name, "size": size, "title_size": title_size}, font_name


def make_figure_config(cfg: dict) -> dict:
    return {
        "theme": cfg.get("theme"),
        "preferred_font": cfg.get("preferred_font"),
        "font_size": cfg.get("font_size"),
        "title_size": cfg.get("title_size"),
        "figure_width": cfg.get("figure_width"),
        "figure_height": cfg.get("figure_height"),
        "dpi": cfg.get("dpi"),
        "background": cfg.get("background"),
        "palette": cfg.get("palette"),
    }


def load_spectrum(theta: int) -> np.ndarray:
    path = RESULTS_DIR / f"synthetic_spectrum_theta{theta}.csv"
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    return data  # [nu, R_clean, R_noisy]


def render_and_register(cfg: dict, style: dict, fig, title: str, kind: str, x_var: str | None, y_vars: list[str], source_hash: str) -> dict:
    fig_width = float(cfg.get("figure_width", 10))
    fig_height = float(cfg.get("figure_height", 6))
    dpi = int(cfg.get("dpi", 180))
    fig.set_size_inches(fig_width, fig_height)
    slug = "".join(char if char.isalnum() else "_" for char in kind.lower()).strip("_")
    stable_id = stable_figure_id(
        problem_id=PROBLEM_ID,
        question_id=QUESTION_ID,
        kind=kind,
        title=title,
        source_hash=source_hash,
        x=x_var,
        y=y_vars,
        style=style,
    )
    png_path = FIGURES_DIR / f"{stable_id}.png"
    fig.savefig(png_path, dpi=dpi, format="png", bbox_inches="tight")
    plt.close(fig)
    quality = inspect_png(png_path, PROBLEM_ID, QUESTION_ID)
    item = {
        "stable_id": stable_id,
        "question_id": QUESTION_ID,
        "assumption_version": ASSUMPTION_VERSION,
        "kind": kind,
        "title": title,
        "path": relative(png_path),
        "source_hash": source_hash,
        "script": relative(SCRIPT_PATH),
        "x": x_var,
        "y": y_vars,
        "included_in_summary": True,
        "quality_status": quality["status"],
        "quality": {
            "width": quality["width"],
            "height": quality["height"],
            "dark_border_ratio": quality["dark_border_ratio"],
            "warnings": quality.get("warnings", []),
        },
        "created_at": utc_now(),
    }
    register_figure(PROBLEM_ID, item)
    print(f"[registered] {stable_id}  {title}  ->  {relative(png_path)}  quality={quality['status']}")
    return item


def fig_reflectance_spectrum(cfg: dict, style: dict, source_hash: str) -> dict:
    """图 1：两入射角合成反射率谱，标注 Reststrahlen 区与模型谱段边界。"""
    fig, ax = plt.subplots()
    spectrum = {}
    for theta in (10, 15):
        data = load_spectrum(theta)
        nu, r_clean = data[:, 0], data[:, 1]
        spectrum[theta] = (nu, r_clean)
        ax.plot(nu, r_clean, lw=1.4, label=f"θ = {theta}°（入射角）",
                color=PALETTE["primary"] if theta == 10 else PALETTE["secondary"])
    # 标注峰极值（2000–4000 cm⁻¹ 弱色散段）
    nu10, r10 = spectrum[10]
    mask = (nu10 >= 2000) & (nu10 <= 4000)
    extrema = model.find_extrema(nu10[mask], r10[mask], kind="max")["max"]
    ax.plot(nu10[mask][extrema], r10[mask][extrema], "^", ms=5, color=PALETTE["accent"],
            label="干涉峰（同型极值）")
    ax.axvspan(*model.RESTSTRAHLEN_EXCLUDE_CM1, color="gray", alpha=0.15,
               label="Reststrahlen 区 [700, 1000] cm^-1（模型不适用）")
    ax.axvline(2000.0, color=PALETTE["neutral"], ls="--", lw=1.1,
               label="Sellmeier 边界 ν=2000 cm^-1（λ=5 µm）")
    ax.axvspan(2000.0, 4000.0, color=PALETTE["accent"], alpha=0.05)
    ax.set_xlabel("波数 ν (cm^-1)")
    ax.set_ylabel("反射率 R（无量纲，s/p 平均）")
    ax.set_title("两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0）")
    ax.set_xlim(400, 4000)
    ax.set_ylim(0.10, 0.27)
    ax.legend(loc="lower left", frameon=True, framealpha=0.9)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    return render_and_register(cfg, style, fig, ax.get_title(), "reflectance_spectrum", "nu_cm1", ["R"], source_hash)


def fig_dispersion_curve(cfg: dict, style: dict, source_hash: str) -> dict:
    """图 2：外延层折射率色散 n(ν)：Sellmeier（ν≥2000 cm⁻¹）与常数延伸（ν<2000 cm⁻¹）。"""
    nu = np.linspace(400.0, 4000.0, 1801)
    n = model.dispersion_from_nu(nu, extension="constant")
    fig, ax = plt.subplots()
    sellmeier_mask = nu >= 2000.0
    ax.plot(nu[sellmeier_mask], n[sellmeier_mask], color=PALETTE["primary"], lw=2.2,
            label="4H-SiC Sellmeier (4.1)（λ ≤ 5 µm）")
    ax.plot(nu[~sellmeier_mask], n[~sellmeier_mask], color=PALETTE["neutral"], lw=2.2, ls="--",
            label="常数延伸 n(5 µm)≈2.495（prob02 反演确定）")
    ax.axvline(2000.0, color=PALETTE["accent"], ls=":", lw=1.2)
    ax.text(2030, ax.get_ylim()[1] * 0.99, "Sellmeier 边界\nν=2000 cm^-1（λ=5 µm）", fontsize=style["size"] - 1, va="top")
    ax.axvspan(*model.RESTSTRAHLEN_EXCLUDE_CM1, color="gray", alpha=0.15,
               label="Reststrahlen 区（强色散/吸收）")
    ax.set_xlabel("波数 ν (cm^-1)")
    ax.set_ylabel("折射率 n（无量纲）")
    ax.set_title("外延层 4H-SiC 折射率色散模型 n(ν)")
    ax.set_xlim(400, 4000)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    ax.legend(loc="upper right", frameon=True, framealpha=0.9)
    # 顶部双轴：λ [µm]
    ax_top = ax.twiny()
    lam_ticks = [25.0, 10.0, 5.0, 2.5]
    ax_top.set_xticks([1e4 / lam for lam in lam_ticks])
    ax_top.set_xticklabels([f"{lam:g}" for lam in lam_ticks])
    ax_top.set_xlabel("波长 λ (µm)")
    ax_top.set_xlim(ax.get_xlim())
    return render_and_register(cfg, style, fig, ax.get_title(), "dispersion_curve", "nu_cm1", ["n"], source_hash)


def fig_phase_function(cfg: dict, style: dict, source_hash: str) -> dict:
    """图 3：色散化相位函数 g(ν)（(3.11)）单调性与同型相邻极值 Δg 恒定（(3.13) 机制）。"""
    nu = np.linspace(2000.0, 4000.0, 2001)
    n_nu = model.dispersion_from_nu(nu)
    theta = 10.0
    g = model.phase_function(nu, n_nu, theta)
    data = load_spectrum(10)
    r = np.interp(nu, data[:, 0], data[:, 1])
    peaks = model.find_extrema(nu, r, kind="max")["max"]
    nu_peaks = nu[peaks]
    g_peaks = g[peaks]
    delta_g = np.diff(g_peaks)

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) / 2.2))
    ax_l.plot(nu, g, color=PALETTE["primary"], lw=2.0, label="g(ν) = n(ν)·ν·cosθ′(ν)")
    for nup in nu_peaks:
        ax_l.axvline(nup, color=PALETTE["accent"], ls=":", lw=0.8, alpha=0.7)
    ax_l.plot(nu_peaks, g_peaks, "o", ms=4, color=PALETTE["accent"], label="干涉峰（m → m+2）")
    ax_l.set_xlabel("波数 ν (cm^-1)")
    ax_l.set_ylabel("相位函数 g(ν) (cm^-1)")
    ax_l.set_title("g(ν) 在弱色散段单调递增（(3.12) 前提）")
    ax_l.legend(loc="upper left", frameon=True, framealpha=0.9)
    ax_l.grid(True, which="major", ls=":", alpha=0.4)

    ax_r.plot(np.arange(1, delta_g.size + 1), delta_g, "o-", color=PALETTE["secondary"], lw=1.4,
              label="Δg = g(ν_{m+2}) − g(ν_m)")
    ax_r.axhline(500.0, color=PALETTE["neutral"], ls="--", lw=1.2, label="理论值 500 cm^-1（t=10 µm）")
    ax_r.set_xlabel("同型相邻极值对序号 k")
    ax_r.set_ylabel("Δg (cm^-1)")
    ax_r.set_title("同型相邻极值 Δg 恒定 → t=1e4/(2Δg)（(3.13)）")
    ax_r.set_ylim(495, 505)
    ax_r.legend(loc="upper right", frameon=True, framealpha=0.9)
    ax_r.grid(True, which="major", ls=":", alpha=0.4)
    fig.suptitle("色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）", fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return render_and_register(cfg, style, fig, "色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）", "phase_function_gap", "nu_cm1", ["g", "delta_g"], source_hash)


def fig_methods_compare(cfg: dict, style: dict, source_hash: str) -> dict:
    """图 4：三种反演方法 × 两入射角的厚度估计与相对偏差。"""
    result = json.loads((RESULTS_DIR / "result.json").read_text(encoding="utf-8"))
    est = result["estimates"]
    methods = ["方法A\n极值间隔 (3.10)", "相位法\n色散化 (3.13)", "全谱 NLS\n(3.5) 拟合"]
    keys = ["spacing", "phase", "nls_full"]
    fig, ax = plt.subplots()
    x_pos = np.arange(len(methods))
    width = 0.32
    for idx, theta in enumerate((10, 15)):
        vals = []
        for key in keys:
            block = est[f"theta_{theta}"][key]
            t = block["t_spacing_um"] if key == "spacing" else block["t_phase_um"] if key == "phase" else block["best"]["t_um"]
            vals.append(t)
        color = PALETTE["primary"] if theta == 10 else PALETTE["secondary"]
        offset = (idx - 0.5) * width
        bars = ax.bar(x_pos + offset, vals, width, color=color, alpha=0.85,
                      label=f"θ = {theta}°", edgecolor="white")
        for bar, v in zip(bars, vals):
            rel = (v - result["t_true_um"]) / result["t_true_um"] * 100
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                    f"{v:.3f}\n({rel:+.2f}%)", ha="center", va="bottom", fontsize=style["size"] - 2)
    ax.axhline(result["t_true_um"], color=PALETTE["neutral"], ls="-", lw=1.4, label="t_true = 10.000 µm")
    ax.axhspan(result["t_true_um"] * 0.99, result["t_true_um"] * 1.01, color=PALETTE["secondary"], alpha=0.08,
               label="±1% 容差带")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(methods)
    ax.set_ylabel("反演厚度 t (µm)")
    ax.set_title("三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注）")
    ax.set_ylim(9.6, 11.2)
    ax.legend(loc="lower left", frameon=True, framealpha=0.9, ncol=2)
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    return render_and_register(cfg, style, fig, ax.get_title(), "thickness_methods_compare", None, ["t_um"], source_hash)


def fig_spacing_bias(cfg: dict, style: dict, source_hash: str) -> dict:
    """图 5：方法 A 常数 n 近似的同型极值间隔偏差（Δν_obs≈188 vs Δν_theory≈196 cm⁻¹，约 4%）。"""
    result = json.loads((RESULTS_DIR / "result.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots()
    for theta in (10, 15):
        data = load_spectrum(theta)
        nu, r = data[:, 0], data[:, 1]
        mask = (nu >= 2000.0) & (nu <= 4000.0)
        peaks = model.find_extrema(nu[mask], r[mask], kind="max")["max"]
        spacings = model.same_type_spacings(nu[mask][peaks])
        color = PALETTE["primary"] if theta == 10 else PALETTE["secondary"]
        k = np.arange(1, spacings.size + 1)
        ax.plot(k, spacings, "o-", color=color, lw=1.3, ms=4, label=f"实测 Δν（θ={theta}°）")
    # 理论值按 (3.8) 用弱色散段 n_eff 计算（result.json verification 同源）
    nu_all = np.linspace(2000.0, 4000.0, 2001)
    n_eff = model.n_band_mean(nu_all)
    for theta in (10, 15):
        theory = model.evaluate_spacing_theory(result["t_true_um"], n_eff, float(theta))
        color = PALETTE["primary"] if theta == 10 else PALETTE["secondary"]
        ax.axhline(theory, color=color, ls="--", lw=1.2)
        ax.text(0.5, theory + 0.6, f"常数 n 理论 Δν（θ={theta}°）= {theory:.1f} cm^-1",
                fontsize=style["size"] - 2, color=color)
    ax.text(
        0.02, 0.02,
        "实测中位数 Δν ≈ 188.0 cm^-1（2000–4000 cm^-1 段）\n常数 n 理论 ≈ 196.2–196.8 cm^-1\n系统偏差约 4.2–4.7%（A3 文档化色散效应，需色散化修正）",
        transform=ax.transAxes, fontsize=style["size"] - 2, color=PALETTE["warning"], va="bottom", ha="left",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["warning"], "alpha": 0.85},
    )
    ax.set_xlabel("同型相邻极值对序号 k（2000–4000 cm^-1）")
    ax.set_ylabel("Δν (cm^-1)")
    ax.set_title("方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）")
    ax.legend(loc="lower left", frameon=True, framealpha=0.9)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    return render_and_register(cfg, style, fig, ax.get_title(), "spacing_constant_n_bias", "spacing_index", ["delta_nu"], source_hash)


def fig_nls_multistart(cfg: dict, style: dict, source_hash: str) -> dict:
    """图 6：NLS 多初值收敛轨迹与厚度周期歧义（rmse 景观）。"""
    solver = json.loads((RESULTS_DIR / "solver_status.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots()
    for theta in (10, 15):
        block = solver["fits"][f"theta_{theta}"]["full_band"]
        starts = block["starts"]
        period = block["period_um_estimate"]
        color = PALETTE["primary"] if theta == 10 else PALETTE["secondary"]
        for start in starts:
            global_sol = start["rmse"] is not None and start["rmse"] < 1e-6
            marker = "o" if global_sol else "x"
            ms = 9 if global_sol else 7
            scatter_kwargs = {"marker": marker, "s": ms**2, "color": PALETTE["accent"] if global_sol else color, "zorder": 3}
            if global_sol:
                scatter_kwargs.update({"edgecolors": "black", "linewidths": 0.8})
            ax.scatter(start["t0_um"], start["rmse"] if start["rmse"] is not None else 0.0, **scatter_kwargs)
            ax.annotate(f"t0={start['t0_um']:.3f}\n→ t={start['t_um']:.3f}",
                        (start["t0_um"], start["rmse"] if start["rmse"] is not None else 0.0),
                        textcoords="offset points", xytext=(8, 6), fontsize=style["size"] - 3)
        ax.axvline(10.0, color=PALETTE["neutral"], ls=":", lw=1.0)
        ax.text(10.0, 0.062, f"周期歧义 period≈{period:.2f} µm（θ={theta}°）", rotation=90,
                ha="right", va="top", fontsize=style["size"] - 3, color=PALETTE["neutral"])
    ax.set_xlabel("NLS 起始厚度 t0 (µm)（方法 A/相位法初值 ± period 布点）")
    ax.set_ylabel("拟合 RMSE（反射率，无量纲）")
    ax.set_title("全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm）")
    ax.set_ylim(-0.002, 0.075)
    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETTE["accent"], markeredgecolor="black", ms=9, label="全局解（t=10.000 µm）"),
        plt.Line2D([0], [0], marker="x", color=PALETTE["primary"], ms=9, label="局部极小（θ=10°）"),
        plt.Line2D([0], [0], marker="x", color=PALETTE["secondary"], ms=9, label="局部极小（θ=15°）"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=True, framealpha=0.9)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    return render_and_register(cfg, style, fig, ax.get_title(), "nls_multistart", "t0_um", ["rmse"], source_hash)


def fig_response_surface(cfg: dict, style: dict, source_hash: str) -> dict:
    """图 7：三维响应面 R(ν, θ) + 二维等高线配套（消歧）。"""
    nu = np.linspace(400.0, 4000.0, 161)
    theta_grid = np.linspace(0.0, 30.0, 31)
    n_nu = model.dispersion_from_nu(nu)
    R = np.empty((theta_grid.size, nu.size))
    for i, theta in enumerate(theta_grid):
        R[i, :] = model.forward_reflectance(nu, 10.0, n_nu, 3.0, float(theta))
    T, N = np.meshgrid(theta_grid, nu, indexing="ij")

    fig = plt.figure(figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) * 0.95))
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    ax3d.plot_surface(N, T, R, cmap="viridis", rstride=1, cstride=1, linewidth=0, antialiased=True, alpha=0.95)
    ax3d.view_init(elev=26, azim=-62)
    ax3d.set_xlabel("波数 ν (cm^-1)")
    ax3d.set_ylabel("入射角 θ (°)")
    ax3d.set_zlabel("反射率 R")
    ax3d.set_title("R(ν, θ) 响应面（t=10 µm，n_sub=3.0）", fontsize=style["title_size"] - 1)

    ax2d = fig.add_subplot(1, 2, 2)
    cf = ax2d.contourf(N, T, R, levels=16, cmap="viridis")
    cs = ax2d.contour(N, T, R, levels=16, colors="k", linewidths=0.4, alpha=0.45)
    ax2d.axhline(10.0, color=PALETTE["accent"], ls="--", lw=1.0)
    ax2d.axhline(15.0, color=PALETTE["accent"], ls="--", lw=1.0)
    ax2d.text(3800, 10.0, "θ=10°", color=PALETTE["accent"], fontsize=style["size"] - 2, ha="left", va="center")
    ax2d.text(3800, 15.0, "θ=15°", color=PALETTE["accent"], fontsize=style["size"] - 2, ha="left", va="center")
    ax2d.axvspan(*model.RESTSTRAHLEN_EXCLUDE_CM1, color="gray", alpha=0.15)
    ax2d.set_xlabel("波数 ν (cm^-1)")
    ax2d.set_ylabel("入射角 θ (°)")
    ax2d.set_title("二维等高线配套（θ=10°/15° 测量线）", fontsize=style["title_size"] - 1)
    fig.colorbar(cf, ax=ax2d, shrink=0.85, label="反射率 R")
    fig.suptitle("两光束干涉反射率随波数与入射角的三维响应面（静态 PNG 配 2D 等高线消歧）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return render_and_register(cfg, style, fig, "两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）", "response_surface", "nu_cm1", ["theta_deg", "R"], source_hash)


def main() -> None:
    cfg = config_section("visualization", PROBLEM_ID, QUESTION_ID)
    style, font_name = setup_style(cfg)
    print(f"[font] 使用中文字体：{font_name}")
    print(f"[cfg] theme={cfg.get('theme')} size={cfg.get('figure_width')}x{cfg.get('figure_height')} dpi={cfg.get('dpi')}")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    style_hash_payload = make_figure_config(cfg)
    source_hash = hash_path(RESULTS_DIR)
    items = []
    items.append(fig_reflectance_spectrum(cfg, style, source_hash))
    items.append(fig_dispersion_curve(cfg, style, source_hash))
    items.append(fig_phase_function(cfg, style, source_hash))
    items.append(fig_methods_compare(cfg, style, source_hash))
    items.append(fig_spacing_bias(cfg, style, source_hash))
    items.append(fig_nls_multistart(cfg, style, source_hash))
    items.append(fig_response_surface(cfg, style, source_hash))
    print(f"[done] 生成并登记 {len(items)} 张图，source_hash={source_hash[:12]}…，style_hash 见 stable_id。")


if __name__ == "__main__":
    main()
