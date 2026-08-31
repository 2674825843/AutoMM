"""把论文源稿转为只含读者语义的 Pandoc AST；追溯信息独立保留。"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Any

from lxml import etree as ET


def nodes(value: Any):
    if isinstance(value, dict):
        if 't' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def plain(value: Any) -> str:
    if isinstance(value, list):
        return ''.join(plain(x) for x in value)
    if not isinstance(value, dict):
        return ''
    kind, content = value.get('t'), value.get('c')
    if kind in {'Str', 'Code', 'Math'}:
        return content if kind == 'Str' else content[-1]
    if kind in {'Space', 'SoftBreak', 'LineBreak'}:
        return ' '
    if kind in {'RawBlock', 'RawInline'}:
        return ''
    if kind in {'Link', 'Image'}:
        return plain(content[1])
    if kind == 'Cite':
        return plain(content[1])
    return plain(content)


def styled(style: str, blocks: list) -> dict:
    return {'t': 'Div', 'c': [['', [], [['custom-style', style]]], blocks]}


def paragraph(text: str) -> dict:
    return {'t': 'Para', 'c': [{'t': 'Str', 'c': text}]}


def public_text_issues(text: str) -> list[str]:
    # A reference URL is not a pipeline identifier, even if its slug contains one.
    text = re.sub(r'https?://[^\s<>]+', '', text)
    patterns = {
        '内部图表标识残留': r'\bprob\d+_(?:fig|table)_\w+',
        '内部证据标识残留': r'\b(?:ev_|warn_|task_)[A-Za-z0-9_]+',
        '内部项目路径残留': r'\breports[/\\]problems[/\\]|\b[A-Za-z]:[/\\][^\s]+',
        '内部质检流水残留': (
            r'自动质检|暗边框|图例无遮挡|视觉复核确认|implementation\s*(?:§|section\b)|'
            r'\bL[1-6]\s+(?:passed|failed|sanity)\b|\bquality_status\s*=|'
            r'\b(?:sanity|Evidence Pack|PASS_WITH_WARNING)\b'
        ),
        '未解析图表引用': r'@(?:fig|tbl):[\w:.-]+',
        '缺失结果或公式': r'[（(]\s*[，,）)]|(?:偏差约|结果为|厚度为)\s*[，,；;）)]',
        '正文占位符': r'\b(?:TODO|TBD)\b|待填写|待补充|\{\{.+?\}\}',
    }
    return [label for label, pattern in patterns.items() if re.search(pattern, text, re.I)]


def audit_public_docx(docx_path: Path) -> dict:
    """只读检查所有 Word XML 的显示文本和图像说明，不扫描资源关系或公式源码。"""
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    issues = []
    checked = []
    with zipfile.ZipFile(docx_path) as archive:
        for name in archive.namelist():
            if not name.startswith('word/') or not name.endswith('.xml'):
                continue
            root = ET.fromstring(archive.read(name), ET.XMLParser(resolve_entities=False, no_network=True))
            checked.append(name)
            # Concatenate runs within each paragraph so splitting an ID across runs cannot hide it.
            paragraphs = root.xpath('.//w:p', namespaces=ns)
            fragments = [''.join(p.xpath('.//w:t/text() | .//w:delText/text()', namespaces=ns)) for p in paragraphs]
            fragments.extend(root.xpath('.//w:t[not(ancestor::w:p)]/text() | '
                                        './/w:delText[not(ancestor::w:p)]/text()', namespaces=ns))
            fragments.extend(root.xpath('.//*[local-name()="docPr" or local-name()="cNvPr"]/@name | '
                                        './/*[local-name()="docPr" or local-name()="cNvPr"]/@descr | '
                                        './/*[local-name()="docPr" or local-name()="cNvPr"]/@title'))
            for fragment in fragments:
                issues.extend(f'{name}: {issue}' for issue in public_text_issues(fragment))
    return {'status': 'FAILED' if issues else 'PASS', 'issues': sorted(set(issues)), 'checked_parts': checked}


def _single_image_paragraph(block: dict) -> bool:
    if block['t'] == 'Figure':
        body = block['c'][2]
        return len(body) == 1 and _single_image_paragraph(body[0])
    if block['t'] not in {'Para', 'Plain'}:
        return False
    return all(node['t'] in {'Image', 'Space', 'SoftBreak', 'LineBreak'} or (
        node['t'] == 'RawInline' and node['c'][0] == 'html' and
        re.fullmatch(r'<!--\s*(?:evidence|warning):[A-Za-z0-9_.:-]+\s*-->', node['c'][1])
    ) for node in block['c'])


def prepare_publication(markdown: str, evidence_pack: dict, *, pandoc: str = 'pandoc') -> dict:
    """解析一次，产生 Word/TEX 共用 AST 和图表引用映射；issues 非空不可发布。"""
    parsed = subprocess.run([pandoc, '-f', 'markdown+tex_math_dollars', '-t', 'json'],
                            input=markdown, capture_output=True, text=True, encoding='utf-8',
                            timeout=60, check=True)
    ast = json.loads(parsed.stdout)
    issues: list[str] = []
    visible_source = re.sub(r'<!--.*?-->', '', markdown, flags=re.S)
    visible_source = re.sub(r'(!?\[[^\]]*\])\([^)]*\)', r'\1', visible_source)
    if re.search(r'\b[A-Za-z]:[\\/][^\s]+', visible_source):
        issues.append('内部项目绝对路径残留')
    manifest: dict[str, Any] = {'figures': [], 'tables': [], 'citations': []}
    known_figures = evidence_pack.get('figures', [])
    known_ev = {x.get('evidence_id') for group in ('artifacts', 'figures', 'citations')
                for x in evidence_pack.get(group, [])}
    citations = {x['citation_id']: x for x in evidence_pack.get('citations', [])}
    figure_blocks: dict[int, dict] = {}
    table_blocks: dict[int, dict] = {}
    blocks = ast['blocks']
    # First pass fixes all visible numbers before resolving forward references.
    for index, block in enumerate(blocks):
        if any(x.get('t') in {'Table', 'Figure'} and x is not block for x in nodes(block)):
            issues.append('不支持嵌套图表布局，请移至独立顶层段落')
        imgs = [x for x in nodes(block) if x.get('t') == 'Image']
        if imgs:
            if len(imgs) != 1 or not _single_image_paragraph(block):
                issues.append('图片必须为独立单图段落')
                continue
            img = imgs[0]
            path = img['c'][2][0]
            registered = next((f for f in known_figures if f.get('path') == path), None)
            if evidence_pack and registered is None:
                issues.append(f'图片未登记或路径不一致：{path}')
            internal_id = (registered or {}).get('stable_id') or (
                block['c'][0][0] if block['t'] == 'Figure' else img['c'][0][0]
            ) or f'figure-{len(manifest["figures"])+1}'
            title = plain(img['c'][1]).replace(internal_id, '').strip()
            if not title:
                issues.append(f'缺少图题：{internal_id}')
            if any(f['internal_id'] == internal_id for f in manifest['figures']):
                issues.append(f'图片重复插入：{internal_id}；请使用正文引用')
            item = {'internal_id': internal_id, 'number': len(manifest['figures']) + 1,
                    'title': title, 'source_path': path,
                    'evidence_ids': [registered['evidence_id']] if registered else []}
            manifest['figures'].append(item)
            figure_blocks[index] = item
        if block['t'] == 'Table':
            title = plain(block['c'][1][1]).strip()
            if not title:
                issues.append('表格缺少表题；请使用 Markdown 的 “: 表题”')
            nearby = json.dumps(blocks[max(0, index - 1):index + 3], ensure_ascii=False)
            evidence_ids = re.findall(r'evidence:([A-Za-z0-9_.:-]+)', nearby)
            if evidence_pack and not any(e in known_ev for e in evidence_ids):
                issues.append(f'表格缺少有效证据：{title}')
            item = {'internal_id': block['c'][0][0] or f'table-{len(manifest["tables"])+1}',
                    'number': len(manifest['tables']) + 1, 'title': title,
                    'evidence_ids': sorted(set(evidence_ids))}
            manifest['tables'].append(item)
            table_blocks[index] = item
    refs = {f'fig:{f["internal_id"]}': f'图{f["number"]}' for f in manifest['figures']}
    refs.update({f'tbl:{t["internal_id"]}': f'表{t["number"]}' for t in manifest['tables']})
    # Reference numbering follows bibliography order, not arbitrary registry insertion order.
    reference_section = False
    for block in blocks:
        if block['t'] == 'Header':
            reference_section = plain(block['c'][2]).strip() == '参考文献' or block['c'][1][0] == 'paper-references'
        if reference_section:
            for node in nodes(block):
                if node.get('t') == 'Cite':
                    for citation in node['c'][0]:
                        key = citation['citationId']
                        if key in citations and key not in [c['internal_id'] for c in manifest['citations']]:
                            manifest['citations'].append({'internal_id': key, 'number': len(manifest['citations']) + 1})
    for key in citations:
        if key not in [c['internal_id'] for c in manifest['citations']]:
            manifest['citations'].append({'internal_id': key, 'number': len(manifest['citations']) + 1})
    refs.update({c['internal_id']: f'[{c["number"]}]' for c in manifest['citations']})

    def clean(value: Any) -> Any:
        if isinstance(value, list):
            return [clean(x) for x in value if not (isinstance(x, dict) and x.get('t') in {'RawBlock', 'RawInline'})]
        if not isinstance(value, dict):
            return value
        kind = value.get('t')
        if kind == 'Cite':
            keys = [c['citationId'] for c in value['c'][0]]
            for key in keys:
                if key not in refs:
                    issues.append(f'未解析图表或文献引用：{key}')
            return {'t': 'Str', 'c': '、'.join(refs.get(k, '@' + k) for k in keys)}
        if kind in {'Str', 'Code'}:
            text = value['c'] if kind == 'Str' else value['c'][-1]
            for item in manifest['figures']:
                text = text.replace(item['internal_id'], str(item['number']))
            text = re.sub(r'\bprob0*(\d+)\b', lambda m: f'问题{int(m[1])}', text)
            if kind == 'Str':
                return {'t': 'Str', 'c': text}
            return {'t': 'Code', 'c': [value['c'][0], text]}
        if kind == 'Math':
            return copy.deepcopy(value)
        return {key: clean(child) for key, child in value.items()}

    output = []
    reference_section = False
    title_seen = False
    abstract_section = False
    for index, block in enumerate(blocks):
        kind = block['t']
        if kind == 'Header':
            abstract_section = plain(block['c'][2]).strip() == '摘要'
        elif abstract_section and kind in {'Para', 'Plain'}:
            visible = [x for x in block['c'] if plain(x).strip()]
            if visible and all(x['t'] == 'Strong' for x in visible):
                issues.append('摘要不能整段加粗，请仅强调有证据的关键结果')
        if kind in {'RawBlock', 'RawInline'}:
            continue
        if index in figure_blocks:
            item = figure_blocks[index]
            img = copy.deepcopy(next(x for x in nodes(block) if x.get('t') == 'Image'))
            img['c'][0][0] = ''
            img['c'][1] = [{'t': 'Str', 'c': item['title']}]
            img['c'][2][1] = ''
            output.extend([styled('图片', [{'t': 'Para', 'c': [img]}]),
                           styled('图注', [paragraph(item['title'])])])
        elif index in table_blocks:
            table = clean(block)
            table['c'][0][0] = ''
            table['c'][1] = [None, []]
            output.extend([styled('表注', [paragraph(table_blocks[index]['title'])]), table])
        elif kind == 'Header':
            text = plain(block['c'][2]).strip()
            reference_section = text == '参考文献' or block['c'][1][0] == 'paper-references'
            if not title_seen:
                output.append(styled('Title', [{'t': 'Para', 'c': clean(block['c'][2])}]))
                title_seen = True
            else:
                style = f'heading {max(1, min(3, block["c"][0] - 1))}'
                if reference_section or text in {'摘要', '关键词', '参考文献', '致谢'} or text.startswith('附录'):
                    style = 'AutoMMUnnumberedHeading1'
                output.append(styled(style, [{'t': 'Para', 'c': clean(block['c'][2])}]))
        else:
            block = copy.deepcopy(block)
            if reference_section and kind in {'Para', 'Plain'}:
                if block['c'] and block['c'][0].get('t') == 'Cite':
                    block['c'] = block['c'][1:]
                output.append(styled('参考文献', [clean(block)]))
            elif kind in {'Para', 'Plain'}:
                output.append(styled('Normal', [clean(block)]))
            else:
                output.append(clean(block))
    ast['blocks'] = output
    ast['meta'] = {}
    # Image resource paths are internal inputs, not visible text; XML media names are generated by Pandoc.
    issues.extend(public_text_issues(plain(output)))
    return {'pandoc_ast': ast, 'manifest': manifest, 'issues': sorted(set(issues))}
