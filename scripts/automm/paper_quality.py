"""未来论文的质量契约、语义计划和哈希绑定审阅；不修改科学门禁。"""

from __future__ import annotations

import re
from pathlib import Path

import jsonschema

from .common import ROOT, hash_json, read_json, read_yaml, write_json, write_text
from .failure_policy import HarnessInvariantError
from .paper_integrity import digest, evidence_digest

GLOBAL_ROLES = (
    "abstract",
    "problem",
    "analysis",
    "assumptions",
    "symbols",
    "data",
    "limitations",
    "conclusions",
    "references",
    "reproduction",
)
QUESTION_ROLES = ("model", "solution", "results", "reliability")


def _rules(path: Path) -> dict:
    try:
        rules = read_json(path)
    except (ValueError, OSError) as exc:
        raise HarnessInvariantError('写作规则 JSON 无法读取') from exc
    if (not isinstance(rules, dict) or rules.get("version") != "award-writing-v1"
            or not isinstance(rules.get('rules'), list) or not rules['rules']):
        raise HarnessInvariantError("写作规则库缺失或版本不支持")
    ids = set()
    for rule in rules["rules"]:
        if (
            not isinstance(rule, dict)
            or not isinstance(rule.get('id'), str)
            or not rule.get("id")
            or rule["id"] in ids
            or not isinstance(rule.get('principle'), str) or not rule.get("principle")
            or not isinstance(rule.get('applies_to'), list) or not rule.get("applies_to")
            or not all(isinstance(x, str) and x for x in rule['applies_to'])
            or not isinstance(rule.get("cautions"), (str, list))
            or not isinstance(rule.get('sources'), list) or not rule.get("sources")
        ):
            raise HarnessInvariantError("写作规则字段不完整或 ID 重复")
        ids.add(rule["id"])
        for source in rule["sources"]:
            if (
                not isinstance(source, dict) or not isinstance(source.get('path'), str) or not source.get("path")
                or not isinstance(source.get('sha256'), str)
                or not re.fullmatch(r"[0-9a-f]{64}", source['sha256'])
                or not isinstance(source.get('pages'), list) or not source.get("pages")
                or any(type(p) is not int or p < 1 for p in source["pages"])
            ):
                raise HarnessInvariantError("写作规则出处缺少合法路径、SHA-256 或页码")
    return rules


def quality_contract(version_dir: Path, evidence: dict) -> dict | None:
    writer = read_json(version_dir / "writer_manifest.json")
    contract = writer.get("quality_contract")
    problem = read_json(ROOT / "problems" / evidence.get("problem_id", "") / "problem_state.json")
    active = problem.get("paper", {})
    expected = problem.get("paper_quality_contracts", {}).get(version_dir.name)
    if active.get("active_version") == version_dir.name:
        expected = active.get("quality_contract") or expected
    quality_files = any(
        (version_dir / name).exists() for name in ("writing_plan.json", "writing_rules.json", "paper_review.json")
    )
    if not contract and (expected or quality_files):
        raise HarnessInvariantError("预期质量契约被删除，不允许降级为旧版")
    if expected and expected != contract:
        raise HarnessInvariantError("写作质量契约与持久化预期不匹配")
    if contract and (
        contract.get("schema_version") != 1
        or contract.get("version") != "award-writing-v1"
        or type(contract.get("max_writer_revisions")) is not int
        or not 0 <= contract["max_writer_revisions"] <= 3
        or type(contract.get('writer_revisions')) is not int
        or not 0 <= contract['writer_revisions'] <= contract['max_writer_revisions']
    ):
        raise HarnessInvariantError("写作质量契约无效")
    if contract and (
        not (version_dir / "writing_rules.json").is_file()
        or digest(version_dir / "writing_rules.json") != contract.get("rules_sha256")
    ):
        raise HarnessInvariantError("冻结写作规则哈希不匹配")
    return contract


