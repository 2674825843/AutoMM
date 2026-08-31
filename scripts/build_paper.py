"""AutoMM 全自动论文构建命令行。"""

from __future__ import annotations

import argparse
import json

from automm.common import ROOT, relative
from automm.paper import (
    build_evidence_pack,
    prepare_paper_writing,
    validate_paper_markdown,
)
from automm.paper_integrity import load_version_evidence
from automm.problems import problem_dir
from automm.state import load_state


def _problem_id(value: str | None) -> str:
    problem_id = value or load_state().get("active_problem")
    if not problem_id:
        raise SystemExit("没有活动题目，请传入 --problem-id")
    return str(problem_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="从已验收证据生成数学建模论文")
    parser.add_argument("action", choices=["evidence", "draft", "validate", "render", "build", "rewrite"])
    parser.add_argument('--confirm-rewrite', action='store_true', help='用户明确授权从已验收证据重写论文')
    parser.add_argument("--problem-id")
    parser.add_argument("--version")
    args = parser.parse_args()
    problem_id = _problem_id(args.problem_id)
    root = problem_dir(problem_id) / "paper"

    if args.action == 'rewrite':
        if not args.confirm_rewrite:
            raise SystemExit('重新写作需要 --confirm-rewrite 明确授权')
        from automm.agent_runtime import apply_agent_commands, new_action_id
        from automm.runner import lock
        guard = lock()
        if not guard.acquire('user-paper-rewrite'):
            raise SystemExit('Runner 正在运行，不能重写')
        try:
            response = {'action_id': new_action_id(), 'commands': [
                {'name': 'request_paper_rewrite', 'arguments': {'reason': '用户明确请求按原生模板重写并交付'}}]}
            result = apply_agent_commands(response, {'problem_id': problem_id, 'user_authorized_rewrite': True})
            print(json.dumps(result, ensure_ascii=False, indent=2))
        finally:
            guard.release()
        return

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
    if args.version:
        version_dir = root / "versions" / args.version
    else:
        versions = sorted((root / "versions").glob("paper_v[0-9][0-9][0-9]"))
        if not versions:
            prepared = prepare_paper_writing(problem_id)
            version_dir = ROOT / prepared['version_dir']
        else:
            version_dir = versions[-1]
    evidence = load_version_evidence(version_dir)
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
