# AutoMM Paper Writer Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在跨小问审查通过后，自动从已验收证据生成完整 Markdown 论文，并派生可编辑 DOCX、TEX 和由 Word 导出的 PDF。

**Architecture:** 新增 `automm.paper` 深模块，依次负责 Evidence Pack、不可覆盖版本、确定性校验、Pandoc 渲染和 Word PDF 导出；Writer Agent 只消费 Evidence Pack 与白名单文件。Runner 在 `paper_writing` 与 `paper_validation` 两个全局阶段调度这些能力，并仅在全部门禁通过后进入 `completed`。

**Tech Stack:** Python 3.11、PyYAML、Pandoc、python-docx、Microsoft Word COM、pytest、JSON/YAML、Markdown/LaTeX。

**Spec:** `docs/superpowers/specs/2026-08-30-paper-writer-agent-design.md`

## Global Constraints

- 主写作源固定为 Markdown，主交付物固定为 DOCX，附加输出为 PDF 和 TEX。
- Writer 不运行模型计算，不修改题面、假设、公式、结果、图表、引用 registry 或 manifest。
- 每个关键事实必须来自 Evidence Pack；未知 evidence、citation 或 figure ID 必须失败。
- 论文版本目录为 `reports/problems/<problem_id>/paper/versions/paper_vNNN/`，不得覆盖旧版本。
- `paper.pdf` 必须由 Microsoft Word 从同版本 `paper.docx` 导出。
- 所有 Harness invariant 严格失败；状态只能由 Runner handler 更新。
- daemon 在实现和验收期间保持暂停，全部验证通过后才执行 RESUME。

---

### Task 1: Evidence Pack 与版本目录

**Files:**
- Create: `scripts/automm/paper.py`
- Create: `tests/test_paper_evidence.py`

**Interfaces:**
- Produces: `build_evidence_pack(problem_id: str) -> dict[str, Any]`
- Produces: `create_paper_version(problem_id: str) -> tuple[str, Path]`
- Consumes: `problem_state.json`、小问 manifest、接受版本目录、task、figure 与 citation registries。

- [ ] **Step 1: 写失败测试**：构造通过门禁的合成题目，断言证据包仅收录接受版本、文件 SHA-256、sanity 警告与审核通过图表；另断言 stale、未通过 L5、缺图、缺引用和 NaN/Inf 会拒绝构建。
- [ ] **Step 2: 验证 RED**：运行 `pytest tests/test_paper_evidence.py -q`，预期因 `automm.paper` 不存在而失败。
- [ ] **Step 3: 最小实现**：实现文件哈希、门禁、事实 ID、证据 JSON/Markdown 以及单调递增且不覆盖的版本目录。
- [ ] **Step 4: 验证 GREEN**：运行 `pytest tests/test_paper_evidence.py -q`，预期全部通过。
- [ ] **Step 5: 提交**：只提交本任务的生产代码和测试。

### Task 2: Markdown 契约与确定性校验

**Files:**
- Modify: `scripts/automm/paper.py`
- Create: `tests/test_paper_validation.py`

**Interfaces:**
- Produces: `validate_paper_markdown(problem_id: str, version_dir: Path, evidence: dict[str, Any]) -> dict[str, Any]`
- Consumes: 带 `<!-- evidence:... -->`、`[@citation]` 和 figure stable ID 的 `paper.md`。

- [ ] **Step 1: 写失败测试**：断言完整章节与全部小问可通过；未知证据 ID、未知引用、未审核图、未披露警告、占位符、缺小问、无图表解释会得到 `NEEDS_REVISION`。
- [ ] **Step 2: 验证 RED**：运行 `pytest tests/test_paper_validation.py -q`，预期缺少校验函数而失败。
- [ ] **Step 3: 最小实现**：实现结构、证据、引用、图表、警告和占位符检查，写入版本内 `validation.json`。
- [ ] **Step 4: 验证 GREEN**：运行论文校验测试与 Evidence 测试，预期全部通过。
- [ ] **Step 5: 提交**：只提交校验实现和测试。

### Task 3: Writer Agent 与可复现 Markdown 生成

**Files:**
- Modify: `agents/paper-writer.md`
- Modify: `skills/paper-writing/SKILL.md`
- Modify: `config/agent_registry.yaml`
- Modify: `config/agent_runtime.yaml`
- Modify: `templates/paper_template.md`
- Modify: `scripts/automm/paper.py`
- Replace: `scripts/build_paper.py`
- Create: `tests/test_paper_writer.py`

**Interfaces:**
- Produces: `prepare_paper_writing(problem_id: str) -> dict[str, Any]`
- Produces: `generate_evidence_markdown(problem_id: str, version_dir: Path, evidence: dict[str, Any]) -> Path`
- CLI: `python scripts/build_paper.py evidence|draft|validate|render|build --problem-id <id>`。

- [ ] **Step 1: 写失败测试**：从合成 Evidence Pack 生成无占位符、覆盖全部章节、小问、数字、警告、图表和参考文献的完整 Markdown；断言生成器不会读取 Evidence Pack 外的事实路径。
- [ ] **Step 2: 验证 RED**：运行 `pytest tests/test_paper_writer.py -q`，预期缺少接口而失败。
- [ ] **Step 3: 最小实现**：启用 Agent、更新专职说明和 Skill；实现确定性初稿作为可靠降级路径，Writer 可在同一契约内润色但不得越界。
- [ ] **Step 4: 验证 GREEN**：运行 Writer、Evidence、Validation 测试，预期全部通过。
- [ ] **Step 5: 提交**：只提交 Writer 契约、CLI、模板和测试。

