#!/usr/bin/env python3
"""docdev 文档看板服务：交互式引用图谱 + Markdown/LaTeX 阅读 + 编辑/新增/删除。

用法:
    python3 docboard_server.py --project <docdev 项目目录> [--port 8600] [--host 0.0.0.0]

只读接口直接读 records；所有写操作一律 subprocess 调用 docdev CLI，
不直接修改 records 或生成的 Markdown（与 skill 的基本规则一致）。
"""

import argparse
import http.server
import json
import mimetypes
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path

PACK_DIR = Path(__file__).resolve().parent.parent
DOCDEV = PACK_DIR / "bin/docdev"
ASSET_DIR = PACK_DIR / "assets/board"
EDITABLE_TYPES = ("idea", "exp", "decision", "lesson")
CREATABLE_TYPES = EDITABLE_TYPES
MAX_BODY = 4 * 1024 * 1024

sys.path.insert(0, str(PACK_DIR / "scripts"))
import docdev  # noqa: E402


class BoardError(Exception):
    def __init__(self, message, status=400, details=None):
        super().__init__(message)
        self.status = status
        self.details = details or {}


def run_docdev(root, arguments, payload=None):
    """调用 docdev CLI；返回 (ok, 解析后的 JSON)。写操作的唯一入口。"""
    command = [sys.executable, str(PACK_DIR / "scripts/docdev.py"), *arguments, "--project", str(root)]
    process = subprocess.run(
        command,
        input=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
        text=True,
        capture_output=True,
        check=False,
    )
    stream = process.stdout if process.returncode == 0 else process.stderr
    try:
        result = json.loads(stream) if stream.strip() else {}
    except json.JSONDecodeError:
        result = {"ok": False, "error": (stream or "docdev produced no output").strip()[:500]}
    return process.returncode == 0, result


def load_state(root):
    project = docdev.load_project(root)
    records = docdev.load_records(root)
    return project, records


def graph_payload(root, project, records):
    reverse = docdev.reverse_refs(records)
    nodes, edges = [], []
    for document_id in sorted(records):
        record = records[document_id]
        forward = [r for r in docdev.refs_for(record) if r in records]
        backward = sorted(reverse.get(document_id, []))
        nodes.append(
            {
                "id": document_id,
                "type": record["type"],
                "title": docdev.title_for(record),
                "path": record["path"],
                "created_at": record["created_at"],
                "updated_at": record["updated_at"],
                "revision": record.get("revision"),
                "domain": record.get("domain"),
                "logs": len(record.get("logs", [])),
                "degree": len(forward) + len(backward),
                "refs": forward,
                "referenced_by": backward,
                "archived": record["archived"],
                "last_read": record["last_read"],
                "editable": record["type"] in EDITABLE_TYPES,
                "removable": record["type"] in EDITABLE_TYPES,
            }
        )
        edges.extend({"source": document_id, "target": target} for target in forward)
    return {
        "ok": True,
        "project": {"name": project["name"], "root": str(root), "index_id": project["index_id"]},
        "counts": {kind: sum(1 for r in records.values() if r["type"] == kind) for kind in docdev.DOCUMENT_TYPES},
        "nodes": nodes,
        "edges": edges,
    }


