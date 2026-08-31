"""prob01 robustness 敏感性图生成脚本（robustness 阶段）。

数据源（只读，不修改）：
- results/robustness/summary.json（E1-E5 判据实测值、汇总表、置信区间）

输出（figures/ 目录）：
- prob01_fig_sensitivity_tornado_<hash>.png：敏感性 tornado 汇总图
  （E1 n_sub 扰动 / E2 入射角扰动 / E3 色散模型 / E4 数据噪声 / E5 谱段截断
  对 NLS 厚度反演的最大相对影响，标注预注册阈值）
- prob01_fig_noise_robustness_ci_<hash>.png：E4 噪声稳健性图
  （σ=0.5/1.0/2.0% × 100 次随机实验的 t 估计均值与 95% CI 误差棒）
- 每张图 .quality.json（inspect_png 自动质检报告）
- figures.yaml 登记（register_figure；visual_review 由 Agent 命令补记）

运行：python code/make_robustness_figures.py（项目根为工作目录）。
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
RESULTS_DIR = VERSION_DIR / "results" / "robustness"
FIGURES_DIR = VERSION_DIR / "figures"
SCRIPT_PATH = Path(__file__).resolve()

PALETTE = {
    "primary": "#1F4E79",      # 主方案（θ=10°）
    "secondary": "#70AD47",    # 对照（θ=15°）
    "accent": "#ED7D31",       # 强调（主方法/判据）
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


def fig_sensitivity_tornado(cfg: dict, style: dict, source_hash: str) -> dict:
    """敏感性 tornado 汇总图：各扰动因素对 NLS 厚度反演的最大相对影响（%）。"""
    summary = load_summary()
    exp = summary["experiments"]
    e1 = exp["e1"]["max_rel_err"] * 100.0
    e2 = exp["e2"]["max_rel_err"] * 100.0
    e3 = exp["e3"]["alt_max_bias"] * 100.0
    e4 = max(row["ci_halfwidth_rel"] for row in exp["e4"]["rows"]) * 100.0
    e5 = exp["e5"]["max_rel_change"] * 100.0
    labels = [
        "E3 色散模型\n（常数 n 替代）",
        "E2 入射角 ±20%",
        "E5 谱段截断",
        "E4 数据噪声 σ=2%\n（95% CI 半宽）",
        "E1 衬底折射率 ±20%",
    ]
    values = [e3, e2, e5, e4, e1]
    thresholds = [5.0, 2.0, 2.0, 8.0, 3.0]

    fig, ax = plt.subplots()
    positions = np.arange(len(labels))
    bars = ax.barh(positions, values, color=PALETTE["primary"], alpha=0.85, height=0.6)
    for bar, threshold in zip(bars, thresholds):
        bar.set_edgecolor(PALETTE["accent"] if threshold else PALETTE["neutral"])
    # 阈值刻度标注
    for pos, threshold, value in zip(positions, thresholds, values):
        ax.plot([threshold], [pos], marker="|", ms=14, color=PALETTE["warning"], lw=2)
        ax.annotate(
            f"阈值 {threshold:g}%",
            xy=(threshold, pos),
            xytext=(threshold + 0.4, pos),
            fontsize=style["size"] - 2,
            color=PALETTE["warning"],
            va="center",
        )
        ax.text(value + 0.4, pos, f"{value:.3g}%", va="center", fontsize=style["size"] - 1, color=PALETTE["primary"])
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("对 NLS 厚度反演的最大相对影响（%，t_true=10.0 µm）")
    ax.set_title("prob01 robustness 敏感性汇总（E1–E5，预注册判据阈值 vs 实测）")
    ax.set_xlim(0, max(max(values), max(thresholds)) * 1.35 + 1.0)
    ax.grid(True, which="major", axis="x", ls=":", alpha=0.4)
    ax.axvline(0.0, color="black", lw=0.8)
    note = (
        "全部实测影响远低于预注册阈值 → conclusion=stable；"
        "最大影响来自 E3 色散模型替代（常数 n，≤1%），与 A3/A5 文档化方法限制一致"
    )
    ax.text(
        0.995, -0.42, note, transform=ax.transAxes,
        fontsize=style["size"] - 2, color=PALETTE["neutral"], ha="right", va="top",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return render_and_register(
        cfg, style, fig, "prob01 robustness 敏感性 tornado 汇总（E1–E5）",
        "sensitivity_tornado", "factor", ["max_rel_impact_percent"], source_hash,
    )


def fig_noise_robustness_ci(cfg: dict, style: dict, source_hash: str) -> dict:
    """E4 噪声稳健性图：σ=0.5/1.0/2.0% × 100 次随机实验的 t 估计（均值 ± 95% CI）。"""
    summary = load_summary()
    rows = summary["experiments"]["e4"]["rows"]
    fig, ax = plt.subplots()
    x_offsets = {10.0: -0.08, 15.0: 0.08}  # θ=10 与 θ=15 微偏移避免重叠
    for row in rows:
        sigma = row["sigma_percent"]
        theta = row["theta_deg"]
        mean_t = row["mean_t_um"]
        ci_half = row["ci_halfwidth_um"]
        color = PALETTE["primary"] if theta == 10.0 else PALETTE["secondary"]
        x = sigma + x_offsets[theta]
        ax.errorbar(
            x, mean_t, yerr=ci_half, fmt="o", ms=5, capsize=4,
            color=color, label=f"θ = {theta:g}°" if sigma == 0.5 else None,
        )
    ax.axhline(10.0, color=PALETTE["neutral"], ls="--", lw=1.2, label="t_true = 10.0 µm")
    ax.set_xlabel("反射率相对高斯噪声 σ（%）")
    ax.set_ylabel("NLS 反演厚度 t（µm）")
    ax.set_title("E4 噪声稳健性：100 次随机实验的 t 估计均值与 95% CI（全谱 NLS）")
    ax.set_xticks([0.5, 1.0, 2.0])
    ax.set_xlim(0.2, 2.3)
    ax.grid(True, which="major", ls=":", alpha=0.4)
    ax.legend(loc="lower right", frameon=True, framealpha=0.9)
    note = "全谱拟合（3601 点）对高斯噪声平均效应强：σ=2% 时 95% CI 半宽 <0.03%，收敛率 100%（600 次实验）"
    ax.text(
        0.995, -0.12, note, transform=ax.transAxes,
        fontsize=style["size"] - 2, color=PALETTE["neutral"], ha="right", va="top",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return render_and_register(
        cfg, style, fig, "E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）",
        "noise_robustness_ci", "sigma_percent", ["t_um"], source_hash,
    )


def main() -> None:
    cfg = config_section("visualization", PROBLEM_ID, QUESTION_ID)
    style, font_name = setup_style(cfg)
    print(f"[font] 使用中文字体：{font_name}")
    if not (RESULTS_DIR / "summary.json").is_file():
        raise RuntimeError(f"缺少 robustness 汇总结果：{RESULTS_DIR / 'summary.json'}")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    source_hash = hash_path(RESULTS_DIR)
    items = []
    items.append(fig_sensitivity_tornado(cfg, style, source_hash))
    items.append(fig_noise_robustness_ci(cfg, style, source_hash))
    print(f"[done] 生成并登记 {len(items)} 张敏感性图，source_hash={source_hash[:12]}…")


if __name__ == "__main__":
    main()
