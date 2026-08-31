from pathlib import Path

import pytest
from automm import paper
from automm.common import read_json, write_json, write_text
from automm.paper_integrity import evidence_digest

pytestmark = pytest.mark.unit


def quality_fixture(project_root: Path, tmp_path: Path):
    from test_paper_evidence import _eligible_problem

    problem_id, _ = _eligible_problem(project_root)
    evidence = paper.build_evidence_pack(problem_id, persist=False)
    rules = tmp_path / "rules.json"
    write_json(
        rules,
        {
            "version": "award-writing-v1",
            "rules": [
                {
                    "id": "answer-first",
                    "principle": "逐问回答，以证据约束主张。",
                    "applies_to": ["abstract", "conclusions"],
                    "cautions": ["不得复制范文事实"],
                    "sources": [{"path": "fixture.pdf", "sha256": "a" * 64, "pages": [1]}],
                }
            ],
        },
    )
    version = project_root / "problems" / problem_id / "paper/versions/paper_v001"
    version.mkdir(parents=True)
    return version, evidence, rules


def test_new_quality_scaffold_freezes_rules_without_fabricating_answers(project_root, tmp_path):
    from automm import paper_quality as quality

    version, evidence, rules = quality_fixture(project_root, tmp_path)
    result = quality.prepare_quality_version(version, evidence, rules_path=rules)
    plan = read_json(version / "writing_plan.json")
    assert result["quality_contract"]["rules_sha256"]
    assert plan["evidence_hash"] == evidence_digest(evidence)
    assert plan["questions"][0]["question_id"] == "prob01"
    assert not plan["questions"][0]["claims"]
    assert quality.validate_plan(version, evidence)["status"] == "NEEDS_REVISION"
    assert "10.2" not in (version / "paper.md").read_text(encoding="utf-8")
    write_text(rules, "changed configured pack")
    assert quality.quality_contract(version, evidence)["rules_sha256"] == result["quality_contract"]["rules_sha256"]


def completed_quality_fixture(project_root, tmp_path):
    from automm import paper_quality as quality

    version, evidence, rules = quality_fixture(project_root, tmp_path)
    quality.prepare_quality_version(version, evidence, rules_path=rules)
    plan = read_json(version / "writing_plan.json")
    result_id = next(a["evidence_id"] for a in evidence["artifacts"] if a["path"].endswith("result.json"))
    draft = ["# 容量受限系统的厚度估计\n"]
    paragraphs = {
        "abstract": "利用最小二乘估计系统厚度为 **10.2 um**，相对误差为 **0.8%**，小样本限制外推。",
        "problem": "目标是在给定观测与容量约束下估计系统厚度。",
        "analysis": "先依据容量识别约束，再拟合响应关系，最后检查相对误差。",
        "assumptions": "在当前观察期内假定容量约束和响应参数保持恒定。",
        "symbols": "厚度符号 t 的单位为 um，响应系数 a 的单位为 s^-1。",
        "data": "使用题目给定观测，不增加新样本，也不推断缺失观测。",
        "limitations": "现有样本较少，无法保证分布漂移后的预测性能。",
        "conclusions": "本问估计厚度为 10.2 um，相对误差为 0.8%，仅适用于当前观测条件。",
        "references": "本模型不使用额外文献主张，仅依据已接受的题目公式。",
        "reproduction": "按问题顺序准备输入，将结果写入独立输出目录，再绘制结果图。",
        "model": "响应模型为 $y=ax$，其中 a 为响应系数，单位为 s^-1。",
        "solution": "在容量约束下使用最小二乘方法估计响应关系。",
        "results": "厚度估计为 10.2 um，相对误差为 0.8%，数值支持当前条件下的拟合。",
        "reliability": "样本量较小，因此该估计尚不能证明跨分布的泛化能力。",
    }
    for i, role in enumerate(plan["roles"]):
        anchor = f"p{i}"
        paragraph = paragraphs[role["role"]]
        role.update(anchor=anchor, excerpt=paragraph, evidence_ids=[result_id])
        draft.extend([f"## 自适应论述{i}\n", f"<!-- paper:{anchor} -->\n{paragraph}\n"])
    q = plan["questions"][0]
    results = next(r for r in plan["roles"] if r["role"] == "results")
    q.update(
        answer=paragraphs["results"],
        claims=[
            dict(
                id="q1-thickness",
                text=paragraphs["results"],
                **{k: results[k] for k in ("anchor", "excerpt", "evidence_ids")},
            )
        ],
    )
    for group in ("figures", "citations"):
        for item in plan[group]:
            item.update(selected=False, reason="该材料不承担独立论证，必要数值与限制已经由正文和结果证据覆盖。")
    reliability = next(r for r in plan["roles"] if r["role"] == "reliability")
    for warning in plan["warnings"]:
        warning.update(**{k: reliability[k] for k in ("anchor", "excerpt", "evidence_ids")})
    write_json(version / "writing_plan.json", plan)
    write_text(version / "paper.md", "\n".join(draft))
    return version, evidence, plan


