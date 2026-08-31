"""把 Pandoc 的语义段落绑定到只读 Word 模板的原生样式。

题注通过模板编号显示标签，正文只保存标题；publication_manifest 是图表
顺序的唯一输入。整个包验证成功后才原子替换目标，模板绝不写入。
"""

from __future__ import annotations

import copy
import hashlib
import os
import posixpath
import re
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

from lxml import etree as ET

DEFAULT_STYLE_MAP = {
    "title": "Title",
    "heading1": "heading 1",
    "heading2": "heading 2",
    "heading3": "heading 3",
    "body": "Normal",
    "image": "图片",
    "figure_caption": "图注",
    "table_caption": "表注",
    "table": "三线表",
    "table_text": "表格",
    "display_math": "行间公式辅助样式",
    "bibliography": "参考文献",
    "ordered_list": "有序列表",
    "unordered_list": "无序列表",
    "code": "Plain Text",
}
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}
W, R, REL, CT = ("{" + NS[key] + "}" for key in ("w", "r", "rel", "ct"))
NUMBERED_ROLES = (
    "heading1",
    "heading2",
    "heading3",
    "figure_caption",
    "table_caption",
    "bibliography",
    "ordered_list",
    "unordered_list",
)
UNNUMBERED_HEADINGS = {"摘要", "abstract", "关键词", "参考文献", "附录", "致谢"}


def _read_package(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        if len(set(archive.namelist())) != len(archive.namelist()):
            raise ValueError("DOCX 包存在重复部件")
        return {name: archive.read(name) for name in archive.namelist()}


def _xml(data: bytes):
    return ET.fromstring(data, ET.XMLParser(resolve_entities=False, no_network=True))


def _bytes(root) -> bytes:
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)


def _value(element, path: str, default=None):
    child = element.find(path, NS)
    return default if child is None else child.get(W + "val", default)


def _style_index(styles):
    return {s.get(W + "styleId"): s for s in styles.findall("w:style", NS)}


def _style_chain(style_id, index):
    seen = set()
    while style_id:
        if style_id in seen or style_id not in index:
            raise ValueError(f"样式继承无效: {style_id}")
        seen.add(style_id)
        style = index[style_id]
        yield style
        style_id = _value(style, "w:basedOn")


def _effective_num(style_id, styles):
    num_id, level = None, None
    for style in _style_chain(style_id, styles):
        if num_id is None:
            num_id = _value(style, "w:pPr/w:numPr/w:numId")
        if level is None:
            level = _value(style, "w:pPr/w:numPr/w:ilvl")
    return num_id, int(level or 0)


def _number_definition(numbering, num_id, level):
    nums = numbering.xpath("w:num[@w:numId=$id]", namespaces=NS, id=str(num_id))
    if len(nums) != 1:
        raise ValueError(f"编号实例无效: {num_id}")
    abstract_id = _value(nums[0], "w:abstractNumId")
    definitions = numbering.xpath("w:abstractNum[@w:abstractNumId=$id]", namespaces=NS, id=abstract_id)
    if len(definitions) != 1:
        raise ValueError(f"编号定义无效: {abstract_id}")
    overrides = nums[0].xpath("w:lvlOverride[@w:ilvl=$level]/w:lvl", namespaces=NS, level=str(level))
    levels = overrides or definitions[0].xpath("w:lvl[@w:ilvl=$level]", namespaces=NS, level=str(level))
    if len(levels) != 1:
        raise ValueError(f"编号层级无效: {num_id}/{level}")
    return abstract_id, levels[0], nums[0]


def _target(source: str, target: str) -> str:
    result = posixpath.normpath(posixpath.join(posixpath.dirname(source), target)).lstrip("/")
    if result == ".." or result.startswith("../") or "\\" in result:
        raise ValueError("DOCX 关系越出包边界")
    return result


def _rels_path(part: str) -> str:
    return posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")


