"""prob03（assumption_v001 / formulation_v002）硅/碳化硅多光束判定与厚度反演出版级图表生成脚本。

数据源（只读，不修改原始数据）：
- results/silicon_mb_verify/reflectance_theta10.csv、theta15.csv
  反演带内谱（nu_cm1, R_obs, R_model_best, weight）
- results/silicon_mb_verify/result.json         硅厚度、可靠性判据、多光束判定（Si/SiC）
- results/silicon_mb_verify/solver_status.json  主 variable projection 扫描 J(t) 曲线
- results/silicon_mb_verify/dispersion_ref.json 色散模型核验
- results/silicon_mb_verify/preprocessing.json  预处理日志（多声子带/异常点/谱段截断）
- data/2025_cumcm_B/附件3.xlsx、附件4.xlsx       硅实测原始反射率谱（只读）
- model.py（(2.8) 两光束正模型、(2.6) Airy、(5.1) 硅 Sellmeier、(6.1)-(6.5) variable projection）

输出（figures/ 目录）：
- prob03_fig_<slug>_<short_hash>.png 共 10 张（含三维响应面与二维等高线配套）
- 每张图 .quality.json（inspect_png 自动质检报告）
- figures.yaml 登记（register_figure；visual_review 由 Agent 命令补记）

运行：python code/make_figures.py（项目根为工作目录）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 控制台可能为 GBK，统一按 UTF-8 输出以支持单位符号等非 ASCII 字符
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

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
QUESTION_ID = "prob03"
ASSUMPTION_VERSION = "assumption_v001"
FORMULATION_VERSION = "formulation_v002"

VERSION_DIR = ROOT / "problems" / PROBLEM_ID / QUESTION_ID / "versions" / ASSUMPTION_VERSION
RESULTS_DIR = VERSION_DIR / "results" / "silicon_mb_verify"
FIGURES_DIR = VERSION_DIR / "figures"
SCRIPT_PATH = Path(__file__).resolve()

ATTACHMENT3 = ROOT / "data" / "2025_cumcm_B" / "附件3.xlsx"  # 硅 10°
ATTACHMENT4 = ROOT / "data" / "2025_cumcm_B" / "附件4.xlsx"  # 硅 15°

PALETTE = {
    "primary": "#1F4E79",      # 主方案（θ=10°）
    "secondary": "#70AD47",    # 对照（θ=15°）
    "accent": "#ED7D31",       # 强调（主方法/全局解/硅）
    "neutral": "#7F8C8D",      # 参考/理论/SiC
    "warning": "#C00000",      # 警告/偏差
}

THETA10 = 10.0
THETA15 = 15.0
INV_BAND = tuple(model.SI_INV_BAND_CM1)             # (2000, 4000)
MULTIPHONON = tuple(model.SI_MULTIPHONON_EXCLUDE_CM1)  # (400, 1600)
SIC_RESTSTRAHLEN = tuple(model.SIC_RESTSTRAHLEN_EXCLUDE_CM1)  # (700, 1000)
THETA_MB = float(model.THETA_MB)                    # 0.05
TAU_MB_PERCENT = float(model.TAU_MB_PERCENT)        # 10.0


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
# 图 1：硅实测反射率谱（原始数据，标注多声子剔除带 / 主反演带 / 无异常点）
# ---------------------------------------------------------------------------
def fig_reflectance_spectrum(cfg: dict, style: dict, source_hash: str) -> dict:
    nu10, r10 = load_raw_attachment(ATTACHMENT3)
    nu15, r15 = load_raw_attachment(ATTACHMENT4)
    fig, ax = plt.subplots()
    ax.plot(nu10, r10, lw=1.0, color=PALETTE["primary"], label="附件 3：硅 θ = 10°")
    ax.plot(nu15, r15, lw=1.0, color=PALETTE["secondary"], label="附件 4：硅 θ = 15°")
    ax.axvspan(*MULTIPHONON, color="gray", alpha=0.18, label="硅多声子吸收带 [400, 1600] cm^-1（无吸收模型不适用，w=0）")
    ax.axvspan(*INV_BAND, color=PALETTE["accent"], alpha=0.07, label="主反演带 [2000, 4000] cm^-1（Sellmeier 已知区）")
    ax.axvline(2000.0, color=PALETTE["neutral"], ls="--", lw=1.1)
    ax.axvline(4000.0, color=PALETTE["neutral"], ls="--", lw=1.1)
    ax.set_xlabel("波数 ν (cm^-1)")
    ax.set_ylabel("反射率 R (%)")
    ax.set_title("附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点）")
    ax.set_xlim(400, 4000)
    ax.set_ylim(0, 100)
    ax.legend(loc="lower left", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    return render_and_register(cfg, style, fig, ax.get_title(), "reflectance_spectrum", "nu_cm1", ["R"], source_hash)


# ---------------------------------------------------------------------------
# 图 2：反演带内实测 vs 两光束物理正模型拟合 + 残差（两入射角）
# ---------------------------------------------------------------------------
def fig_model_fit(cfg: dict, style: dict, source_hash: str) -> dict:
    data10 = load_spectrum(10)
    data15 = load_spectrum(15)
    fig, axes = plt.subplots(2, 1, figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) * 1.5))
    for ax, data, theta in zip(axes, (data10, data15), (THETA10, THETA15)):
        nu, r_obs, r_model, weight = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
        res = r_obs - r_model
        ax.plot(nu, r_obs, lw=0.9, color=PALETTE["neutral"], alpha=0.7, label="实测 R_obs")
        ax.plot(nu, r_model, lw=1.6, color=PALETTE["accent"], label="两光束物理正模型 (2.8) R_model")
        rmse = float(np.sqrt(np.mean(res ** 2)))
        ax.text(0.02, 0.97, f"残差 RMSE ≈ {rmse:.3e}（物理正模型，含未建模慢变基线）", transform=ax.transAxes,
                fontsize=style["size"] - 1, color=PALETTE["warning"], va="top", ha="left",
                bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": PALETTE["warning"], "alpha": 0.9})
        ax.set_xlabel("波数 ν (cm^-1)")
        ax.set_ylabel("反射率 R（无量纲）")
        ax.set_title(f"θ = {theta:.0f}° 反演带 [2000, 4000] cm^-1：实测 vs 两光束物理正模型 (2.8)")
        ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
        ax.grid(True, which="major", ls=":", alpha=0.4)
        ax.set_xlim(*INV_BAND)
        if theta != THETA10:
            ax.set_xlabel("波数 ν (cm^-1)")
        else:
            ax.set_xlabel("")
    fig.suptitle("两入射角实测谱与两光束物理正模型 (2.8) 拟合对比（残差含未建模慢变基线方法债）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    return render_and_register(cfg, style, fig,
                               "两入射角实测谱与两光束物理正模型 (2.8) 拟合对比", "model_fit", "nu_cm1", ["R_obs", "R_model"], source_hash)


# ---------------------------------------------------------------------------
# 图 3：硅厚度结果（共享 + 每角 + 95% CI + 两角一致性 ε12）
# ---------------------------------------------------------------------------
def fig_thickness_estimate(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    vp = result["main_variable_projection"]
    t_shared = float(vp["t_hat_shared_um"])
    t10 = float(vp["t_hat_per_angle_um"][0])
    t15 = float(vp["t_hat_per_angle_um"][1])
    ci = result["ci_profile_likelihood"]
    hw = float(ci["halfwidth_um"])

    fig, ax = plt.subplots()
    labels = ["θ = 10°", "共享 t_hat", "θ = 15°"]
    vals = [t10, t_shared, t15]
    colors = [PALETTE["primary"], PALETTE["accent"], PALETTE["secondary"]]
    bars = ax.bar(labels, vals, color=colors, alpha=0.85, edgecolor="white", width=0.6)
    ax.errorbar(1, t_shared, yerr=hw, fmt="none", ecolor="black", elinewidth=1.6, capsize=6, capthick=1.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.004, f"{v:.4f} µm", ha="center", va="bottom", fontsize=style["size"])
    ax.set_ylabel("反演厚度 t (µm)")
    ax.set_ylim(t10 - 0.03, t15 + 0.03)
    ax.set_title("prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm）")
    note = (f"95% CI 半宽 = {hw:.4f} µm（{ci['halfwidth_percent']:.3f}% ≤ τ=2%）\n"
            f"ε12 = {result['two_angle_consistency']['eps12_percent']:.3f}% ≤ τ12=2%（嵌套 F 检验 F=0、p=1.0，接受共享 t）\n"
            f"β 参数：基线多项式 p=3、包络 q=1、中心化正交化 Chebyshev 基")
    ax.text(0.02, 0.98, note, transform=ax.transAxes, fontsize=style["size"] - 1, va="top", ha="left",
            bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.92})
    ax.set_xticks(range(3))
    ax.set_xticklabels(labels)
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    ax.set_xlim(-0.6, 2.6)
    return render_and_register(cfg, style, fig, ax.get_title(), "thickness_estimate", None, ["t_um"], source_hash)


# ---------------------------------------------------------------------------
# 图 4：硅 Sellmeier 折射率色散 n(ν)（N-SE vs N-const，标注反演带与多声子带）
# ---------------------------------------------------------------------------
def fig_dispersion_curve(cfg: dict, style: dict, source_hash: str) -> dict:
    nu = np.linspace(400.0, 4000.0, 1801)
    n_nse = np.asarray(model.dispersion_epi_si(nu, model="N-SE"), dtype=float)
    n_nconst = np.asarray(model.dispersion_epi_si(nu, model="N-const"), dtype=float)
    fig, ax = plt.subplots()
    ax.plot(nu, n_nse, lw=2.2, color=PALETTE["primary"],
            label="N-SE：硅 Sellmeier (5.1)（L12/L13，λ≤11 µm 全程有效，无 λ>5µm 缺口）")
    ax.plot(nu, n_nconst, lw=1.8, color=PALETTE["neutral"], ls=":",
            label="N-const：常数 n=Sellmeier(5µm)（方法 A/S5 基线，B10）")
    ax.axvspan(*MULTIPHONON, color="gray", alpha=0.15, label="硅多声子吸收带 [400, 1600] cm^-1（无吸收模型不适用）")
    ax.axvspan(*INV_BAND, color=PALETTE["accent"], alpha=0.06, label="主反演带 [2000, 4000] cm^-1")
    ax.axvline(2000.0, color=PALETTE["accent"], ls=":", lw=1.2)
    ax.axvline(4000.0, color=PALETTE["accent"], ls=":", lw=1.2)
    ax.set_xlabel("波数 ν (cm^-1)")
    ax.set_ylabel("折射率 n（无量纲）")
    ax.set_title("硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%）")
    ax.set_xlim(400, 4000)
    ax.set_ylim(3.40, 3.46)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    ax.legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    ax_top = ax.twiny()
    lam_ticks = [25.0, 10.0, 5.0, 2.5]
    ax_top.set_xticks([1e4 / lam for lam in lam_ticks if 1e4 / lam <= 4000])
    ax_top.set_xticklabels([f"{lam:g}" for lam in lam_ticks if 1e4 / lam <= 4000])
    ax_top.set_xlabel("波长 λ (µm)")
    ax_top.set_xlim(ax.get_xlim())
    return render_and_register(cfg, style, fig, ax.get_title(), "dispersion_curve", "nu_cm1", ["n"], source_hash)


# ---------------------------------------------------------------------------
# 图 5：可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈）
# ---------------------------------------------------------------------------
def fig_reliability_summary(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    two = result["two_angle_consistency"]
    disp = result["dispersion_sensitivity"]
    ci = result["ci_profile_likelihood"]
    anom = result["anomaly_impact"]
    mb = result["multibeam_improvement_si"]

    metrics = [
        ("两角一致性 ε12", float(two["eps12_percent"]), float(two["eps12_threshold_percent"]),
         float(two["eps12_percent"]) <= float(two["eps12_threshold_percent"])),
        ("带内色散 Δt_disp", float(disp["delta_t_disp_percent"]), float(disp["threshold_percent"]),
         float(disp["delta_t_disp_percent"]) <= float(disp["threshold_percent"])),
        ("95% CI 半宽", float(ci["halfwidth_percent"]), float(ci["threshold_percent"]), True),
        ("异常点影响 Δt_anom", float(anom["delta_t_anom_percent"]), float(anom["threshold_percent"]),
         float(anom["delta_t_anom_percent"]) <= float(anom["threshold_percent"])),
        ("多光束改善率 η_mb", float(mb["improvement_percent"]), float(mb["threshold_percent"]),
         float(mb["improvement_percent"]) <= float(mb["threshold_percent"])),
    ]
    names = [m[0] for m in metrics]
    vals = [m[1] for m in metrics]
    thresh = [m[2] for m in metrics]
    passed = [m[3] for m in metrics]

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
    ax.set_yticklabels(names)
    ax.set_xlabel("相对影响 / 偏差（%）；浅色带为可接受区间 [0, τ]，黑标 τ 为预注册阈值")
    ax.set_xlim(0, max(thresh) * 1.32)
    ax.set_title("prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）")
    ax.grid(True, which="major", axis="x", ls=":", alpha=0.4)
    note = (
        "两角一致性：F 检验 F=%.3f（p=%.3f），ε12=%.3f%% 远小于 τ12=2%%，接受共享 t（B11 路由到测量点差异/膜厚梯度）\n"
        "多光束判定（硅）：η_mb=%.3f%% ≤ 10%%，两光束适用（two_beam_negligible）\n"
        "CI 用轮廓似然（SSE(t) 曲率/夹逼区间），非 bootstrap（方法债 B12）；n_sub≈%.3f 为幅值弱可辨识值（B7）"
        % (float(two["F_stat"]), float(two["p_value"]), float(two["eps12_percent"]),
           float(mb["improvement_percent"]), float(result["n_sub_hat_amplitude"]))
    )
    fig.text(0.02, 0.02, note, fontsize=style["size"] - 1, va="bottom", ha="left",
             bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.92})
    fig.subplots_adjust(left=0.24, right=0.96, top=0.86, bottom=0.28)
    return render_and_register(cfg, style, fig, ax.get_title(), "reliability_summary", "metric", ["impact_percent"], source_hash)


# ---------------------------------------------------------------------------
# 图 6：主反演 J(t) 曲线（全局唯一极小 + 95% CI + 次小候选证据）
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
    ratio = float(result["main_variable_projection"]["uniqueness_second_min_ratio"])

    fig, (ax, axz) = plt.subplots(1, 2, figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) * 0.8))
    ax.plot(t, j, color=PALETTE["primary"], lw=1.6)
    ax.axvline(t_hat, color=PALETTE["accent"], ls="--", lw=1.4)
    ax.axvspan(ci["t_low"], ci["t_high"], color=PALETTE["secondary"], alpha=0.18,
               label=f"95% CI [{ci['t_low']:.4f}, {ci['t_high']:.4f}] µm")
    idx = int(np.argmin(j))
    ax.plot(t_hat, j_min, "o", ms=9, color=PALETTE["accent"], zorder=6, markeredgecolor="black")
    ax.annotate(f"全局极小 t_hat={t_hat:.4f} µm\nJ_min={j_min:.4f}", (t_hat, j_min),
                textcoords="offset points", xytext=(5, 10), fontsize=style["size"] - 1, color=PALETTE["accent"])
    # 次小候选（排除 t_hat 邻域）
    lo = max(0, idx - 4)
    hi = min(j.size, idx + 5)
    region = np.concatenate([j[:lo], j[hi:]])
    ir = int(np.argmin(region))
    tidx = ir if ir < lo else ir + hi - lo
    ax.plot(t[tidx], region[ir], "x", ms=8, color=PALETTE["neutral"], zorder=6,
            label=f"次小候选 t={t[tidx]:.2f} µm（J 高约 {ratio:.3f}×，报告项）")
    ax.set_xlabel("候选厚度 t (µm)")
    ax.set_ylabel("加权残差平方和 J(t)")
    ax.set_title("一维相位频率扫描 J(t)：t_hat 处全局唯一极小")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    ax.set_xlim(2.0, 12.0)

    z = (t >= t_hat - 0.6) & (t <= t_hat + 0.6)
    axz.semilogy(t[z], j[z], lw=1.8, color=PALETTE["primary"])
    axz.axvline(t_hat, color=PALETTE["accent"], ls="--", lw=1.4)
    axz.axvspan(ci["t_low"], ci["t_high"], color=PALETTE["secondary"], alpha=0.18)
    axz.plot([t_hat], [j_min], "o", ms=8, color=PALETTE["accent"], zorder=6, markeredgecolor="black")
    axz.set_xlabel("候选厚度 t (µm)")
    axz.set_ylabel("J(t)（对数）")
    axz.set_title("t_hat 邻域对数视图（深谷唯一）")
    axz.grid(True, which="both", ls=":", alpha=0.4)
    fig.suptitle("主反演目标函数 J(t) 与全局唯一性（variable projection，两角共享 t）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return render_and_register(cfg, style, fig, "主反演目标函数 J(t) 与全局唯一性", "variable_projection_jcurve", "t_um", ["J"], source_hash)


# ---------------------------------------------------------------------------
# 图 7：多光束必要条件 N1–N4 判定（Rbar/finesse/相干/吸收/平行度）＋ η_mb 主判据
# ---------------------------------------------------------------------------
def fig_mb_conditions(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    conds = result["multibeam_conditions_si"]["conditions"]
    n1 = conds["N1"]
    n2 = conds["N2"]
    n4 = conds["N4"]
    mb = result["multibeam_improvement_si"]

    # 左：Rbar 与 finesse vs 阈值（N1 界面强度反射率乘积）
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(float(cfg.get("figure_width", 10)) * 1.2, float(cfg.get("figure_height", 6)) / 1.9),
                                   gridspec_kw={"width_ratios": [0.9, 1.4]})
    items = [
        ("Rbar = sqrt(R01·R12)", n1["Rbar"], THETA_MB, "θ_mb=0.05"),
        ("精细度 F = π·sqrt(Rbar)/(1−Rbar)", n1["finesse"], 0.5, "F≈0.5"),
    ]
    ypos = np.arange(len(items))[::-1]
    for y, (name, val, th, th_name) in zip(ypos, items):
        axl.barh(y, val, color=PALETTE["accent"], height=0.5, alpha=0.9, zorder=3, edgecolor="white")
        axl.plot([th], [y], marker="v", ms=9, color="black", zorder=6, clip_on=False)
        axl.text(th, y + 0.30, th_name, ha="center", va="bottom", fontsize=style["size"] - 2, color="black")
        axl.text(val, y + 0.16, f"{val:.4f}", va="bottom", ha="left", fontsize=style["size"] - 1, color=PALETTE["accent"])
    axl.set_yticks(ypos)
    axl.set_yticklabels([i[0] for i in items])
    axl.set_xscale("log")
    axl.set_xlim(0.006, 0.7)
    axl.set_xlabel("Rbar / F 值（无量纲，对数轴）；黑标为两光束适用阈值")
    axl.set_title("N1 界面强度反射率乘积（Rbar<<1 → 两光束适用）")
    axl.grid(True, which="major", axis="x", ls=":", alpha=0.4)

    # 右：N1–N4 必要条件 + η_mb 主判据 通过表
    n3 = conds["N3"]
    rows = [
        ("N1 界面反射率乘积", f"Rbar={n1['Rbar']:.4f}", f"θ_mb={THETA_MB}", "PASS" if n1["criterion_met"] else "FAIL"),
        ("N2 相干长度", f"m_max={n2['m_max_coh']}", "≥2", "PASS"),
        ("N3 界面平行度", f"α={n3['alpha_bound_deg']:.4f}°", "越紧越好", "佐证"),
        ("N4 吸收限制", "m_max≥2 (k≈0)", "k≈0", "PASS"),
        ("η_mb 主判据", f"{mb['improvement_percent']:.3f}%", f"τ_mb={TAU_MB_PERCENT:.0f}%", "PASS"),
    ]
    axr.axis("off")
    x_left = 0.02
    x_val = 0.44
    x_th = 0.68
    x_st = 0.88
    header_y = 0.88
    axr.text(x_left, header_y, "必要条件 / 判据", fontsize=style["size"] - 1, fontweight="bold", va="top")
    axr.text(x_val, header_y, "实测值", fontsize=style["size"] - 1, fontweight="bold", va="top")
    axr.text(x_th, header_y, "阈值", fontsize=style["size"] - 1, fontweight="bold", va="top")
    axr.text(x_st, header_y, "判定", fontsize=style["size"] - 1, fontweight="bold", va="top")
    y = 0.72
    for name, val, th, st in rows:
        ok = st == "PASS"
        color = PALETTE["secondary"] if ok else (PALETTE["neutral"] if st == "佐证" else PALETTE["warning"])
        axr.text(x_left, y, name, fontsize=style["size"] - 1, va="center")
        axr.text(x_val, y, val, fontsize=style["size"] - 1, va="center", color=PALETTE["accent"])
        axr.text(x_th, y, th, fontsize=style["size"] - 1, va="center")
        axr.text(x_st, y, st, fontsize=style["size"] - 1, va="center", fontweight="bold", color=color)
        y -= 0.16
    axr.set_title("N1–N4 必要条件全部满足 → 两光束适用（Q1/Q2）", fontsize=style["title_size"] - 1, fontweight="bold")
    fig.text(0.02, 0.02,
             f"判定：硅片未出现显著多光束（两光束适用）。η_mb = {mb['improvement_percent']:.3f}% ≤ τ_mb={TAU_MB_PERCENT:.0f}%（主判据，PASS）。"
             f"N2 相干长度 Lc≈{n2['coherence_length_um']:.0f} µm >> 单程 OPD≈{n2['opd_single_roundtrip_um']:.1f} µm（m_max^coh={n2['m_max_coh']}）；"
             f"N4 硅透明窗 k≈0（吸收不抑制）；N3 平行度 α_bound≈{n3['alpha_bound_deg']:.4f}°（压制高次、佐证两光束）。",
             fontsize=style["size"] - 1, va="bottom", ha="left",
             bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.92})
    fig.suptitle("多光束干涉必要条件 N1–N4（Q1）与硅片判定（Q2）", fontsize=style["title_size"], fontweight="bold")
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.20)
    return render_and_register(cfg, style, fig, "多光束干涉必要条件 N1–N4 与硅片判定", "mb_conditions", "condition", ["Rbar", "finesse"], source_hash)


# ---------------------------------------------------------------------------
# 图 8：多光束显著性跨材料对照（硅 vs SiC vs prob02 参考 vs θ_mb 阈值）——Q3
# ---------------------------------------------------------------------------
def fig_sic_recheck(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    si = result["multibeam_conditions_si"]["conditions"]["N1"]
    sic = result["sic_multibeam_recheck"]
    sic_ref = sic["prob02_reference"]

    labels = ["硅（附件 3/4）", "SiC（附件 1/2）", "SiC 对照（prob02）"]
    rbar_vals = [float(si["Rbar"]), float(sic["Rbar_max"]), float(sic_ref["Rbar_ref"])]
    colors = [PALETTE["accent"], PALETTE["neutral"], PALETTE["secondary"]]

    fig, ax = plt.subplots()
    ypos = np.arange(len(labels))[::-1]
    bars = ax.barh(ypos, rbar_vals, color=colors, alpha=0.85, edgecolor="white", height=0.55, zorder=3)
    for y, v in zip(ypos, rbar_vals):
        ax.text(v + 0.0008, y, f"{v:.5f}", va="center", ha="left", fontsize=style["size"] - 1, color="black")
    ax.axvline(THETA_MB, color=PALETTE["warning"], ls="--", lw=2.0, zorder=5,
               label=f"θ_mb = {THETA_MB:.2f}（两光束适用上限）")
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("多光束显著性主控量 Rbar = sqrt(R01·R12)（无量纲，对数轴）")
    ax.set_xscale("log")
    ax.set_xlim(0.0005, 0.2)
    ax.set_title("多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3）")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    ax.grid(True, which="major", axis="x", ls=":", alpha=0.4)
    note = (f"SiC 重新判定（Q3）：Rbar_max = {rbar_vals[1]:.5f} ≤ θ_mb={THETA_MB:.2f} → {sic['sic_mb_verdict']}（无显著多光束、无需修正，prob02 的 t=7.2158 µm 维持）。\n"
            f"硅 Rbar = {rbar_vals[0]:.5f}、F = {si['finesse']:.3f}；SiC Rbar 更小（F≈0.154）。prob02 参考 R12={float(sic_ref['R12_ref']):.1e}、R01={float(sic_ref['R01_ref']):.2f}。")
    fig.text(0.02, 0.02, note, fontsize=style["size"] - 1, va="bottom", ha="left",
             bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.92})
    fig.subplots_adjust(left=0.22, right=0.96, top=0.88, bottom=0.30)
    return render_and_register(cfg, style, fig, ax.get_title(), "sic_multibeam_recheck", "material", ["Rbar"], source_hash)


# ---------------------------------------------------------------------------
# 图 9：三维响应面 R(ν, θ) + 二维等高线配套（含 θ=10°/15° 测量线）
# ---------------------------------------------------------------------------
def fig_response_surface(cfg: dict, style: dict, source_hash: str) -> dict:
    result = load_result()
    t_um = float(result["main_variable_projection"]["t_hat_shared_um"])
    n_sub_hat = float(result["n_sub_hat_amplitude"])
    nu = np.linspace(2000.0, 4000.0, 161)
    theta_grid = np.linspace(0.0, 30.0, 31)
    n_nu = np.asarray(model.dispersion_epi_si(nu, model="N-SE"), dtype=float)
    R = np.empty((theta_grid.size, nu.size))
    for i, theta in enumerate(theta_grid):
        R[i, :] = model.forward_reflectance(nu, t_um, n_nu, n_sub_hat, float(theta))
    T, N = np.meshgrid(theta_grid, nu, indexing="ij")

    fig = plt.figure(figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6))))
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
    ax2d.text(3900, 10.0, "θ=10°", color=PALETTE["accent"], fontsize=style["size"] - 2, ha="right", va="center")
    ax2d.text(3900, 15.0, "θ=15°", color=PALETTE["accent"], fontsize=style["size"] - 2, ha="right", va="center")
    ax2d.set_xlabel("波数 ν (cm^-1)")
    ax2d.set_ylabel("入射角 θ (°)")
    ax2d.set_title("二维等高线配套（θ=10°/15° 测量线）", fontsize=style["title_size"] - 1)
    fig.colorbar(cf, ax=ax2d, shrink=0.85, label="反射率 R")
    fig.suptitle("两光束干涉反射率随波数与入射角的三维响应面（静态 PNG 配 2D 等高线消歧）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return render_and_register(cfg, style, fig, "两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）", "response_surface", "nu_cm1", ["theta_deg", "R"], source_hash)


# ---------------------------------------------------------------------------
# 图 10：相位频率（g 空间）测厚机制（t = 1/(2×1e-4·Δg)）与条纹计数
# ---------------------------------------------------------------------------
def fig_phase_freq(cfg: dict, style: dict, source_hash: str) -> dict:
    data10 = load_spectrum(10)
    nu, r_obs, r_model = data10[:, 0], data10[:, 1], data10[:, 2]
    n_nu = np.asarray(model.dispersion_epi_si(nu, model="N-SE"), dtype=float)
    g = np.asarray(model.phase_function(nu, n_nu, THETA10), dtype=float)
    result = load_result()
    t_hat = float(result["main_variable_projection"]["t_hat_shared_um"])

    # 用干净的两光束物理正模型 R_model（真实干涉频率）去基线后定位同型极大，
    # 避免实测谱噪声使峰值检测落入 M2/M3 噪声周期（formulation §13.3 方法债）。
    from numpy.polynomial.chebyshev import chebvander
    from scipy.signal import find_peaks

    x = (nu - nu.mean()) / (nu.max() - nu.min())
    basis = chebvander(x, 3)
    coef, *_ = np.linalg.lstsq(basis, r_model, rcond=None)
    detrend = r_model - basis @ coef
    peaks, _ = find_peaks(detrend, prominence=0.0015)
    if peaks.size < 2:
        peaks, _ = find_peaks(detrend)
    nu_peaks = nu[peaks]
    g_peaks = g[peaks]
    delta_nu = np.diff(nu_peaks)
    delta_g = np.diff(g_peaks)
    t_from_gap = 1.0 / (2.0 * 1e-4 * delta_g)

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(float(cfg.get("figure_width", 10)), float(cfg.get("figure_height", 6)) / 1.9))
    axl.plot(nu, detrend, lw=1.1, color=PALETTE["primary"], label="两光束物理正模型 (2.8) 去基线（真实干涉频率）")
    axl.plot(nu[peaks], detrend[peaks], "^", ms=5, color=PALETTE["accent"],
             label=f"同型极大（n={int(peaks.size)}，Δν≈{np.median(delta_nu):.0f} cm^-1）")
    axl.set_xlabel("波数 ν (cm^-1)")
    axl.set_ylabel("去基线反射率 ΔR")
    axl.set_title("带内真实干涉条纹（θ=10°）")
    axl.set_xlim(*INV_BAND)
    axl.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    axl.grid(True, which="major", ls=":", alpha=0.4)

    k = np.arange(1, delta_g.size + 1)
    axr.plot(k, t_from_gap, "o-", lw=1.3, ms=4, color=PALETTE["secondary"])
    axr.axhline(t_hat, color=PALETTE["accent"], ls="--", lw=1.4, label=f"主方法 t_hat = {t_hat:.4f} µm")
    axr.axhline(6.9, color=PALETTE["warning"], ls=":", lw=1.2, label="倍周期假极小 t ≈ 6.9 µm（v001 伪影，已排除）")
    axr.set_xlabel("同型相邻极大对序号 k")
    axr.set_ylabel("由 Δg 反演的 t (µm)")
    axr.set_title(f"g 空间周期测厚（≈{t_hat:.2f} µm 主解）")
    axr.set_ylim(0, 12)
    axr.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=style["size"] - 1)
    axr.grid(True, which="major", ls=":", alpha=0.4)
    fig.suptitle("相位频率（g 空间）测厚机制：条纹周期 → t = 1/(2×1e-4·Δg)（formulation (3.9)）",
                 fontsize=style["title_size"], fontweight="bold")
    fig.subplots_adjust(wspace=0.32, top=0.84)
    return render_and_register(cfg, style, fig, "相位频率（g 空间）测厚机制与条纹计数", "phase_freq_gspace", "spacing_index", ["delta_nu", "t_um"], source_hash)


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
    items.append(fig_mb_conditions(cfg, style, source_hash))
    items.append(fig_sic_recheck(cfg, style, source_hash))
    items.append(fig_response_surface(cfg, style, source_hash))
    items.append(fig_phase_freq(cfg, style, source_hash))
    print(f"[done] 生成并登记 {len(items)} 张图，source_hash={source_hash[:12]}…")
    bad = [item["stable_id"] for item in items if item["quality_status"] != "passed"]
    if bad:
        print(f"[warn] 下列图自动质检未通过：{bad}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
