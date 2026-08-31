"""prob03 ablation 消融图生成脚本（ablation 阶段）。

数据源（只读，不修改）：
- results/ablation/result.json（F0 + A1-A4 各实验实测值、判定、阈值）
- results/ablation/summary.json（汇总表：F0 + A1-A4 的 t_hat、delta_t%、weighted_rmse、R_in_unit_interval）

输出（figures/ 目录）：
- prob03_fig_ablation_summary_<hash>.png：判据汇总（A1-A4 实测 Δt% / ε12 vs 预注册阈值，全部通过）
- prob03_fig_ablation_t_consistency_<hash>.png：厚度对照（F0 + A1-A4 的 t_hat，含 A4 每角独立 t_hat）
- prob03_fig_ablation_rmse_<hash>.png：加权 RMSE 对照（基线 p=0 上升、Airy 高阶下降）
- 每张图 .quality.json（inspect_png 自动质检报告）
- figures.yaml 登记（register_figure；visual_review 由 Agent 命令补记）

运行：python code/make_ablation_figures.py（项目根为工作目录）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[6]  # E:\项目\AutoMM
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # 同目录 import model

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from automm.common import config_section, hash_path, relative, utc_now  # noqa: E402
from automm.visualization import inspect_png, register_figure, stable_figure_id  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib import pyplot as plt  # noqa: E402

PROBLEM_ID = "2025-cumcm-b"
QUESTION_ID = "prob03"
ASSUMPTION_VERSION = "assumption_v001"
FORMULATION_VERSION = "formulation_v002"

VERSION_DIR = ROOT / "problems" / PROBLEM_ID / QUESTION_ID / "versions" / ASSUMPTION_VERSION
RESULTS_DIR = VERSION_DIR / "results" / "ablation"
FIGURES_DIR = VERSION_DIR / "figures"
SCRIPT_PATH = Path(__file__).resolve()

PALETTE = {
    "primary": "#1F4E79",      # 完整模型 F0
    "secondary": "#70AD47",    # 消融项（通过/良性）
    "accent": "#ED7D31",       # 强调（A4 每角独立 t_hat / 实测值）
    "neutral": "#7F8C8D",      # 参考/阈值线
    "warning": "#C00000",      # 警告/超出阈值
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


def render_and_register(
    cfg: dict, style: dict, fig, title: str, kind: str, x_var: str | None, y_vars: list[str], source_hash: str
) -> dict:
    fig_width = float(cfg.get("figure_width", 10))
    fig_height = float(cfg.get("figure_height", 6))
    dpi = int(cfg.get("dpi", 180))
    fig.set_size_inches(fig_width, fig_height)
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


def load_summary() -> dict:
    path = RESULTS_DIR / "summary.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_result() -> dict:
    path = RESULTS_DIR / "result.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _row(summary: dict, name: str) -> dict:
    return next(row for row in summary["rows"] if row["experiment"] == name)


def fig_ablation_summary(cfg: dict, style: dict, source_hash: str) -> dict:
    """判据汇总：A1-A4 实测 Δt% / ε12 vs 预注册阈值（全部通过 -> components_confirmed）。"""
    summary = load_summary()
    f0 = _row(summary, "F0")
    a1 = _row(summary, "A1")
    a2 = _row(summary, "A2")
    a3 = _row(summary, "A3")
    a4 = _row(summary, "A4")

    labels = [
        "A1 色散项消融\n（N-SE → N-const）",
        "A2 多光束高阶项消融\n（加 cos2δ/sin2δ、cos3δ/sin3δ）",
        "A3 基线多项式项消融\n（p=3 → p=0）",
        "A4 两角共享 t 约束消融\n（最大每角偏差 vs 共享）",
    ]
    # A4 的 delta_t 在 summary.json 为 null，需从 result.json 取 delta_t_vs_shared_percent
    result = load_result()
    a4_delta = result["experiments"]["A4"]["delta_t_vs_shared_percent"]
    # 显示值（百分比）；A4 用每角 vs 共享最大偏差
    values = [
        a1["delta_t_percent"],
        a2["delta_t_percent"],
        a3["delta_t_percent"],
        a4_delta,
    ]
    thresholds = [2.0, 1.0, 2.0, 2.0]
    # A4 额外补充 ε12（每角独立结果的两角一致性）
    eps12 = a4["eps12_percent"]

    fig, ax = plt.subplots()
    positions = np.arange(len(labels))
    # 用 log 尺度更好地展示 0.1%-1% 量级（全部远小于阈值）
    ax.set_xscale("log")
    ax.set_xlim(0.05, 6.0)
    for pos, value, threshold in zip(positions, values, thresholds):
        bar_color = PALETTE["secondary"] if value <= threshold else PALETTE["warning"]
        ax.barh(pos, max(value, 0.06), color=bar_color, alpha=0.9, height=0.5, zorder=3, edgecolor="white")
        ax.plot([threshold], [pos], marker="|", ms=18, color=PALETTE["warning"], lw=2.6, zorder=6)
        ax.text(
            max(value, 0.06) * 1.06, pos, f"{value:.3f}%",
            va="center", fontsize=style["size"] - 1, color=PALETTE["primary"], fontweight="bold",
        )
        ax.text(
            threshold * 1.06, pos - 0.24, f"阈值 τ={threshold:g}%",
            fontsize=style["size"] - 3, color=PALETTE["warning"], va="center",
        )
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Δt% = |t_hat_消融 − t_hat_F0| / t_hat_F0 × 100%（对数轴）；黑标为预注册阈值")
    ax.set_title("prob03 ablation 判据汇总：components_confirmed（A1–A4 全部在阈值内）")
    ax.grid(True, which="major", axis="x", ls=":", alpha=0.4)
    note = (
        f"参考 F0（完整模型）：t_hat = {f0['t_hat_um']:.4f} µm，加权 RMSE = {f0['weighted_rmse']:.4g}，"
        f"R ∈ [0,1]（{f0['R_in_unit_interval']}）。"
        f"A4 每角独立 t_hat 的两角一致性 ε12 = {eps12:.3f}% ≤ τ = 2%（共享 t 为安全一致性约束）。"
        "所有消融 Δt% ≤ 1%（A2）或 ≤ 2%（A1/A3/A4），复杂度项不改变 t_hat；dispersive/基线/共享 t 为安全简化，"
        "多光束（Airy）高阶对 t_hat 无贡献（L17 极值不变性，Q1 定量证据）。"
    )
    ax.text(
        0.995, -0.34, note, transform=ax.transAxes,
        fontsize=style["size"] - 2, color=PALETTE["neutral"], ha="right", va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.9},
    )
    fig.tight_layout(rect=[0.02, 0, 1, 0.96])
    return render_and_register(
        cfg, style, fig, "prob03 ablation 判据汇总（F0 + A1–A4）",
        "ablation_summary", "experiment", ["metric_percent"], source_hash,
    )


def fig_ablation_t_consistency(cfg: dict, style: dict, source_hash: str) -> dict:
    """厚度对照：F0 + A1-A4 的 t_hat（含 A4 每角独立 t_hat），显示均落在 F0 邻域窄带内。"""
    summary = load_summary()
    result = load_result()
    f0 = _row(summary, "F0")
    a1 = _row(summary, "A1")
    a2 = _row(summary, "A2")
    a3 = _row(summary, "A3")
    a4 = _row(summary, "A4")

    labels = ["F0\n完整模型", "A1\n色散 N-const", "A2\nAiry 高阶", "A3\n基线 p=0", "A4 θ=10°\n独立", "A4 θ=15°\n独立"]
    t_vals = [f0["t_hat_um"], a1["t_hat_um"], a2["t_hat_um"], a3["t_hat_um"]]
    t_vals.extend(a4["t_hat_per_angle_um"])
    colors = [PALETTE["primary"], PALETTE["secondary"], PALETTE["secondary"], PALETTE["secondary"], PALETTE["accent"], PALETTE["accent"]]

    f0_t = f0["t_hat_um"]
    fig, ax = plt.subplots()
    positions = np.arange(len(labels))
    ax.axhspan(f0_t * 0.99, f0_t * 1.01, color=PALETTE["secondary"], alpha=0.08, label="F0 ±1% 参考带")
    bars = ax.bar(positions, t_vals, color=colors, alpha=0.9, edgecolor="white", width=0.62, zorder=3)
    ax.axhline(f0_t, color=PALETTE["primary"], ls="--", lw=1.4, zorder=4, label=f"F0 完整模型 t_hat = {f0_t:.4f} µm")
    for bar, value in zip(bars, t_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2, value, f"{value:.4f} µm",
            ha="center", va="bottom", fontsize=style["size"] - 2, color=PALETTE["primary"],
        )
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel("反演厚度 t_hat (µm)")
    ax.set_ylim(f0_t - 0.06, f0_t + 0.06)
    ax.set_title("prob03 ablation 厚度对照：各消融项 t_hat 均落在 F0 完整模型邻域（|Δt| ≤ 0.574%）")
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    note = (
        "A4 独立反演：θ=10° → 3.4507 µm，θ=15° → 3.4463 µm；两角一致性 ε12=0.130% ≤ τ=2%。"
        "色散/基线/多光束高阶/共享 t 均不改变 t_hat（相位频率机制主导）；"
        "多光束判定（硅 Rbar≈0.0101、η_mb≈0.111%）由 robustness R5 与 computation 确认两光束适用。"
    )
    ax.text(
        0.995, -0.16, note, transform=ax.transAxes,
        fontsize=style["size"] - 2, color=PALETTE["neutral"], ha="right", va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.9},
    )
    fig.tight_layout(rect=[0.02, 0, 1, 0.94])
    return render_and_register(
        cfg, style, fig, "prob03 ablation 厚度对照（F0 + A1–A4）",
        "ablation_t_consistency", "experiment", ["t_um"], source_hash,
    )


def fig_ablation_rmse(cfg: dict, style: dict, source_hash: str) -> dict:
    """加权 RMSE 对照：基线 p=0 上升（基线项必要吸收慢变背景）、Airy 高阶下降（多光束复杂度微小增益）。"""
    summary = load_summary()
    f0 = _row(summary, "F0")
    a1 = _row(summary, "A1")
    a2 = _row(summary, "A2")
    a3 = _row(summary, "A3")

    labels = ["F0 完整模型", "A1 色散 N-const", "A2 Airy 高阶", "A3 基线 p=0"]
    rmse = [f0["weighted_rmse"], a1["weighted_rmse"], a2["weighted_rmse"], a3["weighted_rmse"]]
    colors = [PALETTE["primary"], PALETTE["secondary"], PALETTE["secondary"], PALETTE["warning"]]

    fig, ax = plt.subplots()
    positions = np.arange(len(labels))
    bars = ax.bar(positions, rmse, color=colors, alpha=0.9, edgecolor="white", width=0.6, zorder=3)
    f0_rmse = f0["weighted_rmse"]
    ax.axhline(f0_rmse, color=PALETTE["primary"], ls="--", lw=1.4, zorder=4, label=f"F0 加权 RMSE = {f0_rmse:.4g}")
    for bar, value in zip(bars, rmse):
        ax.text(
            bar.get_x() + bar.get_width() / 2, value, f"{value:.4g}",
            ha="center", va="bottom", fontsize=style["size"] - 2, color=PALETTE["primary"],
        )
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel("最优拟合加权 RMSE（无量纲）")
    ax.set_title("prob03 ablation 拟合优度对照：基线 p=0 使 RMSE 上升；Airy 高阶仅微小下降")
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    note = (
        f"A3（基线 p=3→p=0）RMSE 由 {f0_rmse:.4g} 升至 {a3['weighted_rmse']:.4g}（+{100*(a3['weighted_rmse']-f0_rmse)/f0_rmse:.1f}%）——"
        "基线多项式项吸收 DC/慢变基线，是拟合优度的必要组件；"
        f"A2（加 Airy 高阶）RMSE 降至 {a2['weighted_rmse']:.4g}（−{100*(f0_rmse-a2['weighted_rmse'])/f0_rmse:.1f}%）——"
        "多光束高阶仅带来微小且不改变 t_hat 的复杂度增益。"
    )
    ax.text(
        0.995, -0.16, note, transform=ax.transAxes,
        fontsize=style["size"] - 2, color=PALETTE["neutral"], ha="right", va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": PALETTE["neutral"], "alpha": 0.9},
    )
    fig.tight_layout(rect=[0.02, 0, 1, 0.94])
    return render_and_register(
        cfg, style, fig, "prob03 ablation 拟合优度对照（加权 RMSE）",
        "ablation_rmse", "experiment", ["weighted_rmse"], source_hash,
    )


def main() -> None:
    cfg = config_section("visualization", PROBLEM_ID, QUESTION_ID)
    style, font_name = setup_style(cfg)
    print(f"[font] 使用中文字体：{font_name}")
    if not (RESULTS_DIR / "summary.json").is_file():
        raise RuntimeError(f"缺少 ablation 汇总结果：{RESULTS_DIR / 'summary.json'}")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    source_hash = hash_path(RESULTS_DIR)
    items = []
    items.append(fig_ablation_summary(cfg, style, source_hash))
    items.append(fig_ablation_t_consistency(cfg, style, source_hash))
    items.append(fig_ablation_rmse(cfg, style, source_hash))
    bad = [item["stable_id"] for item in items if item["quality_status"] != "passed"]
    print(f"[done] 生成并登记 {len(items)} 张消融图，source_hash={source_hash[:12]}…")
    if bad:
        print(f"[warn] 下列消融图自动质检未通过：{bad}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