def test_adaptive_headings_and_audited_omissions_pass_through_public_validator(project_root, tmp_path):
    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    assert paper.validate_paper_markdown(evidence["problem_id"], version, evidence)["status"] == "PASS"
    assert read_json(version / 'publication_manifest.json')['citations'] == []


@pytest.mark.parametrize(
    "missing", ["question", "warning", "role", "omission_reason", "actual_paragraph", "unknown_evidence"]
)
def test_plan_cannot_hide_missing_content_behind_markers(project_root, tmp_path, missing):
    from automm import paper_quality as quality

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    if missing == "question":
        plan["questions"] = []
    elif missing == "warning":
        plan["warnings"] = []
    elif missing == "role":
        plan["roles"] = [r for r in plan["roles"] if r["role"] != "solution"]
    elif missing == "omission_reason":
        plan["figures"][0]["reason"] = ""
    elif missing == "unknown_evidence":
        plan["questions"][0]["claims"][0]["evidence_ids"] = ["fabricated"]
    else:
        write_text(version / "paper.md", "<!-- paper:p0 --><!-- evidence:anything -->\n")
    write_json(version / "writing_plan.json", plan)
    assert quality.validate_plan(version, evidence)["status"] == "NEEDS_REVISION"


@pytest.mark.parametrize("tamper", ["manifest", "rules", "expected_contract"])
def test_quality_contract_cannot_be_removed_or_changed(project_root, tmp_path, tamper):
    from automm import paper_quality as quality
    from automm.problems import load_problem, problem_dir

    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    writer = read_json(version / "writer_manifest.json")
    problem = load_problem(evidence["problem_id"])
    problem["paper"] = {"active_version": version.name, "quality_contract": writer["quality_contract"]}
    write_json(problem_dir(evidence["problem_id"]) / "problem_state.json", problem)
    if tamper == "manifest":
        del writer["quality_contract"]
        write_json(version / "writer_manifest.json", writer)
    elif tamper == "rules":
        write_json(version / "writing_rules.json", {"version": "forged"})
    else:
        writer["quality_contract"]["max_writer_revisions"] = 0
        write_json(version / "writer_manifest.json", writer)
    with pytest.raises(RuntimeError, match="契约|规则"):
        quality.quality_contract(version, evidence)


def test_direct_render_cannot_bypass_independent_review(project_root, tmp_path):
    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    assert paper.validate_paper_markdown(evidence["problem_id"], version, evidence)["status"] == "PASS"
    with pytest.raises(RuntimeError, match="审阅|review"):
        paper.render_paper(version, {"pandoc_executable": "nonexistent"})


