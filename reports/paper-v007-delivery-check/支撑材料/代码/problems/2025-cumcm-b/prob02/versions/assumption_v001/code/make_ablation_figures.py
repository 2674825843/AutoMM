"""prob02 ablation 消融图生成脚本（ablation 阶段）。

数据源（只读，不修改）：
- results/ablation/summary.json（F0 + A1-A4 各实验实测值、判定、阈值）
- results/ablation/result.json（详细判定，含 A4 每角 t̂）

输出（figures/ 目录）：
- prob02_fig_ablation_summary_<hash>.png：F0 + A1-A4 判据判定汇总
  （实测 Δt/ε₁₂ vs 预注册阈值，全部达标 -> components_confirmed）
- prob02_fig_ablation_thickness_<hash>.png：F0/A1-A4 厚度估计对照
  （完整模型 vs 各消融项的 t̂，标注 Δt%）
- prob02_fig_ablation_shared_t_<hash>.png：A4 两角共享-t vs 每角独立 t 对照
  （每角 t̂ ≈ 共享 t̂、ε₁₂ 小 -> 良性一致约束）
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
QUESTION_ID = "prob02"
ASSUMPTION_VERSION = "assumption_v001"

VERSION_DIR = ROOT / "problems" / PROBLEM_ID / QUESTION_ID / "versions" / ASSUMPTION_VERSION
RESULTS_DIR = VERSION_DIR / "results" / "ablation"
FIGURES_DIR = VERSION_DIR / "figures"
SCRIPT_PATH = Path(__file__).resolve()

PALETTE = {
    "primary": "#1F4E79",      # 主方案（完整模型 F0）
    "secondary": "#70AD47",    # 对照（A4 每角独立 t / 通过项）
    "accent": "#ED7D31",       # 强调（消融项 / 实测值）
    "neutral": "#7F8C8D",      # 参考/阈值线
    "warning": "#C00000",      # 警告/超出阈值
}


def probe_font(cfg: dict) -> str:
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


def load_result() -> dict:
    path = RESULTS_DIR / "result.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _row(summary: dict, exp_id: str) -> dict:
    return next(row for row in summary["rows"] if row["id"] == exp_id)


def fig_ablation_summary(cfg: dict, style: dict, source_hash: str) -> dict:
    """F0 + A1-A4 判据判定汇总：实测 Δt / ε₁₂ vs 预注册阈值（全部达标 -> components_confirmed）。"""
    summary = load_summary()
    f0 = _row(summary, "F0")
    a1 = _row(summary, "A1")
    a2 = _row(summary, "A2")
    a3 = _row(summary, "A3")
    a4 = _row(summary, "A4")

    labels = [
        "F0 完整模型\n（t_hat 落在物理带区间）",
        "A1 色散消融\n（Δt_disp）",
        "A2 基线多项式消融\n（Δt_base）",
        "A3 相位-频率消融\n（Δt_vp）",
        "A4 两角共享-t 消融\n（eps12）",
    ]
    values = [
        f0["t_hat_um"],
        a1["metric"],
        a2["metric"],
        a3["metric"],
        a4["metric"],
    ]
    thresholds = [
        None,                       # F0 无百分比阈值（t̂ 区间 [7.2, 8.0] µm）
        1.0,                        # A1 Δt_disp > 1%
        1.0,                        # A2 Δt_base > 1%
        1.0,                        # A3 Δt_vp > 1%
        2.0,                        # A4 ε₁₂ <= 2%
    ]
    # 前 4 组为"贡献确认"（实测>阈值），A4 为"良性一致"（实测<=阈值）
    direction = ["ref", "above", "above", "above", "below"]

    fig, ax = plt.subplots()
    positions = np.arange(len(labels))
    x_max = max(v for v in values if v is not None) * 1.35

    for pos, value, threshold, direct in zip(positions, values, thresholds, direction):
        if direct == "ref":
            # F0：用参考色展示 t̂ 位置（无阈值）
            ax.barh(pos, min(value, x_max), color=PALETTE["primary"], alpha=0.85, height=0.55)
            ax.text(min(value, x_max) + 0.2, pos, f"t_hat={value:.4f} µm", va="center",
                    fontsize=style["size"] - 1, color=PALETTE["primary"])
            continue
        if direct == "above":
            bar_color = PALETTE["secondary"] if value > threshold else PALETTE["warning"]
            ax.barh(pos, min(value, x_max), color=bar_color, alpha=0.85, height=0.55)
            ax.plot([threshold], [pos], marker="|", ms=16, color=PALETTE["warning"], lw=2.5)
            ax.text(min(value, x_max) + 0.2, pos, f"{value:.2f}% (>τ={threshold:g}%)", va="center",
                    fontsize=style["size"] - 1, color=PALETTE["primary"])
            ax.text(threshold + 0.2, pos - 0.22, f"阈值 {threshold:g}%", fontsize=style["size"] - 3,
                    color=PALETTE["warning"], va="center")
        else:  # below
            bar_color = PALETTE["secondary"] if value <= threshold else PALETTE["warning"]
            ax.barh(pos, min(value, x_max), color=bar_color, alpha=0.85, height=0.55)
            ax.plot([threshold], [pos], marker="|", ms=16, color=PALETTE["warning"], lw=2.5)
            ax.text(min(value, x_max) + 0.2, pos, f"{value:.3f}% (≤τ={threshold:g}%)", va="center",
                    fontsize=style["size"] - 1, color=PALETTE["secondary"])
            ax.text(threshold + 0.2, pos - 0.22, f"阈值 {threshold:g}%", fontsize=style["size"] - 3,
                    color=PALETTE["warning"], va="center")

    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("实测指标（%，无真值 t_true：以完整模型 F0 为内部对照的相对差值）")
    ax.set_title("prob02 ablation 判据汇总（components_confirmed：4/4 组件贡献确认 + A4 良性一致约束）")
    ax.set_xlim(0, max(x_max, 3.0))
    ax.grid(True, which="major", axis="x", ls=":", alpha=0.4)
    ax.axvline(0.0, color="black", lw=0.8)
    note = (
        "A1 色散 Δt=8.44%>1%（Sellmeier 必要）；A2 基线多项式 Δt=5.55%>1% 且 RMSE 升 7.03x（基线-稳健分解必要）；"
        "A3 相位-频率方法 Δt=5.44%>1%（相对全谱幅值 NLS 必要）；"
        "A4 两角共享-t Δt=0.087% 且 eps12=0.165% (<=2%)（良性一致约束，不扭曲 t_hat）"
    )
    ax.text(0.995, -0.46, note, transform=ax.transAxes, fontsize=style["size"] - 2,
            color=PALETTE["neutral"], ha="right", va="top")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return render_and_register(
        cfg, style, fig, "prob02 ablation 判据汇总（F0 + A1–A4）",
        "ablation_summary", "experiment", ["metric_percent"], source_hash,
    )


def fig_ablation_thickness(cfg: dict, style: dict, source_hash: str) -> dict:
    """F0/A1-A4 厚度估计对照：完整模型 vs 各消融项的 t̂（标注 Δt%）。"""
    summary = load_summary()
    f0 = _row(summary, "F0")
    a1 = _row(summary, "A1")
    a2 = _row(summary, "A2")
    a3 = _row(summary, "A3")
    a4 = _row(summary, "A4")

    labels = [
        "F0 完整模型\n(对照)", "A1 色散模型消融",
        "A2 基线多项式消融", "A3 相位-频率方法消融", "A4 两角共享-t消融",
    ]
    t_vals = [f0["t_hat_um"], a1["t_hat_um"], a2["t_hat_um"], a3["t_hat_um"], a4["t_hat_um"]]
    tick_labels = [
        "7.2158",
        f"{a1['t_hat_um']:.4f}\n(Δ{a1['metric']:.2f}%)",
        f"{a2['t_hat_um']:.4f}\n(Δ{a2['metric']:.2f}%)",
        f"{a3['t_hat_um']:.4f}\n(Δ{a3['metric']:.2f}%)",
        f"{a4['t_hat_um']:.4f}\n(eps12={a4['metric']:.3f}%)",
    ]
    colors = [PALETTE["primary"], PALETTE["accent"], PALETTE["accent"], PALETTE["accent"], PALETTE["secondary"]]

    fig, ax = plt.subplots()
    xpos = np.arange(len(labels))
    bars = ax.bar(xpos, t_vals, color=colors, alpha=0.88, edgecolor="white", width=0.62)
    ax.axhline(f0["t_hat_um"], color=PALETTE["neutral"], ls="--", lw=1.2,
               label=f"F0 完整模型 t_hat = {f0['t_hat_um']:.4f} µm")
    # ±1% 参考带
    ax.axhspan(f0["t_hat_um"] * 0.99, f0["t_hat_um"] * 1.01, color=PALETTE["secondary"], alpha=0.08,
               label="±1% 参考带")
    for bar, val, tlab in zip(bars, t_vals, tick_labels):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, tlab, ha="center",
                va="bottom", fontsize=style["size"] - 3, color="black")
    ax.set_xticks(xpos)
    ax.set_xticklabels(labels, fontsize=style["size"] - 2)
    ax.set_ylabel("反演厚度 t_hat (µm)")
    ax.set_ylim(min(t_vals) * 0.96, max(t_vals) * 1.04)
    ax.set_title("prob02 ablation：完整模型 vs 各消融项厚度对照（每次只改变一个目标项）")
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    ax.legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=style["size"] - 2)
    note = (
        "A1（去色散）-> t 偏大 8.44%；A2（去基线多项式）-> t 偏大 5.55% 且 RMSE 上升 7.03x；"
        "A3（改幅值 NLS）-> t 偏大 5.44%；均远超 tau=1%。"
        "A4（每角独立 t）-> t_hat 与共享 t_hat 最大差 0.087%（良性约束）。"
    )
    ax.text(0.995, -0.12, note, transform=ax.transAxes, fontsize=style["size"] - 2,
            color=PALETTE["neutral"], ha="right", va="top")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return render_and_register(
        cfg, style, fig, "prob02 ablation 厚度对照（F0 + A1–A4）",
        "ablation_thickness", "experiment", ["t_um"], source_hash,
    )


def fig_ablation_shared_t(cfg: dict, style: dict, source_hash: str) -> dict:
    """A4 两角共享-t vs 每角独立-t 对照：每角 t̂ ≈ 共享 t̂、ε₁₂ 小 -> 良性一致约束。"""
    result = load_result()
    f0 = result["full_model"]["t_hat_shared_um"]
    a4 = result["ablations"]["A4_no_shared_t"]
    per_angle = a4["t_hat_per_angle_um"]
    eps12 = a4["eps12_percent"]  # 用于标题标注两角一致性

    labels = ["共享 t_hat", "θ=10° 独立 t_hat", "θ=15° 独立 t_hat"]
    vals = [f0, per_angle[0], per_angle[1]]
    colors = [PALETTE["accent"], PALETTE["secondary"], PALETTE["secondary"]]

    fig, ax = plt.subplots()
    xpos = np.arange(len(labels))
    bars = ax.bar(xpos, vals, color=colors, alpha=0.88, edgecolor="white", width=0.5)
    for bar, val, lab in zip(bars, vals, ["7.2158", "7.2214", "7.2095"]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.001, f"{val:.4f} µm", ha="center",
                va="bottom", fontsize=style["size"] - 2, color="black")
    ax.axhline(f0, color=PALETTE["neutral"], ls="--", lw=1.2, label=f"共享 t_hat = {f0:.4f} µm")
    ax.set_xticks(xpos)
    ax.set_xticklabels(labels, fontsize=style["size"] - 1)
    ax.set_ylabel("反演厚度 t_hat (µm)")
    ax.set_ylim(f0 * 0.998, f0 * 1.002)
    ax.set_title(f"A4 两角共享-t 消融：每角独立 t_hat ≈ 共享 t_hat（eps12 = {eps12:.3f}% <= 2%）")
    ax.grid(True, which="major", axis="y", ls=":", alpha=0.4)
    ax.legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=style["size"] - 2)
    note = (
        "共享-t（M_shared）与每角独立-t（M_indep，B11）在 eps12=0.165% 下几乎一致："
        "两角共享同一晶圆片同一厚度 t 的约束为良性一致约束，不扭曲 t_hat；"
        "两角一致性以对相位-频率拟合的嵌套 F 检验为主判据（大样本显著但实际意义很小，路由为 B11）。"
    )
    ax.text(0.995, -0.16, note, transform=ax.transAxes, fontsize=style["size"] - 2,
            color=PALETTE["neutral"], ha="right", va="top")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return render_and_register(
        cfg, style, fig, "A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致",
        "ablation_shared_t", "config", ["t_um"], source_hash,
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
    items.append(fig_ablation_thickness(cfg, style, source_hash))
    items.append(fig_ablation_shared_t(cfg, style, source_hash))
    print(f"[done] 生成并登记 {len(items)} 张消融图，source_hash={source_hash[:12]}…")
    bad = [item["stable_id"] for item in items if item["quality_status"] != "passed"]
    if bad:
        print(f"[warn] 下列图自动质检未通过：{bad}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
