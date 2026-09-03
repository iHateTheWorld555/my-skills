#!/usr/bin/env python3
"""docdev 文档合并工具：把碎片文档按主题合成聚合文档，原文档归档（可恢复）。

用法:
    python3 merge_docs.py <groups.json> [--project P] [--dry-run] [--apply]

groups.json 结构:
    [
      {"kind": "lesson", "title": "聚合标题", "ids": ["lesson-...", ...]},
      ...
    ]

行为:
    - 每个组: 新建一篇 <kind> 聚合文档(内容=各原文档正文 + 原引用),
      原文档标记归档(移入 docs/archive/, 引用自动重算, 不产生死链)
    - --dry-run: 只输出计划, 不执行
    - --apply: 执行合并
    - 全程走 docdev CLI, 不手改 records
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
DOCDEV = PACK / "bin/docdev"
WIKI = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def run_docdev(root, args, payload=None, now=None):
    env = os.environ.copy()
    if now:
        env["DOCDEV_NOW"] = now
    proc = subprocess.run(
        [str(DOCDEV), *args, "--project", str(root)],
        input=json.dumps(payload, ensure_ascii=False) if payload else None,
        text=True, capture_output=True, env=env, check=False,
    )
    stream = proc.stdout if proc.returncode == 0 else proc.stderr
    try:
        return proc.returncode == 0, json.loads(stream) if stream.strip() else {}
    except json.JSONDecodeError:
        return False, {"error": (stream or "no output")[:200]}


def load_records(root):
    records = {}
    for path in (Path(root) / "docs/.docdev/records").glob("*.json"):
        r = json.loads(path.read_text(encoding="utf-8"))
        records[r["id"]] = r
    return records


def build_aggregate(group, records):
    """把一组原文档拼成聚合文档的正文。保留各篇标题与引用。"""
    parts = []
    missing = []
    for doc_id in group["ids"]:
        r = records.get(doc_id)
        if not r:
            missing.append(doc_id)
            continue
        content = r["data"]["content"].strip()
        parts.append(f"## {r['data']['title']}\n\n{content}")
    body = "\n\n---\n\n".join(parts)
    return body, missing


def main():
    ap = argparse.ArgumentParser(description="merge docdev documents by topic")
    ap.add_argument("groups_file")
    ap.add_argument("--project", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--now", default=None)
    args = ap.parse_args()

    groups = json.loads(Path(args.groups_file).read_text(encoding="utf-8"))
    root = Path(args.project).resolve()
    records = load_records(root)

    plan = []
    for group in groups:
        kind, title = group["kind"], group["title"]
        ids = group["ids"]
        missing = [i for i in ids if i not in records]
        body, _ = build_aggregate(group, records)
        plan.append({
            "kind": kind, "title": title, "count": len(ids),
            "missing": missing,
            "content_chars": len(body),
        })

    if args.dry_run:
        total_in = sum(p["count"] for p in plan)
        total_out = len(plan)
        print(json.dumps({
            "ok": True, "action": "dry-run",
            "groups": len(plan),
            "docs_in": total_in, "docs_out": total_out,
            "net_reduction": total_in - total_out,
            "plan": plan,
        }, ensure_ascii=False, indent=2))
        return 0

    if not args.apply:
        print(json.dumps({"ok": False, "error": "pass --apply to execute"}, ensure_ascii=False))
        return 1

    results = []
    for group in groups:
        kind, title = group["kind"], group["title"]
        ids = group["ids"]
        body, missing = build_aggregate(group, records)
        # 1. 创建聚合文档
        ok, created = run_docdev(root, ["doc", kind],
                                 {"title": title, "content": body}, now=args.now)
        if not ok:
            results.append({"title": title, "ok": False, "error": created.get("error", "?"), "missing": missing})
            continue
        agg_id = created["id"]
        # 2. 原文档归档（移入 docs/archive/，可恢复，引用自动重算）
        archived = []
        for doc_id in ids:
            if doc_id == agg_id:
                continue
            ok, res = run_docdev(root, ["archive", doc_id, "--apply"], now=args.now)
            if ok:
                archived.append(doc_id)
            else:
                archived.append({"id": doc_id, "error": res.get("error", "?")})
        results.append({
            "title": title, "aggregate_id": agg_id, "ok": True,
            "archived": archived, "missing": missing,
        })

    # 3. 重渲染看板与校验
    run_docdev(root, ["board"], now=args.now)
    ok, val = run_docdev(root, ["validate"], now=args.now)
    print(json.dumps({
        "ok": True, "action": "apply",
        "groups": len(results),
        "results": results,
        "validate_ok": ok,
        "validate_issues": val.get("issues", []),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
