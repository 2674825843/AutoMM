from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from automm import paper
from automm.common import hash_json, read_json, write_json, write_text
from PIL import Image
from pypdf import PdfWriter

pytestmark = pytest.mark.integration


def _version(tmp_path: Path) -> Path:
    version = tmp_path / "paper_v001"
    version.mkdir()
    image = version / "figure.png"
    Image.new("RGB", (320, 180), "white").save(image)
    write_text(
        version / "paper.md",
        "# 测试论文\n\n## 模型\n\n公式为 $y=ax+b$。\n\n![测试图](figure.png)\n",
    )
    import hashlib
    evidence = {'figures': [{'path': 'figure.png', 'stable_id': 'figure1', 'evidence_id': 'ev_fig',
                             'sha256': hashlib.sha256(image.read_bytes()).hexdigest()}]}
    evidence['evidence_hash'] = hash_json(evidence)
    write_json(version / 'evidence_pack.json', evidence)
    write_json(version / 'writer_manifest.json', {'evidence_hash': evidence['evidence_hash']})
    return version


def _one_page_pdf(_docx: Path, pdf: Path, _timeout: int) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=595.276, height=841.89)
    with pdf.open("wb") as handle:
        writer.write(handle)


def test_pandoc_render_produces_editable_formula_image_docx_and_tex(tmp_path: Path) -> None:
    renderer = getattr(paper, "render_paper", None)
    if renderer is None:
        pytest.fail("render_paper 尚未实现")
    version = _version(tmp_path)

    result = renderer(
        version,
        {"minimum_pdf_pages": 1, "pdf_export_timeout_seconds": 5},
        pdf_exporter=_one_page_pdf,
    )

    assert result["status"] == "PASS"
    assert (version / "paper.docx").is_file()
    assert (version / "paper.tex").is_file()
    with zipfile.ZipFile(version / "paper.docx") as archive:
        document = archive.read("word/document.xml")
        media = [name for name in archive.namelist() if name.startswith("word/media/")]
    assert b"<m:oMath" in document
    assert len(media) == 1
    assert read_json(version / "render_report.json")["pdf_pages"] == 1
    assert result['styles']['status'] == 'PASS'
    assert result['evidence_hash'] == read_json(version / 'evidence_pack.json')['evidence_hash']
    assert result['public_audit']['status'] == 'PASS'


def test_missing_user_template_fails_without_default_fallback(tmp_path: Path) -> None:
    with pytest.raises((RuntimeError, FileNotFoundError), match='模板|template'):
        paper.render_paper(_version(tmp_path), {'reference_doc': 'missing-template.docx'},
                           pdf_exporter=_one_page_pdf)


@pytest.mark.parametrize("error", [RuntimeError("Word failed"), TimeoutError("Word timed out")])
def test_pdf_export_failure_preserves_docx_and_reports_failed_render(tmp_path: Path, error: Exception) -> None:
    renderer = getattr(paper, "render_paper", None)
    if renderer is None:
        pytest.fail("render_paper 尚未实现")
    version = _version(tmp_path)

    def failing_exporter(_docx: Path, _pdf: Path, _timeout: int) -> None:
        raise error

    result = renderer(
        version,
        {"minimum_pdf_pages": 1, "pdf_export_timeout_seconds": 5},
        pdf_exporter=failing_exporter,
    )

    assert result["status"] == "FAILED_RENDER"
    assert "Word" in result["errors"][0]
    assert (version / "paper.docx").is_file()
    assert (version / "paper.tex").is_file()
    assert not (version / "paper.pdf").exists()


def test_render_audits_actual_docx_before_pdf_export(tmp_path, monkeypatch):
    from automm import docx_styles
    from lxml import etree as ET
    version = _version(tmp_path)
    original = docx_styles.adapt_docx
    def leak_docx(path, *args):
        report = original(path, *args)
        with zipfile.ZipFile(path) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        xml = ET.fromstring(parts['word/document.xml'])
        ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        xml.find('.//' + ns + 't').text = 'quality_status=passed'
        parts['word/document.xml'] = ET.tostring(xml)
        with zipfile.ZipFile(path, 'w') as archive:
            for name, value in parts.items():
                archive.writestr(name, value)
        return report
    monkeypatch.setattr(docx_styles, 'adapt_docx', leak_docx)
    result = paper.render_paper(version, {'minimum_pdf_pages': 1}, pdf_exporter=_one_page_pdf)
    assert result['status'] != 'PASS'
    assert result['public_audit']['status'] == 'FAILED'
    assert not (version / 'paper.pdf').exists()


def test_render_refuses_snapshot_content_tampering(tmp_path):
    version = _version(tmp_path)
    snapshot = read_json(version / 'evidence_pack.json')
    snapshot['figures'][0]['title'] = 'changed'
    write_json(version / 'evidence_pack.json', snapshot)
    with pytest.raises(RuntimeError, match='证据|快照'):
        paper.render_paper(version, {'minimum_pdf_pages': 1}, pdf_exporter=_one_page_pdf)


def test_render_does_not_bind_old_docx_to_markdown_changed_during_conversion(tmp_path, monkeypatch):
    from automm import docx_styles
    version = _version(tmp_path)
    original = docx_styles.adapt_docx
    def change_source(path, *args):
        result = original(path, *args)
        (version / 'paper.md').write_text('# New unrendered source', encoding='utf-8')
        return result
    monkeypatch.setattr(docx_styles, 'adapt_docx', change_source)
    result = paper.render_paper(version, {'minimum_pdf_pages': 1}, pdf_exporter=_one_page_pdf)
    assert result['status'] != 'PASS'


def test_render_rejects_source_figure_changed_since_evidence_snapshot(tmp_path):
    version = _version(tmp_path)
    Image.new('RGB', (320, 180), 'blue').save(version / 'figure.png')
    with pytest.raises(RuntimeError, match='图|哈希|证据'):
        paper.render_paper(version, {'minimum_pdf_pages': 1}, pdf_exporter=_one_page_pdf)