def prepare_quality_version(
    version_dir: Path, evidence: dict, *, rules_path: Path | None = None, previous: dict | None = None
) -> dict:
    """只为新目录生成诚实的未完成提纲，规则来源不进入科学参考文献。"""
    previous = previous or {}
    settings = read_yaml(ROOT / "config/paper.yaml", {})
    old_contract = previous.get("quality_contract")
    reservation = read_json(version_dir / "preparation.json")
    old_version = version_dir.parent / str(previous.get("active_version", ""))
    path = old_version / "writing_rules.json" if old_contract else rules_path or ROOT / settings["writing_rules"]
    if reservation and (version_dir / "writing_rules.json").exists():
        path = version_dir / "writing_rules.json"
    if old_contract:
        if quality_contract(old_version, evidence) != old_contract:
            raise HarnessInvariantError("修订来源质量契约不匹配")
    pack = _rules(path)
    limit = (
        old_contract["max_writer_revisions"]
        if old_contract
        else reservation.get("max_writer_revisions", settings.get("max_writer_revisions", 3))
    )
    if type(limit) is not int or not 0 <= limit <= 3:
        raise HarnessInvariantError("写作内容修订上限必须为 0..3")
    if old_contract and previous.get('writer_revisions') != old_contract['writer_revisions']:
        raise HarnessInvariantError('修订计数与持久化契约不匹配')
    count = old_contract['writer_revisions'] + 1 if old_contract else 0
    if count > limit:
        raise HarnessInvariantError("已达到论文修订上限，禁止创建第四轮")
    if (version_dir / "writer_manifest.json").exists() or (
        not reservation and any((version_dir / name).exists() for name in ("writing_plan.json", "paper.md"))
    ):
        raise HarnessInvariantError("不得覆盖已有论文质量版本")
    write_json(version_dir / "writing_rules.json", pack)
    contract = {
        "schema_version": 1,
        "version": pack["version"],
        "rules_sha256": digest(version_dir / "writing_rules.json"),
        "max_writer_revisions": limit,
        "writer_revisions": count,
        "parent_version": previous.get("active_version"),
    }
    from .paper import _warning_id

    plan = {
        "schema_version": 1,
        "evidence_hash": evidence["evidence_hash"],
        "rules_sha256": contract["rules_sha256"],
        "roles": [{"role": role, "anchor": "", "excerpt": "", "evidence_ids": []} for role in GLOBAL_ROLES],
        "questions": [
            {"question_id": q["question_id"], "answer": "", "claims": []} for q in evidence.get("questions", [])
        ],
        "figures": [{"id": f["stable_id"], "selected": None, "reason": ""} for f in evidence.get("figures", [])],
        "citations": [{"id": c["citation_id"], "selected": None, "reason": ""} for c in evidence.get("citations", [])],
        "warnings": [
            {
                "id": _warning_id(q["question_id"], str(w).strip()),
                "question_id": q["question_id"],
                "text": str(w),
                "anchor": "",
                "excerpt": "",
                "evidence_ids": [],
            }
            for q in evidence.get("questions", [])
            for w in q.get("warnings", [])
        ],
    }
    for question in plan["questions"]:
        plan["roles"].extend(
            {"role": role, "question_id": question["question_id"], "anchor": "", "excerpt": "", "evidence_ids": []}
            for role in QUESTION_ROLES
        )
    if old_contract:
        plan = read_json(old_version / "writing_plan.json")
    write_json(version_dir / "writing_plan.json", plan)
    write_json(version_dir / "evidence_pack.json", evidence)
    writer = {
        "schema_version": 1,
        "paper_version": version_dir.name,
        "problem_id": evidence["problem_id"],
        "evidence_hash": evidence["evidence_hash"],
        "generator": "quality-planning-scaffold",
        "quality_contract": contract,
    }
    text = (
        (old_version / "paper.md").read_text(encoding="utf-8")
        if old_contract
        else (
            "# 待填写：基于本题任务与方法的论文标题\n\n"
            "<!-- 未完成的写作材料：先阅读证据并完成 writing_plan.json，再撰写正文。 -->\n"
        )
    )
    write_text(version_dir / "paper.md", text)
    write_json(version_dir / "writer_manifest.json", writer)
    return {"quality_contract": contract, "writer_revisions": count, "status": "planning"}


