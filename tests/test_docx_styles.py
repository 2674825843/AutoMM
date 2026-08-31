from __future__ import annotations

import hashlib
import importlib
import importlib.util
import posixpath
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest
from lxml import etree as ET
from PIL import Image

TEMPLATE = Path(__file__).resolve().parents[1] / "数模论文标准模板.docx"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
W = "{" + NS["w"] + "}"
EXPECTED_IDS = {
    "title": "af5",
    "heading1": "1",
    "heading2": "2",
    "heading3": "3",
    "body": "a4",
    "image": "aff1",
    "figure_caption": "a1",
    "table_caption": "a0",
    "table": "afb",
    "table_text": "a9",
    "display_math": "aff7",
    "bibliography": "a",
    "ordered_list": "a3",
    "unordered_list": "a2",
    "code": "ac",
}
MANIFEST = {
    "figures": [{"number": 1, "title": "误差曲线"}, {"number": 2, "title": "成本曲线"}],
    "tables": [{"number": 1, "title": "模型结果"}],
}


def _api():
    assert importlib.util.find_spec("automm.docx_styles") is not None, "原生 Word 样式适配模块尚未实现"
    return importlib.import_module("automm.docx_styles")


def _parts(path):
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def _xml(parts, name="word/document.xml"):
    return ET.fromstring(parts[name])


def _replace_parts(path, updates):
    parts = _parts(path)
    parts.update(updates)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)


def _text(paragraph):
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def _paragraph(document, text):
    return next(p for p in document.xpath(".//w:p", namespaces=NS) if _text(p) == text)


def _value(element, path):
    node = element.find(path, NS)
    return None if node is None else node.get(W + "val")