def review_fixture(version, evidence, plan):
    from automm import paper_quality as quality
    from automm.common import hash_json
    from automm.paper_integrity import digest

    rows = [*plan["roles"], *plan["warnings"], *(c for q in plan["questions"] for c in q["claims"])]
    used_ids = {v for row in rows for v in row["evidence_ids"]}
    reads = []
    for group in ("artifacts", "figures", "citations"):
        for item in evidence[group]:
            if item["evidence_id"] in used_ids:
                path = quality.ROOT / item["path"] if "path" in item else None
                reads.append(
                    {
                        "evidence_id": item["evidence_id"],
                        "sha256": digest(path) if path else hash_json(item),
                        "excerpt": path.read_text(encoding="utf-8") if path else item["title"],
                    }
                )

    def assessment(item, id_key):
        return {
            "id": item[id_key],
            "status": "adequate",
            "reason": "已逐项核对原始结果值、单位与外推限制，正文表述与证据一致。",
            **{k: item[k] for k in ("anchor", "excerpt", "evidence_ids")},
        }

    result_role = next(r for r in plan["roles"] if r["role"] == "results")
    return {
        "schema_version": 1,
        **quality.review_bindings(version, evidence),
        "findings": [],
        "questions": [assessment(dict(result_role, id=q["question_id"]), "id") for q in plan["questions"]],
        "claims": [assessment(c, "id") for q in plan["questions"] for c in q["claims"]],
        "warnings": [assessment(w, "id") for w in plan["warnings"]],
        "evidence_reads": reads,
    }


def test_review_requires_real_assessments_and_exact_hash_bindings(project_root, tmp_path):
    from automm import paper_quality as quality

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    review = review_fixture(version, evidence, plan)
    assert quality.validate_review(version, evidence, review)["findings"] == []
    for field in ("questions", "claims", "warnings", "evidence_reads"):
        invalid = dict(review, **{field: []})
        with pytest.raises(RuntimeError):
            quality.validate_review(version, evidence, invalid)
    write_text(version / "paper.md", (version / "paper.md").read_text(encoding="utf-8") + "\n改动正文。\n")
    with pytest.raises(RuntimeError, match="哈希|绑定"):
        quality.validate_review(version, evidence, review)


def activate_quality(version, evidence, status="reviewing"):
    from automm.problems import load_problem, problem_dir
    from automm.state import load_state, save_state

    problem = load_problem(evidence["problem_id"])
    contract = read_json(version / "writer_manifest.json")["quality_contract"]
    problem["paper"] = {
        "active_version": version.name,
        "version_dir": str(version),
        "status": status,
        "evidence_hash": evidence["evidence_hash"],
        "quality_contract": contract,
        "writer_revisions": contract["writer_revisions"],
    }
    write_json(problem_dir(evidence["problem_id"]) / "problem_state.json", problem)
    state = load_state()
    state.update(
        active_problem=evidence["problem_id"],
        current_question=None,
        current_stage="paper_validation",
        control="running",
    )
    save_state(state, event="quality-test")


def review_response(evidence, review):
    return {
        "schema_version": 1,
        "action_id": "quality-review",
        "status": "success",
        "problem_id": evidence["problem_id"],
        "question_id": None,
        "assumption_version": None,
        "formulation_version": None,
        "artifacts_created": [],
        "artifacts_updated": [],
        "findings": [],
        "warnings": [],
        "blocking_reasons": [],
        "recommended_next_stage": None,
        "commands": [{"name": "record_paper_review", "arguments": {"report": review}}],
    }


def test_reviewer_records_only_validated_review_transaction_and_cannot_transition(project_root, tmp_path):
    import jsonschema
    from automm.agent_runtime import apply_agent_commands
    from automm.workflow import next_action

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    activate_quality(version, evidence)
    review = review_fixture(version, evidence, plan)
    response = review_response(evidence, review)
    jsonschema.validate(response, read_json(project_root / "config/agent_response.schema.json"))
    action = next_action()
    assert action["agent"] == "paper-reviewer"
    assert action["read_only"] is True
    forged = dict(
        response, commands=[{"name": "transition", "arguments": {"target_stage": "completed", "reason": "bypass"}}]
    )
    with pytest.raises(RuntimeError):
        apply_agent_commands(forged, action)
    apply_agent_commands(response, action)
    assert read_json(version / "paper_review.json") == review
    assert next_action()["action"] == "assess_paper_quality"
    with pytest.raises(RuntimeError):
        apply_agent_commands(response, dict(action, agent="paper-writer"))


