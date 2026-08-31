from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from automm.common import hash_json, read_json, write_json


def item(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return {'path': path, 'sha256': hashlib.sha256(content).hexdigest(), 'evidence_id': path}


def setup(root, problem_id='demo', version_name='paper_v005'):
    version = root / f'problems/{problem_id}/paper/versions/{version_name}'
    version.mkdir(parents=True)
    from docx import Document
    doc = Document()
    doc.add_paragraph('Verified result')
    doc.save(version / 'paper.docx')
    code = item(root, 'problems/demo/prob01/versions/assumption_v001/code/model.py', b'print(1)')
    figure = item(root, 'problems/demo/figures/result.png', b'image')
    figure.update(stable_id='prob01_fig_result_x')
    evidence = {'artifacts': [code], 'figures': [figure]}
    evidence['evidence_hash'] = hash_json(evidence)
    manifest = {'figures': [{'internal_id': figure['stable_id'], 'number': 1,
                            'title': '结果对比', 'source_path': figure['path']}]}
    write_json(version / 'evidence_pack.json', evidence)
    write_json(version / 'writer_manifest.json', {'evidence_hash': evidence['evidence_hash']})
    write_json(version / 'publication_manifest.json', manifest)
    requirements = root / 'scripts/requirements.txt'
    write_json(version / 'support_dependencies.json', {'evidence_hash': evidence['evidence_hash'], 'files': [code,
        {'path': 'scripts/requirements.txt', 'sha256': hashlib.sha256(requirements.read_bytes()).hexdigest()}],
        'missing': []})
    for name in ('paper.md', 'paper.tex', 'paper.pdf'):
        (version / name).write_bytes(name.encode())
    report = {'status': 'PASS', 'paper_version': version.name, 'evidence_hash': evidence['evidence_hash']}
    for field, name in [('source', 'paper.md'), ('docx', 'paper.docx'), ('pdf', 'paper.pdf'), ('tex', 'paper.tex'),
                        ('publication_manifest', 'publication_manifest.json'),
                        ('support_dependencies', 'support_dependencies.json')]:
        report[field + '_sha256'] = hashlib.sha256((version / name).read_bytes()).hexdigest()
    write_json(version / 'render_report.json', report)
    return version, evidence, manifest


def test_delivery_contains_only_docx_and_support_and_matching_files(project_root: Path):
    from automm.paper_delivery import build_delivery
    version, evidence, manifest = setup(project_root)
    destination = version.parent.parent / '交付'
    result = build_delivery(version, evidence, manifest, destination)
    assert result['status'] == 'PASS'
    assert {x.name for x in destination.iterdir()} == {'论文.docx', '支撑材料'}
    assert (destination / '论文.docx').read_bytes() == (version / 'paper.docx').read_bytes()
    assert (destination / '支撑材料/图片/图01_结果对比.png').read_bytes() == b'image'
    assert list((destination / '支撑材料/代码').rglob('model.py'))
    assert build_delivery(version, evidence, manifest, destination)['status'] == 'PASS'


def test_changed_source_never_publishes_partial_delivery(project_root: Path):
    from automm.paper_delivery import build_delivery
    version, evidence, manifest = setup(project_root)
    (project_root / evidence['artifacts'][0]['path']).write_bytes(b'changed')
    destination = version.parent.parent / '交付'
    with pytest.raises(RuntimeError, match='哈希'):
        build_delivery(version, evidence, manifest, destination)
    assert not destination.exists()


def test_only_explicitly_distributable_data_is_included(project_root: Path):
    from automm.paper_delivery import build_delivery
    version, evidence, manifest = setup(project_root)
    allowed = item(project_root, 'data/allowed.csv', b'1,2')
    denied = item(project_root, 'data/unknown.csv', b'3,4')
    allowed['redistribution_allowed'] = True
    denied['redistribution_allowed'] = False
    write_json(version / 'support_inputs.json', {'inputs': [allowed, denied]})
    destination = version.parent.parent / '交付'
    result = build_delivery(version, evidence, manifest, destination)
    assert (destination / '支撑材料/数据/data/allowed.csv').exists()
    assert not (destination / '支撑材料/数据/data/unknown.csv').exists()
    assert result['excluded_inputs'] == ['data/unknown.csv']


def test_delivery_rejects_path_escape_and_conflicting_destination(project_root: Path):
    from automm.paper_delivery import build_delivery
    version, evidence, manifest = setup(project_root)
    destination = version.parent.parent / '交付'
    destination.mkdir()
    (destination / 'user-file').write_text('keep')
    with pytest.raises(RuntimeError, match='已有|冲突'):
        build_delivery(version, evidence, manifest, destination)
    assert (destination / 'user-file').read_text() == 'keep'


@pytest.mark.parametrize('changed', ['paper.docx', 'evidence_pack.json', 'writer_manifest.json',
                                   'publication_manifest.json', 'support_dependencies.json'])
def test_delivery_rejects_changed_snapshot_or_accepted_artifact(project_root, changed):
    from automm.paper_delivery import build_delivery
    version, evidence, manifest = setup(project_root)
    target = version / changed
    if changed == 'paper.docx':
        target.write_bytes(b'forged Word')
    else:
        data = read_json(target)
        data['evidence_hash'] = 'another-snapshot'
        write_json(target, data)
    destination = version.parent.parent / '交付'
    with pytest.raises(RuntimeError, match='哈希|证据|快照|manifest'):
        build_delivery(version, evidence, manifest, destination)
    assert not destination.exists()


def test_delivery_rejects_unbound_pass_report(project_root):
    from automm.paper_delivery import build_delivery
    version, evidence, manifest = setup(project_root)
    write_json(version / 'render_report.json', {'status': 'PASS'})
    with pytest.raises(RuntimeError, match='哈希|证据|渲染'):
        build_delivery(version, evidence, manifest, version.parent.parent / '交付')


def test_delivery_rejects_requirements_changed_after_snapshot(project_root):
    from automm.paper_delivery import build_delivery
    version, evidence, manifest = setup(project_root)
    (project_root / 'scripts/requirements.txt').write_text('changed==1', encoding='utf-8')
    with pytest.raises(RuntimeError, match='哈希'):
        build_delivery(version, evidence, manifest, version.parent.parent / '交付')


def test_dependency_snapshot_follows_local_package_and_relative_imports(project_root):
    from automm import paper_delivery
    code = item(project_root, 'problems/demo/prob01/versions/assumption_v001/code/compute.py',
                b'from automm.visualization import figure_record\nfrom helpers import calc\n')
    helper = item(project_root, 'problems/demo/prob01/versions/assumption_v001/code/helpers.py', b'calc=1\n')
    builder = getattr(paper_delivery, 'build_support_dependencies', None)
    assert callable(builder), '缺少依赖快照构建'
    snapshot = builder({'evidence_hash': 'snapshot', 'artifacts': [code]})
    paths = {x['path'] for x in snapshot['files']}
    assert {code['path'], helper['path'], 'scripts/automm/__init__.py', 'scripts/automm/common.py',
            'scripts/automm/visualization.py', 'scripts/requirements.txt'} <= paths
    assert not snapshot['missing']


def test_dependency_snapshot_rejects_missing_local_import(project_root):
    from automm import paper_delivery
    code = item(project_root, 'problems/demo/code/compute.py', b'from automm.no_such_module import result\n')
    builder = getattr(paper_delivery, 'build_support_dependencies', None)
    assert callable(builder), '缺少依赖快照构建'
    with pytest.raises(RuntimeError, match='本地|依赖'):
        builder({'evidence_hash': 'snapshot', 'artifacts': [code]})


def test_copy_rejects_source_changed_between_check_and_copy(project_root, monkeypatch):
    from automm import paper_delivery
    version, evidence, manifest = setup(project_root)
    real = paper_delivery.shutil.copy2
    def corrupt(source, destination, *args, **kwargs):
        if Path(source).name == 'model.py':
            Path(source).write_bytes(b'changed-during-copy')
        return real(source, destination, *args, **kwargs)
    monkeypatch.setattr(paper_delivery.shutil, 'copy2', corrupt)
    destination = version.parent.parent / '交付'
    with pytest.raises(RuntimeError, match='哈希'):
        paper_delivery.build_delivery(version, evidence, manifest, destination)
    assert not destination.exists()


def test_dependency_closure_is_delivered_and_changed_dependency_rejected(project_root):
    from automm.paper_delivery import build_delivery, build_support_dependencies
    version, evidence, manifest = setup(project_root)
    source = project_root / evidence['artifacts'][0]['path']
    source.write_text('from automm.visualization import figure_record\n', encoding='utf-8')
    evidence['artifacts'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    evidence.pop('evidence_hash')
    evidence['evidence_hash'] = hash_json(evidence)
    write_json(version / 'evidence_pack.json', evidence)
    write_json(version / 'writer_manifest.json', {'evidence_hash': evidence['evidence_hash']})
    deps = build_support_dependencies(evidence)
    write_json(version / 'support_dependencies.json', deps)
    render = read_json(version / 'render_report.json')
    dependencies_hash = hashlib.sha256((version / 'support_dependencies.json').read_bytes()).hexdigest()
    render.update(evidence_hash=evidence['evidence_hash'], support_dependencies_sha256=dependencies_hash)
    write_json(version / 'render_report.json', render)
    destination = version.parent.parent / '交付'
    build_delivery(version, evidence, manifest, destination)
    for name in ('__init__.py', 'common.py', 'visualization.py'):
        assert (destination / '支撑材料/代码/scripts/automm' / name).is_file()
    assert (destination / '支撑材料/代码/scripts/requirements.txt').is_file()
    (project_root / 'scripts/automm/common.py').write_text('changed=1', encoding='utf-8')
    with pytest.raises(RuntimeError, match='哈希'):
        build_delivery(version, evidence, manifest, version.parent.parent / 'another-delivery')
