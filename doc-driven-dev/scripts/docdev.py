#!/usr/bin/env python3

import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata
from pathlib import Path

SCHEMA_VERSION = 3
DOCUMENT_TYPES = ("index", "idea", "landing", "exp", "decision", "lesson")
TYPE_DIRS = {
    "index": "docs",
    "idea": "docs/ideas",
    "landing": "docs/landing",
    "exp": "docs/exps",
    "decision": "docs/decisions",
    "lesson": "docs/lessons",
}
ARCHIVE_TYPES = ("exp", "decision", "lesson")
ARCHIVE_DIRS = {kind: f"docs/archive/{TYPE_DIRS[kind].rsplit('/', 1)[-1]}" for kind in ARCHIVE_TYPES}
ARCHIVE_DAYS = 5
PROJECT_DIRS = (
    "docs/ideas",
    "docs/landing",
    "docs/exps",
    "docs/decisions",
    "docs/lessons",
    "docs/archive/exps",
    "docs/archive/decisions",
    "docs/archive/lessons",
    "docs/assets",
    "docs/.docdev/records",
    "exp",
    "src/model",
    "src/modules",
    "src/train",
    "src/infer",
    "src/preprocess",
    "src/eval",
    "src/util",
    "src/dashboard",
    "data",
    "pretrained",
    "dashboard",
    "scripts",
    "configs",
)
GITIGNORE_ENTRIES = ("docs/", "assets/", "exp/", "data/", "pretrained/", "*.pt", "*.pth", "*.ckpt")
DOC_ID_RE = re.compile(r"^(index|idea|landing|exp|decision|lesson)-(\d{8})-(.+)$")
WIKI_REF_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
CLEAN_MARKERS = ("debug", "smoke")
BOARD_PATH = "docs/board.md"
BOARD_MAX_NODES = 40
TYPE_LABELS = {
    "index": "脉搏",
    "idea": "想法",
    "landing": "Landing",
    "exp": "实验",
    "decision": "决策",
    "lesson": "经验",
}


class DocdevError(Exception):
    def __init__(self, message, code=2, details=None):
        super().__init__(message)
        self.code = code
        self.details = details


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise DocdevError(message, code=2)


def now_string():
    value = os.environ.get("DOCDEV_NOW") or dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    parse_timestamp(value, "current time")
    return value


def parse_timestamp(value, field):
    if not isinstance(value, str):
        raise DocdevError(f"invalid {field}: {value}")
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise DocdevError(f"invalid {field}: {value}") from exc


def filename_date(timestamp):
    return timestamp[:10].replace("-", "")


def slugify(value):
    normalized = unicodedata.normalize("NFKC", str(value)).casefold()
    output = []
    separator = False
    for char in normalized:
        if char.isalnum():
            if separator and output:
                output.append("-")
            output.append(char)
            separator = False
        else:
            separator = True
    return ("".join(output).strip("-")[:64].rstrip("-") or "untitled")


def infer_title(content, fallback):
    for line in str(content).splitlines():
        value = line.strip().lstrip("#").strip()
        if value:
            return value[:80]
    return fallback


def atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


