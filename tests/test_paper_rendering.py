from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from automm import paper
from automm.common import read_json, write_text
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