def _template_data(template_path: Path, style_map: dict | None):
    parts = _read_package(template_path)
    names = DEFAULT_STYLE_MAP | (style_map or {})
    if set(names) != set(DEFAULT_STYLE_MAP):
        raise ValueError("style_map 包含未知角色")
    styles, numbering, document = (_xml(parts[f"word/{name}.xml"]) for name in ("styles", "numbering", "document"))
    index = _style_index(styles)
    resolved = {}
    for role, name in names.items():
        matches = [s for s in index.values() if _value(s, "w:name") == name]
        expected_type = "table" if role == "table" else "paragraph"
        if len(matches) != 1 or matches[0].get(W + "type") != expected_type:
            raise ValueError(f"模板必要样式缺失、重名或类型错误: {role}={name} ({expected_type})")
        resolved[role] = {"name": name, "style_id": matches[0].get(W + "styleId"), "type": expected_type}
    for style_id, style in index.items():
        list(_style_chain(style_id, index))
        for tag in ("link", "next"):
            value = _value(style, f"w:{tag}")
            if value and value not in index:
                raise ValueError(f"模板样式引用无效: {style_id}/{tag}/{value}")
    bindings = {}
    for role in NUMBERED_ROLES:
        num_id, level = _effective_num(resolved[role]["style_id"], index)
        abstract_id, _, _ = _number_definition(numbering, num_id, level)
        bindings[role] = {"num_id": num_id, "abstract_num_id": abstract_id, "level": level}
    sections = document.xpath(".//w:sectPr", namespaces=NS)
    if not sections:
        raise ValueError("模板缺少页面章节设置")
    body_index = min(3, len(sections))
    relationships = {rel.get("Id"): rel for rel in _xml(parts["word/_rels/document.xml.rels"])}
    effective = {"header": {}, "footer": {}}
    for section in sections[:body_index]:
        for kind in effective:
            for ref in section.findall(f"w:{kind}Reference", NS):
                rel = relationships.get(ref.get(R + "id"))
                if rel is None or rel.get("TargetMode") == "External":
                    raise ValueError(f"模板{kind}关系无效")
                part = _target("word/document.xml", rel.get("Target"))
                if part not in parts:
                    raise ValueError(f"模板{kind}部件缺失: {part}")
                effective[kind][ref.get(W + "type", "default")] = part
    report = {
        "status": "PASS",
        "template_sha256": hashlib.sha256(template_path.read_bytes()).hexdigest(),
        "style_ids": {role: style["style_id"] for role, style in resolved.items()},
        "styles": resolved,
        "numbering": bindings,
        "body_section_index": body_index,
        "section_count": len(sections),
        "effective_headers": effective["header"],
        "effective_footers": effective["footer"],
    }
    return parts, report, copy.deepcopy(sections[body_index - 1])


def inspect_template(template_path: Path, style_map: dict | None = None) -> dict:
    """只读检查必要样式、继承编号和正文节的有效页眉页脚；无效即抛 ValueError。"""
    return _template_data(Path(template_path), style_map)[1]


def _paragraph_text(paragraph) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def _strip_prefix(paragraph, pattern: str) -> None:
    match = re.match(pattern, _paragraph_text(paragraph))
    if not match:
        return
    remaining = match.end()
    for node in paragraph.xpath(".//w:t", namespaces=NS):
        text = node.text or ""
        consumed = min(remaining, len(text))
        node.text = text[consumed:]
        remaining -= consumed
        if not remaining:
            break


def _ensure(parent, tag):
    child = parent.find("w:" + tag, NS)
    if child is None:
        child = ET.Element(W + tag)
        parent.insert(0, child)
    return child


def _set_num(ppr, num_id, level=0):
    for node in ppr.findall("w:numPr", NS):
        ppr.remove(node)
    num = ET.SubElement(ppr, W + "numPr")
    ET.SubElement(num, W + "ilvl", {W + "val": str(level)})
    ET.SubElement(num, W + "numId", {W + "val": str(num_id)})


