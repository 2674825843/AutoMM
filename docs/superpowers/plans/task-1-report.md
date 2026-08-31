# Task 1：原生 Word 样式模块实施报告

日期：2026-08-31。状态：子任务完成，接口已由主代理接入。

## 范围与文件

只创建／修改以下文件：

- `scripts/automm/docx_styles.py`
- `tests/test_docx_styles.py`
- 本报告 `docs/superpowers/plans/task-1-report.md`

没有修改 daemon、workflow state、manifest、既有论文产物或用户模板，没有创建 worktree、分支或 commit，没有派发子代理。所有测试样例在 pytest 临时目录内由真实 Pandoc 生成；没有运行完整模型数据集或 supervised worker。

## 接口契约

`DEFAULT_STYLE_MAP` 是 role→模板样式名称，不是 styleId。支持部分覆盖，缺少必要样式、重名、类型错误、继承循环或无效编号时严格抛出 `ValueError`。

`inspect_template(template_path, style_map=None)` 只读返回：

- `status="PASS"`、`template_sha256`
- `style_ids: {role: styleId}`
- `styles: {role: {name, style_id, type}}`
- `numbering: {role: {num_id, abstract_num_id, level}}`
- `body_section_index`、`section_count`
- `effective_headers`／`effective_footers`：variant→模板部件路径

`adapt_docx(docx_path, template_path, style_map=None, publication_manifest=None)` 原子替换目标 DOCX。目标不能与模板相同（含硬链接）；任何校验失败均不写目标。返回：

```text
status, template_sha256, style_ids, body_section_index,
counts: {role: paragraph_count},
captions: {figures: [{number, title}], tables: [{number, title}]}
```

### 上游 Pandoc 语义标记

- 常规段落的 Div `custom-style` 使用模板样式名称：Title、heading 1～3、Normal、图片、图注、表注、表格、参考文献等。
- `AutoMMUnnumberedHeading1` 是专用语义标记，输出映射到原 `heading 1` 并添加段落 `numId=0`；该临时样式不会留在最终 styles.xml。
- 规范化文本为“摘要、Abstract、关键词、参考文献、附录、致谢”的标题也会抑制编号。
- 当文档含 Title 段落时，heading 1～3按原层级绑定；没有 Title 段落时兼容旧 Pandoc：heading 1→题目，heading 2→正文一级，后续提升一级。
- 图片段落和独立 OMML 公式按结构识别，不依赖可见文字。
- 图注和表注只保留标题，不保存“图1／表1”文字前缀，分别使用原生编号。
- manifest 的 `figures/tables` 为顺序列表，至少有整数 `number` 和纯文本 `title`，必须从1连续编号，数量／顺序／标题严格匹配；其他字段不消费、不修改。
- 若旧题注文字包含“图1 标题／表1：标题”，仅去除确定的编号前缀；manifest 精确匹配的标题原文始终保留，避免误删“图2025年度…”这类合法标题。
- 文献正文保留模板原生编号；已有 `[1]` 等文字前缀移除，避免双重编号。上游应使用纯文献文本。

## 模板检查证据与实现细节

只读模板 SHA-256（实施前后相同）：

`91710F1D43380961DAE3DCCEEBA78F2353F338704B979CE1C94D70A6F55574DC`

真实样式映射：

| role | styleId |
|---|---|
| title | af5 |
| heading1 / heading2 / heading3 | 1 / 2 / 3 |
| body | a4 |
| image | aff1 |
| figure_caption / table_caption | a1 / a0 |
| table / table_text | afb / a9 |
| display_math | aff7 |
| bibliography | a |
| ordered_list / unordered_list | a3 / a2 |
| code | ac |

