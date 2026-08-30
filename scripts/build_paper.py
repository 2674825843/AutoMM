"""AutoMM 全自动论文构建命令行。"""

from __future__ import annotations

import argparse
import json

from automm.common import read_json, relative
from automm.paper import (
    build_evidence_pack,
    create_paper_version,
    generate_evidence_markdown,
    prepare_paper_writing,
    validate_paper_markdown,
)
from automm.problems import problem_dir
from automm.state import load_state


def _problem_id(value: str | None) -> str:
    problem_id = value or load_state().get("active_problem")
    if not problem_id:
        raise SystemExit("没有活动题目，请传入 --problem-id")
    return str(problem_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="从已验收证据生成数学建模论文")
    parser.add_argument("action", choices=["evidence", "draft", "validate", "render", "build"])
    parser.add_argument("--problem-id")
    parser.add_argument("--version")
    args = parser.parse_args()
    problem_id = _problem_id(args.problem_id)
    root = problem_dir(problem_id) / "paper"

    if args.action == "evidence":
        evidence = build_evidence_pack(problem_id)
        print(
            json.dumps(
                {"evidence": relative(root / "evidence" / "evidence_pack.json"), "hash": evidence["evidence_hash"]},
                ensure_ascii=False,
            )
        )
        return
    if args.action == "draft":
        print(json.dumps(prepare_paper_writing(problem_id), ensure_ascii=False, indent=2))
        return
    evidence = read_json(root / "evidence" / "evidence_pack.json")
    if args.version:
        version_dir = root / "versions" / args.version
    else:
        versions = sorted((root / "versions").glob("paper_v[0-9][0-9][0-9]"))
        if not versions:
            _, version_dir = create_paper_version(problem_id)
            generate_evidence_markdown(problem_id, version_dir, evidence)
        else:
            version_dir = versions[-1]
    validation = validate_paper_markdown(problem_id, version_dir, evidence)
    if validation["status"] != "PASS":
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    if args.action == "validate":
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return
    from automm.paper import render_paper

    rendered = render_paper(version_dir)
    print(json.dumps({"validation": validation, "render": rendered}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
