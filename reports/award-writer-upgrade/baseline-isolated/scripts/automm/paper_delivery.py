"""从已验收来源构建可恢复、可验证的论文交付目录。"""
from __future__ import annotations

import ast
import re
import shutil
import tempfile
from pathlib import Path

from .common import ROOT, read_json, utc_now, write_json, write_text
from .paper_integrity import digest, verify_rendered_version


def build_support_dependencies(evidence_pack: dict) -> dict:
    """静态闭合明确的本地 Python 导入，仅登记逐文件哈希白名单。"""
    registered: dict[str, dict] = {}
    external: set[str] = set()

    def add(path: Path):
        path = path.resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
            raise RuntimeError(f'本地依赖缺失或越界：{path}')
        relative = path.relative_to(ROOT).as_posix()
        if re.search(r'(?i)(secret|credential|password|\.env)', path.name):
            raise RuntimeError(f'本地依赖疑似凭据，拒绝分发：{relative}')
        if relative in registered:
            return
        registered[relative] = {'path': relative, 'sha256': digest(path)}
        if path.suffix != '.py':
            return
        try:
            tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=relative)
        except (SyntaxError, UnicodeError) as exc:
            raise RuntimeError(f'本地依赖无法静态解析：{relative}') from exc
        parent = path.parent
        while (parent / '__init__.py').is_file():
            add(parent / '__init__.py')
            parent = parent.parent

        def resolve(module: str, base: Path | None = None) -> Path | None:
            parts = module.split('.') if module else []
            bases = [base] if base is not None else [path.parent, ROOT / 'scripts']
            for search in bases:
                candidate = search.joinpath(*parts)
                for target in (candidate.with_suffix('.py'), candidate / '__init__.py'):
                    if target.is_file():
                        add(target)
                        return target
                if base is not None or (parts and ((search / parts[0]).is_dir() or
                                                   (search / (parts[0] + '.py')).is_file())):
                    raise RuntimeError(f'无法解析必须存在的本地依赖：{relative} -> {module}')
            external.add(module)
            return None

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolve(alias.name)
            elif isinstance(node, ast.ImportFrom):
                base = None
                if node.level:
                    base = path.parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    if not base.is_relative_to(ROOT):
                        raise RuntimeError('相对本地依赖越界')
                target = resolve(node.module or '', base)
                if target and target.name == '__init__.py':
                    # from package import child may load a submodule or an exported name.
                    declarations = ast.parse(target.read_text(encoding='utf-8-sig'))
                    exported = {x.id for x in ast.walk(declarations) if isinstance(x, ast.Name)}
                    exported.update(x.name for x in ast.walk(declarations)
                                    if isinstance(x, (ast.FunctionDef, ast.ClassDef)))
                    exported.update(x.asname or x.name for x in ast.walk(declarations) if isinstance(x, ast.alias))
                    for alias in node.names:
                        if alias.name != '*' and alias.name not in exported:
                            resolve(alias.name, target.parent)

    for item in evidence_pack.get('artifacts', []):
        path = Path(item['path'])
        if path.suffix == '.py':
            add(verified_source(item))
        elif ((any(p in {'code', 'configs'} for p in path.parts) or path.name == 'parameters.yaml') and
              path.suffix in {'.yaml', '.yml', '.json', '.toml', '.txt'}):
            add(verified_source(item))
    add(ROOT / 'scripts/requirements.txt')
    return {'schema_version': 1, 'evidence_hash': evidence_pack['evidence_hash'],
            'files': [registered[key] for key in sorted(registered)], 'missing': [],
            'external_imports': sorted(external)}


def verified_source(item: dict) -> Path:
    path = (ROOT / item['path']).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise RuntimeError(f'支撑材料路径越界：{item["path"]}')
    if not path.is_file():
        raise RuntimeError(f'支撑材料文件缺失：{item["path"]}')
    expected = item.get('sha256', '')
    if len(expected) != 64 or digest(path) != expected:
        raise RuntimeError(f'支撑材料来源哈希不匹配：{item["path"]}')
    return path


def _files(directory: Path) -> dict:
    return {p.relative_to(directory).as_posix(): digest(p) for p in directory.rglob('*') if p.is_file()}