- 最终 `word/styles.xml` 原字节与模板一致；规范化XML另有独立断言。保留 defaults、basedOn、next、linked styles。Pandoc BodyText、FirstParagraph、Compact、SourceCode及高亮新增样式不进入最终样式库。
- `fontTable.xml`、`theme/theme1.xml` 原字节保留，依赖关系递归复制且重定位，避免覆盖正文图片。
- 模板5节；采用第3节几何设置。其 default header 是 header4.xml，default footer 从第2节继承 footer4.xml（含 PAGE 字段）。所有有效页眉页脚关系重建，输出只保留单节且从1开始，不复制封面正文。
- 复制排版相关 settings；不复制外部 attachedTemplate 链接和模板作者 docVars。
- 图注 a1 从表注 a0 继承 numId1，自身是 lvl8；表注是 lvl7。分别创建独立编号实例引用原 abstractNum1，不重新定义格式；正文标题继续使用原章节实例。
- 有序列表引用模板 abstractNum4，无序列表引用 abstractNum2，文献引用 abstractNum0。列表保留源层级、列表实例边界和起始号。
- 段落／run清除直接字体、字号、对齐、缩进、行距、底纹等排版覆盖，保留真实 bold/italic、语义上下标等；OMML内容和图片尺寸不重写。
- 所有表格绑定三线表 afb，单元格文字绑定 a9；保留列宽及合并结构，清除直接边框和对齐；firstRow启用，tblLook位掩码0620与noHBand/noVBand显式属性一致。
- Pandoc参考模板会额外携带未引用的 `word/media/image1.wmf`。清除未使用图片/OLE关系，再依据包依赖可达性移除孤立模板图片和旧页眉等部件；真正被页眉页脚引用的资源保留。
- 校验所有部件内部关系、关系ID存在性／唯一性、style引用存在性／类型、编号引用有效性；失败在写入之前。
- 重复适配的document、numbering、styles、Content_Types规范化XML保持一致。

## TDD记录

遵循 `superpowers:test-driven-development` 及 `writing-good-tests.md`：先写真实行为测试，观察失败，再写生产实现。以下为各次命令及结果；最初重复堆栈在会话工具日志中保留，本报告列出完整失败项和结果，最终验证保存完整终端输出。

### RED 1：缺失模块

命令：`python -m pytest tests/test_docx_styles.py -q`

全部11项在断言“原生 Word 样式适配模块尚未实现”处失败：

```text
FAILED test_inspection_resolves_real_names_inherited_numbering_and_body_section
FAILED test_required_styles_fail_closed_before_modifying_docx[missing]
FAILED test_required_styles_fail_closed_before_modifying_docx[wrong_type]
FAILED test_original_styles_fonts_theme_and_template_bytes_are_preserved
FAILED test_semantics_emphasis_editable_math_image_geometry_and_code_survive
FAILED test_direct_layout_removed_three_line_table_enabled_and_column_widths_kept
FAILED test_caption_and_list_numbers_use_only_original_definitions_without_double_labels
FAILED test_body_section_inherits_page_footer_restarts_at_one_and_all_relationships_resolve
FAILED test_caption_manifest_mismatch_fails_without_partial_docx_write[manifest0]
FAILED test_caption_manifest_mismatch_fails_without_partial_docx_write[manifest1]
FAILED test_default_pandoc_headings_and_implicit_figure_captions_are_adapted
11 failed in 4.56s
```

### GREEN 1

同一命令：

```text
...........                                                              [100%]
11 passed in 3.93s
```

### RED／GREEN 2：关系与题注边界

新增损坏图片引用、合法数字开头标题、幂等性、模板只读和页眉依赖闭包用例后：

```text
FAILED test_dangling_image_relationship_fails_before_output_is_replaced
  Failed: DID NOT RAISE <class 'ValueError'>
FAILED test_caption_manifest_does_not_strip_legitimate_title_starting_with_figure_number
  ValueError: publication_manifest 题注编号或标题不一致: figures/1
2 failed, 14 passed in 6.31s
```

新增未使用模板图片回归，命令：
`python -m pytest tests/test_docx_styles.py -q -k unused_template`

```text
FAILED test_unused_template_example_media_and_orphan_header_parts_are_removed
  assert "word/media/image1.wmf" not in output
1 failed, 16 deselected in 0.64s
```

修复关系存在性校验、manifest原题保护及孤立部件清理后，命令：
`python -m pytest tests/test_docx_styles.py tests/test_paper_rendering.py -q`

```text
.....................                                                    [100%]
21 passed in 7.96s
```

### RED／GREEN 3：tblLook与重复关系标识符

命令：`python -m pytest tests/test_docx_styles.py -q -k direct_layout`

```text
FAILED test_direct_layout_removed_three_line_table_enabled_and_column_widths_kept
  AssertionError: assert '0020' == '0620'
1 failed, 16 deselected in 0.83s
```

调整位掩码。随后新增关系标识符唯一性、继承循环和重命名映射检查，命令：
`python -m pytest tests/test_docx_styles.py -q -k 'duplicate_relationship or inheritance_cycle or style_map'`

```text
FAILED test_duplicate_relationship_identifiers_are_not_accepted
  Failed: DID NOT RAISE <class 'ValueError'>
1 failed, 2 passed, 17 deselected in 1.37s
```

增加重复ID严格校验后：

```text
24 passed in 9.01s
```

## 最终专项验证完整输出

