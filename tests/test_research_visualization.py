from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from automm.common import read_yaml, write_yaml
from automm.problems import create_assumption_version, problem_dir
from automm.research import add_candidate, decide_reference, finish_round, load_pool, start_round, verify_reference
from automm.visualization import inspect_png, register_figure, stable_figure_id
from PIL import Image
from run_sanity_check import inspect_numeric_file

pytestmark = pytest.mark.unit


def test_research_round_deduplicates_and_archives_used_reference(
    initialized_problem: tuple[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    problem_id, _ = initialized_problem
    start_round(problem_id, "prob01", "linear model capacity")
    candidate = {"id": "ref-1", "title": "Linear Models", "source": "journal", "doi": "10.1/example"}
    add_candidate(problem_id, "prob01", candidate)
    with pytest.raises(RuntimeError, match="重复"):
        add_candidate(problem_id, "prob01", {**candidate, "id": "ref-2"})
    monkeypatch.setattr("automm.research._fetch_json", lambda url, timeout: {"message": {"title": ["Linear Models"]}})
    assert verify_reference(problem_id, "prob01", "ref-1")["verified"] is True
    decide_reference(problem_id, "prob01", "ref-1", "used", "支持关键假设")
    finish_round(problem_id, "prob01", "all_candidates_decided")
    assert load_pool(problem_id, "prob01")["dry"] is True
    citations = read_yaml(problem_dir(problem_id) / "citations.yaml")["references"]
    assert [item["id"] for item in citations] == ["ref-1"]


def test_key_assumption_requires_verified_used_reference(initialized_problem: tuple[str, Path]) -> None:
    from automm.research import check_key_assumptions

    problem_id, _ = initialized_problem
    version_dir = create_assumption_version(problem_id, "prob01")
    version = read_yaml(version_dir / "version.yaml")
    version["assumptions"] = [{"id": "a1", "key": True, "reference_ids": ["ref-1"]}]
    write_yaml(version_dir / "version.yaml", version)
    assert check_key_assumptions(problem_id, "prob01")["passed"] is False
    pool_path = problem_dir(problem_id) / "prob01" / "shared" / "literature_pool.yaml"
    pool = read_yaml(pool_path)
    pool["items"] = [{"id": "ref-1", "verified": True, "status": "used"}]
    write_yaml(pool_path, pool)
    assert check_key_assumptions(problem_id, "prob01")["passed"] is True


def test_key_assumption_accepts_cross_question_used_source(initialized_problem: tuple[str, Path]) -> None:
    from automm.research import check_key_assumptions

    problem_id, _ = initialized_problem
    version_dir = create_assumption_version(problem_id, "prob01")
    version = read_yaml(version_dir / "version.yaml")
    # 关键假设引用一个"跨问复用来源"：不在本问池，但在题目级 citations.yaml 登记为 verified+used。
    # 该场景模拟 prob03 的 inherited/跨问假设（如 C16 引用前问 L01/L06/L07），不应被误判为无文献支撑。
    version["assumptions"] = [{"id": "a1", "key": True, "reference_ids": ["L06"]}]
    write_yaml(version_dir / "version.yaml", version)
    # 本问池放一篇 used 以满足 minimum 数量门禁；题目级 citations.yaml 记录跨问已用来源（真实格式）。
    pool_path = problem_dir(problem_id) / "prob01" / "shared" / "literature_pool.yaml"
    pool = read_yaml(pool_path)
    pool["items"] = [{"id": "ref-p", "verified": True, "status": "used"}]
    write_yaml(pool_path, pool)
    citations_path = problem_dir(problem_id) / "citations.yaml"
    citations = read_yaml(citations_path, {"references": []})
    citations["references"] = [{"citation_id": "L06", "usage_status": "used", "metadata_status": "verified"}]
    write_yaml(citations_path, citations)
    assert check_key_assumptions(problem_id, "prob01")["passed"] is True


def test_key_assumption_rejects_new_c_level_in_citations(initialized_problem: tuple[str, Path]) -> None:
    from automm.research import check_key_assumptions

    problem_id, _ = initialized_problem
    version_dir = create_assumption_version(problem_id, "prob01")
    version = read_yaml(version_dir / "version.yaml")
    version["assumptions"] = [{"id": "a1", "key": True, "reference_ids": ["L48"]}]
    write_yaml(version_dir / "version.yaml", version)
    pool_path = problem_dir(problem_id) / "prob01" / "shared" / "literature_pool.yaml"
    pool = read_yaml(pool_path)
    pool["items"] = [{"id": "ref-p", "verified": True, "status": "used"}]
    write_yaml(pool_path, pool)
    citations_path = problem_dir(problem_id) / "citations.yaml"
    citations = read_yaml(citations_path, {"references": []})
    # C 级 new：verified 但未 used → 关键假设文献仍不满足，应被门禁拒绝。
    citations["references"] = [{"citation_id": "L48", "usage_status": "new", "metadata_status": "verified"}]
    write_yaml(citations_path, citations)
    assert check_key_assumptions(problem_id, "prob01")["passed"] is False


def test_png_quality_and_stable_id(initialized_problem: tuple[str, Path], project_root: Path) -> None:
    problem_id, _ = initialized_problem
    figure_path = project_root / "problems" / problem_id / "prob01" / "figure.png"
    pixels = np.zeros((480, 800, 3), dtype=np.uint8)
    pixels[:, :, 0] = np.arange(800, dtype=np.uint16)[None, :] % 256
    Image.fromarray(pixels).save(figure_path)
    report = inspect_png(figure_path, problem_id, "prob01")
    assert report["status"] == "passed"
    style = {"palette": "publication", "three_dimensional": True}
    first = stable_figure_id(
        problem_id=problem_id,
        question_id="prob01",
        kind="surface",
        title="响应曲面",
        source_hash="abc",
        x="x",
        y=["y", "z"],
        style=style,
    )
    second = stable_figure_id(
        problem_id=problem_id,
        question_id="prob01",
        kind="surface",
        title="响应曲面",
        source_hash="abc",
        x="x",
        y=["y", "z"],
        style=style,
    )
    assert first == second
    register_figure(problem_id, {"stable_id": first, "path": figure_path.relative_to(project_root).as_posix()})
    assert len(read_yaml(problem_dir(problem_id) / "figures.yaml")["figures"]) == 1


def test_blank_png_fails_quality(initialized_problem: tuple[str, Path], project_root: Path) -> None:
    problem_id, _ = initialized_problem
    path = project_root / "problems" / problem_id / "blank.png"
    Image.new("RGB", (800, 480), "white").save(path)
    assert inspect_png(path, problem_id, "prob01")["status"] == "failed"


def test_sanity_numeric_check_warns_for_csv_missing_but_rejects_infinity(project_root: Path) -> None:
    missing_path = project_root / "runtime" / "explicit-na.csv"
    missing_path.write_text("model,value\nM1,\nM2,1.0\n", encoding="utf-8")
    missing = inspect_numeric_file(missing_path)
    assert missing["finite"] is True
    assert missing["missing_numeric_count"] == 1
    assert missing["infinite_numeric_count"] == 0

    infinite_path = project_root / "runtime" / "infinite.csv"
    infinite_path.write_text("value\ninf\n", encoding="utf-8")
    infinite = inspect_numeric_file(infinite_path)
    assert infinite["finite"] is False
    assert infinite["infinite_numeric_count"] == 1
