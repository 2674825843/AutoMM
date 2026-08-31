"""仅恢复能逐字节匹配旧验收SHA256的换行符，不改写科学内容。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
snapshot = json.loads((ROOT / 'problems/2025-cumcm-b/paper/evidence/evidence_pack.json').read_text(encoding='utf-8'))
targets = [(ROOT / item['path'], item['sha256']) for item in snapshot['artifacts']]
for directory in ('versions/paper_v004', 'withdrawn/final-v004-20260831-0405'):
    targets.append((ROOT / 'problems/2025-cumcm-b/paper' / directory / 'paper.md',
                    'f5b23dc442398cf5ea82b58698a0e96eb67dcb690fc2e7ab93e1eeabff27c6f3'))
restored = []
for path, expected in targets:
    if not path.resolve().is_relative_to(ROOT):
        raise RuntimeError('路径越界')
    original = path.read_bytes()
    if hashlib.sha256(original).hexdigest() == expected:
        continue
    normalized = original.replace(b'\r\n', b'\n')
    if hashlib.sha256(normalized).hexdigest() == expected:
        path.write_bytes(normalized)
        restored.append(str(path.relative_to(ROOT)))
print('恢复并精确匹配历史哈希的文件数:', len(restored))