def _clean_paragraph(paragraph, style_id, old_styles, template_styles):
    ppr = _ensure(paragraph, "pPr")
    # numPr is rebuilt after classification; keep content controls, not layout.
    for node in list(ppr):
        ppr.remove(node)
    ET.SubElement(ppr, W + "pStyle", {W + "val": style_id})
    for rpr in paragraph.xpath(".//w:rPr[not(ancestor::m:oMath)]", namespaces=NS):
        old_id = _value(rpr, "w:rStyle")
        if old_id in old_styles and old_id not in template_styles:
            old_name = _value(old_styles[old_id], "w:name", "").lower()
            for name, tag in (("strong", "b"), ("emphasis", "i")):
                if old_name == name and rpr.find("w:" + tag, NS) is None:
                    ET.SubElement(rpr, W + tag)
        for node in list(rpr):
            local = ET.QName(node).localname
            if local == "rStyle":
                old_id = node.get(W + "val")
                if old_id not in template_styles:
                    # Inline code maps to the template's linked character style.
                    old_name = _value(old_styles[old_id], "w:name", "") if old_id in old_styles else ""
                    if old_name in {"Verbatim Char", "Source Code"}:
                        candidates = [s for s in template_styles.values() if _value(s, "w:name") == "Plain Text"]
                        linked = _value(candidates[0], "w:link") if candidates else None
                        if linked:
                            node.set(W + "val", linked)
                            continue
                    rpr.remove(node)
            elif local not in {"b", "bCs", "i", "iCs", "strike", "dstrike", "vertAlign", "u", "lang", "noProof", "rtl"}:
                rpr.remove(node)
    return ppr


def _adapt_tables(document, ids):
    for table in document.xpath(".//w:tbl", namespaces=NS):
        props = _ensure(table, "tblPr")
        for child in list(props):
            if ET.QName(child).localname not in {"tblW", "tblLayout", "tblCaption", "tblDescription"}:
                props.remove(child)
        props.insert(0, ET.Element(W + "tblStyle", {W + "val": ids["table"]}))
        ET.SubElement(
            props,
            W + "tblLook",
            {
                W + "val": "0620",
                W + "firstRow": "1",
                W + "lastRow": "0",
                W + "firstColumn": "0",
                W + "lastColumn": "0",
                W + "noHBand": "1",
                W + "noVBand": "1",
            },
        )
        for cell in table.xpath(".//w:tcPr", namespaces=NS):
            for child in list(cell):
                if ET.QName(child).localname not in {"tcW", "gridSpan", "vMerge", "hMerge"}:
                    cell.remove(child)
        for row in table.findall("w:tr", NS):
            props = row.find("w:trPr", NS)
            if props is not None:
                for child in list(props):
                    if ET.QName(child).localname not in {"tblHeader", "gridBefore", "gridAfter", "wBefore", "wAfter"}:
                        props.remove(child)