### Task 4: DOCX、TEX 与 PDF 渲染

**Files:**
- Modify: `scripts/automm/paper.py`
- Modify: `config/paper.yaml`
- Create: `templates/cumcm_reference.docx`
- Create: `scripts/create_reference_doc.py`
- Create: `tests/test_paper_rendering.py`

**Interfaces:**
- Produces: `render_paper(version_dir: Path, config: dict[str, Any], *, pdf_exporter: Callable | None = None) -> dict[str, Any]`
- Produces: `export_docx_to_pdf(docx_path: Path, pdf_path: Path, timeout_seconds: int) -> None`
- Produces: `inspect_rendered_paper(version_dir: Path, minimum_pdf_pages: int) -> dict[str, Any]`。

- [ ] **Step 1: 写失败测试**：真实 Pandoc 生成可解析 DOCX/TEX，断言 DOCX 含 OMML；注入 PDF exporter 验证成功、异常和超时保留 DOCX 且报告 `FAILED_RENDER`。
- [ ] **Step 2: 验证 RED**：运行 `pytest tests/test_paper_rendering.py -q`，预期渲染接口缺失而失败。
- [ ] **Step 3: 最小实现**：参数数组调用 Pandoc；用 python-docx 生成固定 reference DOCX；通过独立 PowerShell/Word COM 子进程导出 PDF；写派生哈希和 `render_report.json`。
- [ ] **Step 4: 验证 GREEN**：运行渲染测试，预期 DOCX/TEX 测试通过，真实 Word 仅留给本机验收。
- [ ] **Step 5: 提交**：只提交渲染、样式、配置和测试。

### Task 5: 工作流与 Runner 集成

**Files:**
- Modify: `config/workflow.yaml`
- Modify: `config/gates.yaml`
- Modify: `scripts/automm/workflow.py`
- Modify: `scripts/automm/runner.py`
- Modify: `scripts/automm/problems.py`
- Modify: `tests/test_cross_question_progression.py`
- Create: `tests/test_paper_workflow.py`

**Interfaces:**
- Workflow: `cross_question_review -> paper_writing -> paper_validation -> completed`。
- Non-agent actions: `prepare_paper_writing`、`validate_and_render_paper`。
- Problem state: Runner 管理 `paper.evidence`、`paper.active_version`、`paper.status`、`paper.validation`、`paper.docx`、`paper.pdf`。

- [ ] **Step 1: 写失败测试**：跨问通过后进入 `paper_writing`；准备证据与版本后调度 `paper-writer`；验证失败回写作新版本，成功进入 completed；未完成论文禁止 completed。
- [ ] **Step 2: 验证 RED**：运行 `pytest tests/test_cross_question_progression.py tests/test_paper_workflow.py -q`，预期旧状态机行为导致失败。
- [ ] **Step 3: 最小实现**：加入阶段、严格迁移门禁、Runner handlers 与论文状态更新；保留 final summary 作为 completed 后归档。
- [ ] **Step 4: 验证 GREEN**：运行工作流、Runner、事务原子性和论文测试，预期全部通过。
- [ ] **Step 5: 提交**：只提交工作流集成和测试。

### Task 6: 当前题目本机验收

**Files:**
- Generated: `reports/problems/2025-cumcm-b/paper/evidence/*`
- Generated: `reports/problems/2025-cumcm-b/paper/versions/paper_vNNN/*`
- Generated: `reports/problems/2025-cumcm-b/paper/final/*`

**Interfaces:**
- Consumes: 当前题目已验收产物。
- Produces: 完整 `paper.md`、`paper.docx`、`paper.tex`、`paper.pdf`、validation/render reports。

- [ ] **Step 1: 运行 Evidence 门禁**：若当前题目尚未达到跨问与 sanity 门禁，只修复 Writer 对真实合法结构的兼容问题，不伪造研究状态；使用当前已验收产物创建显式验收快照。
- [ ] **Step 2: 生成完整 Markdown**：运行 build CLI，校验无占位符且每问含方法、结果、可靠性和结论。
- [ ] **Step 3: 真实渲染**：用 Pandoc 生成 DOCX/TEX，再用 Microsoft Word 导出 PDF。
- [ ] **Step 4: 文档检查**：解析 DOCX 的段落、表格、媒体与 OMML；解析 PDF 页数、A4 页面和空白页；抽查关键页面预览。
- [ ] **Step 5: 原子发布**：只有内容和渲染均 PASS 时更新 `paper/final/`，保留所有版本。

### Task 7: 全量验证、文档和恢复 daemon

**Files:**
- Modify: `PROJECT.md`
- Modify: `RESEARCH_LOOP.md`

**Interfaces:**
- Produces: 用户可操作的全自动论文阶段说明与故障恢复说明。

- [ ] **Step 1: 更新文档**：记录新阶段、输出路径、依赖和降级行为。
- [ ] **Step 2: 静态验证**：运行配置解析、`python -m compileall scripts` 与 Ruff。
- [ ] **Step 3: 全量测试**：运行 `pytest -q`，记录通过数和任何跳过项。
- [ ] **Step 4: 成品复核**：确认 final DOCX/PDF/TEX 与报告存在、非空、哈希链一致。
- [ ] **Step 5: 恢复 daemon**：运行 `python scripts/harness.py control RESUME`，核对 control、锁、daemon PID 与下一动作。
- [ ] **Step 6: 最终提交**：只提交本功能文件，不纳入用户原有无关改动。
