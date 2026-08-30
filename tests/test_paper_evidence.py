from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from automm.common import read_json, read_yaml, write_json, write_text, write_yaml
from automm.problems import init_problem, question_manifest

pytestmark = pytest.mark.unit


def _paper_module():
    try:
        return importlib.import_module("automm.paper")
    except ModuleNotFoundError:
        pytest.fail("生产模块 automm.paper 尚未实现")


def _eligible_problem(project_root: Path) -> tuple[str, Path]:
    problem_id = "paper-demo"
    root = init_problem(problem_id, 1)
    problem = read_json(root / "problem_state.json")
    problem["cross_question_review"] = "passed"
    write_json(root / "problem_state.json", problem)

    manifest_path, manifest = question_manifest(problem_id, "prob01")
    manifest["stage"] = "locally_completed"
    manifest["status"] = "locally_completed"
    manifest["active_assumption_version"] = 1
    manifest["accepted_assumption_version"] = 1
    manifest["active_formulation_version"] = 1
    manifest["accepted_formulation_version"] = 1
    manifest["sanity"] = {"level_1_4": "PASS_WITH_WARNING", "level_5": "PASS", "level_6": "PASS"}
    manifest["sanity_history"] = [
        {"level": "level_1_4", "status": "PASS_WITH_WARNING", "reason": "样本量较小"},
        {"level": "level_5", "status": "PASS", "reason": "图表复核通过"},
    ]
    manifest["optional_stages"] = {
        "robustness": {"decision": "completed", "reason": "噪声扰动稳定"},
        "ablation": {"decision": "skipped", "reason": "只有一个可辨识模型"},
    }
    write_yaml(manifest_path, manifest)

    version = root / "prob01" / "versions" / "assumption_v001"
    formulation = version / "formulations" / "formulation_v001"
    formulation.mkdir(parents=True)
    write_yaml(version / "version.yaml", {"version": "assumption_v001", "status": "accepted"})
    write_text(version / "assumptions.md", "# 假设\n\n容量约束在观察期内恒定。\n")
    write_yaml(formulation / "formulation.yaml", {"version": "formulation_v001", "status": "accepted"})
    write_text(formulation / "formulation.md", "# 模型\n\n$y=ax$，其中 $a$ 的单位为 s^-1。\n")
    write_text(version / "implementation.md", "# 实现\n\n使用最小二乘求解。\n")
    write_text(version / "question_summary.md", "厚度估计为 10.2 um，相对误差为 0.8%。\n")
    result_dir = version / "results" / "accepted-run"
    result_dir.mkdir(parents=True)
    write_json(
        result_dir / "result.json",
        {
            "thickness_um": 10.2,
            "relative_error_pct": 0.8,
            "note": "约束满足：无 NaN/Inf",
        },
    )

    figure_path = version / "figures" / "fit.png"
    figure_path.parent.mkdir(parents=True)
    figure_path.write_bytes(b"valid-image-fixture")
    write_yaml(
        root / "figures.yaml",
        {
            "figures": [
                {
                    "stable_id": "prob01_fit",
                    "question_id": "prob01",
                    "assumption_version": "assumption_v001",
                    "title": "拟合结果",
                    "path": str(figure_path.relative_to(project_root)).replace("\\", "/"),
                    "quality_status": "passed",
                    "visual_review": {"status": "passed", "reason": "清晰"},
                    "included_in_summary": True,
                }
            ]
        },
    )
    write_yaml(
        root / "citations.yaml",
        {
            "references": [
                {
                    "citation_id": "L01",
                    "question_id": "prob01",
                    "title": "A verified method",
                    "authors": ["A. Author"],
                    "year": 2024,
                    "source": "Journal",
                    "metadata_status": "verified",
                    "usage_status": "used",
                }
            ]
        },
    )
    return problem_id, root


def test_evidence_pack_selects_only_accepted_reviewed_material(project_root: Path) -> None:
    paper = _paper_module()
    problem_id, root = _eligible_problem(project_root)

    evidence = paper.build_evidence_pack(problem_id)

    assert evidence["problem_id"] == problem_id
    assert evidence["questions"][0]["assumption_version"] == "assumption_v001"
    assert evidence["questions"][0]["formulation_version"] == "formulation_v001"
    assert evidence["questions"][0]["warnings"] == ["样本量较小"]
    assert evidence["figures"][0]["stable_id"] == "prob01_fit"
    assert evidence["citations"][0]["citation_id"] == "L01"
    artifact = next(item for item in evidence["artifacts"] if item["path"].endswith("result.json"))
    assert len(artifact["sha256"]) == 64
    assert (root / "paper" / "evidence" / "evidence_pack.json").is_file()
    assert (root / "paper" / "evidence" / "evidence_pack.md").is_file()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("stale", "stale"),
        ("level5", "L5"),
        ("figure", "图表"),
        ("citation", "引用"),
        ("nan", "NaN/Inf"),
    ],
)
def test_evidence_pack_rejects_untrusted_or_incomplete_material(
    project_root: Path, mutation: str, message: str
) -> None:
    paper = _paper_module()
    problem_id, root = _eligible_problem(project_root)
    manifest_path, manifest = question_manifest(problem_id, "prob01")
    if mutation == "stale":
        manifest["stale"] = {"value": True, "caused_by": ["prob00"]}
        write_yaml(manifest_path, manifest)
    elif mutation == "level5":
        manifest["sanity"]["level_5"] = "NEEDS_REVISION"
        write_yaml(manifest_path, manifest)
    elif mutation == "figure":
        figures = read_yaml(root / "figures.yaml")
        figures["figures"][0]["visual_review"]["status"] = "needs_revision"
        write_yaml(root / "figures.yaml", figures)
    elif mutation == "citation":
        write_yaml(root / "citations.yaml", {"references": []})
    else:
        result = root / "prob01" / "versions" / "assumption_v001" / "results" / "accepted-run" / "result.json"
        result.write_text('{"thickness_um": NaN}', encoding="utf-8")

    with pytest.raises(RuntimeError, match=message):
        paper.build_evidence_pack(problem_id)


def test_paper_versions_are_monotonic_and_never_overwritten(project_root: Path) -> None:
    paper = _paper_module()
    problem_id, _ = _eligible_problem(project_root)

    first_name, first_path = paper.create_paper_version(problem_id)
    write_text(first_path / "paper.md", "first")
    second_name, second_path = paper.create_paper_version(problem_id)

    assert (first_name, second_name) == ("paper_v001", "paper_v002")
    assert (first_path / "paper.md").read_text(encoding="utf-8") == "first"
    assert second_path.is_dir()