def _render(tmp_path, markdown):
    pandoc = shutil.which("pandoc")
    if not pandoc:
        pytest.skip("真实样式集成测试需要 Pandoc")
    path = tmp_path / "probe.docx"
    result = subprocess.run(
        [pandoc, "--from=markdown", f"--reference-doc={TEMPLATE}", "-o", str(path)],
        input=markdown,
        text=True,
        encoding="utf-8",
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return path


@pytest.fixture
def semantic_docx(tmp_path):
    Image.new("RGB", (80, 40), "white").save(tmp_path / "figure.png")
    return _render(
        tmp_path,
        """::: {custom-style="Title"}
合成论文
:::

::: {custom-style="AutoMMUnnumberedHeading1"}
摘要
:::

::: {custom-style="Normal"}
这是**强调**和*斜体*，含有行内公式 $x^2$。
:::

::: {custom-style="heading 1"}
模型建立
:::

::: {custom-style="heading 2"}
参数估计
:::

::: {custom-style="heading 3"}
求解步骤
:::

$$
y = \\frac{x^2}{2}
$$

::: {custom-style="图片"}
![](figure.png){width=4cm}
:::

::: {custom-style="图注"}
误差曲线
:::

::: {custom-style="heading 1"}
结果分析
:::

::: {custom-style="图片"}
![](figure.png){width=4cm}
:::

::: {custom-style="图注"}
成本曲线
:::

::: {custom-style="表注"}
模型结果
:::

| 参数 | 数值 |
|:-----|-----:|
| 甲   | 1.0  |
| 乙   | 2.0  |

1. 首项
   1. 嵌套有序项
2. 次项

- 无序项
  - 嵌套无序项

```python
result = 1
```

::: {custom-style="heading 1"}
参考文献
:::

::: {custom-style="参考文献"}
[1] 作者甲. 第一文献.

作者乙. 第二文献.
:::
""",
    )


def test_inspection_resolves_real_names_inherited_numbering_and_body_section():
    result = _api().inspect_template(TEMPLATE)
    assert result["style_ids"] == EXPECTED_IDS
    assert result["body_section_index"] == 3
    assert result["effective_footers"]["default"] == "word/footer4.xml"
    assert result["effective_headers"]["default"] == "word/header4.xml"
    assert result["numbering"]["figure_caption"] == {"num_id": "1", "abstract_num_id": "1", "level": 8}
    assert result["numbering"]["table_caption"]["level"] == 7


@pytest.mark.parametrize("mutation", ["missing", "wrong_type"])
def test_required_styles_fail_closed_before_modifying_docx(tmp_path, semantic_docx, mutation):
    altered = tmp_path / "altered-template.docx"
    shutil.copy2(TEMPLATE, altered)
    styles = _xml(_parts(altered), "word/styles.xml")
    target = styles.xpath("w:style[w:name/@w:val='三线表']", namespaces=NS)[0]
    if mutation == "missing":
        styles.remove(target)
    else:
        target.set(W + "type", "paragraph")
    _replace_parts(altered, {"word/styles.xml": ET.tostring(styles)})
    original = semantic_docx.read_bytes()
    with pytest.raises(ValueError, match="三线表|table"):
        _api().adapt_docx(semantic_docx, altered)
    assert semantic_docx.read_bytes() == original


def test_original_styles_fonts_theme_and_template_bytes_are_preserved(semantic_docx):
    before = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
    result = _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    actual, expected = _parts(semantic_docx), _parts(TEMPLATE)
    assert result["status"] == "PASS"
    assert result["template_sha256"] == before
    assert hashlib.sha256(TEMPLATE.read_bytes()).hexdigest() == before
    for part in ("word/styles.xml", "word/fontTable.xml", "word/theme/theme1.xml"):
        assert actual[part] == expected[part]
    assert ET.tostring(_xml(actual, "word/styles.xml"), method="c14n") == ET.tostring(
        _xml(expected, "word/styles.xml"), method="c14n"
    )
    style_names = _xml(actual, "word/styles.xml").xpath("w:style/w:name/@w:val", namespaces=NS)
    assert not {"Body Text", "First Paragraph", "Compact", "Source Code", "AutoMMUnnumberedHeading1"} & set(style_names)


def test_semantics_emphasis_editable_math_image_geometry_and_code_survive(semantic_docx):
    before = _xml(_parts(semantic_docx))
    original_math = [ET.tostring(node, method="c14n") for node in before.xpath(".//m:oMath", namespaces=NS)]
    extents = [dict(node.attrib) for node in before.xpath(".//wp:extent", namespaces=NS)]
    _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    document = _xml(_parts(semantic_docx))
    for text, style in {
        "合成论文": "af5",
        "摘要": "1",
        "模型建立": "1",
        "参数估计": "2",
        "求解步骤": "3",
        "误差曲线": "a1",
        "成本曲线": "a1",
        "模型结果": "a0",
        "result = 1": "ac",
    }.items():
        assert _value(_paragraph(document, text), "w:pPr/w:pStyle") == style
    assert _value(_paragraph(document, "摘要"), "w:pPr/w:numPr/w:numId") == "0"
    assert _value(_paragraph(document, "参考文献"), "w:pPr/w:numPr/w:numId") == "0"
    assert document.xpath(".//w:r[w:t='强调']/w:rPr/w:b", namespaces=NS)
    assert document.xpath(".//w:r[w:t='斜体']/w:rPr/w:i", namespaces=NS)
    assert [ET.tostring(node, method="c14n") for node in document.xpath(".//m:oMath", namespaces=NS)] == original_math
    assert [dict(node.attrib) for node in document.xpath(".//wp:extent", namespaces=NS)] == extents
    assert all(_value(p, "w:pPr/w:pStyle") == "aff1" for p in document.xpath(".//w:p[.//w:drawing]", namespaces=NS))
    assert all(_value(p, "w:pPr/w:pStyle") == "aff7" for p in document.xpath(".//w:p[m:oMathPara]", namespaces=NS))


def test_direct_layout_removed_three_line_table_enabled_and_column_widths_kept(semantic_docx):
    original = _xml(_parts(semantic_docx))
    widths = original.xpath(".//w:tblGrid/w:gridCol/@w:w", namespaces=NS)
    body = _paragraph(original, "模型建立")
    ppr = body.find("w:pPr", NS)
    ET.SubElement(ppr, W + "spacing", {W + "line": "999"})
    ET.SubElement(ppr, W + "jc", {W + "val": "right"})
    run = body.find("w:r", NS)
    rpr = ET.SubElement(run, W + "rPr")
    ET.SubElement(rpr, W + "rFonts", {W + "ascii": "Arial"})
    ET.SubElement(rpr, W + "sz", {W + "val": "99"})
    _replace_parts(semantic_docx, {"word/document.xml": ET.tostring(original)})
    _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    document = _xml(_parts(semantic_docx))
    assert not document.xpath(".//w:body//w:pPr/w:spacing | .//w:body//w:pPr/w:jc", namespaces=NS)
    assert not document.xpath(".//w:body//w:rPr/w:rFonts | .//w:body//w:rPr/w:sz", namespaces=NS)
    assert document.xpath(".//w:tblGrid/w:gridCol/@w:w", namespaces=NS) == widths
    table = document.find(".//w:tbl", NS)
    assert _value(table, "w:tblPr/w:tblStyle") == "afb"
    assert table.find("w:tblPr/w:tblLook", NS).get(W + "firstRow") == "1"
    assert table.find("w:tblPr/w:tblLook", NS).get(W + "val") == "0620"
    assert not table.xpath(".//w:tcBorders | w:tblPr/w:tblBorders", namespaces=NS)
    assert all(_value(p, "w:pPr/w:pStyle") == "a9" for p in table.xpath(".//w:tc/w:p", namespaces=NS))


def test_caption_and_list_numbers_use_only_original_definitions_without_double_labels(semantic_docx):
    _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    parts = _parts(semantic_docx)
    document, numbering = _xml(parts), _xml(parts, "word/numbering.xml")
    original = _xml(_parts(TEMPLATE), "word/numbering.xml")
    assert [ET.tostring(x, method="c14n") for x in numbering.findall("w:abstractNum", NS)] == [
        ET.tostring(x, method="c14n") for x in original.findall("w:abstractNum", NS)
    ]

    def binding(text):
        p = _paragraph(document, text)
        num_id = _value(p, "w:pPr/w:numPr/w:numId")
        num = numbering.xpath("w:num[@w:numId=$id]", namespaces=NS, id=num_id)[0]
        return num_id, _value(num, "w:abstractNumId"), _value(p, "w:pPr/w:numPr/w:ilvl")

    figure = binding("误差曲线")
    assert figure[1:] == ("1", "8")
    assert binding("成本曲线") == figure
    table = binding("模型结果")
    assert table[1:] == ("1", "7")
    assert figure[0] != table[0] and figure[0] != "1" and table[0] != "1"
    assert binding("首项")[1:] == ("4", "0")
    assert binding("嵌套有序项")[1:] == ("4", "1")
    assert binding("无序项")[1:] == ("2", "0")
    assert binding("嵌套无序项")[1:] == ("2", "1")
    assert binding("作者甲. 第一文献.")[1:] == ("0", "0")
    assert binding("作者乙. 第二文献.") == binding("作者甲. 第一文献.")


def test_body_section_inherits_page_footer_restarts_at_one_and_all_relationships_resolve(semantic_docx):
    _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    parts = _parts(semantic_docx)
    document = _xml(parts)
    sections = document.xpath(".//w:sectPr", namespaces=NS)
    assert len(sections) == 1
    section = sections[0]
    assert section.find("w:pgNumType", NS).get(W + "start") == "1"
    assert section.find("w:pgMar", NS).get(W + "left") == "1418"
    rels = {rel.get("Id"): rel for rel in _xml(parts, "word/_rels/document.xml.rels")}
    footer_ref = section.xpath("w:footerReference[@w:type='default']", namespaces=NS)[0]
    footer_part = posixpath.normpath("word/" + rels[footer_ref.get("{" + NS["r"] + "}id")].get("Target"))
    assert "PAGE" in "".join(_xml(parts, footer_part).xpath(".//w:instrText/text()", namespaces=NS))
    assert _text(document).startswith("合成论文摘要")
    assert "承诺书" not in _text(document)
    for name, data in parts.items():
        if not name.endswith(".rels"):
            continue
        parent = "" if name == "_rels/.rels" else posixpath.dirname(posixpath.dirname(name))
        for rel in ET.fromstring(data):
            if rel.get("TargetMode") != "External":
                target = posixpath.normpath(posixpath.join(parent, rel.get("Target"))).lstrip("/")
                assert target in parts, (name, target)
    ids = set(_xml(parts, "word/styles.xml").xpath("w:style/@w:styleId", namespaces=NS))
    for name, data in parts.items():
        if name.startswith("word/") and name.endswith(".xml"):
            root = ET.fromstring(data)
            refs = root.xpath(".//w:pStyle/@w:val | .//w:rStyle/@w:val | .//w:tblStyle/@w:val", namespaces=NS)
            assert set(refs) <= ids, (name, set(refs) - ids)


@pytest.mark.parametrize(
    "manifest",
    [
        {"figures": [{"number": 2, "title": "误差曲线"}], "tables": []},
        {
            "figures": [{"number": 1, "title": "错误标题"}, {"number": 2, "title": "成本曲线"}],
            "tables": MANIFEST["tables"],
        },
    ],
)
def test_caption_manifest_mismatch_fails_without_partial_docx_write(semantic_docx, manifest):
    original = semantic_docx.read_bytes()
    with pytest.raises(ValueError, match="caption|题注|manifest"):
        _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=manifest)
    assert semantic_docx.read_bytes() == original