@pytest.mark.parametrize("severity,want", [("blocking", "attention"), ("advisory", "validating")])
def test_revision_cap_parks_blocking_but_accepts_advisory_without_fourth_revision(
    project_root, tmp_path, severity, want
):
    from automm.agent_runtime import apply_agent_commands
    from automm.runner import execute_non_agent
    from automm.workflow import next_action

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    writer = read_json(version / "writer_manifest.json")
    writer["quality_contract"]["writer_revisions"] = 3
    write_json(version / "writer_manifest.json", writer)
    activate_quality(version, evidence)
    review = review_fixture(version, evidence, plan)
    claim = plan["questions"][0]["claims"][0]
    review["findings"] = [
        dict(
            severity=severity,
            reason="结果解释需要进一步区分样本内拟合与外推能力。",
            instruction="请将结果表述限定在当前样本范围，并在结论再次说明。",
            **{k: claim[k] for k in ("anchor", "excerpt", "evidence_ids")},
        )
    ]
    apply_agent_commands(review_response(evidence, review), next_action())
    result = execute_non_agent(next_action())
    assert result["paper"]["status"] == want
    assert result["paper"]["writer_revisions"] == 3
    for _ in range(4):
        assert next_action()["action"] == ("paper_attention" if severity == "blocking" else "validate_and_render_paper")
    assert len(list(version.parent.iterdir())) == 1


def test_revisions_preserve_frozen_policy_and_repeated_preparation_is_idempotent(project_root, tmp_path):
    from automm.agent_runtime import apply_agent_commands
    from automm.common import read_yaml, write_yaml
    from automm.runner import execute_non_agent
    from automm.workflow import next_action

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    activate_quality(version, evidence)
    initial_science = read_json(project_root / "problems/paper-demo/problem_state.json")["cross_question_review"]
    for count in range(3):
        review = review_fixture(version, evidence, plan)
        claim = plan["questions"][0]["claims"][0]
        review["findings"] = [
            dict(
                severity="advisory",
                reason="结果段文字存在可进一步压缩的重复解释。",
                instruction="请减少重复解释，保留定量结论、证据和必要限制。",
                **{k: claim[k] for k in ("anchor", "excerpt", "evidence_ids")},
            )
        ]
        apply_agent_commands(review_response(evidence, review), next_action())
        execute_non_agent(next_action())
        prepare_action = next_action()
        assert prepare_action["action"] == "prepare_paper_writing"
        # Runtime configuration edits do not reset this lineage's frozen budget.
        settings = read_yaml(project_root / "config/paper.yaml")
        settings["max_writer_revisions"] = 0
        write_yaml(project_root / "config/paper.yaml", settings)
        result = execute_non_agent(prepare_action)
        current = result["paper"]
        assert current["writer_revisions"] == count + 1
        assert current["quality_contract"]["max_writer_revisions"] == 3
        assert current["revision_requests"][0]["instruction"].startswith("请减少")
        again = execute_non_agent(prepare_action)
        assert again["paper"]["active_version"] == current["active_version"]
        version = project_root / current["version_dir"]
        plan = read_json(version / "writing_plan.json")
        activate_quality(version, evidence)
    assert len(list(version.parent.glob("paper_v*"))) == 4
    assert (
        read_json(project_root / "problems/paper-demo/problem_state.json")["cross_question_review"] == initial_science
    )


def test_planning_then_drafting_are_separate_checkpointed_invocations(project_root, tmp_path):
    from automm.agent_runtime import apply_agent_commands
    from automm.state import load_state, save_state
    from automm.workflow import next_action

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    text = (version / "paper.md").read_text(encoding="utf-8")
    write_text(version / "paper.md", "# 待填写标题\n")
    activate_quality(version, evidence, status="planning")
    state = load_state()
    state["current_stage"] = "paper_writing"
    save_state(state, event="planning-test")
    response = review_response(evidence, {})
    response["commands"] = [{"name": "record_paper_checkpoint", "arguments": {"phase": "planning"}}]
    action = next_action()
    assert action["paper_phase"] == "planning"
    apply_agent_commands(response, action)
    assert next_action()["paper_phase"] == "drafting"
    apply_agent_commands(response, action)  # transport replay does not spend a revision
    write_text(version / "paper.md", text)
    response["commands"][0]["arguments"]["phase"] = "drafting"
    apply_agent_commands(response, next_action())
    assert load_state()["current_stage"] == "paper_validation"
    assert next_action()["action"] == "assess_paper_quality"
    assert read_json(version / "drafting_checkpoint.json")["plan_sha256"]


