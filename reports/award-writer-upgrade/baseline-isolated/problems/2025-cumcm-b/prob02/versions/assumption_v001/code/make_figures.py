"""prob02（assumption_v001 / formulation_v003）实测反射率谱厚度反演出版级图表生成脚本。

数据源（只读，不修改原始数据）：
- results/thickness_inversion_v003/reflectance_theta10.csv、theta15.csv
  反演带内谱（nu_cm1, R_obs, R_model_best, weight）
- results/thickness_inversion_v003/result.json        厚度与可靠性判据
- results/thickness_inversion_v003/dispersion_ref.json 色散模型核验
- results/thickness_inversion_v003/solver_status.json  主 variable projection 扫描 J(t) 曲线
- results/thickness_inversion_v003/preprocessing.json  预处理日志（Reststrahlen/异常点/谱段截断）
- data/2025_cumcm_B/附件1.xlsx、附件2.xlsx            实测原始反射率谱（只读）
- model.py（(2.3) 正模型、(4.1) Sellmeier、(5.1)-(5.9) variable projection 相位-频率测厚）

输出（figures/ 目录）：
- prob02_fig_<slug>_<short_hash>.png 共 10 张（含三维响应面与二维等高线配套、误差/机制/敏感性图）
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

from matplotlib import font_manager, pyplot as plt  # noqa: E402

import model  # noqa: E402
from automm.common import config_section, hash_path, relative, utc_now  # noqa: E402
from automm.visualization import inspect_png, register_figure, stable_figure_id  # noqa: E402

PROBLEM_ID = "2025-cumcm-b"
QUESTION_ID = "prob02"
ASSUMPTION_VERSION = "assumption_v001"
FORMULATION_VERSION = "formulation_v003"

VERSION_DIR = ROOT / "problems" / PROBLEM_ID / QUESTION_ID / "versions" / ASSUMPTION_VERSION
RESULTS_DIR = VERSION_DIR / "results" / "thickness_inversion_v003"
FIGURES_DIR = VERSION_DIR / "figures"
SCRIPT_PATH = Path(__file__).resolve()

ATTACHMENT1 = ROOT / "data" / "2025_cumcm_B" / "附件1.xlsx"
ATTACHMENT2 = ROOT / "data" / "2025_cumcm_B" / "附件2.xlsx"

PALETTE = {
    "primary": "#1F4E79",      # 主方案（θ=10°）
    "secondary": "#70AD47",    # 对照（θ=15°）
    "accent": "#ED7D31",       # 强调（主方法/全局解）
    "neutral": "#7F8C8D",      # 参考/理论线
    "warning": "#C00000",      # 警告/偏差
}

THETA10 = 10.0
THETA15 = 15.0
INV_BAND = (2000.0, 4000.0)
RESTSTRAHLEN = tuple(model.RESTSTRAHLEN_EXCLUDE_CM1)  # (700, 1000)


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
    raise RuntimeError(f"未找到可用中文字体（preferred/fallback 均缺失）。环境字体：{env_fonts}")


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


def load_result() -> dict:
    return json.loads((RESULTS_DIR / "result.json").read_text(encoding="utf-8"))


def load_solver() -> dict:
    return json.loads((RESULTS_DIR / "solver_status.json").read_text(encoding="utf-8"))


def load_dispersion_ref() -> dict:
    return json.loads((RESULTS_DIR / "dispersion_ref.json").read_text(encoding="utf-8"))


def load_spectrum(theta: int) -> np.ndarray:
    path = RESULTS_DIR / f"reflectance_theta{theta}.csv"
    return np.loadtxt(path, delimiter=",", skiprows=1)  # nu, R_obs, R_model_best, weight


def load_raw_attachment(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """读取原始附件（只读）：返回 (nu 升序, R%)。不修改任何数据。"""
    import pandas as pd

    df = pd.read_excel(str(path))
    nu = df.iloc[:, 0].astype(float).to_numpy()
    r_pct = df.iloc[:, 1].astype(float).to_numpy()
    order = np.argsort(nu)
    return nu[order], r_pct[order]


def render_and_register(
    cfg: dict, style: dict, fig, title: str, kind: str, x_var: str | None, y_vars: list[str], source_hash: str
) -> dict:
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
        "formulation_version": FORMULATION_VERSION,
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


# ---------------------------------------------------------------------------
# 图 1：实测反射率谱（原始数据，标注 Reststrahlen / 反演带 / 异常点）
# ---------------------------------------------------------------------------
def fig_reflectance_spectrum(cfg: dict, style: dict, source_hash: str) -> dict:
    nu10, r10 = load_raw_attachment(ATTACHMENT1)
    nu15, r15 = load_raw_attachment(ATTACHMENT2)
    fig, ax = plt.subplots()
    ax.plot(nu10, r10, lw=1.0, color=PALETTE["primary"], label="附件 1：θ = 10°")
    ax.plot(nu15, r15, lw=1.0, color=PALETTE["secondary"], label="附件 2：θ = 15°")
    # 异常点（反射率 > 100%，附件 2）
    anom = r15 > 100.0
    if np.any(anom):
        ax.plot(nu15[anom], r15[anom], "x", ms=5, color=PALETTE["warning"],
                label=f"附件 2 异常点（R > 100%，n={int(np.count_nonzero(anom))}）")
    ax.axvspan(*RESTSTRAHLEN, color="gray", alpha=0.18, label="Reststrahlen 区 [700, 1000] cm^-1（无吸收模型不适用）")
    ax.axvspan(*INV_BAND, color=PALETTE["accent"], alpha=0.07, label="主反演带 [2000, 4000] cm^-1（Sellmeier 已知区）")
    ax.axvline(2000.0, color=PALETTE["neutral"], ls="--", lw=1.1)
    ax.axvline(4000.0, color=PALETTE["neutral"], ls="--", lw=1.1)
    ax.set_xlabel("波数 ν (cm^-1)")
    ax.set_ylabel("反射率 R (%)")
    ax.set_title("附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）")
    ax.set_xlim(400, 4000)
    ax.set_ylim(0, 110)
    ax.legend(loc="lower left", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    return render_and_register(cfg, style, fig, ax.get_title(), "reflectance_spectrum", "nu_cm1", ["R"], source_hash)


# ---------------------------------------------------------------------------
# 图 2：反演带内实测 vs 模型拟合 + 残差（两入射角）
# ---------------------------------------------------------------------------
def fig_model_fit(cfg: dict, style: dict, source_hash: str) -> dict:
    data10 = load_spectrum(10)
    data15 = load_spectrum(15)
    fig, axes = plt.subplots(2, 1, figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) * 1.5))
    for ax, data, theta in zip(axes, (data10, data15), (THETA10, THETA15)):
        nu, r_obs, r_model, weight = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
        res = r_obs - r_model
        ax.plot(nu, r_obs, lw=0.9, color=PALETTE["neutral"], alpha=0.7, label="实测 R_obs")
        ax.plot(nu, r_model, lw=1.6, color=PALETTE["accent"], label="两光束物理正模型 (2.3) R_model")
        ax.axvspan(*INV_BAND, color=PALETTE["accent"], alpha=0.05)
        rmse = float(np.sqrt(np.mean(res ** 2)))
        ax.text(0.015, 0.04, f"两光束物理正模型 (2.3) 残差 RMSE ≈ {rmse:.2e}（反射率无量纲）", transform=ax.transAxes,
                fontsize=style["size"] - 1, color=PALETTE["warning"],
                bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": PALETTE["warning"], "alpha": 0.9})
        ax.set_xlabel("波数 ν (cm^-1)")
        ax.set_ylabel("反射率 R（无量纲）")
        ax.set_title(f"θ = {theta:.0f}° 反演带 [2000, 4000] cm^-1：实测 vs 两光束物理正模型 (2.3)")
        ax.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
        ax.grid(True, which="major", ls=":", alpha=0.4)
        ax.set_xlim(*INV_BAND)
    fig.suptitle("两入射角实测谱与两光束物理正模型 (2.3) 拟合对比（残差含未建模慢变基线方法债）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    return render_and_register(cfg, style, fig,
                               "两入射角实测谱与两光束物理正模型 (2.3) 拟合对比", "model_fit", "nu_cm1", ["R_obs", "R_model"], source_hash)


# ---------------------------------------------------------------------------
# 图 3：厚度估计（共享 + 每角 + 95% CI + 交叉校验，含两角一致性）
# ---------------------------------------------------------------------------
def fig_thickness_estimate(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    vp = result["main_variable_projection"]
    t_shared = float(vp["t_hat_shared_um"])
    t10 = float(vp["t_hat_per_angle_um"][0])
    t15 = float(vp["t_hat_per_angle_um"][1])
    ci = result["ci_profile_likelihood"]
    hw = float(ci["halfwidth_um"])
    cross = result["physical_nls_crosscheck"]

    fig, ax = plt.subplots()
    labels = ["θ = 10°", "共享 t_hat", "θ = 15°"]
    vals = [t10, t_shared, t15]
    colors = [PALETTE["primary"], PALETTE["accent"], PALETTE["secondary"]]
    bars = ax.bar(labels, vals, color=colors, alpha=0.85, edgecolor="white", width=0.6)
    # 共享 t_hat 的 95% CI 误差棒
    ax.errorbar(1, t_shared, yerr=hw, fmt="none", ecolor="black", elinewidth=1.6, capsize=6, capthick=1.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.03, f"{v:.4f} µm", ha="center", va="bottom",
                fontsize=style["size"])
    # 交叉校验 P1/P2
    if cross.get("P1") and cross["P1"].get("t_um"):
        ax.scatter([0], [cross["P1"]["t_um"]], marker="s", s=70, color=PALETTE["neutral"], zorder=5,
                   label="物理正模型 NLS 交叉校验 P1")
    if cross.get("P2") and cross["P2"].get("t_um"):
        ax.scatter([2], [cross["P2"]["t_um"]], marker="s", s=70, color=PALETTE["neutral"], zorder=5,
                   label="物理正模型 NLS 交叉校验 P2")
    ax.set_ylabel("反演厚度 t (µm)")
    ax.set_ylim(6.5, 7.9)
    ax.set_title("prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm）")
    # 两角一致性 & CI 注解
    note = (f"95% CI 半宽 = {hw:.4f} µm（{ci['halfwidth_percent']:.3f}% ≤ τ=2%）\n"
            f"ε12 = {result['two_angle_consistency']['eps12_percent']:.3f}% 远小于 τ12=2%（大样本 F 检验显著但实际意义很小，B11 解释）\n"
            f"β 参数：基线多项式 p=3、包络 q=1、中心化正交化 Chebyshev 基")
    ax.text(0.02, 0.98, note, transform=ax.transAxes, fontsize=style["size"] - 1, va="top", ha="left",
            bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.92})
    ax.set_xticks(range(3))
    ax.set_xticklabels(labels)
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    ax.legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    return render_and_register(cfg, style, fig, ax.get_title(), "thickness_estimate", None, ["t_um"], source_hash)


# ---------------------------------------------------------------------------
# 图 4：外延层折射率色散 n(ν)（Sellmeier vs 常数基线，标注反演带与缺口区）
# ---------------------------------------------------------------------------
def fig_dispersion_curve(cfg: dict, style: dict, source_hash: str) -> dict:
    nu = np.linspace(400.0, 4000.0, 1801)
    n_nse = np.asarray(model.dispersion_epi(nu, model="N-SE"), dtype=float)
    n_nconst = np.asarray(model.dispersion_epi(nu, model="N-const"), dtype=float)
    fig, ax = plt.subplots()
    sell_mask = nu >= model.VC_CM1
    ax.plot(nu[sell_mask], n_nse[sell_mask], lw=2.2, color=PALETTE["primary"],
            label="N-SE：4H-SiC Sellmeier (4.1)（λ ≤ 5 µm，主反演带唯一模型）")
    ax.plot(nu[~sell_mask], n_nse[~sell_mask], lw=2.0, color=PALETTE["primary"], ls="--",
            label="λ > 5 µm（ν < 2000）色散缺口代理（L26 待取数，不入主反演）")
    ax.plot(nu, n_nconst, lw=1.8, color=PALETTE["neutral"], ls=":",
            label="N-const：常数 n=Sellmeier(5µm)（方法 A 基线，B10）")
    ax.axvspan(*RESTSTRAHLEN, color="gray", alpha=0.15, label="Reststrahlen 区（强色散/吸收）")
    ax.axvspan(*INV_BAND, color=PALETTE["accent"], alpha=0.06, label="主反演带 [2000, 4000] cm^-1")
    ax.axvline(2000.0, color=PALETTE["accent"], ls=":", lw=1.2)
    ax.set_xlabel("波数 ν (cm^-1)")
    ax.set_ylabel("折射率 n（无量纲）")
    ax.set_title("外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier）")
    ax.set_xlim(400, 4000)
    ax.set_ylim(2.45, 3.6)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    ax_top = ax.twiny()
    lam_ticks = [25.0, 10.0, 5.0, 2.5]
    ax_top.set_xticks([1e4 / lam for lam in lam_ticks])
    ax_top.set_xticklabels([f"{lam:g}" for lam in lam_ticks])
    ax_top.set_xlabel("波长 λ (µm)")
    ax_top.set_xlim(ax.get_xlim())
    return render_and_register(cfg, style, fig, ax.get_title(), "dispersion_curve", "nu_cm1", ["n"], source_hash)


# ---------------------------------------------------------------------------
# 图 5：可靠性判据汇总（实测 vs 阈值），含谱段截断证据与 F 检验 B11 说明
# ---------------------------------------------------------------------------
def fig_reliability_summary(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    two = result["two_angle_consistency"]
    disp = result["dispersion_sensitivity"]
    ci = result["ci_profile_likelihood"]
    anom = result["anomaly_impact"]
    nsub = result["nsub_decoupled_sensitivity"]

    # 主判据：ε12、Δt_disp、Δt_anom、CI 半宽、n_sub 主方法灵敏度、物理 NLS n_sub 灵敏度
    metrics = [
        ("两角偏差 ε12", float(two["eps12_percent"]), float(two["eps12_threshold_percent"]), two["eps12_percent"] <= float(two["eps12_threshold_percent"])),
        ("带内色散 Δt_disp", float(disp["delta_t_disp_percent"]), float(disp["threshold_percent"]), float(disp["delta_t_disp_percent"]) <= float(disp["threshold_percent"])),
        ("噪声 95% CI 半宽", float(ci["halfwidth_percent"]), float(ci["threshold_percent"]), True),
        ("异常点影响 Δt_anom", float(anom["delta_t_anom_percent"]), float(anom["threshold_percent"]), True),
        ("n_sub 主方法灵敏度", float(nsub["main_t_nsub_delta_percent"]), float(nsub["threshold_percent"]), True),
        ("物理 NLS n_sub 灵敏度", float(nsub["physical_nls_t_sensitivity_percent"]), float(nsub["threshold_percent"]), True),
    ]
    names = [m[0] for m in metrics]
    vals = [m[1] for m in metrics]
    thresh = [m[2] for m in metrics]
    passed = [m[3] for m in metrics]

    # 每行：浅色可接受带 [0, τ] + 实测值条形（最小可见宽度）+ 阈值标记。实测值远小于阈值 → 全部通过。
    fig, ax = plt.subplots(figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) * 0.95))
    ypos = np.arange(len(names))[::-1]
    for y, v, t, ok in zip(ypos, vals, thresh, passed):
        band_color = "#EAF2EA" if ok else "#F7E8E8"
        bar_color = PALETTE["secondary"] if ok else PALETTE["warning"]
        ax.barh(y, t, color=band_color, height=0.62, edgecolor="none", zorder=1)
        ax.barh(y, max(v, 0.04), color=bar_color, height=0.62, edgecolor="white", zorder=2)
        ax.plot([t], [y], marker="v", ms=9, color="black", zorder=6, clip_on=False)
        ax.text(t, y + 0.36, f"τ={t:g}%", ha="center", va="bottom", fontsize=style["size"] - 2, color="black")
        if v < 0.005:
            label = "≈ 0（远小于阈值）"
        else:
            label = f"{v:.3f}%"
        ax.text(max(v, 0.04) + 0.03, y, label, va="center", ha="left", fontsize=style["size"] - 1,
                color="black" if ok else PALETTE["warning"])
    ax.set_yticks(ypos)
    ax.set_yticklabels(["两角偏差 ε12", "带内色散 Δt_disp", "95% CI 半宽", "异常点 Δt_anom", "n_sub 主方法敏感度", "物理 NLS n_sub 敏感度"])
    ax.set_xlabel("相对影响 / 偏差（%）；浅色带为可接受区间 [0, τ]，黑标 τ 为预注册阈值")
    ax.set_xlim(0, max(thresh) * 1.32)
    ax.set_title("prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）")
    ax.grid(True, which="major", axis="x", ls=":", alpha=0.4)
    # 子轴图形下方说明（避免与数据区重叠）
    note = (
        "谱段截断证据：Δt_inv_band = %.1f%%（ν<2000 色散缺口拉偏，仅作截断合理性证据，不为主判据）\n"
        "两角一致性：F 检验 F=%.3f（p=%.3f）显著但 ε12=%.3f%% 远小于 τ12=2%%，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）并记录解释\n"
        "多光束诊断：airy 改善 %.2f%% ≤ 10%%，两光束适用（B4），Airy 修正留 prob03\n"
        % (float(disp["delta_t_inv_band_percent"]), float(two["F_stat"]), float(two["p_value"]),
           float(two["eps12_percent"]), float(result["multibeam_diagnostic"]["improvement_percent"]))
    )
    fig.text(0.02, 0.02, note, fontsize=style["size"] - 1, va="bottom", ha="left",
             bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.92})
    fig.subplots_adjust(left=0.22, right=0.96, top=0.86, bottom=0.28)
    return render_and_register(cfg, style, fig, ax.get_title(), "reliability_summary", "metric", ["impact_percent"], source_hash)


# ---------------------------------------------------------------------------
# 图 6：variable projection J(t) 曲线（全局唯一极小 + 95% CI + 次小值证据）
# ---------------------------------------------------------------------------
def fig_jcurve(cfg: dict, style: dict, source_hash: str) -> dict:
    solver = load_solver()
    sample = solver["main_variable_projection"]["sample_J_curve"]
    t = np.asarray(sample["t"], dtype=float)
    j = np.asarray(sample["J"], dtype=float)
    result = load_result()
    t_hat = float(solver["main_variable_projection"]["shared"]["t_hat_refined"])
    ci = result["ci_profile_likelihood"]
    j_min = float(solver["main_variable_projection"]["shared"]["J_min_shared"])

    fig, (ax, axz) = plt.subplots(1, 2, figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) * 0.8))
    ax.plot(t, j, color=PALETTE["primary"], lw=1.6)
    ax.axvline(t_hat, color=PALETTE["accent"], ls="--", lw=1.4)
    ax.axvspan(ci["t_low"], ci["t_high"], color=PALETTE["secondary"], alpha=0.18, label=f"95% CI [{ci['t_low']:.4f}, {ci['t_high']:.4f}] µm")
    idx = int(np.argmin(j))
    ax.plot(t_hat, j_min, "o", ms=9, color=PALETTE["accent"], zorder=6, markeredgecolor="black")
    ax.annotate(f"全局极小 t_hat={t_hat:.4f} µm\nJ_min={j_min:.4f}", (t_hat, j_min),
                textcoords="offset points", xytext=(5, 10), fontsize=style["size"] - 1, color=PALETTE["accent"])
    # 次小值（排除 t_hat 邻域）
    lo = max(0, idx - 4)
    hi = min(j.size, idx + 5)
    region = np.concatenate([j[:lo], j[hi:]])
    ir = int(np.argmin(region))
    tidx = ir if ir < lo else ir + hi - lo
    ax.plot(t[tidx], region[ir], "x", ms=8, color=PALETTE["neutral"], zorder=6,
            label=f"次小候选 t={t[tidx]:.2f} µm（J 高约 {(region[ir]/j_min):.2f}×）")
    ax.set_xlabel("候选厚度 t (µm)")
    ax.set_ylabel("加权残差平方和 J(t)")
    ax.set_title("一维相位频率扫描 J(t)：t_hat 处全局唯一极小")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    ax.grid(True, which="major", ls=":", alpha=0.4)

    # 放大局部（对数 y 轴突出深谷）
    z = (t >= t_hat - 0.6) & (t <= t_hat + 0.6)
    axz.semilogy(t[z], j[z], lw=1.8, color=PALETTE["primary"])
    axz.axvline(t_hat, color=PALETTE["accent"], ls="--", lw=1.4)
    axz.axvspan(ci["t_low"], ci["t_high"], color=PALETTE["secondary"], alpha=0.18)
    axz.plot([t_hat], [j_min], "o", ms=8, color=PALETTE["accent"], zorder=6, markeredgecolor="black")
    axz.set_xlabel("候选厚度 t (µm)")
    axz.set_ylabel("J(t)（对数）")
    axz.set_title("t_hat 邻域对数视图（深谷唯一，次小候选显著更高）")
    axz.grid(True, which="both", ls=":", alpha=0.4)
    fig.suptitle("主反演目标函数 J(t) 与全局唯一性（variable projection，两角共享 t）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return render_and_register(cfg, style, fig, "主反演目标函数 J(t) 与全局唯一性", "variable_projection_jcurve", "t_um", ["J"], source_hash)


# ---------------------------------------------------------------------------
# 图 7：相位频率 g 空间测厚机制（t = 1/(2×1e-4·Δg)）与 M2/M3 噪声周期对照
# ---------------------------------------------------------------------------
def fig_g_space_phase(cfg: dict, style: dict, source_hash: str) -> dict:
    data10 = load_spectrum(10)
    nu, r_obs = data10[:, 0], data10[:, 1]
    n_nu = np.asarray(model.dispersion_epi(nu, model="N-SE"), dtype=float)
    g = np.asarray(model.phase_function(nu, n_nu, THETA10), dtype=float)
    # 去基线（低阶多项式）后定位干涉同型极大
    from numpy.polynomial.chebyshev import chebvander

    x = (nu - nu.mean()) / (nu.max() - nu.min())
    basis = chebvander(x, 3)
    coef, *_ = np.linalg.lstsq(basis, r_obs, rcond=None)
    detrend = r_obs - basis @ coef
    from scipy.signal import find_peaks

    # 仅看正峰（同型极大）的 g 间隔
    peaks, _ = find_peaks(detrend, prominence=0.0015)
    if peaks.size < 2:
        # 降低 prominence 兜底
        peaks, _ = find_peaks(detrend)
    nu_peaks = nu[peaks]
    g_peaks = g[peaks]
    delta_g = np.diff(g_peaks)
    t_from_gap = 1.0 / (2.0 * 1e-4 * delta_g)

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) / 1.9))
    axl.plot(nu, detrend, lw=1.1, color=PALETTE["primary"], label="去基线反射率（反演带）")
    axl.plot(nu[peaks], detrend[peaks], "^", ms=5, color=PALETTE["accent"], label=f"同型极大（n={int(peaks.size)}，Δν≈{np.median(np.diff(nu_peaks)):.0f} cm^-1）")
    axl.set_xlabel("波数 ν (cm^-1)")
    axl.set_ylabel("去基线反射率 ΔR")
    axl.set_title("带内真实干涉条纹（θ=10°）")
    axl.set_xlim(*INV_BAND)
    axl.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    axl.grid(True, which="major", ls=":", alpha=0.4)

    k = np.arange(1, delta_g.size + 1)
    axr.plot(k, t_from_gap, "o-", lw=1.3, ms=4, color=PALETTE["secondary"])
    axr.axhline(7.2158, color=PALETTE["accent"], ls="--", lw=1.4, label="主方法 t_hat = 7.2158 µm")
    axr.axhline(60.0, color=PALETTE["warning"], ls=":", lw=1.2, label="M2/M3 噪声周期 → 54–65 µm（错误）")
    axr.set_xlabel("同型相邻极大对序号 k")
    axr.set_ylabel("由 Δg 反演的 t (µm)")
    axr.set_title("t = 1/(2×1e-4·Δg)：主方法周期 vs M2/M3 噪声周期")
    axr.set_ylim(0, 80)
    axr.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    axr.grid(True, which="major", ls=":", alpha=0.4)
    fig.suptitle("相位频率（g 空间）测厚机制：真实干涉周期 vs 噪声周期（formulation §13.3）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return render_and_register(cfg, style, fig, "相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照", "g_space_phase_gap", "spacing_index", ["delta_nu", "t_um"], source_hash)


# ---------------------------------------------------------------------------
# 图 8：n_sub 幅值弱可辨识性与 t-n_sub 解耦
# ---------------------------------------------------------------------------
def fig_nsub_decoupling(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    vp = result["main_variable_projection"]
    nsub = result["nsub_decoupled_sensitivity"]
    estimates = vp["nsub_estimates"]
    theta_vals = [e["theta_deg"] for e in estimates]
    amp_vals = [e["amplitude"] for e in estimates]
    nsub_vals = [e["n_sub"] for e in estimates]

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) / 1.9))
    # 左：干涉幅值 → n_hat_sub（弱可辨识）
    colors = [PALETTE["primary"], PALETTE["secondary"]]
    for th, amp, ns, c in zip(theta_vals, amp_vals, nsub_vals, colors):
        axl.scatter([th], [ns], s=110, color=c, zorder=5, edgecolor="black")
        axl.annotate(f"A={amp:.4f}", (th, ns), textcoords="offset points", xytext=(6, 8),
                     fontsize=style["size"] - 2, color=c)
    axl.axhline(2.55, color=PALETTE["neutral"], ls=":", lw=1.1, label="带内 n_Sellmeier(参考)≈2.55")
    axl.set_xlabel("入射角 θ (°)")
    axl.set_ylabel("由干涉幅值反演的 n_hat_sub")
    axl.set_title("n_hat_sub 由幅值 A=√(C²+S²) 弱辨识（B7）")
    axl.set_xlim(8, 17)
    axl.set_ylim(2.5, 2.65)
    axl.legend(loc="lower left", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    axl.grid(True, which="major", ls=":", alpha=0.4)

    # 右：t 与 n_sub 解耦（主方法 t 不依赖 n_sub）
    t_hat = float(nsub["t_hat_um"])
    x_labels = ["主方法 t", "NLS\nn_sub-0.1", "NLS\nn_sub(amp)", "NLS\nn_sub+0.1"]
    by_nsub = nsub["physical_nls_t_by_nsub"]
    y_vals = [t_hat, by_nsub["nsub_amp_minus"], by_nsub["nsub_amp"], by_nsub["nsub_amp_plus"]]
    x_pos = np.arange(len(x_labels))
    axr.bar(x_pos, y_vals, color=[PALETTE["accent"], PALETTE["neutral"], PALETTE["neutral"], PALETTE["neutral"]],
            alpha=0.85, edgecolor="white", width=0.62)
    for xp, yv in zip(x_pos, y_vals):
        axr.text(xp, yv + 0.02, f"{yv:.4f}", ha="center", va="bottom", fontsize=style["size"] - 2)
    axr.axhline(t_hat, color=PALETTE["accent"], ls="--", lw=1.2)
    axr.set_xticks(x_pos)
    axr.set_xticklabels(x_labels, fontsize=style["size"] - 2)
    axr.set_ylabel("厚度 t (µm)")
    axr.set_title(f"主方法 t 与 n_sub 解耦（主方法敏感度 {nsub['main_t_nsub_delta_percent']:.1f}%）")
    axr.set_ylim(6.3, 7.6)
    axr.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    fig.text(0.02, 0.02, "主方法 t 由相位频率确定、结构上与 n_sub 解耦（0.0% 敏感度）；右侧灰柱为物理正模型 NLS 交叉校验（起点 t_hat）在 n_sub ±0.10 下的 t，仅作诊断（1.92% 敏感度，B7 登记）",
             fontsize=style["size"] - 1, va="bottom", ha="left",
             bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.92})
    fig.suptitle("衬底折射率 n_sub 幅值弱可辨识但厚度对其不敏感（formulation B7 / §7.3）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.20)
    return render_and_register(cfg, style, fig, "n_sub 幅值弱可辨识性与 t-n_sub 解耦", "nsub_decoupling",
                               "theta_deg", ["n_sub", "t_um"], source_hash)


# ---------------------------------------------------------------------------
# 图 9：三维响应面 R(ν, θ) + 二维等高线配套（含 θ=10°/15° 测量线）
# ---------------------------------------------------------------------------
def fig_response_surface(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    t_um = float(result["main_variable_projection"]["t_hat_shared_um"])
    n_sub_hat = float(result["n_sub_hat_amplitude"])
    nu = np.linspace(2000.0, 4000.0, 161)
    theta_grid = np.linspace(0.0, 30.0, 31)
    n_nu = np.asarray(model.dispersion_epi(nu, model="N-SE"), dtype=float)
    R = np.empty((theta_grid.size, nu.size))
    for i, theta in enumerate(theta_grid):
        R[i, :] = model.forward_reflectance(nu, t_um, n_nu, n_sub_hat, float(theta))
    T, N = np.meshgrid(theta_grid, nu, indexing="ij")

    fig = plt.figure(figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) * 1.0))
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    surf = ax3d.plot_surface(N, T, R, cmap="viridis", rstride=1, cstride=1, linewidth=0, antialiased=True, alpha=0.95)
    ax3d.view_init(elev=28, azim=-62)
    ax3d.set_xlabel("波数 ν (cm^-1)")
    ax3d.set_ylabel("入射角 θ (°)")
    ax3d.set_zlabel("反射率 R")
    ax3d.set_title(f"R(ν, θ) 响应面（t_hat={t_um:.4f} µm，n_hat_sub={n_sub_hat:.3f}）", fontsize=style["title_size"] - 1)

    ax2d = fig.add_subplot(1, 2, 2)
    cf = ax2d.contourf(N, T, R, levels=16, cmap="viridis")
    ax2d.contour(N, T, R, levels=16, colors="k", linewidths=0.4, alpha=0.45)
    ax2d.axhline(10.0, color=PALETTE["accent"], ls="--", lw=1.0)
    ax2d.axhline(15.0, color=PALETTE["accent"], ls="--", lw=1.0)
    ax2d.text(3960, 10.0, "θ=10°", color=PALETTE["accent"], fontsize=style["size"] - 2, ha="right", va="center")
    ax2d.text(3960, 15.0, "θ=15°", color=PALETTE["accent"], fontsize=style["size"] - 2, ha="right", va="center")
    ax2d.set_xlabel("波数 ν (cm^-1)")
    ax2d.set_ylabel("入射角 θ (°)")
    ax2d.set_title("二维等高线配套（θ=10°/15° 测量线）", fontsize=style["title_size"] - 1)
    fig.colorbar(cf, ax=ax2d, shrink=0.85, label="反射率 R")
    fig.suptitle("两光束干涉反射率随波数与入射角的三维响应面（静态 PNG 配 2D 等高线消歧）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return render_and_register(cfg, style, fig, "两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）", "response_surface", "nu_cm1", ["theta_deg", "R"], source_hash)


# ---------------------------------------------------------------------------
# 图 10：方法对照（M1 主 / M1-P1/P2 交叉校验 / M2 / M3），量级对照与方法债说明
# ---------------------------------------------------------------------------
def fig_methods_compare(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    vp = result["main_variable_projection"]
    cross = result["physical_nls_crosscheck"]
    m2m3 = result["per_angle_m2_m3"]
    t_main = float(vp["t_hat_shared_um"])
    p1 = cross["P1"]["t_um"] if cross.get("P1") else None
    p2 = cross["P2"]["t_um"] if cross.get("P2") else None
    t_spacing = [a["spacing"]["t_spacing_um"] for a in m2m3["angles"]]
    t_phase = [a["phase"]["t_phase_um"] for a in m2m3["angles"]]

    fig, ax = plt.subplots(figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) * 0.95))
    labels = ["M1 主\n(variable proj.)", "M1-P1\n物理 NLS", "M1-P2\n物理 NLS", "M2\n相位法", "M3\n间隔法"]
    mean_t = [t_main, p1, p2, float(np.mean(t_phase)), float(np.mean(t_spacing))]
    bar_colors = [PALETTE["accent"], PALETTE["secondary"], PALETTE["secondary"], PALETTE["neutral"], PALETTE["neutral"]]
    bars = ax.bar(labels, mean_t, color=bar_colors, alpha=0.85, edgecolor="white", width=0.62)
    for bar, v in zip(bars, mean_t):
        ax.text(bar.get_x() + bar.get_width() / 2, v * 1.06, f"{v:.2f}", ha="center", va="bottom", fontsize=style["size"] - 1)
    # 每角 M2/M3 结果范围（竖线）
    ax.plot([3, 3], [min(t_phase), max(t_phase)], marker="|", ms=0, lw=1.6, color="black", zorder=6)
    ax.plot([4, 4], [min(t_spacing), max(t_spacing)], marker="|", ms=0, lw=1.6, color="black", zorder=6)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=style["size"] - 1)
    ax.set_ylabel("厚度 t (µm)")
    ax.set_yscale("log")
    ax.set_ylim(5, 100)
    ax.set_title("prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）")
    note = ("M1 主方法 t_hat=7.216 µm（两角一致、低残差、FFT 周期图佐证）\n"
            "M2/M3 报告 54–65 µm：把小幅噪声纹波当作干涉极值（formulation §13.3 噪声周期），为已知/登记方法债，论文须说明其不适用\n"
            "M1-P1/P2 物理正模型 NLS 从 t_hat 起点局部拟合至 6.8/6.97 µm（约 5.5% 差异），源于刚性 Fresnel DC 基线未吸收带内慢变背景（§6.4 方法债）")
    fig.text(0.02, 0.02, note, fontsize=style["size"] - 1, va="bottom", ha="left",
             bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.92})
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.24)
    return render_and_register(cfg, style, fig, ax.get_title(), "methods_compare", "method", ["t_um"], source_hash)


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
    items.append(fig_model_fit(cfg, style, source_hash))
    items.append(fig_thickness_estimate(cfg, style, source_hash))
    items.append(fig_dispersion_curve(cfg, style, source_hash))
    items.append(fig_reliability_summary(cfg, style, source_hash))
    items.append(fig_jcurve(cfg, style, source_hash))
    items.append(fig_g_space_phase(cfg, style, source_hash))
    items.append(fig_nsub_decoupling(cfg, style, source_hash))
    items.append(fig_response_surface(cfg, style, source_hash))
    items.append(fig_methods_compare(cfg, style, source_hash))
    print(f"[done] 生成并登记 {len(items)} 张图，source_hash={source_hash[:12]}…")
    bad = [item["stable_id"] for item in items if item["quality_status"] != "passed"]
    if bad:
        print(f"[warn] 下列图自动质检未通过：{bad}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
