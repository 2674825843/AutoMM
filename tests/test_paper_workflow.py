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
    from test_paper_delivery import setup
    version_dir, evidence, _ = setup(problem_dir(problem_id).parents[1], problem_id, 'paper_v001')
    write_json(version_dir / 'validation.json', {'status': 'PASS', 'evidence_hash': evidence['evidence_hash']})
    evidence_path = problem_dir(problem_id) / "paper" / "evidence" / "evidence_pack.json"
    evidence_path.parent.mkdir(parents=True)
    write_json(evidence_path, {"problem_id": problem_id, "evidence_hash": "x"})
    problem = load_problem(problem_id)
    problem["paper"] = {"status": "validating", "active_version": "paper_v001", "evidence": str(evidence_path),
                        'evidence_hash': evidence['evidence_hash']}
    write_json(problem_dir(problem_id) / "problem_state.json", problem)

    def no_rerender(*_):
        pytest.fail('未变化且已验收的产物不应重新渲染')
    monkeypatch.setattr('automm.runner.render_paper', no_rerender)

    result = execute_non_agent({"action": "validate_and_render_paper", "problem_id": problem_id})

    assert result["paper"]["status"] == "passed"
    assert load_state()["current_stage"] == "completed"
    final = problem_dir(problem_id) / "paper" / "final"
    assert (final / "paper.docx").is_file() and (final / "paper.pdf").is_file()
    assert read_json(problem_dir(problem_id) / "problem_state.json")["paper"]["active_version"] == "paper_v001"
    assert (final / '交付/论文.docx').is_file()
    assert result['paper']['delivery_status'] == 'PASS'


def test_delivery_failure_does_not_complete_or_publish(initialized_problem, monkeypatch):
    problem_id, _ = initialized_problem
    _global_review_passed(problem_id)
    transition(target_stage='paper_writing', problem_id=problem_id, reason='review passed')
    transition(target_stage='paper_validation', problem_id=problem_id, reason='draft ready')
    from test_paper_delivery import setup
    version, evidence, _ = setup(problem_dir(problem_id).parents[1], problem_id, 'paper_v001')
    write_json(version / 'validation.json', {'status': 'PASS', 'evidence_hash': evidence['evidence_hash']})
    problem = load_problem(problem_id)
    problem['paper'] = {'status': 'validating', 'active_version': 'paper_v001',
                        'evidence_hash': evidence['evidence_hash']}
    write_json(problem_dir(problem_id) / 'problem_state.json', problem)
    monkeypatch.setattr('automm.runner.validate_paper_markdown', lambda *_: {'status': 'PASS'})
    monkeypatch.setattr('automm.runner.render_paper', lambda *_: {'status': 'PASS'})
    def fail(*_, **kwargs):
        raise RuntimeError('input hash changed')
    monkeypatch.setattr('automm.paper_delivery.build_delivery', fail)
    with pytest.raises(RuntimeError, match='input hash'):
        execute_non_agent({'action': 'validate_and_render_paper', 'problem_id': problem_id})
    assert load_state()['current_stage'] == 'paper_validation'
    assert not (problem_dir(problem_id) / 'paper/final').exists()


