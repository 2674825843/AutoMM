from __future__ import annotations

from pathlib import Path

import pytest
from automm import paper
from automm.common import read_json, write_text

pytestmark = pytest.mark.unit


def _writer_evidence(project_root: Path) -> dict:
    source = project_root / "problems" / "paper-demo" / "prob01" / "versions" / "assumption_v001"
    source.mkdir(parents=True)
    write_text(source / "assumptions.md", "# 假设\n\n观测噪声为零均值，参数在观测期恒定。\n")
    write_text(
        source / "formulation.md",
        "# 公式\n\n采用 $y=ax+b$，其中 $a$ 为响应系数（s^-1），$b$ 为基线。\n",
    )
    write_text(
        source / "question_summary.md",
        "使用约束最小二乘得到厚度 10.2 um，相对误差 0.8%；扰动后变化 0.2%。\n",
    )
    write_text(source / "rogue.md", "机密虚构结论：准确率 100%。\n")
    artifacts = []
    for name, evidence_id in (
        ("assumptions.md", "ev_assumptions"),
        ("formulation.md", "ev_formulation"),
        ("question_summary.md", "ev_summary"),
    ):
        artifacts.append(
            {
                "evidence_id": evidence_id,
                "question_id": "prob01",
                "kind": "artifact",
                "path": str((source / name).relative_to(project_root)).replace("\\", "/"),
                "sha256": evidence_id,
            }
        )
    return {
        "schema_version": 1,
        "problem_id": "paper-demo",
        "evidence_hash": "e" * 64,
        "cross_question_review": {"status": "passed", "reason": "符号一致"},
        "questions": [
            {
                "question_id": "prob01",
                "assumption_version": "assumption_v001",
                "formulation_version": "formulation_v001",
                "sanity": {"level_1_4": "PASS_WITH_WARNING", "level_5": "PASS"},
                "warnings": ["样本量较小"],
                "optional_stages": {
                    "robustness": {"decision": "completed", "reason": "扰动后变化 0.2%"},
                    "ablation": {"decision": "skipped", "reason": "没有可删除的独立模块"},
                },
                "artifact_evidence_ids": ["ev_assumptions", "ev_formulation", "ev_summary"],
            }
        ],
        "artifacts": artifacts,
        "figures": [
            {
                "evidence_id": "ev_figure_fit",
                "stable_id": "prob01_fit",
                "question_id": "prob01",
                "title": "约束模型拟合与残差",
                "path": "problems/paper-demo/prob01/versions/assumption_v001/figures/fit.png",
                "visual_review": {"status": "passed", "reason": "残差围绕零线分布"},
            }
        ],
        "citations": [
            {
                "evidence_id": "ev_citation_l01",
                "citation_id": "L01",
                "title": "Constrained least squares",
                "authors": ["A. Author", "B. Author"],
                "year": 2024,
                "source": "Modeling Journal",
            }
        ],
    }


def test_generator_builds_complete_valid_paper_from_whitelisted_evidence(project_root: Path, tmp_path: Path) -> None:
    generator = getattr(paper, "generate_evidence_markdown", None)
    if generator is None:
        pytest.fail("generate_evidence_markdown 尚未实现")
    evidence = _writer_evidence(project_root)
    version = tmp_path / "paper_v001"
    version.mkdir()

    output = generator("paper-demo", version, evidence)
    text = output.read_text(encoding="utf-8")

    assert "## prob01 模型建立、求解与结果" in text
    assert "10.2 um" in text and "0.8%" in text
    assert "样本量较小" in text
    assert "prob01_fit" in text and "[@L01]" in text
    assert "机密虚构结论" not in text
    assert "TODO" not in text and "待填写" not in text
    assert paper.validate_paper_markdown("paper-demo", version, evidence)["status"] == "PASS"
    manifest = read_json(version / "writer_manifest.json")
    assert manifest["evidence_hash"] == evidence["evidence_hash"]
    assert manifest["generator"] == "deterministic_evidence_writer"


def test_generator_refuses_artifact_outside_evidence_pack(project_root: Path, tmp_path: Path) -> None:
    generator = getattr(paper, "generate_evidence_markdown", None)
    if generator is None:
        pytest.fail("generate_evidence_markdown 尚未实现")
    evidence = _writer_evidence(project_root)
    evidence["artifacts"].append(
        {
            "evidence_id": "ev_escape",
            "question_id": "prob01",
            "kind": "artifact",
            "path": "../outside.md",
            "sha256": "escape",
        }
    )
    version = tmp_path / "paper_v001"
    version.mkdir()

    with pytest.raises(RuntimeError, match="Evidence Pack 路径越界"):
        generator("paper-demo", version, evidence)
