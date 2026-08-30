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