def _copy_verified(source: Path, destination: Path, expected: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if digest(destination) != expected:
        raise RuntimeError(f'复制后的交付哈希与来源不匹配：{source.name}')


def build_delivery(version_dir: Path, evidence_pack: dict, publication_manifest: dict,
                   destination: Path, *, published_destination: Path | None = None) -> dict:
    """临时目录准备后同盘原子发布；已有目录仅在所有内容完全一致时复用。"""
    destination = destination.resolve()
    if not destination.is_relative_to(ROOT.resolve()) or destination == ROOT.resolve():
        raise RuntimeError('交付目标越出项目目录')
    rendered = verify_rendered_version(version_dir, evidence_pack, publication_manifest)
    dependencies = read_json(version_dir / 'support_dependencies.json')
    if (dependencies.get('evidence_hash') != evidence_pack.get('evidence_hash') or
            not dependencies.get('files') or dependencies.get('missing')):
        raise RuntimeError('支撑依赖快照缺失、不完整或证据哈希不匹配')
    # Verify every frozen source before copying any public artifact.
    for item in dependencies['files']:
        verified_source(item)
    source_docx = version_dir / 'paper.docx'
    if not source_docx.is_file():
        raise RuntimeError('缺少已渲染 Word')
    if destination.exists() and not (version_dir / 'delivery_manifest.json').is_file():
        raise RuntimeError('已有交付目录，拒绝覆盖冲突内容')
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.delivery-pending-', dir=destination.parent))
    support = staging / '支撑材料'
    for name in ('代码', '图片', '数据'):
        (support / name).mkdir(parents=True)
    _copy_verified(source_docx, staging / '论文.docx', rendered['docx_sha256'])
    copied = []
    sources = []
    inputs = read_json(version_dir / 'support_inputs.json', {'inputs': []}).get('inputs', [])
    excluded = [x['path'] for x in inputs if x.get('redistribution_allowed') is not True]
    # Copy only the dependency closure frozen while preparing this version.
    for item in dependencies['files']:
        path = Path(item['path'])
        source = verified_source(item)
        target = support / '代码' / path
        _copy_verified(source, target, item['sha256'])
        sources.append({'path': item['path'], 'sha256': item['sha256']})
        if path.name in {'compute.py', 'make_figures.py', 'ablation.py', 'robustness.py'}:
            copied.append(path.as_posix())
    registered = {x['stable_id']: x for x in evidence_pack.get('figures', [])}
    for item in publication_manifest.get('figures', []):
        source_item = registered.get(item['internal_id'])
        if source_item is None or source_item['path'] != item['source_path']:
            raise RuntimeError('交付图片与论文证据映射不一致')
        source = verified_source(source_item)
        title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', item['title']).strip('. ')[:70]
        name = f'图{int(item["number"]):02d}_{title}{source.suffix.lower()}'
        _copy_verified(source, support / '图片' / name, source_item['sha256'])
        sources.append({'path': source_item['path'], 'sha256': source_item['sha256']})
    for item in inputs:
        if item.get('redistribution_allowed') is not True:
            continue
        source = verified_source(item)
        target = support / '数据' / Path(item['path'])
        _copy_verified(source, target, item['sha256'])
        sources.append({'path': item['path'], 'sha256': item['sha256']})
    entries = '\n'.join(f'- `{path}`' for path in copied) or '- 没有登记独立程序入口。'
    missing = '\n'.join(
        f'- `{path}`：分发权限未确认，未随包提供。' for path in sorted(set(excluded))
    ) or '- 无已登记但被排除的输入。'
    write_text(support / '运行说明.md', f'''# 论文支撑材料运行说明

本包对应论文版本 `{version_dir.name}`；图片文件名与论文正式图号一致。

## 环境与目录

使用 Python 3.11 或项目原有 Python 环境，依赖见代码/scripts/requirements.txt。
代码目录保留原始项目相对路径，以“代码”目录作为工作目录。
运行前将“数据”目录的内容按相同相对路径复制到“代码”目录中；不要修改原始数据。
例如 数据/data 对应 代码/data；代码内依赖数据也按保留的完整目录路径放置。

## 入口和顺序

{entries}

按问题编号从小到大运行。先查看相应程序的 --help；完整主计算命令见同版本
configs/task_spec.yaml 的 command 字段，输入参数登记位置见 input_path，
运行配置位置见 config_path，预期输出文件清单见 expected_outputs。
将 command 中的 {{python}} 换为自己的 Python 解释器；常用参数是 --config、--input、--output，
具体以各入口 --help 为准。--output 指向独立输出目录，禁止覆盖已验收结果。
同版本 configs 中还包含扰动/消融配置，应在主计算之后运行对应程序，再生成图表。
生成图片前先准备相应计算输出，不能把交付图片当作计算输入。
绘图脚本如要求 --results-dir 或同类参数，请先运行同版本计算入口，以其独立 --output-dir 作为结果目录。
验收运行的 results 及 metadata 未自动打包；须通过上述步骤重新生成，或取得其授权副本后保留原相对路径。
支撑材料中的“图片”是论文采用的验收图片副本；重新运行产生的图片保留在独立输出目录。

## 未附输入

{missing}

第三方竞赛附件请从题目发布方取得合法副本，再放入程序约定的 data 目录；勿使用未经核对的替代数据。
本次只核验来源、文件完整性和静态目录关系，没有重新运行完整模型，因此不宣称已在全新环境完成数值复现。
''')
    hashes = _files(staging)
    report = {'status': 'PASS', 'paper_version': version_dir.name,
              'evidence_hash': evidence_pack.get('evidence_hash'), 'created_at': utc_now(),
              'destination': (published_destination or destination).relative_to(ROOT).as_posix(),
              'files': hashes, 'sources': sources, 'excluded_inputs': sorted(set(excluded))}
    if destination.exists():
        previous = read_json(version_dir / 'delivery_manifest.json', {})
        if (previous.get('paper_version') != version_dir.name or
                previous.get('evidence_hash') != evidence_pack['evidence_hash'] or
                previous.get('files') != _files(destination) or _files(destination) != hashes):
            raise RuntimeError('已有交付与当前版本冲突，拒绝覆盖')
        # Preserve staging for inspection; no recursive cleanup of user paths.
    else:
        write_json(version_dir / 'delivery_manifest.json', report)
        staging.rename(destination)
    write_json(version_dir / 'delivery_manifest.json', report)
    return report


def publish_paper(version_dir: Path, evidence: dict, paper_state: dict, final_dir: Path) -> dict:
    """一次 rename 发布内部产物和对外交付；完整 final 可无覆盖恢复状态。"""
    publication = read_json(version_dir / 'publication_manifest.json')
    verify_rendered_version(version_dir, evidence, publication)
    filenames = ('paper.md', 'paper.docx', 'paper.tex', 'paper.pdf', 'writer_manifest.json',
                 'evidence_pack.json', 'publication_manifest.json', 'support_dependencies.json',
                 'validation.json', 'render_report.json')
    source_hashes = {name: digest(version_dir / name) for name in filenames}
    if final_dir.exists():
        manifest = read_json(final_dir / 'manifest.json')
        actual = _files(final_dir)
        actual.pop('manifest.json', None)
        if (manifest.get('paper_version') != version_dir.name or
                manifest.get('evidence_hash') != evidence['evidence_hash'] or
                manifest.get('files') != actual or any(actual.get(k) != v for k, v in source_hashes.items())):
            raise RuntimeError('已有 final 版本、证据或完整产物哈希冲突，拒绝覆盖')
        delivery = read_json(final_dir / 'delivery_manifest.json')
        if delivery.get('files') != _files(final_dir / '交付'):
            raise RuntimeError('已有 final 交付哈希冲突')
        write_json(version_dir / 'delivery_manifest.json', delivery)
        return manifest
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.final-pending-', dir=final_dir.parent))
    for name, expected in source_hashes.items():
        _copy_verified(version_dir / name, staging / name, expected)
    delivery = build_delivery(version_dir, evidence, publication, staging / '交付',
                              published_destination=final_dir / '交付')
    write_json(staging / 'delivery_manifest.json', delivery)
    manifest = dict(paper_state, status='passed', paper_version=version_dir.name,
                    evidence_hash=evidence['evidence_hash'], completed_at=utc_now(),
                    delivery=delivery['destination'], delivery_status='PASS', files=_files(staging))
    write_json(staging / 'manifest.json', manifest)
    # A final verification detects source changes during a long copy operation.
    verify_rendered_version(version_dir, evidence, publication)
    if any(digest(version_dir / name) != expected for name, expected in source_hashes.items()):
        raise RuntimeError('发布期间来源哈希发生变化')
    staging.rename(final_dir)
    return manifest
