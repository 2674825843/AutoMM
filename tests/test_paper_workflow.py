from __future__ import annotations

from pathlib import Path

import pytest

from automm.common import read_json, write_json
from automm.problems import load_problem, problem_dir, question_manifest
from automm.runner import execute_non_agent
from automm.state import load_state, save_state
from automm.workflow import next_action, transition

pytestmark = pytest.mark.unit


def _global_review_passed(problem_id: str) -> None:
    problem = load_problem(problem_id)
    problem["cross_question_review"] = "passed"
    problem["current_question"] = None
    write_json(problem_dir(problem_id) / "problem_state.json", problem)
    for question_id in problem["questions"]:
        path, manifest = question_manifest(problem_id, question_id)
        manifest["stage"] = "locally_completed"
        manifest["status"] = "locally_completed"
        manifest["accepted_assumption_version"] = 1
        manifest["accepted_formulation_version"] = 1
        manifest["sanity"] = {"level_1_4": "PASS", "level_5": "PASS", "level_6": "PASS"}
        from automm.common import write_yaml

        write_yaml(path, manifest)
    state = load_state()
    state["current_question"] = None
    state["current_stage"] = "cross_question_review"
    save_state(state, event="paper_test_setup")


def test_cross_question_review_advances_to_paper_writing_before_completed(
    initialized_problem: tuple[str, Path],
) -> None:
    problem_id, _ = initialized_problem
    _global_review_passed(problem_id)

    transition(target_stage="paper_writing", problem_id=problem_id, reason="review passed")

    assert load_state()["current_stage"] == "paper_writing"
    assert next_action()["action"] == "prepare_paper_writing"


def test_prepared_paper_dispatches_writer_agent(initialized_problem: tuple[str, Path]) -> None:
    problem_id, _ = initialized_problem
    _global_review_passed(problem_id)
    transition(target_stage="paper_writing", problem_id=problem_id, reason="review passed")
    problem = load_problem(problem_id)
    problem["paper"] = {
        "status": "drafting",
        "active_version": "paper_v001",
        "evidence": "evidence.json",
    }
    write_json(problem_dir(problem_id) / "problem_state.json", problem)

    action = next_action()

    assert action["action"] == "run_agent"
    assert action["agent"] == "paper-writer"
    assert action["stage"] == "paper_writing"


def test_completed_stage_requires_a_passed_rendered_paper(initialized_problem: tuple[str, Path]) -> None:
    problem_id, _ = initialized_problem
    _global_review_passed(problem_id)
    transition(target_stage="paper_writing", problem_id=problem_id, reason="review passed")
    transition(target_stage="paper_validation", problem_id=problem_id, reason="draft ready")

    with pytest.raises(RuntimeError, match="论文.*未通过"):
        transition(target_stage="completed", problem_id=problem_id, reason="attempted bypass")


def test_validation_handler_publishes_final_and_completes(
    initialized_problem: tuple[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    problem_id, _ = initialized_problem
    _global_review_passed(problem_id)
    transition(target_stage="paper_writing", problem_id=problem_id, reason="review passed")
    transition(target_stage="paper_validation", problem_id=problem_id, reason="draft ready")
    version_dir = problem_dir(problem_id) / "paper" / "versions" / "paper_v001"
    version_dir.mkdir(parents=True)
    for name in ("paper.md", "paper.docx", "paper.tex", "paper.pdf", "validation.json", "render_report.json"):
        (version_dir / name).write_bytes(name.encode())
    evidence_path = problem_dir(problem_id) / "paper" / "evidence" / "evidence_pack.json"
    evidence_path.parent.mkdir(parents=True)
    write_json(evidence_path, {"problem_id": problem_id, "evidence_hash": "x"})
    problem = load_problem(problem_id)
    problem["paper"] = {"status": "validating", "active_version": "paper_v001", "evidence": str(evidence_path)}
    write_json(problem_dir(problem_id) / "problem_state.json", problem)

    monkeypatch.setattr("automm.runner.validate_paper_markdown", lambda *_: {"status": "PASS", "errors": []})
    monkeypatch.setattr("automm.runner.render_paper", lambda *_: {"status": "PASS", "errors": []})

    result = execute_non_agent({"action": "validate_and_render_paper", "problem_id": problem_id})

    assert result["paper"]["status"] == "passed"
    assert load_state()["current_stage"] == "completed"
    final = problem_dir(problem_id) / "paper" / "final"
    assert (final / "paper.docx").is_file() and (final / "paper.pdf").is_file()
    assert read_json(problem_dir(problem_id) / "problem_state.json")["paper"]["active_version"] == "paper_v001"
