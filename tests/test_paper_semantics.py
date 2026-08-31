from __future__ import annotations

import json

import pytest


def prepare(text, evidence=None):
    from automm import paper_semantics
    return paper_semantics.prepare_publication(text, evidence or {})


def fixture_evidence():
    return {
        'figures': [{'stable_id': 'prob01_fig_test_abcd', 'path': 'plot.png',
                     'title': '厚度对比', 'evidence_id': 'ev_fig_1'}],
        'artifacts': [{'evidence_id': 'ev_result_1'}],
        'citations': [{'citation_id': 'L01', 'title': 'Optics'}],
    }


def test_semantics_creates_separate_caption_and_removes_internal_ids():
    result = prepare('# 论文\n\n## 结果\n\n![厚度对比](plot.png){#prob01_fig_test_abcd}\n\n'
                     '见 @fig:prob01_fig_test_abcd。<!-- evidence:ev_fig_1 -->\n', fixture_evidence())
    assert not result['issues']
    assert result['manifest']['figures'][0]['number'] == 1
    public = json.dumps(result['pandoc_ast'], ensure_ascii=False)
    assert '图1' in public
    assert '图注' in public
    assert 'prob01_fig_test_abcd' not in public
    assert 'ev_fig_1' not in public


def test_legacy_escaped_ids_are_mapped_without_touching_math():
    result = prepare('# 论文\n\n![prob01\\_fig\\_test\\_abcd 厚度对比](plot.png)\n\n'
                     '图 prob01\\_fig\\_test\\_abcd 展示 $t_{true}=10$。', fixture_evidence())
    assert not result['issues']
    text = json.dumps(result['pandoc_ast'], ensure_ascii=False)
    assert 'prob01' not in text
    assert 't_{true}=10' in text


def test_table_requires_caption_and_has_separate_template_caption():
    body = '# 标题\n\n|方法|结果|\n|---|---|\n|A|2|\n'
    assert any('表题' in str(issue) for issue in prepare(body)['issues'])
    result = prepare(body + '\n: 方法对比\n\n<!-- evidence:ev_result_1 -->\n', fixture_evidence())
    assert result['manifest']['tables'][0]['title'] == '方法对比'
    assert '表注' in json.dumps(result['pandoc_ast'], ensure_ascii=False)


@pytest.mark.parametrize('bad', ['自动质检 passed', '偏差约 ，', '单初值（，偏差约 0）', '@fig:missing'])
def test_unpublishable_content_fails_closed(bad):
    assert prepare('# 论文\n\n' + bad)['issues']


def test_semantic_emphasis_and_numeric_citation_survive():
    result = prepare('# 标题\n\n## 摘要\n\n**厚度为 $10\\,\\mu m$**，采用*相位法*。\n\n'
                     '## 方法\n\n依据 [@L01]。\n\n## 参考文献\n\n[@L01] Optics.\n', fixture_evidence())
    public = json.dumps(result['pandoc_ast'], ensure_ascii=False)
    assert 'Strong' in public and 'Emph' in public
    assert '[1]' in public and 'L01' not in public


def test_unknown_image_path_is_not_accepted_as_evidence():
    result = prepare('# 标题\n\n![厚度](other.png)\n', fixture_evidence())
    assert any('登记' in str(issue) for issue in result['issues'])


@pytest.mark.parametrize('body', [
    'Before ![Result](plot.png) after with warning.',
    '> |A|B|\n> |---|---|\n> |1|2|\n>\n> : Nested',
    '- item\n\n  |A|B|\n  |---|---|\n  |1|2|\n\n  : Nested',
])
def test_mixed_image_text_and_nested_tables_are_rejected(body):
    assert prepare('# Title\n\n' + body)['issues']


@pytest.mark.parametrize('body', [
    'L5 passed, implementation section 6.1, quality_status=passed.',
    'reports/problems/demo/task_123/metadata.json',
    r'E:\项目\AutoMM\problems\demo\result.json',
    'ev_result123 warn_example task_123',
])
def test_internal_pipeline_text_is_not_public(body):
    assert prepare('# Title\n\n' + body)['issues']


def test_math_and_legitimate_reference_link_are_not_pipeline_leaks():
    assert not prepare('# Title\n\nLet $L5=x_1$; see [article](https://doi.org/10.1000/task_123).')['issues']


@pytest.mark.parametrize('part,fragment', [
    ('document', '<w:p><w:r><w:t>quality_status=passed</w:t></w:r></w:p>'),
    ('header1', '<w:p><w:r><w:t>reports/problems/demo/result.json</w:t></w:r></w:p>'),
    ('footer1', '<w:p><w:fldSimple w:instr="PAGE"><w:r><w:t>task_123</w:t></w:r></w:fldSimple></w:p>'),
    ('comments', '<w:comment><w:p><w:r><w:t>ev_private</w:t></w:r></w:p></w:comment>'),
    ('document', '<wp:docPr id="1" name="plot" descr="warn_private" title="result"/>'),
    ('customPart', '<w:t>task_private</w:t>'),
])
def test_public_docx_audit_reads_all_word_visible_parts(tmp_path, part, fragment):
    import zipfile

    from automm import paper_semantics
    path = tmp_path / 'leak.docx'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('word/' + part + '.xml',
                         '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
                         'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
                         + fragment + '</w:document>')
    audit = getattr(paper_semantics, 'audit_public_docx', None)
    assert callable(audit), 'DOCX 公开审计尚未实现'
    assert audit(path)['status'] == 'FAILED'


def test_abstract_whole_paragraph_bold_is_rejected():
    assert prepare('# Title\n\n## 摘要\n\n**厚度为 10.2 um，误差为 0.8%。**')['issues']


def test_visible_source_path_gate_excludes_image_resource_locations():
    path = 'C:/project/reports/problems/demo/plot.png'
    evidence = {'figures': [{'stable_id': 'fig1', 'path': path, 'evidence_id': 'ev_fig'}]}
    result = prepare('# Title\n\n![Result](' + path + ')\n\n<!-- evidence:ev_fig -->', evidence)
    assert not result['issues']


def test_normal_list_and_table_math_are_preserved():
    from automm.paper_semantics import nodes
    result = prepare('# Title\n\n- $x_1=2$\n\n| A | B |\n|---|---|\n| $y_2$ | 3 |\n\n: Results\n')
    assert not result['issues']
    assert [x['c'][1] for x in nodes(result['pandoc_ast']) if x['t'] == 'Math'] == ['x_1=2', 'y_2']