def test_publication_and_cached_render_reject_stale_review_before_outputs(project_root, tmp_path):
    from automm.paper_delivery import publish_paper
    from automm.paper_integrity import verify_rendered_version

    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    for attempt in (
        lambda: verify_rendered_version(version, evidence),
        lambda: publish_paper(version, evidence, {}, version.parent.parent / "final"),
    ):
        with pytest.raises(RuntimeError, match="审阅"):
            attempt()
    assert not (version.parent.parent / "final").exists()


def test_transport_failure_budget_is_per_phase_and_idempotent(project_root, tmp_path):
    from automm import paper_quality as quality
    from automm.workflow import next_action

    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    activate_quality(version, evidence)
    action = next_action()
    for attempt in range(3):
        quality.note_agent_failure(action, f"attempt-{attempt}", "review transport unavailable")
        quality.note_agent_failure(action, f"attempt-{attempt}", "review transport unavailable")
    assert next_action()["action"] == "paper_attention"
    state = read_json(project_root / "problems/paper-demo/problem_state.json")
    assert state["paper"]["writer_revisions"] == 0
    assert state["paper"]["agent_failures"] == 3


def test_readonly_guard_detects_unreported_review_mutation(project_root, tmp_path):
    from automm import paper_quality as quality

    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    activate_quality(version, evidence)
    action = {"agent": "paper-reviewer", "problem_id": evidence["problem_id"], "paper_version": version.name}
    snapshot = quality.protected_snapshot(action)
    write_text(version / "paper.md", "未经授权的审阅者改稿")
    with pytest.raises(RuntimeError, match="只读|修改"):
        quality.verify_protected_snapshot(action, snapshot)


def test_invoke_agent_detects_protected_mutation_even_when_transport_fails(project_root, tmp_path, monkeypatch):
    from automm import agent_runtime
    from automm.failure_policy import AgentTransportError
    from automm.workflow import next_action

    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    activate_quality(version, evidence)
    action = next_action()

    def mutate_then_fail(*args):
        write_text(version / "paper.md", "坏的只读工具意外修改了论文")
        raise AgentTransportError("transport died")

    from types import SimpleNamespace

    monkeypatch.setattr(agent_runtime, "get_provider", lambda _: SimpleNamespace(probe=mutate_then_fail))
    with pytest.raises(RuntimeError, match="只读"):
        agent_runtime.invoke_agent("paper-reviewer", action, "guard-test")


def test_failed_quality_agent_responses_exhaust_without_human_block_or_content_revision(
    project_root, tmp_path, monkeypatch
):
    from automm import runner
    from automm.failure_policy import AgentTransportError
    from automm.state import load_state
    from automm.workflow import next_action

    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    activate_quality(version, evidence)

    def fail(*args):
        raise AgentTransportError("malformed JSON from reviewer")

    monkeypatch.setattr(runner, "invoke_agent", fail)
    for _ in range(3):
        runner.run_once()
    assert next_action()["action"] == "paper_attention"
    assert load_state()["blocking"] == []
    assert read_json(project_root / "problems/paper-demo/problem_state.json")["paper"]["writer_revisions"] == 0


def test_prepare_interruption_reuses_reserved_version_and_frozen_rules(project_root, tmp_path, monkeypatch):
    from automm.common import read_yaml, write_yaml
    from automm.runner import execute_non_agent
    from test_paper_evidence import _eligible_problem

    problem_id, root = _eligible_problem(project_root)
    rules = project_root / "templates/test-rules.json"
    write_json(
        rules,
        {
            "version": "award-writing-v1",
            "rules": [
                {
                    "id": "fixture",
                    "principle": "每问先明确任务，再据证据给出回答。",
                    "applies_to": ["results"],
                    "cautions": ["不可虚构"],
                    "sources": [{"path": "test.pdf", "sha256": "a" * 64, "pages": [1]}],
                }
            ],
        },
    )
    settings = read_yaml(project_root / "config/paper.yaml")
    settings["writing_rules"] = "templates/test-rules.json"
    write_yaml(project_root / "config/paper.yaml", settings)
    real_write = paper.write_json
    failed = False

    def crash(path, value):
        nonlocal failed
        if path.name == "support_dependencies.json" and not failed:
            failed = True
            raise OSError("interrupted preparation")
        return real_write(path, value)

    monkeypatch.setattr(paper, "write_json", crash)
    with pytest.raises(OSError):
        execute_non_agent({"action": "prepare_paper_writing", "problem_id": problem_id})
    result = execute_non_agent({"action": "prepare_paper_writing", "problem_id": problem_id})
    assert result["paper"]["active_version"] == "paper_v001"
    assert len(list((root / "paper/versions").glob("paper_v*"))) == 1