def _adapt_body(document, old_styles, old_numbering, template_parts, info, manifest):
    ids = info["style_ids"]
    template_styles = _style_index(_xml(template_parts["word/styles.xml"]))
    numbering = _xml(template_parts["word/numbering.xml"])
    by_name = {style["name"].lower(): role for role, style in info["styles"].items()}
    aliases = {
        "image caption": "figure_caption",
        "figure caption": "figure_caption",
        "table caption": "table_caption",
        "source code": "code",
        "bibliography": "bibliography",
        "imagecaption": "figure_caption",
    }
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    names = {
        p: _value(old_styles[sid], "w:name", sid) if sid in old_styles else sid
        for p in paragraphs
        for sid in [_value(p, "w:pPr/w:pStyle", "Normal")]
    }
    semantic_headings = any(name.lower() == info["styles"]["title"]["name"].lower() for name in names.values())
    next_id = max(int(n.get(W + "numId")) for n in numbering.findall("w:num", NS)) + 1
    instances, counts, captions = {}, Counter(), {"figures": [], "tables": []}
    next_abstract = max(int(n.get(W + 'abstractNumId')) for n in numbering.findall('w:abstractNum', NS)) + 1

    def instance(role, key, level, start=1):
        nonlocal next_id, next_abstract
        if key not in instances:
            binding = info["numbering"][role]
            abstract_id = binding['abstract_num_id']
            if role.startswith('heading') or role in {'figure_caption', 'table_caption'}:
                # Word joins style-linked levels across numId instances. Isolate
                # counters while retaining every native number/font/layout rule.
                # The original template abstract definitions and styles stay intact.
                original = numbering.xpath('w:abstractNum[@w:abstractNumId=$id]',
                                            namespaces=NS, id=abstract_id)[0]
                isolated = copy.deepcopy(original)
                abstract_id = str(next_abstract)
                next_abstract += 1
                isolated.set(W + 'abstractNumId', abstract_id)
                nsid = isolated.find('w:nsid', NS)
                if nsid is not None:
                    nsid.set(W + 'val', hashlib.sha256(f'automm:{key}:{abstract_id}'.encode()).hexdigest()[:8].upper())
                for link in isolated.xpath('.//w:pStyle', namespaces=NS):
                    link.getparent().remove(link)
                numbering.insert(len(numbering.findall('w:abstractNum', NS)), isolated)
            num = ET.SubElement(numbering, W + "num", {W + "numId": str(next_id)})
            ET.SubElement(num, W + "abstractNumId", {W + "val": abstract_id})
            instances[key] = str(next_id)
            next_id += 1
        num = numbering.xpath('w:num[@w:numId=$id]', namespaces=NS, id=instances[key])[0]
        if not num.xpath('w:lvlOverride[@w:ilvl=$level]', namespaces=NS, level=str(level)):
            override = ET.SubElement(num, W + "lvlOverride", {W + "ilvl": str(level)})
            ET.SubElement(override, W + "startOverride", {W + "val": str(start)})
        return instances[key]

    for paragraph in paragraphs:
        name = names[paragraph]
        compact_name = re.sub(r"\s+", "", name).lower()
        unnumbered = compact_name == "autommunnumberedheading1"
        role = "heading1" if unnumbered else by_name.get(name.lower(), aliases.get(name.lower(), "body"))
        heading = re.fullmatch(r"heading([1-9])", compact_name)
        if heading and not semantic_headings:
            depth = int(heading[1])
            role = "title" if depth == 1 else f"heading{min(depth - 1, 3)}"
        source_num = _value(paragraph, "w:pPr/w:numPr/w:numId")
        source_level = int(_value(paragraph, "w:pPr/w:numPr/w:ilvl", "0"))
        start = 1
        if source_num not in (None, "0") and role in {"body", "ordered_list", "unordered_list"}:
            _, source_definition, source_instance = _number_definition(old_numbering, source_num, source_level)
            role = "unordered_list" if _value(source_definition, "w:numFmt") == "bullet" else "ordered_list"
            overrides = source_instance.xpath(
                "w:lvlOverride[@w:ilvl=$level]/w:startOverride/@w:val", namespaces=NS, level=str(source_level)
            )
            start = int(overrides[0]) if overrides else int(_value(source_definition, "w:start", "1"))
        if paragraph.xpath("ancestor::w:tc", namespaces=NS):
            role = "table_text"
        elif paragraph.xpath(".//w:drawing | .//w:pict", namespaces=NS):
            role = "image"
        elif paragraph.find("m:oMathPara", NS) is not None:
            role = "display_math"
        text = _paragraph_text(paragraph).strip()
        if role == 'image' and manifest is not None:
            ordinal = counts['image'] + 1
            entries = manifest.get('figures', [])
            if ordinal > len(entries):
                raise ValueError('图片缺少公开图号与题注登记')
            alternative = f"图{ordinal} {entries[ordinal - 1]['title']}"
            # Pandoc also puts the source path in pic:cNvPr/@descr.
            # Publish semantic alt text, not a path from the evidence registry.
            for node in paragraph.iter():
                if ET.QName(node).localname in {'docPr', 'cNvPr'}:
                    node.set('name', f'图{ordinal}')
                    node.set('descr', alternative)
                    if 'title' in node.attrib:
                        node.set('title', alternative)
        if role.startswith("heading") and re.sub(r"\s+", "", text).lower() in UNNUMBERED_HEADINGS:
            unnumbered = True
        ppr = _clean_paragraph(paragraph, ids[role], old_styles, template_styles)
        if unnumbered or source_num == "0":
            _set_num(ppr, "0")
        elif role.startswith('heading'):
            level = info['numbering'][role]['level']
            _set_num(ppr, instance(role, 'body_headings', level), level)
        elif role in {"figure_caption", "table_caption"}:
            kind = "figures" if role == "figure_caption" else "tables"
            label = "图" if role == "figure_caption" else "表"
            ordinal = len(captions[kind]) + 1
            entries = manifest.get(kind, []) if manifest is not None else []
            exact_title = entries[ordinal - 1].get("title") if ordinal <= len(entries) else None
            # Native template numbering owns the prefix, never leave a second label.
            if text != exact_title:
                _strip_prefix(paragraph, rf"^\s*{label}\s*\d+(?:\s+|[：:.、]\s*)")
            title = _paragraph_text(paragraph).strip()
            captions[kind].append({"number": ordinal, "title": title})
            level = info["numbering"][role]["level"]
            _set_num(ppr, instance(role, role, level), level)
        elif role == "bibliography":
            _strip_prefix(paragraph, r"^\s*\[\d+\]\s*")
            level = info["numbering"][role]["level"]
            _set_num(ppr, instance(role, role, level), level)
        elif role in {"ordered_list", "unordered_list"}:
            key = (role, source_num or role)
            _set_num(ppr, instance(role, key, source_level, start), source_level)
        counts[role] += 1
    if manifest is not None:
        for kind, actual in captions.items():
            expected = manifest.get(kind, [])
            if len(expected) != len(actual):
                raise ValueError(f"publication_manifest 题注数量不一致: {kind}")
            for i, (entry, observed) in enumerate(zip(expected, actual, strict=True), 1):
                if entry.get("number") != i or str(entry.get("title", "")).strip() != observed["title"]:
                    raise ValueError(f"publication_manifest 题注编号或标题不一致: {kind}/{i}")
    _adapt_tables(document, ids)
    return numbering, dict(counts), captions