@pytest.mark.parametrize('point', ['copy', 'manifest', 'state'])
def test_atomic_publication_recovers_after_interruption(initialized_problem, monkeypatch, point):
    from automm import paper_delivery, runner
    from test_paper_delivery import setup
    problem_id, root = initialized_problem
    _global_review_passed(problem_id)
    transition(target_stage='paper_writing', problem_id=problem_id, reason='review passed')
    transition(target_stage='paper_validation', problem_id=problem_id, reason='draft ready')
    version, evidence, _ = setup(root.parents[1], problem_id, 'paper_v001')
    write_json(version / 'validation.json', {'status': 'PASS', 'evidence_hash': evidence['evidence_hash']})
    problem = load_problem(problem_id)
    problem['paper'] = {'status': 'validating', 'active_version': version.name,
                        'evidence_hash': evidence['evidence_hash']}
    write_json(root / 'problem_state.json', problem)
    original_docx = (version / 'paper.docx').read_bytes()
    final = root / 'paper/final'
    if point == 'copy':
        real = paper_delivery.shutil.copy2
        def crash(source, destination, *args, **kwargs):
            raise OSError('injected copy interruption')
        monkeypatch.setattr(paper_delivery.shutil, 'copy2', crash)
    else:
        module = runner if point == 'state' else paper_delivery
        real = module.write_json
        def crash(path, value):
            if (point == 'state' and path.name == 'problem_state.json' and final.exists()) or (
                    point == 'manifest' and path.name == 'manifest.json'):
                raise OSError('injected manifest/state interruption')
            return real(path, value)
        monkeypatch.setattr(module, 'write_json', crash)
    with pytest.raises(OSError, match='injected'):
        execute_non_agent({'action': 'validate_and_render_paper', 'problem_id': problem_id})
    assert final.exists() == (point == 'state')
    assert load_state()['current_stage'] == 'paper_validation'
    monkeypatch.undo()
    result = execute_non_agent({'action': 'validate_and_render_paper', 'problem_id': problem_id})
    assert result['paper']['status'] == 'passed'
    assert (final / '交付/论文.docx').read_bytes() == original_docx
    assert (version / 'paper.docx').read_bytes() == original_docx
    assert read_json(final / 'manifest.json')['delivery'].endswith('/paper/final/交付')
    assert '.pending' not in (version / 'delivery_manifest.json').read_text(encoding='utf-8')


def test_runner_rejects_paper_hash_different_from_version_snapshot(initialized_problem):
    from test_paper_delivery import setup
    problem_id, root = initialized_problem
    version, evidence, _ = setup(root.parents[1], problem_id, 'paper_v001')
    write_json(version / 'validation.json', {'status': 'PASS', 'evidence_hash': evidence['evidence_hash']})
    problem = load_problem(problem_id)
    problem['paper'] = {'status': 'validating', 'active_version': version.name, 'evidence_hash': 'other-snapshot'}
    write_json(root / 'problem_state.json', problem)
    with pytest.raises(RuntimeError, match='证据|快照'):
        execute_non_agent({'action': 'validate_and_render_paper', 'problem_id': problem_id})
    assert not (root / 'paper/final').exists()


def test_retry_rejects_corrupted_accepted_docx_without_rerender(initialized_problem, monkeypatch):
    from test_paper_delivery import setup
    problem_id, root = initialized_problem
    version, evidence, _ = setup(root.parents[1], problem_id, 'paper_v001')
    problem = load_problem(problem_id)
    problem['paper'] = {'status': 'validating', 'active_version': version.name,
                        'evidence_hash': evidence['evidence_hash']}
    write_json(root / 'problem_state.json', problem)
    (version / 'paper.docx').write_bytes(b'changed accepted output')
    def no_render(*args):
        pytest.fail('损坏的已验收产物不能被重新生成而隐藏')
    monkeypatch.setattr('automm.runner.render_paper', no_render)
    with pytest.raises(RuntimeError, match='哈希'):
        execute_non_agent({'action': 'validate_and_render_paper', 'problem_id': problem_id})
    assert (version / 'paper.docx').read_bytes() == b'changed accepted output'


def test_existing_final_with_tampered_delivery_is_not_overwritten(initialized_problem):
    from automm.paper_delivery import publish_paper
    from test_paper_delivery import setup
    problem_id, root = initialized_problem
    version, evidence, _ = setup(root.parents[1], problem_id, 'paper_v001')
    write_json(version / 'validation.json', {'status': 'PASS', 'evidence_hash': evidence['evidence_hash']})
    final = root / 'paper/final'
    publish_paper(version, evidence, {}, final)
    public_docx = final / '交付/论文.docx'
    public_docx.write_bytes(b'changed published output')
    with pytest.raises(RuntimeError, match='冲突|哈希'):
        publish_paper(version, evidence, {}, final)
    assert public_docx.read_bytes() == b'changed published output'