命令：`python -m pytest tests/test_docx_styles.py tests/test_paper_rendering.py -v --tb=short`（进程exit code 0）

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- E:\anaconda\python.exe
cachedir: .pytest_cache
rootdir: E:\项目\AutoMM
configfile: pyproject.toml
plugins: anyio-4.10.0, langsmith-0.7.22
collecting ... collected 24 items

tests/test_docx_styles.py::test_inspection_resolves_real_names_inherited_numbering_and_body_section PASSED [  4%]
tests/test_docx_styles.py::test_required_styles_fail_closed_before_modifying_docx[missing] PASSED [  8%]
tests/test_docx_styles.py::test_required_styles_fail_closed_before_modifying_docx[wrong_type] PASSED [ 12%]
tests/test_docx_styles.py::test_original_styles_fonts_theme_and_template_bytes_are_preserved PASSED [ 16%]
tests/test_docx_styles.py::test_semantics_emphasis_editable_math_image_geometry_and_code_survive PASSED [ 20%]
tests/test_docx_styles.py::test_direct_layout_removed_three_line_table_enabled_and_column_widths_kept PASSED [ 25%]
tests/test_docx_styles.py::test_caption_and_list_numbers_use_only_original_definitions_without_double_labels PASSED [ 29%]
tests/test_docx_styles.py::test_body_section_inherits_page_footer_restarts_at_one_and_all_relationships_resolve PASSED [ 33%]
tests/test_docx_styles.py::test_caption_manifest_mismatch_fails_without_partial_docx_write[manifest0] PASSED [ 37%]
tests/test_docx_styles.py::test_caption_manifest_mismatch_fails_without_partial_docx_write[manifest1] PASSED [ 41%]
tests/test_docx_styles.py::test_default_pandoc_headings_and_implicit_figure_captions_are_adapted PASSED [ 45%]
tests/test_docx_styles.py::test_dangling_image_relationship_fails_before_output_is_replaced PASSED [ 50%]
tests/test_docx_styles.py::test_caption_manifest_does_not_strip_legitimate_title_starting_with_figure_number PASSED [ 54%]
tests/test_docx_styles.py::test_repeated_adaptation_is_semantically_idempotent PASSED [ 58%]
tests/test_docx_styles.py::test_template_target_is_never_writable PASSED [ 62%]
tests/test_docx_styles.py::test_header_dependency_closure_is_copied_without_overwriting_body_image PASSED [ 66%]
tests/test_docx_styles.py::test_unused_template_example_media_and_orphan_header_parts_are_removed PASSED [ 70%]
tests/test_docx_styles.py::test_duplicate_relationship_identifiers_are_not_accepted PASSED [ 75%]
tests/test_docx_styles.py::test_template_inheritance_cycle_fails_without_writing_target PASSED [ 79%]
tests/test_docx_styles.py::test_style_map_resolves_replacement_name_without_changing_template PASSED [ 83%]
tests/test_paper_rendering.py::test_pandoc_render_produces_editable_formula_image_docx_and_tex PASSED [ 87%]
tests/test_paper_rendering.py::test_missing_user_template_fails_without_default_fallback PASSED [ 91%]
tests/test_paper_rendering.py::test_pdf_export_failure_preserves_docx_and_reports_failed_render[error0] PASSED [ 95%]
tests/test_paper_rendering.py::test_pdf_export_failure_preserves_docx_and_reports_failed_render[error1] PASSED [100%]

============================= 24 passed in 9.37s ==============================
```

命令：`python -m ruff check scripts/automm/docx_styles.py tests/test_docx_styles.py`

```text
All checks passed!
```

命令：`python -m compileall -q scripts/automm/docx_styles.py tests/test_docx_styles.py`

结果：exit code 0，无输出。

## 全套回归与主代理交接

本子任务另运行过一次 `python -m pytest -q`：

```text
FAILED tests/test_agent_runtime.py::test_schema_enum_nodes_declare_type
  node = {'const': 'request_paper_rewrite'}
  AssertionError: assert 'type' in {'const': 'request_paper_rewrite'}
1 failed, 142 passed in 47.95s
```

该失败位于主代理同时修改的响应schema，不在本子任务范围。已反馈主代理；主代理随后确认已修复且专项通过。按主代理要求没有再次运行全套测试。

主代理还反馈真实Microsoft Word烟测通过：摘要无编号，正文标题显示一／二，表注表1、图注图1。本子任务未独立启动Word，最终PDF／整篇排版验收仍由主代理负责。

无剩余接口疑问。可以继续整篇论文及正式交付验证。

