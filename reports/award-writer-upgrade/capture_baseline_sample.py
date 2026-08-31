"""冻结升级前生成器样稿；不调用研究/Writer/发布，也不改正式论文。"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[2]
    destination = root / 'reports/award-writer-upgrade/baseline-isolated'
    if destination.exists():
        raise SystemExit('基线已存在，拒绝覆盖')
    source = root / 'problems/2025-cumcm-b/paper/versions/paper_v007/evidence_pack.json'
    evidence = json.loads(source.read_text(encoding='utf-8'))
    destination.mkdir(parents=True)
    for name in ('scripts', 'config', 'templates', 'agents'):
        shutil.copytree(root / name, destination / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    copied = []
    for group in ('artifacts', 'figures'):
        for item in evidence.get(group, []):
            path = (root / item['path']).resolve()
            if not path.is_relative_to(root):
                raise RuntimeError('证据路径越界')
            data = path.read_bytes()
            actual = hashlib.sha256(data).hexdigest()
            if actual != item.get('sha256'):
                raise RuntimeError(f'证据哈希不匹配：{item["path"]}')
            target = destination / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            copied.append({'path': item['path'], 'sha256': actual})
    draft_dir = destination / 'sample'
    draft_dir.mkdir()
    shutil.copy2(source, draft_dir / 'evidence_pack.json')
    env = {**os.environ, 'AUTOMM_ROOT': str(destination),
           'PYTHONPATH': str(destination / 'scripts'), 'PYTHONIOENCODING': 'utf-8'}
    code = ('import json; from pathlib import Path; from automm.paper import generate_evidence_markdown; '
            'v=Path("sample"); e=json.loads((v/"evidence_pack.json").read_text(encoding="utf-8")); '
            'print(generate_evidence_markdown(e["problem_id"],v,e))')
    result = subprocess.run([sys.executable, '-c', code], cwd=destination, env=env,
                            text=True, encoding='utf-8', capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr)
    text = (draft_dir / 'paper.md').read_text(encoding='utf-8')
    manifest = {'purpose': '旧生成器隔离样稿，非已验收论文，不发布',
                'evidence_hash': evidence['evidence_hash'], 'copied_evidence': copied,
                'draft_sha256': hashlib.sha256((draft_dir / 'paper.md').read_bytes()).hexdigest(),
                'draft_chars': len(text), 'figures': text.count('!['),
                'scientific_computation_run': False, 'live_agent_run': False}
    (destination.parent / 'baseline-sample.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'copied_evidence'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
