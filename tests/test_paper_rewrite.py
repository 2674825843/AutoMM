import pytest
from automm.common import write_json
from automm.problems import load_problem, problem_dir
from automm.state import load_state, save_state


def completed(problem_id):
    problem = load_problem(problem_id)
    problem.update(cross_question_review='passed', status='completed',
                   paper={'status': 'passed', 'active_version': 'paper_v004', 'evidence_hash': 'old'})
    write_json(problem_dir(problem_id) / 'problem_state.json', problem)
    state = load_state()
    state.update(control='paused', current_stage='completed', current_question=None)
    save_state(state, event='test')


def test_rewrite_requires_user_authorization_and_preserves_history(initialized_problem, monkeypatch):
    from automm.agent_runtime import apply_agent_commands
    problem_id, _ = initialized_problem
    completed(problem_id)
    monkeypatch.setattr('automm.paper.build_evidence_pack', lambda *a, **kw: {'evidence_hash': 'old'})
    response = {'action_id': 'rewrite-test', 'commands': [
        {'name': 'request_paper_rewrite', 'arguments': {'reason': 'user requested'}}]}
    action = {'problem_id': problem_id, 'stage': 'completed'}
    with pytest.raises(RuntimeError, match='授权'):
        apply_agent_commands(response, action)
    assert load_state()['current_stage'] == 'completed'
    action['user_authorized_rewrite'] = True
    apply_agent_commands(response, action)
    problem = load_problem(problem_id)
    assert problem['paper_history'][0]['active_version'] == 'paper_v004'
    assert problem['paper']['status'] == 'needs_revision'
    assert problem['paper']['rewrite_evidence_hash'] == 'old'
    assert load_state()['current_stage'] == 'paper_writing'
    assert problem['cross_question_review'] == 'passed'


def test_rewrite_refuses_stale_evidence_without_changing_state(initialized_problem, monkeypatch):
    from automm.agent_runtime import apply_agent_commands
    problem_id, _ = initialized_problem
    completed(problem_id)
    monkeypatch.setattr('automm.paper.build_evidence_pack', lambda *a, **kw: {'evidence_hash': 'changed'})
    response = {'action_id': 'rewrite-test', 'commands': [
        {'name': 'request_paper_rewrite', 'arguments': {'reason': 'user requested'}}]}
    with pytest.raises(RuntimeError, match='证据'):
        apply_agent_commands(response, {'problem_id': problem_id, 'user_authorized_rewrite': True})
    assert load_state()['current_stage'] == 'completed'
    assert load_problem(problem_id)['paper']['active_version'] == 'paper_v004'


@pytest.mark.parametrize('field', ['rewrite_evidence_hash', 'evidence_hash'])
def test_preparation_refuses_changed_authorized_evidence_before_any_write(project_root, field):
    from automm.paper import build_evidence_pack, prepare_paper_writing
    from test_paper_evidence import _eligible_problem
    problem_id, root = _eligible_problem(project_root)
    snapshot = build_evidence_pack(problem_id)
    shared_path = root / 'paper/evidence/evidence_pack.json'
    shared_before = shared_path.read_bytes()
    problem = load_problem(problem_id)
    problem['paper'] = {'status': 'needs_revision', field: snapshot['evidence_hash']}
    write_json(root / 'problem_state.json', problem)
    summary = root / 'prob01/versions/assumption_v001/question_summary.md'
    summary.write_text('新的未授权结论', encoding='utf-8')
    with pytest.raises(RuntimeError, match='证据'):
        prepare_paper_writing(problem_id)
    assert not (root / 'paper/versions').exists()
    assert shared_path.read_bytes() == shared_before