class _TemplateParts:
    """复制模板依赖闭包并重定位关系，避免与正文图片等部件重名。"""

    def __init__(self, output, source):
        self.output, self.source = output, source
        self.mapping = {}
        self.types = _xml(output["[Content_Types].xml"])
        source_types = _xml(source["[Content_Types].xml"])
        self.overrides = {
            e.get("PartName").lstrip("/"): e.get("ContentType") for e in source_types.findall("ct:Override", NS)
        }
        self.defaults = {e.get("Extension"): e.get("ContentType") for e in source_types.findall("ct:Default", NS)}

    def copy(self, part, destination=None):
        if part in self.mapping:
            return self.mapping[part]
        if part not in self.source:
            raise ValueError(f"模板依赖部件缺失: {part}")
        destination = destination or "word/automm_template/" + part
        self.mapping[part] = destination
        self.output[destination] = self.source[part]
        content_type = self.overrides.get(part) or self.defaults.get(part.rsplit(".", 1)[-1])
        if not content_type:
            raise ValueError(f"模板依赖缺少 ContentType: {part}")
        for entry in list(self.types):
            if entry.get("PartName") == "/" + destination:
                self.types.remove(entry)
        ET.SubElement(self.types, CT + "Override", {"PartName": "/" + destination, "ContentType": content_type})
        relationships = _rels_path(part)
        if relationships in self.source:
            root = _xml(self.source[relationships])
            for rel in root:
                if rel.get("TargetMode") != "External":
                    target = self.copy(_target(part, rel.get("Target")))
                    rel.set("Target", posixpath.relpath(target, posixpath.dirname(destination)))
            self.output[_rels_path(destination)] = _bytes(root)
        else:
            self.output.pop(_rels_path(destination), None)
        return destination