def write_json(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def read_json(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DocdevError(f"cannot read JSON: {path}: {exc}") from exc
    return value


def marker_path(root):
    return Path(root) / "docs/.docdev/project.json"


def record_path(root, document_id):
    if not isinstance(document_id, str) or not DOC_ID_RE.fullmatch(document_id):
        raise DocdevError(f"invalid record ID: {document_id}")
    return Path(root) / "docs/.docdev/records" / f"{document_id}.json"


def expected_path(record):
    kind = record.get("type")
    document_id = record.get("id")
    if kind not in TYPE_DIRS or not isinstance(document_id, str):
        raise DocdevError(f"invalid record identity: {document_id}")
    match = DOC_ID_RE.fullmatch(document_id)
    if not match or match.group(1) != kind:
        raise DocdevError(f"invalid record identity: {document_id}")
    if record.get("archived"):
        if kind not in ARCHIVE_DIRS:
            raise DocdevError(f"{kind} documents cannot be archived: {document_id}")
        return f"{ARCHIVE_DIRS[kind]}/{document_id}.md"
    return f"{TYPE_DIRS[kind]}/{document_id}.md"


def document_path(root, record):
    root = Path(root).resolve()
    path = (root / expected_path(record)).resolve()
    if not path.is_relative_to(root):
        raise DocdevError(f"document path escapes project root: {record.get('id')}")
    return path


def find_project(start=None):
    current = Path(start or os.getcwd()).expanduser().resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if marker_path(candidate).is_file():
            return candidate
    raise DocdevError("not inside a docdev project; run `docdev init` or pass --project")


def resolve_project(explicit=None):
    if explicit:
        root = Path(explicit).expanduser().resolve()
        if not marker_path(root).is_file():
            raise DocdevError(f"not a docdev project: {root}")
        return root
    return find_project()


def load_project(root):
    project = read_json(marker_path(root))
    required = {"schema_version", "name", "created_at", "index_id", "landing_ids"}
    if not isinstance(project, dict) or set(project) != required:
        raise DocdevError("project metadata is invalid")
    if project["schema_version"] == 2:
        project["schema_version"] = SCHEMA_VERSION
        write_json(marker_path(root), project)
    return project


def migrate_record(record, timestamp):
    """把 v2 record 升级到 v3：补 last_read 与 archived。返回 (record, changed)。"""
    if record.get("schema_version") == SCHEMA_VERSION:
        return record, False
    if record.get("schema_version") != 2:
        raise DocdevError(f"unsupported record schema_version: {record.get('id')}")
    upgraded = dict(record)
    upgraded["schema_version"] = SCHEMA_VERSION
    # 迁移当天视为“刚读过”，归档计时从升级时刻开始，不追溯历史。
    upgraded.setdefault("last_read", timestamp)
    upgraded.setdefault("archived", False)
    return upgraded, True


def load_records(root):
    records = {}
    timestamp = now_string()
    directory = Path(root) / "docs/.docdev/records"
    for path in sorted(directory.glob("*.json")) if directory.exists() else ():
        record = read_json(path)
        if not isinstance(record, dict):
            raise DocdevError(f"record must be a JSON object: {path}")
        document_id = record.get("id")
        if not document_id or document_id in records or path.name != f"{document_id}.json":
            raise DocdevError(f"invalid or duplicate record: {path}")
        record, changed = migrate_record(record, timestamp)
        if changed:
            write_json(path, record)
        records[document_id] = record
    return records


@contextlib.contextmanager
def project_lock(root, exclusive=True, timeout=5.0):
    path = Path(root) / "docs/.docdev/lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        operation = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(handle.fileno(), operation | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise DocdevError("project is busy; lock acquisition timed out", code=3)
                time.sleep(0.05)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def merge_gitignore(root):
    path = Path(root) / ".gitignore"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    changed = False
    for entry in GITIGNORE_ENTRIES:
        if entry not in lines:
            lines.append(entry)
            changed = True
    if changed or not path.exists():
        atomic_write(path, "\n".join(lines).rstrip() + "\n")


def allocate_identity(root, records, kind, docname, timestamp):
    prefix = f"{kind}-{filename_date(timestamp)}-{slugify(docname)}"
    candidate = prefix
    suffix = 2
    while (
        candidate in records
        or record_path(root, candidate).exists()
        or (Path(root) / TYPE_DIRS[kind] / f"{candidate}.md").exists()
        or (kind in ARCHIVE_DIRS and (Path(root) / ARCHIVE_DIRS[kind] / f"{candidate}.md").exists())
    ):
        candidate = f"{prefix}-{suffix}"
        suffix += 1
    return candidate, f"{TYPE_DIRS[kind]}/{candidate}.md"


def refs_for(record):
    texts = [record.get("data", {}).get("content", "")]
    texts.extend(log.get("content", "") for log in record.get("logs", []))
    refs = []
    for text in texts:
        for match in WIKI_REF_RE.finditer(text):
            reference = match.group(1).strip()
            if reference not in refs:
                refs.append(reference)
    return refs


def validate_refs(record, records):
    for reference in refs_for(record):
        if reference == record["id"]:
            raise DocdevError(f"self-reference in {record['id']}")
        if reference not in records:
            raise DocdevError(f"unresolved reference `{reference}` in {record['id']}")


def title_for(record):
    return record.get("data", {}).get("title") or record["id"]


def markdown_label(value):
    return str(value).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def cell(value):
    return str(value).replace("|", "｜").replace("\n", " ").strip() or "—"


def mermaid_label(value, limit=28):
    text = " ".join(str(value).split()).replace("|", "｜")
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text.replace('"', "#quot;")


def excerpt(text, limit=6):
    lines = [line for line in str(text).strip().splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    selected = lines[:limit]
    while selected and not selected[-1].strip():
        selected.pop()
    if len(lines) > len(selected):
        selected.append("…")
    return "\n".join(selected)


def link_from(root, base, target, label=None):
    relative = os.path.relpath(document_path(root, target), base).replace(os.sep, "/")
    return f"[{markdown_label(label or title_for(target))}]({relative})"


def relative_link(root, source, target, label=None):
    return link_from(root, document_path(root, source).parent, target, label)


def expand_refs_from(root, base, text, source_id, records):
    def replace(match):
        document_id = match.group(1).strip()
        target = records.get(document_id)
        if not target:
            raise DocdevError(f"unresolved reference `{document_id}` in {source_id}")
        return link_from(root, base, target, match.group(2))

    return WIKI_REF_RE.sub(replace, text)


def expand_refs(root, source, text, records):
    return expand_refs_from(root, document_path(root, source).parent, text, source["id"], records)


def reverse_refs(records):
    reverse = {document_id: [] for document_id in records}
    for record in records.values():
        for reference in refs_for(record):
            if reference in reverse:
                reverse[reference].append(record["id"])
    return reverse



def render_document(root, record, records):
    kind = record["type"]
    heading = {
        "index": "项目脉搏",
        "idea": "想法",
        "landing": "Landing",
        "exp": "实验",
        "decision": "决策",
        "lesson": "经验",
    }[kind]
    lines = [f"# {heading}：{title_for(record)}", "", f"> 创建：{record['created_at']}  ", f"> 更新：{record['updated_at']}"]
    if kind == "landing":
        lines.append(f"> Revision：{record['revision']}")
    lines.extend(["", expand_refs(root, record, record["data"]["content"], records).rstrip() or "暂无内容", ""])
    if kind == "exp" and record.get("logs"):
        lines.extend(["## 实验日志", ""])
        for log in record["logs"]:
            title = log.get("title") or infer_title(log["content"], "记录")
            lines.extend(
                [f"### {log['created_at']} — {title}", "", expand_refs(root, record, log["content"], records).rstrip(), ""]
            )
    if kind == "index":
        lines.extend([
            "---",
            "",
            "> 文档清单直接看目录（文件名即标题）：`docs/ideas`、`docs/landing`、`docs/exps`、"
            "`docs/decisions`、`docs/lessons`；长期未读的实验/决策/经验在 `docs/archive/`。  ",
            "> 用 `docdev read <id>` 读正文（会刷新未读计时），`docdev search <关键词>` 按全文检索。",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def board_table(rows, headers, empty="无"):
    lines = [f"| {' | '.join(headers)} |", f"|{'---|' * len(headers)}"]
    if not rows:
        lines.append(f"| {empty} |{' |' * (len(headers) - 1)}")
    lines.extend(f"| {' | '.join(row)} |" for row in rows)
    return lines


def board_graph(root, records, edges, max_nodes, enabled):
    if not enabled:
        return ["> 图谱已通过 `--no-graph` 关闭，引用关系见下方明细表。", ""]
    if not edges:
        return ["> 暂无交叉引用，图谱留空；用 `[[文档 ID]]` 建立引用后重新生成。", ""]
    if len(records) > max_nodes:
        return [
            f"> 文档数 {len(records)} 超过 `--max-nodes {max_nodes}`，图谱已降级；引用关系见下方明细表。",
            "",
        ]
    nodes = {document_id: f"n{number}" for number, document_id in enumerate(sorted(records), start=1)}
    lines = ["```mermaid", "graph LR"]
    for document_id, node in nodes.items():
        record = records[document_id]
        label = mermaid_label(f"{TYPE_LABELS[record['type']]}｜{title_for(record)}")
        shape = f'{node}(["{label}"])' if record["archived"] else f'{node}["{label}"]'
        lines.append(f"    {shape}:::{record['type']}")
    for source_id, target_id in edges:
        lines.append(f"    {nodes[source_id]} --> {nodes[target_id]}")
    for kind in DOCUMENT_TYPES:
        lines.append(f"    classDef {kind} stroke-width:1px;")
    lines.extend(["```", ""])
    return lines


def render_board(root, project, records, max_nodes=BOARD_MAX_NODES, graph=True):
    base = (Path(root) / "docs").resolve()
    timestamp = now_string()
    reverse = reverse_refs(records)
    edges = [
        (record["id"], reference)
        for record in sorted(records.values(), key=lambda r: r["id"])
        for reference in refs_for(record)
        if reference in records
    ]
    ordered = sorted(records.values(), key=lambda r: (r["created_at"], r["id"]))
    counts = {kind: sum(1 for r in records.values() if r["type"] == kind) for kind in DOCUMENT_TYPES}
    archived_count = sum(1 for r in records.values() if r["archived"])

    def link(record, label=None):
        return link_from(root, base, record, label)

    lines = [
        f"# 文档看板：{project['name']}",
        "",
        f"> 生成：{timestamp}  ",
        f"> 文档：{len(records)} 篇（活跃 {len(records) - archived_count} ／ 归档 {archived_count}）  ",
        "> " + " ／ ".join(f"{TYPE_LABELS[kind]} {counts[kind]}" for kind in DOCUMENT_TYPES) + "  ",
        f"> 交叉引用：{len(edges)} 条",
        "",
        "> 本文件由 `docdev board` 生成，会被下次生成整体覆盖；正文改动请写回对应文档。",
        "",
    ]

    index = records.get(project["index_id"])
    lines.extend(["## 项目脉搏", ""])
    if index:
        lines.append(f"来源：{link(index)}")
        lines.append("")
        content = expand_refs_from(root, base, index["data"]["content"], index["id"], records).strip()
        lines.extend([excerpt(content) if content else "index 暂无正文。", ""])
    else:
        lines.extend(["index 缺失。", ""])

    lines.extend(["## 交叉引用图谱", ""])
    lines.extend(board_graph(root, records, edges, max_nodes, graph))

    lines.extend(["## 交叉引用明细", ""])
    rows = []
    for record in ordered:
        forward = [records[r] for r in refs_for(record) if r in records]
        backward = [records[r] for r in reverse.get(record["id"], []) if r in records]
        if not forward and not backward:
            continue
        rows.append(
            [
                cell(link(record, record["id"])),
                cell("、".join(link(target) for target in forward)),
                cell("、".join(link(source) for source in backward)),
            ]
        )
    lines.extend(board_table(rows, ["文档", "引用 →", "← 被引用"], empty="暂无交叉引用"))
    lines.append("")

    lines.extend(["## 孤立文档", ""])
    orphans = [
        record
        for record in ordered
        if record["type"] != "index"
        and record["data"]["content"].strip()
        and not refs_for(record)
        and not reverse.get(record["id"])
    ]
    lines.append("> 已写正文但没有任何交叉引用的文档；空白占位文档不计入。")
    lines.append("")
    lines.extend(
        board_table(
            [[cell(link(record, record["id"])), cell(TYPE_LABELS[record["type"]]), cell(record["updated_at"])] for record in orphans],
            ["文档", "类型", "更新"],
            empty="无孤立文档",
        )
    )
    lines.append("")

    lines.extend(["## 实验看板", ""])
    experiments = [record for record in ordered if record["type"] == "exp"]
    lines.extend(
        board_table(
            [
                [
                    cell(link(record, record["id"])),
                    cell(title_for(record)),
                    cell(len(record.get("logs", []))),
                    cell(record["logs"][-1]["created_at"] if record.get("logs") else record["updated_at"]),
                ]
                for record in experiments
            ],
            ["实验", "标题", "日志", "最后活动"],
            empty="暂无实验",
        )
    )
    lines.append("")

    lines.extend(["## Landing 状态", ""])
    landings = sorted(
        (record for record in records.values() if record["type"] == "landing"),
        key=lambda r: (r.get("domain") or "", r["id"]),
    )
    lines.extend(
        board_table(
            [
                [cell(record.get("domain")), cell(link(record, record["id"])), cell(f"r{record['revision']}"), cell(record["updated_at"])]
                for record in landings
            ],
            ["领域", "文档", "Revision", "更新"],
            empty="暂无 Landing",
        )
    )
    lines.append("")

    for kind in ("decision", "lesson"):
        lines.extend([f"## {TYPE_LABELS[kind]}速查", ""])
        lines.extend(
            board_table(
                [
                    [cell(link(record, record["id"])), cell(title_for(record)), cell(record["updated_at"])]
                    for record in ordered
                    if record["type"] == kind
                ],
                ["文档", "标题", "更新"],
                empty=f"暂无{TYPE_LABELS[kind]}",
            )
        )
        lines.append("")

    lines.extend(["## 最近活动", ""])
    recent = sorted(records.values(), key=lambda r: (r["updated_at"], r["id"]), reverse=True)[:10]
    lines.extend(
        board_table(
            [
                [cell(record["updated_at"]), cell(TYPE_LABELS[record["type"]]), cell(link(record, record["id"])), cell(title_for(record))]
                for record in recent
            ],
            ["更新", "类型", "文档", "标题"],
            empty="暂无活动",
        )
    )
    rendered = "\n".join(lines).rstrip() + "\n"
    return rendered, {
        "generated_at": timestamp,
        "documents": len(records),
        "counts": counts,
        "archived": archived_count,
        "edges": len(edges),
        "graph": "```mermaid" in rendered,
        "orphans": len(orphans),
    }


def board_command(args):
    root = resolve_project(args.project)
    with project_lock(root):
        project = load_project(root)
        records = load_records(root)
        issues = validate_project_state(root, project, records)
        if issues:
            raise DocdevError("cannot render board", code=4, details={"issues": issues})
        rendered, summary = render_board(root, project, records, args.max_nodes, not args.no_graph)
        atomic_write(Path(root) / BOARD_PATH, rendered)
    return {"ok": True, "project": str(root), "path": BOARD_PATH, **summary}


def validate_record(record, records):
    required = {"schema_version", "id", "type", "path", "created_at", "updated_at", "last_read", "archived", "data"}
    if record.get("type") == "landing":
        required |= {"domain", "revision"}
    if record.get("type") == "exp":
        required |= {"logs"}
    if set(record) != required or record.get("schema_version") != SCHEMA_VERSION:
        raise DocdevError(f"invalid record fields: {record.get('id')}")
    if record["type"] not in DOCUMENT_TYPES:
        raise DocdevError(f"invalid document type: {record['type']}")
    if record["path"] != expected_path(record):
        raise DocdevError(f"invalid path: {record['id']}")
    created = parse_timestamp(record["created_at"], "created_at")
    updated = parse_timestamp(record["updated_at"], "updated_at")
    parse_timestamp(record["last_read"], "last_read")
    if not isinstance(record["archived"], bool):
        raise DocdevError(f"archived must be a boolean: {record['id']}")
    if record["archived"] and record["type"] not in ARCHIVE_TYPES:
        raise DocdevError(f"{record['type']} documents cannot be archived: {record['id']}")
    if updated < created or filename_date(record["created_at"]) != DOC_ID_RE.fullmatch(record["id"]).group(2):
        raise DocdevError(f"invalid timestamp order or filename date: {record['id']}")
    if not isinstance(record["data"], dict) or set(record["data"]) != {"title", "content"}:
        raise DocdevError(f"invalid content record: {record['id']}")
    if not all(isinstance(record["data"][key], str) for key in ("title", "content")):
        raise DocdevError(f"title and content must be strings: {record['id']}")
    if record["type"] == "landing":
        if record["domain"] not in {"dataset", "model", "pipeline"}:
            raise DocdevError(f"invalid landing domain: {record['id']}")
        if not isinstance(record["revision"], int) or record["revision"] < 1:
            raise DocdevError(f"invalid landing revision: {record['id']}")
    if record["type"] == "exp":
        if not isinstance(record["logs"], list):
            raise DocdevError(f"invalid logs: {record['id']}")
        for log in record["logs"]:
            if not isinstance(log, dict) or set(log) != {"created_at", "title", "content"}:
                raise DocdevError(f"invalid experiment log: {record['id']}")
            parse_timestamp(log["created_at"], "log created_at")
            if not isinstance(log["title"], str) or not isinstance(log["content"], str):
                raise DocdevError(f"invalid experiment log content: {record['id']}")
    validate_refs(record, records)


def validate_project_state(root, project, records):
    issues = []
    if project.get("schema_version") != SCHEMA_VERSION:
        issues.append("unsupported project schema_version")
    try:
        parse_timestamp(project.get("created_at"), "project created_at")
    except DocdevError as exc:
        issues.append(str(exc))
    index = records.get(project.get("index_id"))
    if not index or index.get("type") != "index":
        issues.append("project index_id must target the index record")
    landings = {
        r.get("domain"): r["id"] for r in records.values() if r.get("type") == "landing" and r.get("domain")
    }
    if landings != project.get("landing_ids") or set(landings) != {"dataset", "model", "pipeline"}:
        issues.append("project landing_ids do not match dataset/model/pipeline records")
    for record in records.values():
        try:
            validate_record(record, records)
        except (DocdevError, KeyError, TypeError, AttributeError) as exc:
            issues.append(str(exc))
    return sorted(set(issues))


def rerender_all(root, records):
    for record in records.values():
        if record["type"] != "index":
            atomic_write(document_path(root, record), render_document(root, record, records))


def refresh_index(root, project, records, timestamp):
    index = records[project["index_id"]]
    rendered = render_document(root, index, records)
    path = document_path(root, index)
    if not path.exists() or path.read_text(encoding="utf-8") != rendered:
        index["updated_at"] = timestamp
        write_json(record_path(root, index["id"]), index)
        records[index["id"]] = index
        atomic_write(path, render_document(root, index, records))


def reconcile(root, project, records, timestamp):
    issues = validate_project_state(root, project, records)
    if issues:
        raise DocdevError("project records are invalid", code=4, details={"issues": issues})
    rerender_all(root, records)
    refresh_index(root, project, records, timestamp)


def make_record(root, records, kind, title, content, timestamp, domain=None):
    document_id, path = allocate_identity(root, records, kind, title, timestamp)
    record = {
        "schema_version": SCHEMA_VERSION,
        "id": document_id,
        "type": kind,
        "path": path,
        "created_at": timestamp,
        "updated_at": timestamp,
        "last_read": timestamp,
        "archived": False,
        "data": {"title": title, "content": content},
    }
    if kind == "landing":
        record.update({"domain": domain, "revision": 1})
    if kind == "exp":
        record["logs"] = []
    return record


def save_record(root, record):
    write_json(record_path(root, record["id"]), record)


def init_project(args):
    root = Path(args.project_dir or os.getcwd()).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for directory in PROJECT_DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)
    marker = marker_path(root)
    timestamp = now_string()
    with project_lock(root):
        if marker.exists():
            project = load_project(root)
            records = load_records(root)
            reconcile(root, project, records, timestamp)
            merge_gitignore(root)
            return {"ok": True, "project": str(root), "existing": True, **ids_result(project)}
        records = load_records(root)
        if records:
            indexes = [r for r in records.values() if r.get("type") == "index"]
            landings = {r.get("domain"): r["id"] for r in records.values() if r.get("type") == "landing"}
            if len(indexes) != 1 or set(landings) != {"dataset", "model", "pipeline"}:
                raise DocdevError("cannot recover interrupted initialization")
            project = {
                "schema_version": SCHEMA_VERSION,
                "name": args.name or root.name,
                "created_at": indexes[0]["created_at"],
                "index_id": indexes[0]["id"],
                "landing_ids": landings,
            }
            reconcile(root, project, records, timestamp)
            merge_gitignore(root)
            write_json(marker, project)
            return {"ok": True, "project": str(root), "existing": False, "recovered": True, **ids_result(project)}
        name = args.name or root.name
        index = make_record(root, records, "index", name, "", timestamp)
        records[index["id"]] = index
        landing_ids = {}
        labels = {"dataset": "数据集", "model": "模型", "pipeline": "流水线"}
        for domain, title in labels.items():
            landing = make_record(root, records, "landing", title, "", timestamp, domain=domain)
            records[landing["id"]] = landing
            landing_ids[domain] = landing["id"]
        project = {
            "schema_version": SCHEMA_VERSION,
            "name": name,
            "created_at": timestamp,
            "index_id": index["id"],
            "landing_ids": landing_ids,
        }
        for record in records.values():
            save_record(root, record)
        rerender_all(root, records)
        refresh_index(root, project, records, timestamp)
        merge_gitignore(root)
        write_json(marker, project)
        return {"ok": True, "project": str(root), "existing": False, **ids_result(project)}


def ids_result(project):
    return {"index_id": project["index_id"], "landing_ids": project["landing_ids"]}


def load_payload(source):
    text = sys.stdin.read() if source in (None, "-") else Path(source).read_text(encoding="utf-8")
    if not text.strip():
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DocdevError(f"invalid input JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise DocdevError("input must be a JSON object")
    return value


def validate_content_payload(payload, append=False):
    allowed = {"content", "title"}
    unknown = set(payload) - allowed
    if unknown:
        raise DocdevError(f"unknown fields: {', '.join(sorted(unknown))}")
    if "content" not in payload or not isinstance(payload["content"], str) or not payload["content"].strip():
        raise DocdevError("`content` is required and must be a non-empty string")
    if "title" in payload and not isinstance(payload["title"], str):
        raise DocdevError("`title` must be a string")
    if append and not payload["content"].strip():
        raise DocdevError("append content cannot be empty")


def resolve_target(kind, requested, project):
    if kind == "index" and not requested:
        return project["index_id"]
    if kind == "landing" and requested in project["landing_ids"]:
        return project["landing_ids"][requested]
    return requested


def doc_command(args):
    root = resolve_project(args.project)
    payload = load_payload(args.input)
    validate_content_payload(payload, append=args.append)
    timestamp = now_string()
    with project_lock(root):
        project = load_project(root)
        records = load_records(root)
        target_id = resolve_target(args.document_type, args.id, project)
        # 先归档到期文档，再让下面的 reconcile 统一重渲染（含引用链接重算）。
        # 本次要写的文档排除在外：它马上就要被更新，归档它没有意义。
        auto_archived = auto_archive(root, records, timestamp, skip=target_id)
        reconcile(root, project, records, timestamp)
        if args.append:
            if args.document_type != "exp" or not target_id:
                raise DocdevError("--append is supported only for an existing exp")
            record = records.get(target_id)
            if not record or record["type"] != "exp":
                raise DocdevError(f"unknown exp: {target_id}")
            log = {
                "created_at": timestamp,
                "title": payload.get("title") or infer_title(payload["content"], "记录"),
                "content": payload["content"],
            }
            prospective = dict(record)
            prospective["logs"] = [*record["logs"], log]
            prospective["updated_at"] = timestamp
            validate_refs(prospective, records)
            save_record(root, prospective)
            records[target_id] = prospective
            reconcile(root, project, records, timestamp)
            return result_for(prospective, "append", True, auto_archived)
        if target_id:
            record = records.get(target_id)
            if not record or record["type"] != args.document_type:
                raise DocdevError(f"unknown {args.document_type}: {target_id}")
            data = {
                "title": payload.get("title", record["data"]["title"]),
                "content": payload["content"],
            }
            if data == record["data"]:
                return result_for(record, "update", False, auto_archived)
            prospective = dict(record)
            prospective["data"] = data
            prospective["updated_at"] = timestamp
            if record["type"] == "landing" and data["content"] != record["data"]["content"]:
                prospective["revision"] = record["revision"] + 1
            validate_refs(prospective, records)
            save_record(root, prospective)
            records[target_id] = prospective
            reconcile(root, project, records, timestamp)
            return result_for(prospective, "update", True, auto_archived)
        if args.document_type in {"index", "landing"}:
            raise DocdevError(f"{args.document_type} is initialized automatically; update it with --id")
        title = payload.get("title") or infer_title(payload["content"], args.document_type)
        for existing in records.values():
            if existing["type"] == args.document_type and existing["data"] == {"title": title, "content": payload["content"]}:
                return result_for(existing, "recover", False, auto_archived)
        record = make_record(root, records, args.document_type, title, payload["content"], timestamp)
        prospective_records = {**records, record["id"]: record}
        validate_refs(record, prospective_records)
        save_record(root, record)
        records[record["id"]] = record
        reconcile(root, project, records, timestamp)
        return result_for(record, "create", True, auto_archived)


def result_for(record, action, changed, auto_archived=None):
    result = {
        "ok": True,
        "action": action,
        "changed": changed,
        "id": record["id"],
        "type": record["type"],
        "path": record["path"],
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
    }
    if record["type"] == "landing":
        result["revision"] = record["revision"]
    if auto_archived:
        result["auto_archived"] = auto_archived
    return result


def search_command(args):
    root = resolve_project(args.project)
    terms = [value.casefold() for value in args.query.split() if value]
    with project_lock(root, exclusive=False):
        records = load_records(root)
    reverse = reverse_refs(records)
    results = []
    for record in records.values():
        refs = refs_for(record)
        if not args.all and record["archived"] is not bool(args.archived):
            continue
        if args.type and record["type"] not in args.type:
            continue
        if args.ref and args.ref not in refs and args.ref not in reverse.get(record["id"], []):
            continue
        text = "\n".join(
            [record["id"], title_for(record), record["data"]["content"], *(log["content"] for log in record.get("logs", []))]
        )
        folded = text.casefold()
        if terms and not all(term in folded for term in terms):
            continue
        results.append(
            {
                "id": record["id"],
                "type": record["type"],
                "title": title_for(record),
                "updated_at": record["updated_at"],
                **({"archived": True} if record["archived"] else {}),
                **(
                    {
                        "path": record["path"],
                        "created_at": record["created_at"],
                        "revision": record.get("revision"),
                        "snippet": snippet(text, terms),
                        "references": refs,
                        "referenced_by": sorted(reverse.get(record["id"], [])),
                    }
                    if args.verbose
                    else {}
                ),
            }
        )
    results.sort(key=lambda r: (r["id"] != args.query, r["title"].casefold() != args.query.casefold(), r["id"]))
    return {"ok": True, "query": args.query, "count": min(len(results), args.limit), "results": results[: args.limit]}


def snippet(text, terms, width=180):
    folded = text.casefold()
    positions = [position for term in terms if (position := folded.find(term)) >= 0]
    start = max(0, (min(positions) if positions else 0) - width // 3)
    return text[start : start + width].replace("\n", " ")


def clean_command(args):
    root = resolve_project(args.project)
    exp_path = root / "exp"
    if exp_path.is_symlink():
        raise DocdevError("refusing to clean: project exp directory is a symlink")
    exp_root = exp_path.resolve()
    if not exp_root.is_relative_to(root.resolve()):
        raise DocdevError("refusing to clean: project exp directory escapes project root")
    with project_lock(root):
        candidates = []
        for path in exp_root.rglob("*"):
            if path.is_symlink() or not path.is_dir() or not any(marker in path.name.casefold() for marker in CLEAN_MARKERS):
                continue
            resolved = path.resolve()
            if resolved == exp_root or not resolved.is_relative_to(exp_root):
                continue
            candidates.append(resolved)
        candidates.sort(key=lambda path: len(path.parts))
        selected = []
        for candidate in candidates:
            if not any(candidate.is_relative_to(parent) for parent in selected):
                selected.append(candidate)
        relative = [path.relative_to(root).as_posix() for path in selected]
        if not args.dry_run:
            for path in reversed(selected):
                shutil.rmtree(path)
        return {"ok": True, "dry_run": args.dry_run, "count": len(relative), "removed": relative}


def referrers_of(document_id, records):
    return sorted(
        record["id"]
        for record in records.values()
        if record["id"] != document_id and document_id in refs_for(record)
    )


def strip_refs(text, document_id, label):
    def replace(match):
        if match.group(1).strip() != document_id:
            return match.group(0)
        return match.group(2) or label

    return WIKI_REF_RE.sub(replace, text)


def rm_command(args):
    root = resolve_project(args.project)
    timestamp = now_string()
    with project_lock(root):
        project = load_project(root)
        records = load_records(root)
        issues = validate_project_state(root, project, records)
        if issues:
            raise DocdevError("project records are invalid", code=4, details={"issues": issues})
        record = records.get(args.id)
        if not record:
            raise DocdevError(f"unknown document: {args.id}")
        if record["type"] in {"index", "landing"}:
            raise DocdevError(f"{record['type']} documents cannot be removed")
        referrers = referrers_of(args.id, records)
        impact = {
            "ok": True,
            "id": args.id,
            "type": record["type"],
            "title": title_for(record),
            "path": record["path"],
            "referenced_by": referrers,
            "references": [reference for reference in refs_for(record) if reference in records],
        }
        if args.dry_run:
            return {**impact, "action": "dry-run", "changed": False, "removed": False, "rewritten": []}
        if referrers and not args.force:
            raise DocdevError(
                f"{args.id} is referenced by {len(referrers)} document(s); rerun with --force to remove it and strip those references",
                code=5,
                details={"referenced_by": referrers},
            )
        label = title_for(record)
        rewritten = []
        for referrer_id in referrers:
            referrer = dict(records[referrer_id])
            data = dict(referrer["data"])
            data["content"] = strip_refs(data["content"], args.id, label)
            changed = data["content"] != referrer["data"]["content"]
            referrer["data"] = data
            if referrer["type"] == "exp":
                logs = [{**log, "content": strip_refs(log["content"], args.id, label)} for log in referrer["logs"]]
                changed = changed or logs != referrer["logs"]
                referrer["logs"] = logs
            if referrer["type"] == "landing" and changed:
                referrer["revision"] = referrer["revision"] + 1
            referrer["updated_at"] = timestamp
            records[referrer_id] = referrer
            save_record(root, referrer)
            rewritten.append(referrer_id)
        del records[args.id]
        record_path(root, args.id).unlink(missing_ok=True)
        document_path(root, record).unlink(missing_ok=True)
        reconcile(root, project, records, timestamp)
        return {**impact, "action": "remove", "changed": True, "removed": True, "rewritten": rewritten}


def read_command(args):
    root = resolve_project(args.project)
    timestamp = now_string()
    with project_lock(root):
        project = load_project(root)
        records = load_records(root)
        issues = validate_project_state(root, project, records)
        if issues:
            raise DocdevError("project records are invalid", code=4, details={"issues": issues})
        record = records.get(args.id)
        if not record:
            raise DocdevError(f"unknown document: {args.id}")
        touch_calendar(root, timestamp)
        record = dict(record)
        record["last_read"] = timestamp
        save_record(root, record)
        records[args.id] = record
        result = {
            "ok": True,
            "id": record["id"],
            "type": record["type"],
            "title": title_for(record),
            "path": record["path"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
            "last_read": timestamp,
            "archived": record["archived"],
        }
        if record["type"] == "landing":
            result["revision"] = record["revision"]
        if not args.quiet:
            result["content"] = record["data"]["content"]
            if record["type"] == "exp":
                result["logs"] = record["logs"]
        return result


def stale_records(records, timestamp, days, calendar):
    """到期未读的可归档文档，按 last_read 从旧到新。

    计的是“活跃日”——docdev 实际被使用过的日期——而不是自然日，
    所以长时间不干活不会让文档被误归档。
    """
    today = timestamp[:10]
    candidates = []
    for record in records.values():
        if record["type"] not in ARCHIVE_TYPES or record["archived"]:
            continue
        idle = active_days_since(calendar, record["last_read"][:10], today)
        if idle > days:
            candidates.append((record, idle))
    candidates.sort(key=lambda item: (item[0]["last_read"], item[0]["id"]))
    return candidates


def set_archived(root, records, record, archived, timestamp):
    """切换归档状态并移动 Markdown；records 就地更新。返回新 record。"""
    source = document_path(root, record)
    updated = dict(record)
    updated["archived"] = archived
    updated["path"] = expected_path(updated)
    updated["last_read"] = timestamp
    target = document_path(root, updated)
    save_record(root, updated)
    records[updated["id"]] = updated
    if source != target and source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
    return updated


def auto_archive(root, records, timestamp, days=ARCHIVE_DAYS, skip=None):
    """写命令顺手归档到期文档；返回被归档的 ID。skip 指定本次要写的文档，不归档它。"""
    # 日历记录与归档开关无关：即使关掉自动归档，今天也确实是活跃日。
    calendar = touch_calendar(root, timestamp)
    if os.environ.get("DOCDEV_NO_AUTO_ARCHIVE"):
        return []
    archived = []
    for record, _ in stale_records(records, timestamp, days, calendar):
        if record["id"] == skip:
            continue
        set_archived(root, records, record, True, timestamp)
        archived.append(record["id"])
    return archived


def archive_command(args):
    root = resolve_project(args.project)
    timestamp = now_string()
    with project_lock(root):
        project = load_project(root)
        records = load_records(root)
        issues = validate_project_state(root, project, records)
        if issues:
            raise DocdevError("project records are invalid", code=4, details={"issues": issues})
        calendar = touch_calendar(root, timestamp)
        if args.id:
            # 显式归档指定文档（合并等场景用），不走天数筛选
            record = records.get(args.id)
            if not record:
                raise DocdevError(f"unknown document: {args.id}")
            if record["type"] not in ARCHIVE_TYPES:
                raise DocdevError(f"{record['type']} documents cannot be archived: {args.id}")
            listed = [{
                "id": record["id"], "type": record["type"], "title": title_for(record),
                "last_read": record["last_read"], "idle_active_days": None,
            }]
            if args.dry_run or not args.apply:
                return {"ok": True, "action": "dry-run", "changed": False, "id": args.id,
                        "active_days_recorded": len(calendar), "count": len(listed), "candidates": listed}
            set_archived(root, records, record, True, timestamp)
            reconcile(root, project, records, timestamp)
            return {"ok": True, "action": "archive", "changed": True, "id": args.id,
                    "active_days_recorded": len(calendar), "count": 1,
                    "archived": [record["id"]]}
        candidates = stale_records(records, timestamp, args.days, calendar)
        listed = [
            {"id": record["id"], "type": record["type"], "title": title_for(record),
             "last_read": record["last_read"], "idle_active_days": idle}
            for record, idle in candidates
        ]
        if args.dry_run or not args.apply:
            return {"ok": True, "action": "dry-run", "changed": False, "days": args.days,
                    "active_days_recorded": len(calendar), "count": len(listed), "candidates": listed}
        for record, _ in candidates:
            set_archived(root, records, record, True, timestamp)
        if candidates:
            reconcile(root, project, records, timestamp)
        return {"ok": True, "action": "archive", "changed": bool(candidates), "days": args.days,
                "active_days_recorded": len(calendar), "count": len(listed),
                "archived": [item["id"] for item in listed]}


def unarchive_command(args):
    root = resolve_project(args.project)
    timestamp = now_string()
    with project_lock(root):
        project = load_project(root)
        records = load_records(root)
        issues = validate_project_state(root, project, records)
        if issues:
            raise DocdevError("project records are invalid", code=4, details={"issues": issues})
        record = records.get(args.id)
        if not record:
            raise DocdevError(f"unknown document: {args.id}")
        if not record["archived"]:
            return {"ok": True, "action": "unarchive", "changed": False, "id": record["id"],
                    "path": record["path"], "archived": False}
        restored = set_archived(root, records, record, False, timestamp)
        reconcile(root, project, records, timestamp)
        return {"ok": True, "action": "unarchive", "changed": True, "id": restored["id"],
                "path": restored["path"], "archived": False}


def calendar_path(root):
    return Path(root) / "docs/.docdev/calendar.json"


def load_calendar(root):
    """活跃日列表（升序、去重的 YYYY-MM-DD）。日历缺失时视为空。"""
    path = calendar_path(root)
    if not path.is_file():
        return []
    value = read_json(path)
    if not isinstance(value, dict) or not isinstance(value.get("active_days"), list):
        raise DocdevError("calendar is invalid; delete docs/.docdev/calendar.json to reset")
    days = []
    for day in value["active_days"]:
        parse_timestamp(f"{day} 00:00", "calendar day")
        if day not in days:
            days.append(day)
    return sorted(days)


def touch_calendar(root, timestamp):
    """把 timestamp 所在日期记入活跃日历，返回更新后的日历。"""
    today = timestamp[:10]
    days = load_calendar(root)
    if today not in days:
        days = sorted([*days, today])
        write_json(calendar_path(root), {"active_days": days})
    return days


def active_days_since(days, since_day, today):
    """since_day 之后、today（含）之前的活跃日数量。

    只数 since_day 之后新出现的活跃日，所以空闲期完全不计入 ——
    休假十天没动过 docdev，任何文档的活跃日计数都不会增加。
    """
    return sum(1 for day in days if since_day < day <= today)


def validation_issues(root, project, records, include_files=True):
    issues = validate_project_state(root, project, records)
    if include_files:
        for directory in PROJECT_DIRS:
            if not (root / directory).is_dir():
                issues.append(f"missing directory: {directory}")
        for record in records.values():
            try:
                path = document_path(root, record)
                expected = render_document(root, record, records)
                if not path.exists():
                    issues.append(f"missing Markdown: {expected_path(record)}")
                elif path.read_text(encoding="utf-8") != expected:
                    issues.append(f"generated Markdown differs: {expected_path(record)}")
            except (DocdevError, KeyError, TypeError) as exc:
                issues.append(str(exc))
        gitignore = (root / ".gitignore").read_text(encoding="utf-8").splitlines() if (root / ".gitignore").exists() else []
        for entry in GITIGNORE_ENTRIES:
            if entry not in gitignore:
                issues.append(f"missing .gitignore entry: {entry}")
    return sorted(set(issues))


def validate_command(args):
    root = resolve_project(args.project)
    with project_lock(root, exclusive=args.fix):
        project = load_project(root)
        records = load_records(root)
        structural = validation_issues(root, project, records, include_files=False)
        if structural:
            raise DocdevError("validation failed", code=4, details={"issues": structural})
        if args.fix:
            for directory in PROJECT_DIRS:
                (root / directory).mkdir(parents=True, exist_ok=True)
            rerender_all(root, records)
            refresh_index(root, project, records, now_string())
            merge_gitignore(root)
        issues = validation_issues(root, project, records)
        if issues:
            raise DocdevError("validation failed", code=4, details={"issues": issues})
        return {"ok": True, "project": str(root), "documents": len(records), "issues": []}


def positive_integer(value):
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def build_parser():
    parser = JsonArgumentParser(prog="docdev", description="Document CLI for doc-driven research projects")
    commands = parser.add_subparsers(dest="command", required=True)

    init_parser = commands.add_parser("init", help="initialize a project directory")
    init_parser.add_argument("project_dir", nargs="?")
    init_parser.add_argument("--name")
    init_parser.set_defaults(handler=init_project)

    doc_parser = commands.add_parser("doc", help="create, replace, or append document content")
    doc_parser.add_argument("document_type", choices=DOCUMENT_TYPES)
    doc_parser.add_argument("--project")
    doc_parser.add_argument("--id", help="document ID; landing accepts dataset/model/pipeline")
    doc_parser.add_argument("--append", action="store_true", help="append one exp log entry")
    doc_parser.add_argument("--input", default="-", help="JSON file or - for stdin")
    doc_parser.set_defaults(handler=doc_command)

    search_parser = commands.add_parser("search", help="search records and references")
    search_parser.add_argument("query", nargs="?", default="")
    search_parser.add_argument("--project")
    search_parser.add_argument("--type", action="append", choices=DOCUMENT_TYPES)
    search_parser.add_argument("--ref")
    search_parser.add_argument("--limit", type=positive_integer, default=20)
    search_parser.add_argument("--verbose", action="store_true", help="include snippet, path and reference lists")
    search_parser.add_argument("--archived", action="store_true", help="search archived documents instead of active ones")
    search_parser.add_argument("--all", action="store_true", help="search both active and archived documents")
    search_parser.set_defaults(handler=search_command)

    clean_parser = commands.add_parser("clean", help="remove experiment directories containing debug or smoke")
    clean_parser.add_argument("--project")
    clean_parser.add_argument("--dry-run", action="store_true")
    clean_parser.set_defaults(handler=clean_command)

    board_parser = commands.add_parser("board", help="render the Markdown document board")
    board_parser.add_argument("--project")
    board_parser.add_argument("--max-nodes", type=positive_integer, default=BOARD_MAX_NODES)
    board_parser.add_argument("--no-graph", action="store_true")
    board_parser.set_defaults(handler=board_command)

    rm_parser = commands.add_parser("rm", help="remove one idea/exp/decision/lesson document")
    rm_parser.add_argument("id")
    rm_parser.add_argument("--project")
    rm_parser.add_argument("--force", action="store_true", help="remove even when referenced, stripping those references")
    rm_parser.add_argument("--dry-run", action="store_true", help="report the impact without removing")
    rm_parser.set_defaults(handler=rm_command)

    read_parser = commands.add_parser("read", help="read one document and record the access time")
    read_parser.add_argument("id")
    read_parser.add_argument("--project")
    read_parser.add_argument("--quiet", action="store_true", help="only record the access, omit content")
    read_parser.set_defaults(handler=read_command)

    archive_parser = commands.add_parser("archive", help="archive exp/decision/lesson documents left unread")
    archive_parser.add_argument("id", nargs="?", help="explicitly archive one document instead of stale candidates")
    archive_parser.add_argument("--project")
    archive_parser.add_argument("--days", type=positive_integer, default=ARCHIVE_DAYS)
    archive_parser.add_argument("--apply", action="store_true", help="move the candidates; omit for a dry run")
    archive_parser.add_argument("--dry-run", action="store_true", help="explicitly report without moving")
    archive_parser.set_defaults(handler=archive_command)

    unarchive_parser = commands.add_parser("unarchive", help="restore an archived document")
    unarchive_parser.add_argument("id")
    unarchive_parser.add_argument("--project")
    unarchive_parser.set_defaults(handler=unarchive_command)

    validate_parser = commands.add_parser("validate", help="validate or rebuild generated Markdown")
    validate_parser.add_argument("--project")
    validate_parser.add_argument("--fix", action="store_true")
    validate_parser.set_defaults(handler=validate_command)
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
        result = args.handler(args)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except DocdevError as exc:
        error = {"ok": False, "error": str(exc), "code": exc.code}
        if exc.details:
            error.update(exc.details)
        print(json.dumps(error, ensure_ascii=False, indent=2, sort_keys=True), file=sys.stderr)
        return exc.code
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": 2}, ensure_ascii=False), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print(json.dumps({"ok": False, "error": "interrupted", "code": 130}), file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