def test_default_pandoc_headings_and_implicit_figure_captions_are_adapted(tmp_path):
    Image.new("RGB", (80, 40), "white").save(tmp_path / "figure.png")
    path = _render(tmp_path, "# 默认题目\n\n## 模型\n\n### 子节\n\n正文\n\n![默认图](figure.png)\n")
    _api().adapt_docx(path, TEMPLATE)
    document = _xml(_parts(path))
    assert _value(_paragraph(document, "默认题目"), "w:pPr/w:pStyle") == "af5"
    assert _value(_paragraph(document, "模型"), "w:pPr/w:pStyle") == "1"
    assert _value(_paragraph(document, "子节"), "w:pPr/w:pStyle") == "2"
    assert _value(_paragraph(document, "正文"), "w:pPr/w:pStyle") == "a4"
    assert _value(_paragraph(document, "默认图"), "w:pPr/w:pStyle") == "a1"


def test_dangling_image_relationship_fails_before_output_is_replaced(semantic_docx):
    document = _xml(_parts(semantic_docx))
    document.find(".//a:blip", NS).set("{" + NS["r"] + "}embed", "rIdDoesNotExist")
    _replace_parts(semantic_docx, {"word/document.xml": ET.tostring(document)})
    before = semantic_docx.read_bytes()
    with pytest.raises(ValueError, match="关系|relationship"):
        _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    assert semantic_docx.read_bytes() == before


