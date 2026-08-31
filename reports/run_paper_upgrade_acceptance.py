"""隔离的真实 Word 验收样例及只读摘要复核记录；不启动模型计算。"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from automm.common import read_json, write_json, write_text, relative
from automm.paper import build_evidence_pack, render_paper
from automm.paper_integrity import digest, evidence_digest, verify_summary_review


def smoke():
    target = ROOT / 'reports/paper-upgrade-smoke-final'
    source = (ROOT / 'reports/paper-upgrade-smoke/paper.md').read_text(encoding='utf-8')
    source = source.replace(': 符号说明（排版样例）', ': 符号说明（排版样例）\n\n<!-- evidence:ev_symbols -->')
    source = source.replace('## 图形展示', '#### 三级标题检查\n\n检查层级与公式。\n\n## 图形展示\n\n### 第二章的首个子节')
    write_text(target / 'paper.md', source)
    image = 'problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_reflectance_spectrum_1d4fb899d1.png'
    evidence = {'figures': [{'path': image, 'stable_id': 'sample', 'evidence_id': 'ev_sample',
                             'sha256': digest(ROOT / image)}],
                'artifacts': [{'evidence_id': 'ev_symbols', 'path': 'paper.md'}]}
    evidence['evidence_hash'] = evidence_digest(evidence)
    write_json(target / 'evidence_pack.json', evidence)
    write_json(target / 'writer_manifest.json', {'evidence_hash': evidence['evidence_hash']})
    result = render_paper(target, {'minimum_pdf_pages': 1})
    print({'sample_status': result['status'], 'pages': result.get('pdf_pages')})


def review():
    root = ROOT / 'problems/2025-cumcm-b/paper'
    old = read_json(root / 'evidence/evidence_pack.json')
    current = build_evidence_pack('2025-cumcm-b', persist=False)
    report = root / 'reviews/summary-review-20260831-v002.json'
    if report.exists():
        raise RuntimeError('复核记录已存在，不覆盖历史')
    sources = [
        'prob01/versions/assumption_v001/sanity_report.md',
        'prob01/versions/assumption_v001/robustness/conclusion.md',
        'prob01/versions/assumption_v001/ablation/conclusion.md',
        'prob02/versions/assumption_v001/results/thickness_inversion_v003/sanity_report.md',
        'prob02/versions/assumption_v001/results/thickness_inversion_v003/verification.json',
        'prob02/versions/assumption_v001/robustness/conclusion.md',
        'prob02/versions/assumption_v001/ablation/conclusion.md',
        'prob03/versions/assumption_v001/results/silicon_mb_verify/sanity_report.md',
        'prob03/versions/assumption_v001/results/silicon_mb_verify/verification.json',
        'prob03/versions/assumption_v001/robustness/conclusion.md',
        'prob03/versions/assumption_v001/ablation/conclusion.md',
    ]
    write_json(report, {
        'status': 'PASS', 'scope': 'summary_only', 'before': old,
        'after_evidence_hash': current['evidence_hash'],
        'reason': '用户允许继续后逐句核对三份摘要与既有验收报告、可靠性及消融结论；仅接纳摘要归纳，不重新认可原始数据或重跑计算。数值、方法、假设及推广限制均有既有证据。',
        'review_sources': [{'path': relative(root.parent / p), 'sha256': digest(root.parent / p)} for p in sources],
        'publication_requirements': [
            '问题1明确为合成实验，常数折射率约4%偏差不得写成实测精度。',
            '问题2 F检验p=0.022为统计拒绝共享厚度，0.165%小于2%是工程阈值判断；不声称统计检验通过。',
            '问题3多光束0.11%为物理两光束基线的最大残差改善，不与变量投影拟合误差混淆。',
            '无吸收平行板条件下的极值位置论断保留其物理假设，不推广到吸收、非平行界面。',
            '保留色散缺口、弱可辨识、近简并、物理NLS交叉验证偏差以及原始附件哈希不一致。',
            '数据未确认分发许可，排除原始附件并说明获取方式与复现缺口。',
        ],
    })
    result = verify_summary_review(report, root / 'reviews', old['evidence_hash'], current)
    print({'review': relative(report), **result})


if __name__ == '__main__':
    {'smoke': smoke, 'review': review}[sys.argv[1]]()