def validate_plan(version_dir: Path, evidence: dict, *, require_draft: bool = True) -> dict:
    contract = quality_contract(version_dir, evidence)
    plan = read_json(version_dir / "writing_plan.json")
    errors = []
    if (
        plan.get("schema_version") != 1
        or plan.get("evidence_hash") != evidence_digest(evidence)
        or plan.get("rules_sha256") != (contract or {}).get("rules_sha256")
    ):
        errors.append("写作计划证据哈希不匹配")
    text = (version_dir / "paper.md").read_text(encoding="utf-8") if require_draft else ""
    anchors = paragraph_anchors(text)
    known_ev = {a["evidence_id"] for group in ("artifacts", "figures", "citations") for a in evidence.get(group, [])}

    def location(item: dict, label: str) -> None:
        ids = item.get("evidence_ids", [])
        if not ids or not set(ids) <= known_ev:
            errors.append(f"{label} 缺少已登记的证据")
        if require_draft and not valid_location(item, anchors):
            errors.append(f"{label} 缺少真实段落锚点/摘录，不接受空标记")

    expected_questions = {q["question_id"] for q in evidence.get("questions", [])}
    questions = plan.get("questions", [])
    if {q.get("question_id") for q in questions} != expected_questions or len(questions) != len(expected_questions):
        errors.append("小问覆盖不完整或重复")
    claim_ids = set()
    for question in plan.get("questions", []):
        if not substantive(question.get("answer")) or not question.get("claims"):
            errors.append(f"小问回答或主张未完成：{question.get('question_id')}")
        for claim in question.get("claims", []):
            if not claim.get("id") or claim["id"] in claim_ids or not substantive(claim.get("text")):
                errors.append("主张缺少实质内容或唯一 ID")
            claim_ids.add(claim.get("id"))
            location(claim, f"主张 {claim.get('id')}")
    required = {(r, None) for r in GLOBAL_ROLES if r != "reproduction"}
    if (version_dir / "support_dependencies.json").exists() or any(
        a.get("path", "").endswith(".py") for a in evidence.get("artifacts", [])
    ):
        required.add(("reproduction", None))
    required.update((r, q) for q in expected_questions for r in QUESTION_ROLES)
    roles = {(r.get("role"), r.get("question_id")) for r in plan.get("roles", [])}
    for missing in sorted(required - roles, key=str):
        errors.append(f"缺少必需语义角色：{missing}")
    for role in plan.get("roles", []):
        location(role, f"语义角色 {role.get('role')}")
    from .paper import _warning_id

    warnings = {
        _warning_id(q["question_id"], str(w).strip()): (q["question_id"], str(w))
        for q in evidence.get("questions", [])
        for w in q.get("warnings", [])
    }
    provided = plan.get("warnings", [])
    if {w.get("id") for w in provided} != set(warnings) or len(provided) != len(warnings):
        errors.append("警告/反例披露覆盖不完整或重复")
    for warning in provided:
        if warnings.get(warning.get("id")) != (warning.get("question_id"), warning.get("text")):
            errors.append("警告来源或原文不匹配")
        location(warning, "警告披露")
    for group, id_key in (("figures", "stable_id"), ("citations", "citation_id")):
        expected = {x[id_key]: x for x in evidence.get(group, [])}
        decisions = plan.get(group, [])
        if {x.get("id") for x in decisions} != set(expected) or len(decisions) != len(expected):
            errors.append(f"{group} 材料取舍必须逐项审计")
        for item in decisions:
            if type(item.get("selected")) is not bool or not substantive(item.get("reason")):
                errors.append(f"{group} 取舍缺少决定或理由：{item.get('id')}")
        if require_draft:
            selected = {x["id"] for x in decisions if x.get("selected") is True}
            if group == "citations":
                used = set(re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", text))
                used = {x for x in used if not x.startswith(("fig:", "tbl:"))}
            else:
                paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
                used = {k for k, v in expected.items() if v["path"] in paths}
                if set(paths) - {v["path"] for v in expected.values()}:
                    errors.append("使用未登记图片路径")
                for figure_id in selected:
                    if f"@fig:{figure_id}" not in text:
                        errors.append(f"选用图片缺少正文引用：{figure_id}")
            if used != selected:
                errors.append(f"{group} 正文使用与材料取舍不一致/存在未知引用")
    if require_draft:
        unknown = set(re.findall(r"<!--\s*evidence:([\w.:-]+)\s*-->", text)) - known_ev
        if unknown:
            errors.append("正文出现未知证据标记")
        from .paper_semantics import public_text_issues

        visible = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        visible = re.sub(r"@(?:fig|tbl):[\w.:-]+", "", visible)
        errors.extend(public_text_issues(visible))
    return {"status": "NEEDS_REVISION" if errors else "PASS", "errors": errors}


def substantive(text) -> bool:
    return isinstance(text, str) and len(re.sub(r"\W", "", re.sub(r"<!--.*?-->", "", text, flags=re.S))) >= 8


def paragraph_anchors(text: str) -> dict[str, str]:
    """显式源码锚点仅定位其后真实段落，不把标记本身当内容。"""
    found = {}
    for match in re.finditer(r"<!--\s*paper:([A-Za-z0-9_.:-]+)\s*-->|\{#([A-Za-z0-9_.:-]+)\}", text):
        anchor = match.group(1) or match.group(2)
        if anchor in found:
            found[anchor] = ""
            continue
        body = text[match.end() :].lstrip()
        body = re.split(r"\n\s*\n|\n(?=#{1,6}\s)|<!--\s*paper:", body, maxsplit=1)[0]
        found[anchor] = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()
    return found


def valid_location(item: dict, anchors: dict) -> bool:
    excerpt = item.get("excerpt", "")
    return substantive(excerpt) and excerpt in anchors.get(item.get("anchor"), "")


def review_bindings(version_dir: Path, evidence: dict) -> dict:
    contract = quality_contract(version_dir, evidence)
    if not contract:
        raise HarnessInvariantError("版本没有质量审阅契约")
    if evidence_digest(evidence) != evidence.get("evidence_hash"):
        raise HarnessInvariantError("审阅证据内容哈希不匹配")
    for group in ('artifacts', 'figures'):
        for item in evidence.get(group, []):
            path = (ROOT / item.get('path', '')).resolve()
            if (not path.is_relative_to(ROOT.resolve()) or not path.is_file()
                    or digest(path) != item.get('sha256')):
                raise HarnessInvariantError('审阅证据文件与冻结来源哈希不匹配')
    return {
        "paper_version": version_dir.name,
        "draft_sha256": digest(version_dir / "paper.md"),
        "plan_sha256": digest(version_dir / "writing_plan.json"),
        "evidence_hash": evidence["evidence_hash"],
        "rules_sha256": contract["rules_sha256"],
        "contract_sha256": hash_json(contract),
    }


def validate_review(version_dir: Path, evidence: dict, report: dict) -> dict:
    """核实审阅确实定位文本和原始证据；真假/充分性仍由独立语义审阅判断。"""
    schema = read_json(ROOT / 'config/agent_response.schema.json')
    try:
        jsonschema.Draft202012Validator({'$ref': '#/$defs/paperReview', '$defs': schema['$defs']}).validate(report)
    except (KeyError, jsonschema.ValidationError) as exc:
        raise HarnessInvariantError(f'论文审阅 schema 结构无效：{exc}') from exc
    bindings = review_bindings(version_dir, evidence)
    if report.get("schema_version") != 1 or any(report.get(k) != v for k, v in bindings.items()):
        raise HarnessInvariantError("审阅报告哈希绑定缺失或过期")
    plan = read_json(version_dir / "writing_plan.json")
    if validate_plan(version_dir, evidence)["status"] != "PASS":
        raise HarnessInvariantError("审阅对应的草稿没有通过确定性语义计划门禁")
    anchors = paragraph_anchors((version_dir / "paper.md").read_text(encoding="utf-8"))
    known = {a["evidence_id"]: a for g in ("artifacts", "figures", "citations") for a in evidence.get(g, [])}
    checks = {
        "questions": {q["question_id"] for q in plan["questions"]},
        "claims": {c["id"] for q in plan["questions"] for c in q["claims"]},
        "warnings": {w["id"] for w in plan["warnings"]},
    }
    revision_assessments = []
    for group, expected in checks.items():
        rows = report.get(group, [])
        if not isinstance(rows, list) or {r.get("id") for r in rows} != expected or len(rows) != len(expected):
            raise HarnessInvariantError(f"审阅 {group} 逐项覆盖不完整")
        for row in rows:
            if (
                row.get("status") not in {"adequate", "needs_revision"}
                or not substantive(row.get("reason"))
                or not valid_location(row, anchors)
                or not row.get("evidence_ids")
                or not set(row["evidence_ids"]) <= set(known)
            ):
                raise HarnessInvariantError(f"审阅 {group} 缺少实质评估、真实位置或证据")
            if row["status"] == "needs_revision":
                revision_assessments.append(row["id"])
    reads = report.get("evidence_reads", [])
    read_ids = [r.get("evidence_id") for r in reads]
    rows = [*plan["roles"], *plan["warnings"], *(c for q in plan["questions"] for c in q["claims"])]
    required_reads = {v for row in rows for v in row["evidence_ids"]}
    required_reads.update(v for group in checks for row in report[group] for v in row["evidence_ids"])
    if not required_reads <= set(read_ids) or len(read_ids) != len(set(read_ids)):
        raise HarnessInvariantError("审阅未检查所有主张/警告/角色引用的实际证据")
    for read in reads:
        item = known.get(read.get("evidence_id"))
        if item is None or not substantive(read.get("excerpt")):
            raise HarnessInvariantError("审阅原始证据摘录为空或来源未知")
        if "path" in item:
            path = (ROOT / item["path"]).resolve()
            if not path.is_relative_to(ROOT.resolve()) or not path.is_file() or digest(path) != item.get("sha256"):
                raise HarnessInvariantError("审阅实际证据来源哈希不匹配")
            expected_hash = item["sha256"]
            if item in evidence.get("artifacts", []) and read["excerpt"] not in path.read_text(encoding="utf-8"):
                raise HarnessInvariantError("审阅摘录不存在于被引用的原始证据")
        else:
            expected_hash = hash_json(item)
            if read["excerpt"] not in str(item):
                raise HarnessInvariantError("审阅文献摘录与登记内容不匹配")
        if read.get("sha256") != expected_hash:
            raise HarnessInvariantError("审阅原始证据 SHA-256 不匹配")
    findings = report.get("findings")
    if not isinstance(findings, list):
        raise HarnessInvariantError("审阅缺少 findings 数组")
    for finding in findings:
        if (
            finding.get("severity") not in {"blocking", "advisory"}
            or not valid_location(finding, anchors)
            or not substantive(finding.get("reason"))
            or not substantive(finding.get("instruction"))
            or not finding.get("evidence_ids")
            or not set(finding["evidence_ids"]) <= set(read_ids)
        ):
            raise HarnessInvariantError("审阅发现必须包含级别、真实位置、证据理由和具体修改指令")
    if revision_assessments and not any(f.get("severity") == "blocking" for f in findings):
        raise HarnessInvariantError("覆盖评估未通过但缺少阻断性发现")
    return report


def check_review(version_dir: Path, evidence: dict, *, require_accepted: bool = True) -> dict:
    if not quality_contract(version_dir, evidence):
        return {}
    path = version_dir / "paper_review.json"
    if not path.is_file():
        raise HarnessInvariantError("缺少独立论文审阅报告")
    report = validate_review(version_dir, evidence, read_json(path))
    problem = read_json(ROOT / "problems" / evidence["problem_id"] / "problem_state.json")
    paper = problem.get("paper", {})
    if paper.get("active_version") == version_dir.name and paper.get("review_sha256") != digest(path):
        raise HarnessInvariantError("审阅报告与受控事务登记的哈希不匹配")
    if require_accepted:
        accepted = read_json(version_dir / "quality_acceptance.json")
        expected = {**review_bindings(version_dir, evidence), "review_sha256": digest(path)}
        if accepted.get("status") not in {"PASS", "PASS_WITH_WARNING"} or any(
            accepted.get(k) != v for k, v in expected.items()
        ):
            raise HarnessInvariantError("独立审阅未验收或验收哈希过期")
        if any(f["severity"] == "blocking" for f in report["findings"]):
            raise HarnessInvariantError("阻断性审阅不能发布")
        if paper.get("active_version") == version_dir.name and paper.get("quality_acceptance_sha256") != digest(
            version_dir / "quality_acceptance.json"
        ):
            raise HarnessInvariantError("质量验收与持久化回执不匹配")
    return report


def quality_audit_hashes(version_dir: Path, evidence: dict) -> dict:
    if not quality_contract(version_dir, evidence):
        return {}
    return {
        name: digest(version_dir / name)
        for name in (
            "writing_plan.json",
            "writing_rules.json",
            "paper_review.json",
            "quality_acceptance.json",
            "writer_manifest.json",
        )
    }


def publication_evidence(version_dir: Path, evidence: dict) -> dict:
    """原始证据快照不变，只向排版层投影正文选用的图表和文献。"""
    if not quality_contract(version_dir, evidence):
        return evidence
    plan = read_json(version_dir / 'writing_plan.json')
    selected = dict(evidence)
    for group, key in (('figures', 'stable_id'), ('citations', 'citation_id')):
        ids = {x['id'] for x in plan.get(group, []) if x.get('selected') is True}
        selected[group] = [x for x in evidence.get(group, []) if x[key] in ids]
    return selected


def record_paper_review(problem_id: str, report: dict) -> dict:
    from .problems import load_problem, problem_dir

    problem = load_problem(problem_id)
    paper = problem["paper"]
    version = problem_dir(problem_id) / "paper/versions" / paper["active_version"]
    from .paper_integrity import load_version_evidence

    evidence = load_version_evidence(version, paper["evidence_hash"])
    validate_review(version, evidence, report)
    path = version / "paper_review.json"
    if path.exists() and read_json(path) != report:
        raise HarnessInvariantError("不能覆盖既有独立审阅历史")
    if paper.get("status") not in {"reviewing", "reviewed"}:
        raise HarnessInvariantError("当前论文不在独立审阅阶段")
    write_json(path, report)
    paper.update(status="reviewed", review_sha256=digest(path), agent_failures=0)
    write_json(problem_dir(problem_id) / "problem_state.json", problem)
    return {"recorded": True, "review_sha256": paper["review_sha256"]}


def record_paper_checkpoint(problem_id: str, phase: str) -> dict:
    from .paper_integrity import load_version_evidence
    from .problems import load_problem, problem_dir
    from .workflow import transition

    problem = load_problem(problem_id)
    paper = problem["paper"]
    version = problem_dir(problem_id) / "paper/versions" / paper["active_version"]
    evidence = load_version_evidence(version, paper["evidence_hash"])
    if phase not in {"planning", "drafting"}:
        raise HarnessInvariantError("未知论文写作检查点")
    bindings = review_bindings(version, evidence)
    path = version / f"{phase}_checkpoint.json"
    if path.exists():
        previous = read_json(path)
        if all(previous.get(k) == v for k, v in bindings.items()):
            return {"recorded": True, "replayed": True}
        raise HarnessInvariantError("检查点哈希已变化，禁止覆盖完成历史")
    if paper.get("status") != phase:
        raise HarnessInvariantError("论文写作检查点与当前阶段不匹配")
    if phase == "planning":
        validation = validate_plan(version, evidence, require_draft=False)
        if validation["status"] != "PASS":
            raise HarnessInvariantError("写作计划未完成：" + "；".join(validation["errors"]))
    write_json(path, {"phase": phase, **bindings})
    paper.update(status="drafting" if phase == "planning" else "content_check", agent_failures=0)
    write_json(problem_dir(problem_id) / "problem_state.json", problem)
    if phase == "drafting":
        transition(
            target_stage="paper_validation", problem_id=problem_id, reason="论文草稿检查点完成，进入内容与独立审阅"
        )
    return {"recorded": True, "phase": phase}


def assess_paper_quality(problem_id: str) -> dict:
    """确定性门禁和语义发现分开处理；到期只停止论文，不回退科学验收。"""
    from .paper import validate_paper_markdown
    from .paper_integrity import load_version_evidence
    from .problems import load_problem, problem_dir
    from .workflow import transition

    problem = load_problem(problem_id)
    paper = problem["paper"]
    version = problem_dir(problem_id) / "paper/versions" / paper["active_version"]
    evidence = load_version_evidence(version, paper["evidence_hash"])
    contract = quality_contract(version, evidence)
    if not contract:
        raise HarnessInvariantError("质量评审只处理带契约的版本")
    if paper.get("status") in {"attention", "validating", "needs_revision"}:
        return {"paper": paper}
    validation = validate_paper_markdown(problem_id, version, evidence)
    blocking = validation["errors"]
    advisory = []
    if not blocking and paper.get("status") == "content_check":
        paper.update(status="reviewing", review_bindings=review_bindings(version, evidence))
        write_json(problem_dir(problem_id) / "problem_state.json", problem)
        return {"paper": paper, "validation": validation}
    if not blocking:
        report = check_review(version, evidence, require_accepted=False)
        if digest(version / "paper_review.json") != paper.get("review_sha256"):
            raise HarnessInvariantError("审阅报告与受控登记哈希不匹配")
        blocking = [f for f in report["findings"] if f["severity"] == "blocking"]
        advisory = [f for f in report["findings"] if f["severity"] == "advisory"]
    count = paper.get("writer_revisions", 0)
    if count != contract["writer_revisions"]:
        raise HarnessInvariantError("论文修订计数与冻结契约不匹配")
    paper["revision_requests"] = [*blocking, *advisory]
    if (blocking or advisory) and count < contract["max_writer_revisions"]:
        paper["status"] = "needs_revision"
    elif blocking:
        paper.update(status="attention", attention_reason="阻断性内容问题已达到论文修订上限")
    else:
        accepted = {
            **review_bindings(version, evidence),
            "review_sha256": digest(version / "paper_review.json"),
            "status": "PASS_WITH_WARNING" if advisory else "PASS",
            "warnings": advisory,
        }
        write_json(version / "quality_acceptance.json", accepted)
        paper.update(
            status="validating",
            quality_status=accepted["status"],
            quality_acceptance_sha256=digest(version / "quality_acceptance.json"),
        )
    write_json(problem_dir(problem_id) / "problem_state.json", problem)
    if paper["status"] == "needs_revision":
        transition(target_stage="paper_writing", problem_id=problem_id, reason="论文内容修订；科学验收保持不变")
    return {"paper": paper, "validation": validation}


def note_agent_failure(action: dict, action_id: str, error: str) -> None:
    """一次运输尝试仅记一次，预算耗尽停止调度，不消耗内容修订轮数。"""
    from .problems import load_problem, problem_dir

    if not action.get("problem_id") or action.get("agent") not in {"paper-writer", "paper-reviewer"}:
        return
    problem = load_problem(action["problem_id"])
    paper = problem.get("paper", {})
    if not paper.get("quality_contract"):
        return
    seen = paper.setdefault("failed_agent_actions", [])
    if action_id in seen:
        return
    seen.append(action_id)
    paper["agent_failures"] = int(paper.get("agent_failures", 0)) + 1
    paper["last_agent_error"] = error
    if paper["agent_failures"] >= 3:
        paper.update(status="attention", attention_reason="当前论文阶段连续三次 Agent 失败，保留检查点待关注")
    write_json(problem_dir(action["problem_id"]) / "problem_state.json", problem)


def protected_snapshot(action: dict) -> dict[str, str]:
    """写作仅开放两份工作文件；审阅不开放任何项目文件写权限。"""
    if action.get("agent") not in {"paper-writer", "paper-reviewer"} or not action.get("problem_id"):
        return {}
    from .problems import problem_dir

    root = problem_dir(action["problem_id"])
    paper = read_json(root / "problem_state.json").get("paper", {})
    if not paper.get("quality_contract"):
        return {}
    version = root / "paper/versions" / paper["active_version"]
    excluded = set()
    if action["agent"] == "paper-writer":
        excluded = {version / "paper.md", version / "writing_plan.json"}
    paths = [
        p
        for directory in (
            root,
            ROOT / "config",
            ROOT / "request",
            ROOT / "scripts",
            ROOT / "templates",
            ROOT / "agents",
        )
        for p in directory.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    ]
    paths.extend(
        p
        for p in (
            ROOT / "runtime/workflow_state.json",
            ROOT / "AGENTS.md",
            ROOT / "PROJECT.md",
            ROOT / "RESEARCH_LOOP.md",
        )
        if p.is_file()
    )
    return {str(p): digest(p) for p in paths if p not in excluded}


def verify_protected_snapshot(action: dict, snapshot: dict) -> None:
    if snapshot and protected_snapshot(action) != snapshot:
        raise HarnessInvariantError("论文只读保护文件被 Agent 修改、删除或新增")