def test_caption_manifest_does_not_strip_legitimate_title_starting_with_figure_number(tmp_path, semantic_docx):
    document = _xml(_parts(semantic_docx))
    title = "图2025年度误差分析"
    _paragraph(document, "误差曲线").find("w:r/w:t", NS).text = title
    _replace_parts(semantic_docx, {"word/document.xml": ET.tostring(document)})
    manifest = {
        "figures": [{"number": 1, "title": title}, {"number": 2, "title": "成本曲线"}],
        "tables": MANIFEST["tables"],
    }
    _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=manifest)
    assert _paragraph(_xml(_parts(semantic_docx)), title) is not None


def test_repeated_adaptation_is_semantically_idempotent(semantic_docx):
    _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    first = _parts(semantic_docx)
    _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    second = _parts(semantic_docx)
    for part in ("word/document.xml", "word/numbering.xml", "word/styles.xml", "[Content_Types].xml"):
        assert ET.tostring(_xml(first, part), method="c14n") == ET.tostring(_xml(second, part), method="c14n")


def test_template_target_is_never_writable():
    before = TEMPLATE.read_bytes()
    with pytest.raises(ValueError, match="模板"):
        _api().adapt_docx(TEMPLATE, TEMPLATE)
    assert TEMPLATE.read_bytes() == before


def test_header_dependency_closure_is_copied_without_overwriting_body_image(tmp_path, semantic_docx):
    from copy import deepcopy

    template = tmp_path / "template-with-header-image.docx"
    shutil.copy2(TEMPLATE, template)
    body_parts = _parts(semantic_docx)
    body_image = next(name for name in body_parts if name.startswith("word/media/"))
    header = _xml(_parts(template), "word/header4.xml")
    drawing = deepcopy(_xml(body_parts).find(".//w:drawing", NS))
    drawing.find(".//a:blip", NS).set("{" + NS["r"] + "}embed", "rIdHeaderImage")
    ET.SubElement(header.find("w:p", NS), W + "r").append(drawing)
    rels = ET.Element("{" + NS["rel"] + "}Relationships", nsmap={None: NS["rel"]})
    ET.SubElement(
        rels,
        "{" + NS["rel"] + "}Relationship",
        {
            "Id": "rIdHeaderImage",
            "Type": NS["r"] + "/image",
            "Target": posixpath.relpath(body_image, "word"),
        },
    )
    types = _xml(_parts(template), "[Content_Types].xml")
    ct = "{http://schemas.openxmlformats.org/package/2006/content-types}"
    ET.SubElement(types, ct + "Override", {"PartName": "/" + body_image, "ContentType": "image/png"})
    header_image = b"different header resource: must not replace body image"
    _replace_parts(
        template,
        {
            "word/header4.xml": ET.tostring(header),
            body_image: header_image,
            "word/_rels/header4.xml.rels": ET.tostring(rels),
            "[Content_Types].xml": ET.tostring(types),
        },
    )
    _api().adapt_docx(semantic_docx, template, publication_manifest=MANIFEST)
    output = _parts(semantic_docx)
    assert output[body_image] == body_parts[body_image]
    imported = [name for name, data in output.items() if data == header_image]
    assert len(imported) == 1 and imported[0] != body_image
    root = _xml(output)
    relationships = {r.get("Id"): r for r in _xml(output, "word/_rels/document.xml.rels")}
    ref = root.xpath(".//w:sectPr/w:headerReference[@w:type='default']", namespaces=NS)[0]
    header_part = posixpath.normpath("word/" + relationships[ref.get("{" + NS["r"] + "}id")].get("Target"))
    header_rels = posixpath.join(posixpath.dirname(header_part), "_rels", posixpath.basename(header_part) + ".rels")
    dependency = _xml(output, header_rels)[0]
    assert posixpath.normpath(posixpath.join(posixpath.dirname(header_part), dependency.get("Target"))) == imported[0]