def document_payload(root, records, document_id):
    record = records.get(document_id)
    if not record:
        raise BoardError(f"unknown document: {document_id}", status=404)
    reverse = docdev.reverse_refs(records)

    def brief(target_id):
        target = records.get(target_id)
        return {"id": target_id, "title": docdev.title_for(target) if target else target_id}

    return {
        "ok": True,
        "id": document_id,
        "type": record["type"],
        "title": docdev.title_for(record),
        "path": record["path"],
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
        "revision": record.get("revision"),
        "domain": record.get("domain"),
        "content": record["data"]["content"],
        "logs": record.get("logs", []),
        "archived": record["archived"],
        "last_read": record["last_read"],
        "refs": [brief(r) for r in docdev.refs_for(record) if r in records],
        "referenced_by": [brief(r) for r in sorted(reverse.get(document_id, []))],
        "editable": record["type"] in EDITABLE_TYPES,
        "removable": record["type"] in EDITABLE_TYPES,
    }


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    @property
    def root(self):
        return self.server.project_root

    def _send(self, body, status=200, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
        self.wfile.flush()

    def _fail(self, exc):
        if isinstance(exc, BoardError):
            self._send({"ok": False, "error": str(exc), **exc.details}, status=exc.status)
        else:
            self._send({"ok": False, "error": str(exc)}, status=500)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        if length > MAX_BODY:
            raise BoardError("request body too large", status=413)
        try:
            value = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise BoardError(f"invalid JSON body: {exc}") from exc
        if not isinstance(value, dict):
            raise BoardError("body must be a JSON object")
        return value

    def _asset(self, name):
        target = (ASSET_DIR / name).resolve()
        if not target.is_relative_to(ASSET_DIR.resolve()) or not target.is_file():
            return self._send({"ok": False, "error": "not found"}, status=404)
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "image/svg+xml"):
            ctype += "; charset=utf-8"
        self._send(target.read_bytes(), ctype=ctype)

    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = urllib.parse.unquote(parsed.path)
            if path in ("/", "/index.html"):
                # 优先返回自包含单文件：经端口转发访问时子路径资源常拿不到
                return self._asset("board.inline.html" if (ASSET_DIR / "board.inline.html").is_file() else "board.html")
            if path == "/favicon.ico":
                return self._send(b"", status=204, ctype="image/x-icon")
            if path.endswith(".map"):
                # 内联库残留的 sourceMappingURL 探测：静默应答，避免污染控制台
                return self._send(b"", status=204, ctype="application/json")
            if path.startswith("/assets/"):
                return self._asset(path[len("/assets/"):])
            if path == "/api/graph":
                project, records = load_state(self.root)
                return self._send(graph_payload(self.root, project, records))
            if path == "/api/doc":
                query = urllib.parse.parse_qs(parsed.query)
                document_id = (query.get("id") or [""])[0]
                _, records = load_state(self.root)
                return self._send(document_payload(self.root, records, document_id))
            if path == "/api/types":
                return self._send({"ok": True, "creatable": list(CREATABLE_TYPES), "editable": list(EDITABLE_TYPES)})
            return self._send({"ok": False, "error": "not found"}, status=404)
        except (BoardError, docdev.DocdevError, OSError) as exc:
            self._fail(exc)

    do_HEAD = do_GET

    def do_POST(self):
        try:
            path = urllib.parse.urlparse(self.path).path
            body = self._body()
            if path == "/api/save":
                return self._save(body)
            if path == "/api/create":
                return self._create(body)
            if path == "/api/append":
                return self._append(body)
            if path == "/api/remove":
                return self._remove(body)
            if path == "/api/archive":
                arguments = ["archive", "--days", str(int(body.get("days") or 5))]
                if body.get("apply"):
                    arguments.append("--apply")
                ok, result = run_docdev(self.root, arguments)
                return self._send(result, status=200 if ok else 400)
            if path == "/api/unarchive":
                document_id = body.get("id")
                if not isinstance(document_id, str) or not document_id:
                    raise BoardError("`id` is required")
                ok, result = run_docdev(self.root, ["unarchive", document_id])
                return self._send(result, status=200 if ok else 400)
            if path == "/api/touch":
                # 在看板里读过也算读过：刷新 last_read，避免正在看的文档被归档。
                document_id = body.get("id")
                if not isinstance(document_id, str) or not document_id:
                    raise BoardError("`id` is required")
                ok, result = run_docdev(self.root, ["read", document_id, "--quiet"])
                return self._send(result, status=200 if ok else 400)
            if path == "/api/board":
                ok, result = run_docdev(self.root, ["board"])
                return self._send(result, status=200 if ok else 400)
            return self._send({"ok": False, "error": "not found"}, status=404)
        except (BoardError, docdev.DocdevError, OSError) as exc:
            self._fail(exc)

    def _content(self, body):
        content = body.get("content")
        if not isinstance(content, str) or not content.strip():
            raise BoardError("`content` is required and must be a non-empty string")
        payload = {"content": content}
        title = body.get("title")
        if isinstance(title, str) and title.strip():
            payload["title"] = title.strip()
        return payload

    def _save(self, body):
        document_id = body.get("id")
        _, records = load_state(self.root)
        record = records.get(document_id)
        if not record:
            raise BoardError(f"unknown document: {document_id}", status=404)
        arguments = ["doc", record["type"], "--id", document_id]
        ok, result = run_docdev(self.root, arguments, self._content(body))
        return self._send(result, status=200 if ok else 400)

    def _create(self, body):
        kind = body.get("type")
        if kind not in CREATABLE_TYPES:
            raise BoardError(f"type must be one of {', '.join(CREATABLE_TYPES)}")
        ok, result = run_docdev(self.root, ["doc", kind], self._content(body))
        return self._send(result, status=200 if ok else 400)

    def _append(self, body):
        document_id = body.get("id")
        _, records = load_state(self.root)
        record = records.get(document_id)
        if not record or record["type"] != "exp":
            raise BoardError("append is only supported for an existing exp", status=404)
        ok, result = run_docdev(self.root, ["doc", "exp", "--id", document_id, "--append"], self._content(body))
        return self._send(result, status=200 if ok else 400)

    def _remove(self, body):
        document_id = body.get("id")
        if not isinstance(document_id, str) or not document_id:
            raise BoardError("`id` is required")
        arguments = ["rm", document_id]
        if body.get("dry_run", True):
            arguments.append("--dry-run")
        elif body.get("force"):
            arguments.append("--force")
        ok, result = run_docdev(self.root, arguments)
        return self._send(result, status=200 if ok else 400)


def main():
    parser = argparse.ArgumentParser(description="docdev document board server")
    parser.add_argument("--project", required=True)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8600)
    args = parser.parse_args()

    root = docdev.resolve_project(args.project)
    if not DOCDEV.exists():
        print(f"missing docdev CLI: {DOCDEV}", file=sys.stderr)
        return 1

    class Server(http.server.ThreadingHTTPServer):
        project_root = root
        allow_reuse_address = True
        daemon_threads = True

    try:
        server = Server((args.host, args.port), Handler)
    except OSError as exc:
        print(f"failed to bind {args.host}:{args.port}: {exc}", file=sys.stderr)
        return 1
    print(f"docdev board: http://{args.host}:{args.port}/  (project: {root})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
