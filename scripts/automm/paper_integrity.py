"""论文版本的内容寻址和已验收产物校验；不读取可变共享证据。"""
from __future__ import annotations

import hashlib
from pathlib import Path

from .common import hash_json, read_json
from .paper_semantics import audit_public_docx


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_digest(evidence: dict) -> str:
    return hash_json({k: v for k, v in evidence.items() if k not in {'created_at', 'evidence_hash'}})


def load_version_evidence(version_dir: Path, expected_hash: str | None = None) -> dict:
    evidence = read_json(version_dir / 'evidence_pack.json')
    actual = evidence_digest(evidence)
    if not evidence or evidence.get('evidence_hash') != actual:
        raise RuntimeError('版本证据快照内容哈希不匹配或缺失')
    if expected_hash is not None and expected_hash != actual:
        raise RuntimeError('活动论文与版本证据快照哈希不匹配')
    writer = read_json(version_dir / 'writer_manifest.json')
    if writer.get('evidence_hash') != actual:
        raise RuntimeError('writer_manifest 与版本证据快照哈希不匹配')
    return evidence


def verify_rendered_version(version_dir: Path, evidence: dict, publication_manifest: dict | None = None) -> dict:
    snapshot = load_version_evidence(version_dir, evidence.get('evidence_hash', ''))
    if evidence_digest(evidence) != evidence_digest(snapshot):
        raise RuntimeError('交付证据内容与版本快照不匹配')
    report = read_json(version_dir / 'render_report.json')
    if (report.get('status') != 'PASS' or report.get('paper_version') != version_dir.name or
            report.get('evidence_hash') != snapshot['evidence_hash']):
        raise RuntimeError('渲染 PASS 报告未绑定当前版本证据')
    artifacts = {'source': 'paper.md', 'docx': 'paper.docx', 'pdf': 'paper.pdf', 'tex': 'paper.tex',
                 'publication_manifest': 'publication_manifest.json'}
    if (version_dir / 'support_dependencies.json').is_file():
        artifacts['support_dependencies'] = 'support_dependencies.json'
    for field, filename in artifacts.items():
        path = version_dir / filename
        if not path.is_file() or report.get(field + '_sha256') != digest(path):
            raise RuntimeError(f'已验收产物哈希不匹配：{filename}')
    if (publication_manifest is not None and
            publication_manifest != read_json(version_dir / 'publication_manifest.json')):
        raise RuntimeError('publication_manifest 与已验收论文不匹配')
    if audit_public_docx(version_dir / 'paper.docx')['status'] != 'PASS':
        raise RuntimeError('已验收 DOCX 公开审计失败')
    return report
