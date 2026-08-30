from __future__ import annotations

from pathlib import Path

import pytest
from automm.llm.dsh import DshHeadlessProvider

pytestmark = pytest.mark.unit


def test_prepare_bypasses_cmd_wrapper_for_multiline_prompt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    wrapper = tmp_path / "dsh.CMD"
    wrapper.write_text("@echo off\n", encoding="utf-8")
    entrypoint = tmp_path / "node_modules" / "@deepseek-ai" / "dsh" / "lib" / "bin.js"
    entrypoint.parent.mkdir(parents=True)
    entrypoint.write_text("", encoding="utf-8")
    node = tmp_path / "node.exe"
    node.write_bytes(b"")

    provider = DshHeadlessProvider({"profile": "headless"})
    monkeypatch.setattr(provider, "_executable", lambda: str(wrapper))
    monkeypatch.setattr("automm.llm.dsh.shutil.which", lambda name: str(node) if name == "node" else None)
    prompt = "第一行同步动作。\n当前动作 ID：act-current"

    invocation = provider.prepare(prompt, tmp_path / "response.json")

    assert invocation.command == [
        str(node),
        str(entrypoint),
        "--profile",
        "headless",
        prompt,
    ]