def test_unused_template_example_media_and_orphan_header_parts_are_removed(semantic_docx):
    before = _parts(semantic_docx)
    assert "word/media/image1.wmf" in before  # Pandoc keeps unused reference-doc media.
    _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    output = _parts(semantic_docx)
    assert "word/media/image1.wmf" not in output
    assert not any(name.startswith("word/header") for name in output)
    assert [name for name in output if name.startswith("word/media/")] == [
        name for name in before if name.startswith("word/media/") and name.endswith(".png")
    ]
    assert b"image1.wmf" not in output["[Content_Types].xml"]


def test_duplicate_relationship_identifiers_are_not_accepted(semantic_docx):
    from copy import deepcopy

    parts = _parts(semantic_docx)
    relationships = _xml(parts, "word/_rels/document.xml.rels")
    used_image = next(rel for rel in relationships if rel.get("Target", "").endswith(".png"))
    relationships.append(deepcopy(used_image))
    _replace_parts(semantic_docx, {"word/_rels/document.xml.rels": ET.tostring(relationships)})
    before = semantic_docx.read_bytes()
    with pytest.raises(ValueError, match="重复|关系"):
        _api().adapt_docx(semantic_docx, TEMPLATE, publication_manifest=MANIFEST)
    assert semantic_docx.read_bytes() == before


def test_template_inheritance_cycle_fails_without_writing_target(tmp_path, semantic_docx):
    template = tmp_path / "cyclic.docx"
    shutil.copy2(TEMPLATE, template)
    styles = _xml(_parts(template), "word/styles.xml")
    figure = styles.xpath("w:style[w:name/@w:val='图注']", namespaces=NS)[0]
    figure.find("w:basedOn", NS).set(W + "val", "a1")
    _replace_parts(template, {"word/styles.xml": ET.tostring(styles)})
    with pytest.raises(ValueError, match="继承"):
        _api().adapt_docx(semantic_docx, template)


def test_style_map_resolves_replacement_name_without_changing_template(tmp_path, semantic_docx):
    template = tmp_path / "renamed.docx"
    shutil.copy2(TEMPLATE, template)
    styles = _xml(_parts(template), "word/styles.xml")
    body_name = styles.xpath("w:style[w:name/@w:val='Normal']/w:name", namespaces=NS)[0]
    body_name.set(W + "val", "论文正文")
    _replace_parts(template, {"word/styles.xml": ET.tostring(styles)})
    original = template.read_bytes()
    result = _api().adapt_docx(semantic_docx, template, {"body": "论文正文"}, MANIFEST)
    assert result["style_ids"]["body"] == "a4"
    assert template.read_bytes() == original


def test_heading_levels_restart_from_one_in_fresh_body_numbering(tmp_path):
    path = _render(tmp_path, '# Title\n\n## Chapter one\n\n### First child\n\n#### First grandchild\n\n'
                            '## Chapter two\n\n### Second chapter child\n')
    _api().adapt_docx(path, TEMPLATE)
    document = _xml(_parts(path))
    numbering = _xml(_parts(path), 'word/numbering.xml')
    bindings = []
    for label, level in [('Chapter one', '0'), ('First child', '1'), ('First grandchild', '2'),
                         ('Chapter two', '0'), ('Second chapter child', '1')]:
        para = _paragraph(document, label)
        num_id = _value(para, 'w:pPr/w:numPr/w:numId')
        assert num_id is not None, '正文标题没有新编号实例，继承了模板历史计数'
        assert _value(para, 'w:pPr/w:numPr/w:ilvl') == level
        num = numbering.xpath('w:num[@w:numId=$id]', namespaces=NS, id=num_id)[0]
        assert num.xpath('w:lvlOverride[@w:ilvl=$level]/w:startOverride/@w:val', namespaces=NS, level=level) == ['1']
        bindings.append(num_id)
    assert len(set(bindings)) == 1