def _install_template(output, source, section, info):
    copier = _TemplateParts(output, source)
    rels = _xml(output["word/_rels/document.xml.rels"])
    replaced = {"styles", "numbering", "fontTable", "theme", "header", "footer"}
    for rel in list(rels):
        if rel.get("Type", "").rsplit("/", 1)[-1] in replaced:
            rels.remove(rel)
    used = {rel.get("Id") for rel in rels}

    def add_relationship(kind, target):
        suffix = 1
        while f"rIdAutoMM{suffix}" in used:
            suffix += 1
        rid = f"rIdAutoMM{suffix}"
        used.add(rid)
        ET.SubElement(
            rels,
            REL + "Relationship",
            {
                "Id": rid,
                "Type": NS["r"] + "/" + kind,
                "Target": posixpath.relpath(target, "word"),
            },
        )
        return rid

    for kind, part in (
        ("styles", "word/styles.xml"),
        ("numbering", "word/numbering.xml"),
        ("fontTable", "word/fontTable.xml"),
        ("theme", "word/theme/theme1.xml"),
    ):
        add_relationship(kind, copier.copy(part, part))
    for node in list(section):
        if ET.QName(node).localname in {"headerReference", "footerReference", "pgNumType"}:
            section.remove(node)
    refs = []
    for kind, field in (("header", "effective_headers"), ("footer", "effective_footers")):
        for variant, part in info[field].items():
            rid = add_relationship(kind, copier.copy(part))
            refs.append(ET.Element(W + kind + "Reference", {W + "type": variant, R + "id": rid}))
    for index, ref in enumerate(refs):
        section.insert(index, ref)
    # pgNumType precedes cols in the WordprocessingML section schema.
    index = next((i for i, node in enumerate(section) if node.tag in {W + "cols", W + "docGrid"}), len(section))
    section.insert(index, ET.Element(W + "pgNumType", {W + "start": "1"}))
    # Preserve rendering settings, not template author history or external .dotm links.
    if "word/settings.xml" in source and "word/settings.xml" in output:
        settings, original = _xml(output["word/settings.xml"]), _xml(source["word/settings.xml"])
        layout = {
            "defaultTabStop",
            "characterSpacingControl",
            "compat",
            "themeFontLang",
            "clrSchemeMapping",
            "evenAndOddHeaders",
            "mirrorMargins",
            "bordersDoNotSurroundHeader",
            "bordersDoNotSurroundFooter",
        }
        for node in list(settings):
            if ET.QName(node).localname in layout | {"attachedTemplate", "updateStyles", "docVars"}:
                settings.remove(node)
        for node in original:
            if ET.QName(node).localname in layout:
                settings.append(copy.deepcopy(node))
        output["word/settings.xml"] = _bytes(settings)
        settings_rels = _rels_path("word/settings.xml")
        if settings_rels in output:
            root = _xml(output[settings_rels])
            for rel in list(root):
                if rel.get("Type", "").endswith("/attachedTemplate"):
                    root.remove(rel)
            output[settings_rels] = _bytes(root)
    output["word/_rels/document.xml.rels"] = _bytes(rels)
    output["[Content_Types].xml"] = _bytes(copier.types)


def _repair_auxiliary_styles(output, source_styles, template_styles, body_id):
    by_name = {_value(s, "w:name", "").lower(): sid for sid, s in template_styles.items()}
    for name, data in list(output.items()):
        if (
            not name.startswith("word/")
            or not name.endswith(".xml")
            or name in {"word/styles.xml", "word/document.xml"}
        ):
            continue
        root = _xml(data)
        changed = False
        for ref in root.xpath(".//w:pStyle | .//w:rStyle | .//w:tblStyle", namespaces=NS):
            sid = ref.get(W + "val")
            if sid in template_styles:
                continue
            source_name = _value(source_styles[sid], "w:name", "") if sid in source_styles else sid
            replacement = by_name.get(source_name.lower())
            if replacement is not None:
                ref.set(W + "val", replacement)
            elif ref.tag == W + "pStyle":
                ref.set(W + "val", body_id)
            else:
                ref.getparent().remove(ref)
            changed = True
        if changed:
            output[name] = _bytes(root)


def _validate_package(parts):
    styles = _style_index(_xml(parts["word/styles.xml"]))
    numbering = _xml(parts["word/numbering.xml"])
    valid_nums = {node.get(W + "numId") for node in numbering.findall("w:num", NS)} | {"0"}
    for name, data in parts.items():
        if name.endswith(".rels"):
            source = (
                ""
                if name == "_rels/.rels"
                else posixpath.join(posixpath.dirname(posixpath.dirname(name)), posixpath.basename(name)[:-5])
            )
            relations = _xml(data)
            relation_ids = [rel.get("Id") for rel in relations]
            if len(set(relation_ids)) != len(relation_ids) or None in relation_ids:
                raise ValueError(f"DOCX 关系标识符缺失或重复: {name}")
            for rel in relations:
                if rel.get("TargetMode") != "External" and _target(source, rel.get("Target")) not in parts:
                    raise ValueError(f"DOCX 关系缺失: {name}/{rel.get('Id')}")
        elif name.startswith("word/") and name.endswith(".xml"):
            root = _xml(data)
            relationship_part = _rels_path(name)
            relationship_ids = (
                {r.get("Id") for r in _xml(parts[relationship_part])} if relationship_part in parts else set()
            )
            for ref in root.xpath("//@r:id | //@r:embed | //@r:link", namespaces=NS):
                if ref not in relationship_ids:
                    raise ValueError(f"DOCX 关系引用无效: {name}/{ref}")
            for tag, expected in (("pStyle", "paragraph"), ("rStyle", "character"), ("tblStyle", "table")):
                for ref in root.xpath(f".//w:{tag}", namespaces=NS):
                    sid = ref.get(W + "val")
                    if sid not in styles or styles[sid].get(W + "type") != expected:
                        raise ValueError(f"DOCX 样式引用无效: {name}/{sid}")
            for ref in root.xpath(".//w:numId", namespaces=NS):
                if ref.get(W + "val") not in valid_nums:
                    raise ValueError(f"DOCX 编号引用无效: {name}/{ref.get(W + 'val')}")


