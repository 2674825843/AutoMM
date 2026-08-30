# ruff: noqa: E501 -- 测试夹具保留真实论文段落，避免拼接掩盖占位符边界。
from __future__ import annotations

from pathlib import Path

import pytest
from automm import paper
from automm.common import read_json, write_text

pytestmark = pytest.mark.unit


def _validate(*args):
    function = getattr(paper, "validate_paper_markdown", None)
    if function is None:
        pytest.fail("validate_paper_markdown 尚未实现")
    return function(*args)


def _evidence() -> dict:
    return {
        "problem_id": "paper-demo",
        "evidence_hash": "a" * 64,
        "questions": [
            {
                "question_id": "prob01",
                "warnings": ["样本量较小"],
                "artifact_evidence_ids": ["ev_artifact_result"],
            }
        ],
        "artifacts": [{"evidence_id": "ev_artifact_result", "path": "result.json"}],
        "figures": [
            {
                "evidence_id": "ev_figure_fit",
                "stable_id": "prob01_fit",
                "question_id": "prob01",
                "path": "fit.png",
            }
        ],
        "citations": [{"evidence_id": "ev_citation_l01", "citation_id": "L01"}],
    }


def _valid_markdown() -> str:
    return """# 合成数学建模题

## 摘要

针对 prob01 的容量估计问题，建立线性约束模型，得到厚度 10.2 um；相对误差为 0.8%，并通过扰动检验。<!-- evidence:ev_artifact_result -->

## 关键词

容量约束；最小二乘；敏感性分析

## 问题重述

在给定观测下估计系统参数。

## 问题分析与总体流程

先识别变量，再建立模型，最后验证误差。

## 模型假设

观察期内参数恒定 [@L01]。<!-- evidence:ev_citation_l01 -->

## 符号说明

| 符号 | 含义 | 单位 |
|---|---|---|
| t | 厚度 | um |

## 数据说明与预处理

对异常值进行规则化筛查。

## prob01 模型建立、求解与结果

问题分析表明需要估计厚度。模型为 $y=ax$，其中 $a$ 表示响应系数，单位为 s^-1。求解得到厚度 10.2 um。<!-- evidence:ev_artifact_result -->

![prob01_fit 拟合结果](fit.png)

图 prob01_fit 展示拟合值与观测值的一致性，相对误差 0.8% 低于验收阈值，因此支持厚度结论。<!-- evidence:ev_figure_fit -->

### prob01 可靠性与结论

扰动检验表明结论稳定；但样本量较小，结果外推需谨慎。<!-- evidence:ev_artifact_result -->

## 跨小问一致性、稳健性与消融分析

本题只有一个小问；噪声扰动下结论保持稳定。

## 模型评价、局限与推广

模型参数少且可解释；样本量较小，推广到分布漂移场景前需重新标定。

## 结论

prob01 的厚度估计为 10.2 um，误差 0.8%。<!-- evidence:ev_artifact_result -->

## 参考文献

[@L01] A. Author. A verified method. Journal, 2024.

## 附录：复现说明、文件清单和核心代码索引

运行论文构建命令即可从证据包复现本论文。
"""


def test_complete_evidence_closed_markdown_passes(tmp_path: Path) -> None:
    version = tmp_path / "paper_v001"
    version.mkdir()
    write_text(version / "paper.md", _valid_markdown())

    result = _validate("paper-demo", version, _evidence())

    assert result["status"] == "PASS"
    assert result["errors"] == []
    assert read_json(version / "validation.json")["status"] == "PASS"


def test_paraphrased_warning_passes_with_stable_warning_marker(tmp_path: Path) -> None:
    version = tmp_path / "paper_v001"
    version.mkdir()
    text = _valid_markdown().replace(
        "但样本量较小，结果外推需谨慎。",
        "但现有样本不足以支持跨分布外推，应用到新场景前应重新标定。<!-- warning:warn_prob01_f26fb05b36f7 -->",
    ).replace("样本量较小，推广到分布漂移场景前需重新标定。", "推广到分布漂移场景前需重新标定。")
    write_text(version / "paper.md", text)

    result = _validate("paper-demo", version, _evidence())

    assert result["status"] == "PASS"
    assert result["errors"] == []


def test_figure_explanation_accepts_markdown_code_id_and_natural_verb(tmp_path: Path) -> None:
    version = tmp_path / "paper_v001"
    version.mkdir()
    text = _valid_markdown().replace(
        "图 prob01_fit 展示拟合值与观测值的一致性",
        "图 `prob01_fit` 给出拟合值与观测值的一致性",
    )
    write_text(version / "paper.md", text)

    result = _validate("paper-demo", version, _evidence())

    assert result["status"] == "PASS"
    assert result["errors"] == []


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("ev_artifact_result", "ev_unknown", "未知 evidence ID"),
        ("[@L01]", "[@UNKNOWN]", "未登记引用"),
        ("prob01_fit", "prob01_unknown", "缺少审核图表"),
        ("样本量较小", "数据条件理想", "未披露警告"),
        ("## prob01 模型建立、求解与结果", "## 其他模型", "缺少小问章节"),
        ("参数恒定", "TODO", "占位符"),
        ("图 prob01_fit 展示拟合值与观测值的一致性", "见上图", "图表缺少正文解释"),
    ],
)
def test_validator_rejects_specific_paper_integrity_breaks(tmp_path: Path, old: str, new: str, message: str) -> None:
    version = tmp_path / "paper_v001"
    version.mkdir()
    write_text(version / "paper.md", _valid_markdown().replace(old, new))

    result = _validate("paper-demo", version, _evidence())

    assert result["status"] == "NEEDS_REVISION"
    assert any(message in error for error in result["errors"])
