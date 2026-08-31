"""prob01 ablation 消融图生成脚本（ablation 阶段）。

数据源（只读，不修改）：
- results/ablation/summary.json（F0 + A1-A4 各实验实测值、判定、阈值）

输出（figures/ 目录）：
- prob01_fig_ablation_summary_<hash>.png：F0 + A1-A4 判据判定汇总
  （实测指标 vs 预注册阈值，全部通过 -> components_confirmed）
- prob01_fig_ablation_polarization_<hash>.png：A3 偏振一致性
  （avg / s / p 三种偏振反演厚度 vs t_true=10 µm）
- prob01_fig_ablation_init_strategy_<hash>.png：A4 初值策略对比
  （单初值落入周期歧义局部极小 vs 多初值全局解）
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
QUESTION_ID = "prob01"
ASSUMPTION_VERSION = "assumption_v001"

VERSION_DIR = ROOT / "problems" / PROBLEM_ID / QUESTION_ID / "versions" / ASSUMPTION_VERSION
RESULTS_DIR = VERSION_DIR / "results" / "ablation"
FIGURES_DIR = VERSION_DIR / "figures"
SCRIPT_PATH = Path(__file__).resolve()

PALETTE = {
    "primary": "#1F4E79",      # 主方案（完整模型/多初值）
    "secondary": "#70AD47",    # 对照（消融/s/p 偏振）
    "accent": "#ED7D31",       # 强调（单初值退化/实测值）
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


def fig_ablation_summary(cfg: dict, style: dict, source_hash: str) -> dict:
    """F0 + A1-A4 判据判定汇总：实测指标 vs 预注册阈值（全部通过 -> components_confirmed）。"""
    summary = load_summary()
    exp = summary["experiments"]

    f0 = exp["f0"]
    a1 = exp["a1"]
    a2 = exp["a2"]
    a3 = exp["a3"]
    a4 = exp["a4"]

    labels = [
        "F0 完整模型\n（NLS 相对真值误差）",
        "A1 干涉项消融\n（rmse 平坦度）",
        "A2 衬底反射消融\n（rmse 平坦度）",
        "A3 偏振平均消融\n（s/p/avg 最大相对差）",
        "A4 单初值 NLS\n（相对真值误差）",
    ]
    # 显示值（百分比）；A4 另附多初值对照 ~0%
    values = [
        f0["max_rel_err"] * 100.0,
        a1["max_flatness"] * 100.0,
        a2["max_flatness"] * 100.0,
        a3["max_pairwise_rel_diff"] * 100.0,
        a4["max_single_init_rel_err"] * 100.0,
    ]
    thresholds = [
        f0["thresholds"]["rel_err"] * 100.0,
        a1["flatness_threshold"] * 100.0,
        a2["flatness_threshold"] * 100.0,
        a3["pol_pairwise_tol"] * 100.0,
        a4["thresholds"]["single_init_err"] * 100.0,
    ]
    # 方向：前 4 组实测<=阈值通过（保守）；A4 单初值 实测>阈值 才是「多初值必要」的预期证据
    direction = ["below", "below", "below", "below", "above"]

    fig, ax = plt.subplots()
    positions = np.arange(len(labels))
    x_max = max(thresholds) * 1.8
    # 前 4 组：实测条 + 阈值标记（below 通过）
    for pos, value, threshold, direct in zip(positions[:4], values[:4], thresholds[:4], direction[:4]):
        bar_color = PALETTE["primary"] if value <= threshold else PALETTE["warning"]
        ax.barh(pos, min(value, x_max), color=bar_color, alpha=0.85, height=0.55)
        ax.plot([threshold], [pos], marker="|", ms=16, color=PALETTE["warning"], lw=2.5)
        ax.text(
            min(value, x_max) + 0.2, pos, f"{value:.4g}%" if value > 0 else "≈0",
            va="center", fontsize=style["size"] - 1, color=PALETTE["primary"],
        )
        ax.text(
            threshold + 0.2, pos - 0.22, f"阈值 {threshold:g}%",
            fontsize=style["size"] - 3, color=PALETTE["warning"], va="center",
        )
    # A4：单初值（应显著>阈值，accent）+ 多初值对照（~0，secondary）
    pos4 = positions[4]
    value4, th4 = values[4], thresholds[4]
    ax.barh(pos4, min(value4, x_max), color=PALETTE["accent"], alpha=0.85, height=0.55)
    ax.plot([th4], [pos4], marker="|", ms=16, color=PALETTE["warning"], lw=2.5)
    ax.text(
        min(value4, x_max) + 0.2, pos4, f"{value4:.3g}%",
        va="center", fontsize=style["size"] - 1, color=PALETTE["accent"],
    )
    ax.text(
        th4 + 0.2, pos4 - 0.22, f"阈值 {th4:g}%（应超出=多初值必要）",
        fontsize=style["size"] - 3, color=PALETTE["warning"], va="center",
    )
    ax.text(
        min(value4, x_max) + 0.2, pos4 + 0.22, "多初值 ≈0%（≤1% 通过）",
        fontsize=style["size"] - 3, color=PALETTE["secondary"], va="center",
    )

    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("实测指标（%，t_true=10.0 µm 合成谱；A4 单初值为退化对照）")
    ax.set_title("prob01 ablation 判据汇总（components_confirmed：5/5 预注册判据通过）")
    ax.set_xlim(0, max(x_max, 8.0))
    ax.grid(True, which="major", axis="x", ls=":", alpha=0.4)
    ax.axvline(0.0, color="black", lw=0.8)
    note = (
        "F0 精确恢复（误差≈0）；A1/A2 平坦度=0 → 厚度不可辨识（干涉项/衬底反射项必要）；"
        "A3 s/p/avg 最大差 0.012%（偏振平均安全）；A4 单初值 6.03% 落入周期歧义局部极小 → 多初值模块必要"
    )
    ax.text(
        0.995, -0.46, note, transform=ax.transAxes,
        fontsize=style["size"] - 2, color=PALETTE["neutral"], ha="right", va="top",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return render_and_register(
        cfg, style, fig, "prob01 ablation 判据汇总（F0 + A1–A4）",
        "ablation_summary", "experiment", ["metric_percent"], source_hash,
    )


def fig_ablation_polarization(cfg: dict, style: dict, source_hash: str) -> dict:
    """A3 偏振一致性：avg / s / p 三种偏振反演厚度 vs t_true=10 µm（两入射角）。"""
    summary = load_summary()
    rows = summary["experiments"]["a3"]["rows"]
    thetas = sorted({row["theta_deg"] for row in rows if row.get("pol") != "pairwise_max_rel_diff"})
    pols = ["avg", "s", "p"]
    colors = {"avg": PALETTE["primary"], "s": PALETTE["secondary"], "p": PALETTE["accent"]}
    width = 0.24

    fig, ax = plt.subplots()
    for index, pol in enumerate(pols):
        t_vals = [
            next(row["t_nls_um"] for row in rows if row["theta_deg"] == theta and row["pol"] == pol)
            for theta in thetas
        ]
        x_positions = np.arange(len(thetas)) + (index - 1) * width
        bars = ax.bar(x_positions, t_vals, width, color=colors[pol], alpha=0.9, label=f"{pol} 偏振")
        for bar, value in zip(bars, t_vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2, value + 0.0002,
                f"{value:.4f}", ha="center", fontsize=style["size"] - 3,
                color=PALETTE["neutral"],
            )
    ax.axhline(10.0, color=PALETTE["neutral"], ls="--", lw=1.2, label="t_true = 10.0 µm")
    ax.axhspan(9.9, 10.1, color=PALETTE["secondary"], alpha=0.08, label="±1% 容差带")
    ax.set_xticks(np.arange(len(thetas)))
    ax.set_xticklabels([f"θ = {theta:g}°" for theta in thetas])
    ax.set_ylabel("NLS 反演厚度 t（µm）")
    ax.set_title("A3 偏振平均消融：avg / s / p 反演厚度一致（最大相对差 0.012%，远低于 1% 阈值）")
    ax.set_ylim(9.95, 10.05)
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    ax.legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=style["size"] - 2)
    note = "相位 δ 与偏振无关（A4 跃变不改变同型极值间隔）：偏振平均是安全简化，prob02 无需逐偏振反演"
    ax.text(
        0.995, -0.10, note, transform=ax.transAxes,
        fontsize=style["size"] - 2, color=PALETTE["neutral"], ha="right", va="top",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return render_and_register(
        cfg, style, fig, "A3 偏振一致性：avg/s/p 反演厚度 vs t_true",
        "ablation_polarization", "theta_deg", ["t_um"], source_hash,
    )


def fig_ablation_init_strategy(cfg: dict, style: dict, source_hash: str) -> dict:
    """A4 初值策略对比：单初值（周期歧义局部极小）vs 多初值（全局解）反演厚度。"""
    summary = load_summary()
    rows = summary["experiments"]["a4"]["rows"]
    thetas = sorted({row["theta_deg"] for row in rows})
    width = 0.3

    single_t = [next(row["single_t_nls_um"] for row in rows if row["theta_deg"] == theta) for theta in thetas]
    single_t0 = [next(row["single_t0_um"] for row in rows if row["theta_deg"] == theta) for theta in thetas]
    multi_t = [next(row["multi_t_nls_um"] for row in rows if row["theta_deg"] == theta) for theta in thetas]
    single_err = [next(row["single_rel_err_vs_true"] * 100.0 for row in rows if row["theta_deg"] == theta) for theta in thetas]
    multi_err = [next(row["multi_rel_err_vs_true"] * 100.0 for row in rows if row["theta_deg"] == theta) for theta in thetas]

    fig, ax = plt.subplots()
    x_positions = np.arange(len(thetas))
    bars_single = ax.bar(
        x_positions - width / 2, single_t, width,
        color=PALETTE["accent"], alpha=0.9, label="单初值（方法 A 解析初值）",
    )
    bars_multi = ax.bar(
        x_positions + width / 2, multi_t, width,
        color=PALETTE["primary"], alpha=0.9, label="多初值（网格扫描 + ±period）",
    )
    for pos, t0, t, err in zip(x_positions, single_t0, single_t, single_err):
        ax.annotate(
            f"t0={t0:.2f}\n→ t={t:.3f}（偏差 {err:.1f}%）",
            xy=(pos - width / 2, t + 0.03), ha="center",
            fontsize=style["size"] - 3, color=PALETTE["accent"],
        )
    for pos, t, err in zip(x_positions, multi_t, multi_err):
        ax.annotate(
            f"t={t:.3f}（偏差 {err:.1e}%）",
            xy=(pos + width / 2, t + 0.03), ha="center",
            fontsize=style["size"] - 3, color=PALETTE["primary"],
        )
    ax.axhline(10.0, color=PALETTE["neutral"], ls="--", lw=1.2, label="t_true = 10.0 µm")
    ax.set_xticks(x_positions)
    ax.set_xticklabels([f"θ = {theta:g}°" for theta in thetas])
    ax.set_ylabel("NLS 反演厚度 t（µm）")
    ax.set_title("A4 多初值模块消融：单初值落入周期歧义局部极小（偏差 ~6%），多初值精确恢复")
    ax.set_ylim(9.7, 10.75)
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    ax.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=style["size"] - 2)
    note = (
        "cosδ 对 t 周期歧义（formula_validation §6，周期约 0.9 µm）：仅方法 A 解析初值单次 NLS "
        "收敛到相邻周期局部极小；多初值布点规避歧义 → prob02 实测反演必须沿用多初值策略"
    )
    ax.text(
        0.995, -0.15, note, transform=ax.transAxes,
        fontsize=style["size"] - 2, color=PALETTE["neutral"], ha="right", va="top",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return render_and_register(
        cfg, style, fig, "A4 初值策略对比：单初值局部极小 vs 多初值全局解",
        "ablation_init_strategy", "theta_deg", ["t_um"], source_hash,
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
    items.append(fig_ablation_polarization(cfg, style, source_hash))
    items.append(fig_ablation_init_strategy(cfg, style, source_hash))
    print(f"[done] 生成并登记 {len(items)} 张消融图，source_hash={source_hash[:12]}…")


if __name__ == "__main__":
    main()