def _prune_unused_parts(parts):
    # Pandoc copies the reference document's unused image/OLE relationships.
    # Structural relationships (styles/settings/notes) are implicit and retained.
    for name, data in list(parts.items()):
        if not name.endswith(".rels") or name == "_rels/.rels":
            continue
        source = posixpath.join(posixpath.dirname(posixpath.dirname(name)), posixpath.basename(name)[:-5])
        if source not in parts or not source.endswith(".xml"):
            continue
        root = _xml(parts[source])
        used_ids = {value for node in root.iter() for value in node.attrib.values()}
        relationships = _xml(data)
        changed = False
        for rel in list(relationships):
            kind = rel.get("Type", "").rsplit("/", 1)[-1]
            if kind in {"image", "oleObject", "header", "footer"} and rel.get("Id") not in used_ids:
                relationships.remove(rel)
                changed = True
        if changed:
            parts[name] = _bytes(relationships)
    reachable = {"[Content_Types].xml"}

    def visit(part):
        if part in reachable:
            return
        if part and part not in parts:
            raise ValueError(f"DOCX 依赖关系缺失: {part}")
        reachable.add(part)
        rels = "_rels/.rels" if not part else _rels_path(part)
        if rels in parts:
            reachable.add(rels)
            for rel in _xml(parts[rels]):
                if rel.get("TargetMode") != "External":
                    visit(_target(part, rel.get("Target")))

    visit("")
    for name in list(parts):
        if name not in reachable:
            del parts[name]
    types = _xml(parts["[Content_Types].xml"])
    for entry in list(types):
        if entry.tag == CT + "Override" and entry.get("PartName", "").lstrip("/") not in parts:
            types.remove(entry)
    parts["[Content_Types].xml"] = _bytes(types)


def adapt_docx(
    docx_path: Path, template_path: Path, style_map: dict | None = None, publication_manifest: dict | None = None
) -> dict:
    """适配现有 DOCX，返回审计信息；校验失败不修改目标或模板。

    custom-style 使用 DEFAULT_STYLE_MAP 的样式名称。特殊标记
    AutoMMUnnumberedHeading1 映射原 heading 1 并关闭编号。没有 Title
    段落时兼容旧 Pandoc：heading 1 是题目，其余标题向上提升一级。
    """
    docx_path, template_path = Path(docx_path), Path(template_path)
    if docx_path.resolve() == template_path.resolve() or os.path.samefile(docx_path, template_path):
        raise ValueError("不得把只读模板作为适配输出")
    template, info, section = _template_data(template_path, style_map)
    output = _read_package(docx_path)
    document = _xml(output["word/document.xml"])
    old_styles = _style_index(_xml(output["word/styles.xml"]))
    old_numbering = _xml(output["word/numbering.xml"])
    numbering, counts, captions = _adapt_body(document, old_styles, old_numbering, template, info, publication_manifest)
    for old_section in document.xpath(".//w:sectPr", namespaces=NS):
        old_section.getparent().remove(old_section)
    _install_template(output, template, section, info)
    document.find("w:body", NS).append(section)
    output["word/document.xml"] = _bytes(document)
    output["word/numbering.xml"] = _bytes(numbering)
    _repair_auxiliary_styles(
        output, old_styles, _style_index(_xml(template["word/styles.xml"])), info["style_ids"]["body"]
    )
    _prune_unused_parts(output)
    _validate_package(output)
    with tempfile.NamedTemporaryFile(
        prefix=".automm-docx-", suffix=".docx", dir=docx_path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in output.items():
                archive.writestr(name, data)
        os.replace(temporary, docx_path)
    finally:
        temporary.unlink(missing_ok=True)
    return {
        "status": "PASS",
        "template_sha256": info["template_sha256"],
        "style_ids": info["style_ids"],
        "body_section_index": info["body_section_index"],
        "counts": counts,
        "captions": captions,
    }
