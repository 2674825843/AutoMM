"""论文版本的内容寻址和已验收产物校验；不读取可变共享证据。"""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path

from .common import hash_json, read_json
from .paper_semantics import audit_public_docx


def verify_summary_review(path: Path, review_root: Path, expected_hash: str, current: dict) -> dict:
    """复核记录只能接纳摘要文字差异，不允许改变任何科学证据或门禁。"""
    if not path.resolve().is_relative_to(review_root.resolve()) or not path.is_file():
        raise RuntimeError('摘要复核记录必须位于当前论文 reviews 目录')
    review = read_json(path)
    before = review.get('before', {})
    old_digests = {evidence_digest(before), hash_json({k: v for k, v in before.items() if k != 'evidence_hash'})}
    if (review.get('status') != 'PASS' or review.get('scope') != 'summary_only'
            or not str(review.get('reason', '')).strip()
            or before.get('evidence_hash') != expected_hash or expected_hash not in old_digests
            or review.get('after_evidence_hash') != current.get('evidence_hash')
            or evidence_digest(current) != current.get('evidence_hash')):
        raise RuntimeError('摘要复核未通过或证据快照哈希不匹配')
    old = {item['path']: item for item in before.get('artifacts', [])}
    new = {item['path']: item for item in current.get('artifacts', [])}
    if (old.keys() != new.keys() or len(old) != len(before.get('artifacts', []))
            or len(new) != len(current.get('artifacts', []))):
        raise RuntimeError('摘要复核不允许增加或删除证据')
    allowed = {f"problems/{current['problem_id']}/{q['question_id']}/versions/"
               f"{q['assumption_version']}/question_summary.md" for q in current['questions']}
    changed = [name for name in old if old[name] != new[name]]
    if not changed or not set(changed).issubset(allowed):
        raise RuntimeError('摘要以外的已验收证据发生变化')
    normalized = copy.deepcopy(current)
    id_map = {new[name]['evidence_id']: old[name]['evidence_id'] for name in changed}
    normalized['artifacts'] = [old[item['path']] if item['path'] in changed else item
                               for item in normalized['artifacts']]
    for question in normalized['questions']:
        question['artifact_evidence_ids'] = [id_map.get(value, value)
                                             for value in question['artifact_evidence_ids']]
    if evidence_digest(normalized) != evidence_digest(before):
        raise RuntimeError('摘要复核范围之外的图表、引用、门禁或证据结构发生变化')
    return {'sha256': digest(path), 'changed_summaries': changed}


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
    from .paper_quality import quality_contract
    quality_contract(version_dir, evidence)
    return evidence


def verify_rendered_version(version_dir: Path, evidence: dict, publication_manifest: dict | None = None) -> dict:
    snapshot = load_version_evidence(version_dir, evidence.get('evidence_hash', ''))
    from .paper_quality import check_review, quality_audit_hashes
    check_review(version_dir, snapshot)
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
    if report.get('quality_audit', {}) != quality_audit_hashes(version_dir, snapshot):
        raise RuntimeError('渲染报告质量审阅来源哈希不匹配')
    if audit_public_docx(version_dir / 'paper.docx')['status'] != 'PASS':
        raise RuntimeError('已验收 DOCX 公开审计失败')
    return report