def test_alternative_reference_heading_keeps_selected_citations_numbered(project_root, tmp_path):
    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    plan["citations"][0]["selected"] = True
    text = (version / "paper.md").read_text(encoding="utf-8")
    text = text.replace("## 自适应论述8", "## 理论资料 {#paper-references}")
    text += "\n[@L01] A. Author. A verified method. Journal, 2024.\n"
    write_text(version / "paper.md", text)
    write_json(version / "writing_plan.json", plan)
    assert paper.validate_paper_markdown(evidence["problem_id"], version, evidence)["status"] == "PASS"
    assert read_json(version / "publication_manifest.json")["citations"] == [{"internal_id": "L01", "number": 1}]


def accepted_quality_fixture(project_root, tmp_path):
    from automm.agent_runtime import apply_agent_commands
    from automm.runner import execute_non_agent
    from automm.workflow import next_action

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    activate_quality(version, evidence)
    apply_agent_commands(review_response(evidence, review_fixture(version, evidence, plan)), next_action())
    execute_non_agent(next_action())
    return version, evidence, plan


def test_quality_render_publication_and_delivery_preserve_hash_bound_audits(project_root, tmp_path):
    from automm.paper_delivery import build_support_dependencies, publish_paper
    from automm.paper_integrity import verify_rendered_version
    from test_paper_rendering import _one_page_pdf

    version, evidence, _ = accepted_quality_fixture(project_root, tmp_path)
    write_json(version / "support_dependencies.json", build_support_dependencies(evidence))
    result = paper.render_paper(version, {"minimum_pdf_pages": 1}, pdf_exporter=_one_page_pdf)
    assert result["status"] == "PASS"
    verify_rendered_version(version, evidence)
    final = version.parent.parent / "final"
    published = publish_paper(version, evidence, {}, final)
    assert published["quality_audit"]["paper_review.json"]
    assert (final / "paper_review.json").is_file()
    assert (final / "writing_plan.json").is_file()
    assert not list((final / "交付/支撑材料/图片").iterdir())


def test_review_changed_during_render_is_not_a_pass(project_root, tmp_path):
    from test_paper_rendering import _one_page_pdf

    version, _, _ = accepted_quality_fixture(project_root, tmp_path)

    def exporter(docx, pdf, timeout):
        _one_page_pdf(docx, pdf, timeout)
        write_json(version / "paper_review.json", {"changed": True})

    with pytest.raises(RuntimeError, match="审阅"):
        paper.render_paper(version, {"minimum_pdf_pages": 1}, pdf_exporter=exporter)
    assert read_json(version / "render_report.json")["status"] != "PASS"


def test_unreviewed_direct_runner_validation_does_not_spend_revisions(project_root, tmp_path):
    from automm.runner import execute_non_agent

    version, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    activate_quality(version, evidence, status="content_check")
    write_text(version / "paper.md", "# incomplete draft\n")
    with pytest.raises(RuntimeError, match="审阅"):
        execute_non_agent({"action": "validate_and_render_paper", "problem_id": evidence["problem_id"]})
    assert read_json(project_root / "problems/paper-demo/problem_state.json")["paper"]["status"] == "content_check"


