from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from automm.common import write_json, write_yaml
from automm.problems import question_manifest
from automm.runner import acquire_runner_lock, recover_incomplete_transactions, run_once
from automm.state import load_state, save_state

pytestmark = pytest.mark.integration


def test_prompt_contains_degraded_quality_contract(project_root: Path) -> None:
    prompt = (project_root / "agents" / "sanity-checker.md").read_text(encoding="utf-8")
    assert "PASS_WITH_WARNING" in prompt
    assert "mip_gap" in prompt
    assert "NaN/Inf" in prompt


def test_implementation_prompt_forbids_long_computation(project_root: Path) -> None:
    prompt = (project_root / "agents" / "implementation-agent.md").read_text(encoding="utf-8")
    assert "完整数据集" in prompt
    assert "supervised worker" in prompt
    assert "commands" in prompt


def test_orchestrator_runner_help_does_not_execute_action(project_root: Path) -> None:
    action_root = project_root / "runtime" / "actions"
    before = set(action_root.glob("*"))
    script = Path(__file__).resolve().parents[1] / "scripts" / "orchestrator_runner.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert set(action_root.glob("*")) == before


def test_transaction_recovery_marks_unfinished_action(tmp_path: Path) -> None:
    journal = tmp_path / "transactions.jsonl"
    journal.write_text('{"action_id":"act-1","phase":"started"}\n', encoding="utf-8")
    assert recover_incomplete_transactions(journal) == ["act-1"]


def test_runner_immediately_recovers_lock_owned_by_dead_process(project_root: Path) -> None:
    lock_path = project_root / "runtime" / "locks" / "orchestrator.lock"
    write_json(
        lock_path,
        {"owner": "interrupted-action", "pid": 2_000_000_000, "created_at": "2099-01-01T00:00:00+00:00"},
    )

    runner_lock, acquired = acquire_runner_lock("replacement-action")

    assert acquired is True
    assert runner_lock.info()["owner"] == "replacement-action"
    runner_lock.release()


def test_problem_conclusion_metadata_is_written(initialized_problem: tuple[str, Path]) -> None:
    problem_id, _ = initialized_problem
    from automm.workflow import record_conclusion

    record_conclusion(problem_id, "prob01", "c1", "synthetic conclusion")
    _, manifest = question_manifest(problem_id, "prob01")
    assert manifest["conclusion"]["conclusion_id"] == "c1"
    assert manifest["conclusion"]["content_hash"]


def test_successful_agent_recommendation_advances_when_transition_command_is_omitted(
    initialized_problem: tuple[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """防止 Agent 成功登记产物后因漏发 transition 而无限重跑当前阶段。"""
    problem_id, _ = initialized_problem
    state = load_state()
    state["current_stage"] = "visualization"
    save_state(state, event="test_setup")
    manifest_path, manifest = question_manifest(problem_id, "prob01")
    manifest["stage"] = "visualization"
    write_yaml(manifest_path, manifest)

    def successful_visualization(
        agent_name: str, action: dict[str, object], action_id: str
    ) -> tuple[dict[str, object], dict[str, object]]:
        assert agent_name == "visualization-agent"
        assert action["stage"] == "visualization"
        return (
            {
                "schema_version": 1,
                "action_id": action_id,
                "status": "success",
                "failure_class": None,
                "problem_id": problem_id,
                "question_id": "prob01",
                "assumption_version": None,
                "formulation_version": None,
                "artifacts_created": [],
                "artifacts_updated": [],
                "findings": ["visualization completed"],
                "warnings": [],
                "blocking_reasons": [],
                "recommended_next_stage": "robustness",
                "commands": [
                    {"name": "record_artifact", "arguments": {"name": "visualization", "completed": True}}
                ],
            },
            {"provider": "test"},
        )

    monkeypatch.setattr("automm.runner.invoke_agent", successful_visualization)

    result = run_once()

    assert result["status"] == "completed"
    assert load_state()["current_stage"] == "robustness"
