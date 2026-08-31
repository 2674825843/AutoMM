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


def _reviewed_summary(project_root):
    from automm.common import relative, write_text
    from automm.paper import build_evidence_pack
    from test_paper_evidence import _eligible_problem
    problem_id, root = _eligible_problem(project_root)
    before = build_evidence_pack(problem_id)
    completed(problem_id)
    problem = load_problem(problem_id)
    problem['paper']['evidence_hash'] = before['evidence_hash']
    write_json(root / 'problem_state.json', problem)
    summary = root / 'prob01/versions/assumption_v001/question_summary.md'
    write_text(summary, '已复核：厚度为10.2 um，误差0.8%。')
    after = build_evidence_pack(problem_id, persist=False)
    report = root / 'paper/reviews/summary-review.json'
    write_json(report, {'status': 'PASS', 'scope': 'summary_only', 'before': before,
                        'after_evidence_hash': after['evidence_hash'],
                        'reason': '逐句对照已验收结果，无新增科学主张。'})
    response = {'action_id': 'reviewed-rewrite', 'commands': [
        {'name': 'request_paper_rewrite', 'arguments':
         {'reason': '用户批准摘要复核后重写', 'summary_review': relative(report)}}]}
    return problem_id, root, response, before, after


@pytest.mark.parametrize('legacy_timestamp_hash', [False, True])
def test_authorized_review_accepts_only_summary_change_and_preserves_previous_hash(project_root, legacy_timestamp_hash):
    from automm.agent_runtime import apply_agent_commands
    from automm.common import hash_json, read_json
    problem_id, root, response, before, after = _reviewed_summary(project_root)
    if legacy_timestamp_hash:
        before['evidence_hash'] = hash_json({k: v for k, v in before.items() if k != 'evidence_hash'})
        report_path = root / 'paper/reviews/summary-review.json'
        report = read_json(report_path)
        report['before'] = before
        write_json(report_path, report)
        problem = load_problem(problem_id)
        problem['paper']['evidence_hash'] = before['evidence_hash']
        write_json(root / 'problem_state.json', problem)
    apply_agent_commands(response, {'problem_id': problem_id, 'user_authorized_rewrite': True})
    problem = load_problem(problem_id)
    assert problem['paper_history'][0]['evidence_hash'] == before['evidence_hash']
    assert problem['paper']['rewrite_evidence_hash'] == after['evidence_hash']
    assert problem['paper']['summary_review'].endswith('summary-review.json')
    assert load_state()['current_stage'] == 'paper_writing'


@pytest.mark.parametrize('mutation', ['after_review', 'other_artifact', 'snapshot_tamper', 'not_pass'])
def test_summary_review_cannot_bypass_changed_science_or_stale_review(project_root, mutation):
    from automm.agent_runtime import apply_agent_commands
    from automm.common import read_json, write_text
    from automm.paper import build_evidence_pack
    problem_id, root, response, before, _ = _reviewed_summary(project_root)
    report_path = root / 'paper/reviews/summary-review.json'
    report = read_json(report_path)
    if mutation == 'after_review':
        write_text(root / 'prob01/versions/assumption_v001/question_summary.md', '复核后又变更')
    elif mutation == 'other_artifact':
        write_text(root / 'prob01/versions/assumption_v001/assumptions.md', '改变模型假设')
        report['after_evidence_hash'] = build_evidence_pack(problem_id, persist=False)['evidence_hash']
    elif mutation == 'snapshot_tamper':
        report['before']['artifacts'][0]['sha256'] = 'forged'
    else:
        report['status'] = 'NEEDS_REVISION'
    write_json(report_path, report)
    with pytest.raises(RuntimeError):
        apply_agent_commands(response, {'problem_id': problem_id, 'user_authorized_rewrite': True})
    assert load_state()['current_stage'] == 'completed'
    assert load_problem(problem_id)['paper']['evidence_hash'] == before['evidence_hash']