def test_dsh_review_invocation_forces_readonly_even_when_parent_env_requests_full_access(project_root, monkeypatch):
    from automm.llm.dsh import DshHeadlessProvider

    monkeypatch.setenv("DSH_PERMISSION_MODE", "danger-full-access")
    monkeypatch.setattr(DshHeadlessProvider, "_command_prefix", lambda _: ["dsh"])
    provider = DshHeadlessProvider({"read_only": True, "profile": "headless"})
    invocation = provider.prepare("read only review", project_root / "response.json")
    assert invocation.env["DSH_PERMISSION_MODE"] == "read-only"
    assert "--patch" in invocation.command
    patch_path = Path(invocation.command[invocation.command.index("--patch") + 1])
    assert patch_path.is_file()


def test_codex_reviewer_config_cannot_keep_write_approval(project_root, monkeypatch):
    from automm import agent_runtime
    from automm.llm.codex import CodexProvider

    captured = []
    monkeypatch.setattr(CodexProvider, "_executable", lambda _: "codex")

    def provider(config):
        captured.append(config)
        raise RuntimeError("configuration captured")

    monkeypatch.setattr(agent_runtime, "get_provider", provider)
    monkeypatch.setattr(
        agent_runtime,
        "runtime_config",
        lambda: {
            "provider": "codex_exec",
            "sandbox": "workspace-write",
            "automatic_approval": True,
            "output_schema": "config/agent_response.schema.json",
        },
    )
    with pytest.raises(RuntimeError, match="captured"):
        agent_runtime.invoke_agent("paper-reviewer", {"agent": "paper-reviewer"}, "readonly-test")
    invocation = CodexProvider(captured[0]).prepare("review", project_root / "response.json")
    assert "--approve-for-me" not in invocation.command
    assert invocation.command[invocation.command.index("--sandbox") + 1] == "read-only"


def test_quality_reviewer_rejects_changed_uncited_evidence(project_root, tmp_path):
    from automm import paper_quality as quality

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    report = review_fixture(version, evidence, plan)
    unused = next(a for a in evidence['artifacts'] if a['path'].endswith('assumptions.md'))
    write_text(project_root / unused['path'], '被修改的未引述科学假设')
    with pytest.raises(RuntimeError, match='证据|哈希'):
        quality.validate_review(version, evidence, report)


def test_review_payload_rejects_uncontrolled_extra_fields(project_root, tmp_path):
    from automm import paper_quality as quality

    version, evidence, plan = completed_quality_fixture(project_root, tmp_path)
    report = review_fixture(version, evidence, plan)
    report['transition'] = 'completed'
    with pytest.raises(RuntimeError, match='schema|结构'):
        quality.validate_review(version, evidence, report)


def test_adaptive_reference_heading_uses_native_bibliography_style(project_root, tmp_path):
    from automm.paper_semantics import prepare_publication

    _, evidence, _ = completed_quality_fixture(project_root, tmp_path)
    output = prepare_publication('# 本题方法\n\n## 方法来源 {#paper-references}\n\n'
                                 '[@L01] A. Author. A verified method. Journal, 2024.\n', evidence)
    assert any(block['t'] == 'Div' and ['custom-style', '参考文献'] in block['c'][0][2]
               for block in output['pandoc_ast']['blocks'])


@pytest.mark.parametrize('limit', ['3', None, True, 4, -1])
def test_invalid_revision_policy_is_strict_invariant(project_root, tmp_path, limit):
    from automm import paper_quality as quality
    from automm.common import read_yaml, write_yaml
    from automm.failure_policy import HarnessInvariantError

    version, evidence, rules = quality_fixture(project_root, tmp_path)
    settings = read_yaml(project_root / 'config/paper.yaml')
    settings['max_writer_revisions'] = limit
    write_yaml(project_root / 'config/paper.yaml', settings)
    with pytest.raises(HarnessInvariantError):
        quality.prepare_quality_version(version, evidence, rules_path=rules)


def test_malformed_rules_are_rejected_as_harness_invariant(project_root, tmp_path):
    from automm import paper_quality as quality
    from automm.failure_policy import HarnessInvariantError

    version, evidence, rules = quality_fixture(project_root, tmp_path)
    write_json(rules, {'version': 'award-writing-v1', 'rules': ['not a structured rule']})
    with pytest.raises(HarnessInvariantError):
        quality.prepare_quality_version(version, evidence, rules_path=rules)
