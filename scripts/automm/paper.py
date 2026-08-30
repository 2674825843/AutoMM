"""论文证据闭合、版本管理、写作校验与渲染。"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from .common import ROOT, read_json, read_yaml, relative, utc_now, write_json, write_text
from .problems import load_problem, problem_dir, question_manifest


_TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".csv", ".py"}
_NONFINITE_RE = re.compile(r"(?<![A-Za-z])(?:NaN|[+-]?Inf(?:inity)?)(?![A-Za-z])", re.IGNORECASE)
_EVIDENCE_MARKER_RE = re.compile(r"<!--\s*evidence:([A-Za-z0-9_.:-]+)\s*-->")
_CITATION_RE = re.compile(r"\[@([A-Za-z0-9_.:-]+)\]")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _evidence_id(kind: str, path: str, digest: str) -> str:
    token = hashlib.sha256(f"{kind}:{path}:{digest}".encode()).hexdigest()[:12]
    return f"ev_{kind}_{token}"


def _is_pass(value: Any) -> bool:
    return str(value or "").upper() in {"PASS", "PASS_WITH_WARNING"}


def _citation_id(item: dict[str, Any]) -> str:
    return str(item.get("citation_id") or item.get("id") or "")


def _check_finite_file(path: Path) -> None:
    if path.suffix.lower() not in {".json", ".csv"}:
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if _NONFINITE_RE.search(text):
        raise RuntimeError(f"关键结果包含 NaN/Inf：{relative(path)}")
    if path.suffix.lower() == ".json":
        def reject_constant(value: str) -> None:
            raise ValueError(value)

        try:
            payload = json.loads(text, parse_constant=reject_constant)
        except ValueError as exc:
            raise RuntimeError(f"关键结果包含 NaN/Inf：{relative(path)}") from exc

        def walk(value: Any) -> None:
            if isinstance(value, float) and not math.isfinite(value):
                raise RuntimeError(f"关键结果包含 NaN/Inf：{relative(path)}")
            if isinstance(value, dict):
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(payload)


def _artifact(path: Path, kind: str, question_id: str | None = None) -> dict[str, Any]:
    digest = _sha256(path)
    item: dict[str, Any] = {
        "evidence_id": _evidence_id(kind, relative(path), digest),
        "kind": kind,
        "path": relative(path),
        "sha256": digest,
        "size": path.stat().st_size,
    }
    if question_id:
        item["question_id"] = question_id
    return item


def build_evidence_pack(problem_id: str) -> dict[str, Any]:
    """从已接受且通过门禁的产物构建带哈希的论文证据包。"""
    problem = load_problem(problem_id)
    if problem.get("cross_question_review") != "passed":
        raise RuntimeError("跨小问审查未通过，不能构建论文证据包")
    root = problem_dir(problem_id)
    artifacts: list[dict[str, Any]] = []
    question_entries: list[dict[str, Any]] = []

    for question_id in problem.get("questions", []):
        _, manifest = question_manifest(problem_id, question_id)
        if manifest.get("stage") != "locally_completed" and manifest.get("status") != "locally_completed":
            raise RuntimeError(f"{question_id} 尚未 locally_completed")
        if manifest.get("stale", {}).get("value"):
            raise RuntimeError(f"{question_id} 仍为 stale")
        if not _is_pass(manifest.get("sanity", {}).get("level_1_4")):
            raise RuntimeError(f"{question_id} L1-L4 sanity 未通过")
        if not _is_pass(manifest.get("sanity", {}).get("level_5")):
            raise RuntimeError(f"{question_id} L5 sanity 未通过")
        assumption_number = int(manifest.get("accepted_assumption_version", 0))
        formulation_number = int(manifest.get("accepted_formulation_version", 0))
        if assumption_number < 1 or formulation_number < 1:
            raise RuntimeError(f"{question_id} 缺少接受版本")
        assumption_name = f"assumption_v{assumption_number:03d}"
        formulation_name = f"formulation_v{formulation_number:03d}"
        version_dir = root / question_id / "versions" / assumption_name
        assumption_meta = read_yaml(version_dir / "version.yaml")
        formulation_dir = version_dir / "formulations" / formulation_name
        formulation_meta = read_yaml(formulation_dir / "formulation.yaml")
        if assumption_meta.get("status") != "accepted" or formulation_meta.get("status") != "accepted":
            raise RuntimeError(f"{question_id} 接受版本状态不一致")

        required = [
            version_dir / "version.yaml",
            version_dir / "assumptions.md",
            formulation_dir / "formulation.yaml",
            formulation_dir / "formulation.md",
        ]
        for path in required:
            if not path.is_file():
                raise RuntimeError(f"{question_id} 缺少关键产物：{relative(path)}")
        question_artifacts: list[str] = []
        for path in sorted(version_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            _check_finite_file(path)
            item = _artifact(path, "artifact", question_id)
            artifacts.append(item)
            question_artifacts.append(item["evidence_id"])
        warnings = [
            str(item.get("reason"))
            for item in manifest.get("sanity_history", [])
            if str(item.get("status", "")).upper() == "PASS_WITH_WARNING" and item.get("reason")
        ]
        question_entries.append(
            {
                "question_id": question_id,
                "assumption_version": assumption_name,
                "formulation_version": formulation_name,
                "sanity": manifest.get("sanity", {}),
                "warnings": warnings,
                "optional_stages": manifest.get("optional_stages", {}),
                "conclusion": manifest.get("conclusion", {}),
                "artifact_evidence_ids": question_artifacts,
            }
        )

    figures = read_yaml(root / "figures.yaml", {"figures": []}).get("figures", [])
    selected_figures: list[dict[str, Any]] = []
    for question in question_entries:
        candidates = [
            item
            for item in figures
            if item.get("question_id") == question["question_id"]
            and item.get("assumption_version") == question["assumption_version"]
            and item.get("quality_status") == "passed"
            and item.get("visual_review", {}).get("status") == "passed"
            and item.get("included_in_paper", item.get("included_in_summary", True))
        ]
        if not candidates:
            raise RuntimeError(f"{question['question_id']} 没有审核通过的论文图表")
        for raw in candidates:
            path_value = raw.get("path")
            path = ROOT / str(path_value) if path_value else Path()
            if not path_value or not path.is_file():
                raise RuntimeError(f"论文图表文件不存在：{raw.get('stable_id', '?')}")
            item = dict(raw)
            digest = _sha256(path)
            item["sha256"] = digest
            item["evidence_id"] = _evidence_id("figure", relative(path), digest)
            selected_figures.append(item)

    references = read_yaml(root / "citations.yaml", {"references": []}).get("references", [])
    selected_citations: list[dict[str, Any]] = []
    for raw in references:
        citation_id = _citation_id(raw)
        if raw.get("usage_status") != "used":
            continue
        if not citation_id or not all(raw.get(key) for key in ("title", "year", "source")):
            raise RuntimeError(f"引用字段不完整：{citation_id or '?'}")
        item = dict(raw)
        item["citation_id"] = citation_id
        item["evidence_id"] = _evidence_id("citation", citation_id, hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode()).hexdigest())
        selected_citations.append(item)
    if not selected_citations:
        raise RuntimeError("引用登记中没有 usage_status=used 的完整引用")

    shared_paths = [ROOT / "request" / "problem.md", root / "problem_understanding.md", root / "global_symbols.yaml"]
    for path in shared_paths:
        if path.is_file():
            artifacts.append(_artifact(path, "shared"))

    evidence = {
        "schema_version": 1,
        "problem_id": problem_id,
        "created_at": utc_now(),
        "cross_question_review": {
            "status": problem.get("cross_question_review"),
            "reason": problem.get("cross_question_review_reason", ""),
        },
        "questions": question_entries,
        "artifacts": artifacts,
        "figures": selected_figures,
        "citations": selected_citations,
    }
    canonical = json.dumps(evidence, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    evidence["evidence_hash"] = hashlib.sha256(canonical).hexdigest()
    evidence_dir = root / "paper" / "evidence"
    write_json(evidence_dir / "evidence_pack.json", evidence)
    lines = [f"# {problem_id} 论文证据包", "", f"- Evidence hash：`{evidence['evidence_hash']}`", ""]
    for question in question_entries:
        lines.extend(
            [
                f"## {question['question_id']}",
                "",
                f"- 假设版本：`{question['assumption_version']}`",
                f"- 公式版本：`{question['formulation_version']}`",
                f"- sanity：`{question['sanity']}`",
                f"- 警告：{question['warnings'] or '无'}",
                "",
            ]
        )
    lines.extend(["## 图表", ""] + [f"- `{item['stable_id']}`：{item.get('title', '')}" for item in selected_figures])
    lines.extend(["", "## 引用", ""] + [f"- `[@{item['citation_id']}]`：{item['title']}" for item in selected_citations])
    write_text(evidence_dir / "evidence_pack.md", "\n".join(lines) + "\n")
    return evidence


def create_paper_version(problem_id: str) -> tuple[str, Path]:
    """原子式占用下一个论文版本目录；已有版本永不覆盖。"""
    versions = problem_dir(problem_id) / "paper" / "versions"
    versions.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in versions.glob("paper_v[0-9][0-9][0-9]"):
        try:
            existing.append(int(path.name.removeprefix("paper_v")))
        except ValueError:
            continue
    number = max(existing, default=0) + 1
    while True:
        name = f"paper_v{number:03d}"
        path = versions / name
        try:
            path.mkdir(parents=False, exist_ok=False)
            return name, path
        except FileExistsError:
            number += 1


def validate_paper_markdown(
    problem_id: str, version_dir: Path, evidence: dict[str, Any]
) -> dict[str, Any]:
    """确定性检查论文的结构、事实来源、引用、图表与警告披露。"""
    draft_path = version_dir / "paper.md"
    if not draft_path.is_file():
        raise RuntimeError(f"论文 Markdown 不存在：{draft_path}")
    text = draft_path.read_text(encoding="utf-8")
    errors: list[str] = []
    required_headings = [
        "摘要",
        "关键词",
        "问题重述",
        "问题分析与总体流程",
        "模型假设",
        "符号说明",
        "数据说明与预处理",
        "跨小问一致性、稳健性与消融分析",
        "模型评价、局限与推广",
        "结论",
        "参考文献",
        "附录：复现说明、文件清单和核心代码索引",
    ]
    headings = [match.group(1).strip() for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)]
    for required in required_headings:
        if not any(heading == required for heading in headings):
            errors.append(f"缺少章节：{required}")
    for question in evidence.get("questions", []):
        question_id = str(question.get("question_id", ""))
        if not any(heading.startswith(f"{question_id} ") for heading in headings):
            errors.append(f"缺少小问章节：{question_id}")
        if f"{question_id} 可靠性与结论" not in text:
            errors.append(f"{question_id} 缺少可靠性与结论")
        for warning in question.get("warnings", []):
            if str(warning).strip() and str(warning).strip() not in text:
                errors.append(f"未披露警告：{question_id} / {warning}")

    placeholder_patterns = [
        r"(?<![A-Za-z])TODO(?![A-Za-z])",
        r"(?<![A-Za-z])TBD(?![A-Za-z])",
        r"待填写",
        r"待补充",
        r"\{\{.+?\}\}",
    ]
    if any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in placeholder_patterns):
        errors.append("正文包含占位符")

    known_evidence = {
        str(item.get("evidence_id"))
        for group in ("artifacts", "figures", "citations")
        for item in evidence.get(group, [])
        if item.get("evidence_id")
    }
    used_evidence = set(_EVIDENCE_MARKER_RE.findall(text))
    for evidence_id in sorted(used_evidence - known_evidence):
        errors.append(f"未知 evidence ID：{evidence_id}")
    if not used_evidence:
        errors.append("正文没有 evidence 标记")

    known_citations = {str(item.get("citation_id")) for item in evidence.get("citations", [])}
    used_citations = set(_CITATION_RE.findall(text))
    for citation_id in sorted(used_citations - known_citations):
        errors.append(f"未登记引用：{citation_id}")
    for citation_id in sorted(known_citations - used_citations):
        errors.append(f"登记引用未在正文使用：{citation_id}")

    prose_lines = [line for line in text.splitlines() if not line.lstrip().startswith("![")]
    prose = "\n".join(prose_lines)
    for figure in evidence.get("figures", []):
        stable_id = str(figure.get("stable_id", ""))
        question_id = str(figure.get("question_id", ""))
        if not stable_id or stable_id not in text:
            errors.append(f"缺少审核图表：{stable_id or '?'}")
            continue
        if stable_id not in prose:
            errors.append(f"图表缺少正文解释：{stable_id}")
        if question_id and not re.search(
            rf"图\s*{re.escape(stable_id)}[^\n]*(?:展示|表明|说明|验证|支持|低于|高于)",
            prose,
        ):
            errors.append(f"图表缺少正文解释：{stable_id}")

    result = {
        "checked_at": utc_now(),
        "problem_id": problem_id,
        "paper_version": version_dir.name,
        "evidence_hash": evidence.get("evidence_hash"),
        "status": "PASS" if not errors else "NEEDS_REVISION",
        "errors": errors,
        "evidence_ids_used": sorted(used_evidence),
        "citation_ids_used": sorted(used_citations),
        "figure_ids_used": sorted(
            str(item.get("stable_id")) for item in evidence.get("figures", []) if item.get("stable_id") in text
        ),
    }
    write_json(version_dir / "validation.json", result)
    return result
