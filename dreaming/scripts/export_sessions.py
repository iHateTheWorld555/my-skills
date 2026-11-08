#!/usr/bin/env python3
"""Export Claude Code sessions as labeled plain text for a dream.

Reads ~/.claude/projects/<project-slug>/*.jsonl, writes one .txt per session
plus manifest.json, and records which content hashes a previous dream covered.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

LABEL_LINE = re.compile(
    r"^(USER:|AGENT:|TOOL CALL |TOOL RESULT \(|EVENT |SESSION |NOTE ABOUT THIS FILE:|=== )"
)


def read_jsonl(path):
    """Return the file's JSON events and the number of undecodable lines."""
    events = []
    bad = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1
    return events, bad


def text_of(content):
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    elif isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False)
    else:
        return "" if content is None else str(content)


def block(label, text, max_chars):
    """One labeled block. Label-looking body lines are indented so parsers keep them as body."""
    if max_chars and len(text) > max_chars:
        text = text[:max_chars] + f"\n[... truncated {len(text) - max_chars} chars ...]"
    body = "\n".join(" " + line if LABEL_LINE.match(line) else line for line in text.splitlines())
    return f"{label}\n{body}\n"


def render_input(value):
    if not isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    parts = []
    for name, item in value.items():
        text = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
        parts.append(f"{name}:\n{text}" if "\n" in text else f"{name}: {text}")
    return "\n".join(parts)


def render_events(events, max_chars):
    """Render one thread's events into labeled blocks."""
    tool_names = {}
    blocks = []
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        kind = event.get("type")
        content = message.get("content")
        if kind == "user" and isinstance(content, str):
            blocks.append(block("USER:", content, max_chars))
        elif kind == "user" and isinstance(content, list):
            for part in content:
                if part.get("type") == "text" and part.get("text"):
                    blocks.append(block("USER:", part["text"], max_chars))
                elif part.get("type") == "tool_result":
                    name = tool_names.get(part.get("tool_use_id"), "tool")
                    suffix = " [error]" if part.get("is_error") else ""
                    blocks.append(block(f"TOOL RESULT ({name}){suffix}:", text_of(part.get("content")), max_chars))
        elif kind == "assistant" and isinstance(content, str):
            blocks.append(block("AGENT:", content, max_chars))
        elif kind == "assistant" and isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    blocks.append(block("AGENT:", part.get("text", ""), max_chars))
                elif part.get("type") == "tool_use":
                    name = part.get("name", "tool")
                    tool_names[part.get("id")] = name
                    blocks.append(block(f"TOOL CALL {name}:", render_input(part.get("input")), max_chars))
        elif kind == "system":
            text = text_of(content)
            if text:
                blocks.append(block(f"EVENT {message.get('subtype') or 'system'}:", text, max_chars))
    return blocks


def session_title(events, fallback):
    for kind, field in (("custom-title", "customTitle"), ("ai-title", "aiTitle"), ("agent-name", "agentName")):
        for event in reversed(events):
            if event.get("type") == kind and event.get(field):
                return str(event[field]).replace("\n", " ")
    return fallback


def session_meta(events):
    for event in events:
        if event.get("cwd"):
            return event.get("cwd", ""), event.get("gitBranch", ""), event.get("timestamp", "")
    return "", "", ""


def subagent_label(path):
    meta_path = path.with_name(path.stem + ".meta.json")
    if not meta_path.exists():
        return path.stem
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return " | ".join(
        str(meta[key]) for key in ("agentType", "description", "model") if meta.get(key)
    ) or path.stem


def export_session(path, max_tool_chars, max_session_chars, with_subagents):
    """Return the rendered text, the session title and the number of bad lines."""
    events, bad = read_jsonl(path)
    session_id = path.stem
    title = session_title(events, session_id)
    cwd, branch, started = session_meta(events)
    header = [f"SESSION {session_id} | title: {title}"]
    header.append(f"NOTE ABOUT THIS FILE: started {started or 'unknown'}; cwd {cwd or 'unknown'}; branch {branch or 'unknown'}")
    header.append(
        "NOTE ABOUT THIS FILE: subagent threads are included as sub-thread sections."
        if with_subagents
        else "NOTE ABOUT THIS FILE: subagent threads are not exported; their conclusions appear as Agent tool results."
    )
    header.append(f"=== primary thread {session_id}: main ===")
    sub_threads = []
    if with_subagents:
        for sub_path in sorted((path.parent / path.stem / "subagents").glob("*.jsonl")):
            sub_events, sub_bad = read_jsonl(sub_path)
            bad += sub_bad
            sub_threads.append((sub_path, sub_events))

    def build(cap):
        lines = list(header)
        lines.extend(render_events(events, cap))
        for sub_path, sub_events in sub_threads:
            lines.append(f"=== sub-thread {sub_path.stem}: {subagent_label(sub_path)} ===")
            lines.extend(render_events(sub_events, cap))
        return "\n".join(lines) + "\n"

    text = build(max_tool_chars)
    if len(text) > max_session_chars:
        # Tool output dominates; shrink every tool block proportionally before cutting anything.
        cap = max(150, max_tool_chars * max_session_chars // len(text))
        text = build(cap)
    if len(text) > max_session_chars:
        text = trim_middle(text, max_session_chars)
    return text, title, bad


def trim_middle(text, budget):
    """Keep the opening and the conclusion; mark the omitted middle."""
    keep_head = budget * 2 // 3
    keep_tail = budget - keep_head - 200
    omitted = len(text) - keep_head - keep_tail
    return f"{text[:keep_head]}\n[... {omitted} chars omitted from the middle ...]\n{text[-keep_tail:]}"


def private_write(path, text):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)


def parse_since(value):
    if value.endswith("d") and value[:-1].isdigit():
        return datetime.now(timezone.utc) - timedelta(days=int(value[:-1]))
    return datetime.fromisoformat(value)


def project_dir(cwd):
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(cwd.resolve()))
    return Path.home() / ".claude" / "projects" / slug


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="working directory whose sessions to export")
    parser.add_argument("--store", type=Path, help="memory store root (default ~/.claude/dreams/<project-slug>)")
    parser.add_argument("--since", default="14d", help="ISO timestamp or Nd, e.g. 14d (default)")
    parser.add_argument("--limit", type=int, help="at most this many sessions, newest first")
    parser.add_argument("--id", action="append", help="export only this session id (repeatable)")
    parser.add_argument("--min-bytes", type=int, default=4096, help="skip JSONL files smaller than this")
    parser.add_argument("--min-age-minutes", type=int, default=5, help="skip sessions modified this recently (live ones)")
    parser.add_argument("--max-tool-chars", type=int, default=2000, help="truncate each tool call or result beyond this")
    parser.add_argument("--max-session-chars", type=int, default=2000000, help="character budget per exported transcript")
    parser.add_argument("--with-subagents", action="store_true", help="also export subagent transcripts")
    parser.add_argument("--include-unchanged", action="store_true", help="export sessions a previous dream covered")
    parser.add_argument("--commit", type=Path, metavar="MANIFEST", help="mark the sessions in this run's manifest.json as dreamed")
    args = parser.parse_args()

    if args.commit:
        manifest = json.loads(args.commit.read_text(encoding="utf-8"))
        store = args.store or Path(manifest["store"])
        state_path = store / ".dream" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"version": 1, "seen": {}}
        now = datetime.now(timezone.utc).isoformat()
        done = [record for record in manifest["transcripts"] if record["written"]]
        for record in done:
            state["seen"][record["id"]] = {"sha256": record["sha256"], "dreamed_at": now}
        state["last_run"] = now
        state_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        private_write(state_path, json.dumps(state, ensure_ascii=False, indent=2))
        print(f"marked {len(done)} sessions as dreamed in {state_path}")
        return

    sessions_dir = project_dir(args.project)
    if not sessions_dir.is_dir():
        sys.exit(f"No transcript directory at {sessions_dir}. Run one session in {args.project} first.")

    store = args.store or Path.home() / ".claude" / "dreams" / sessions_dir.name
    state_path = store / ".dream" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"version": 1, "seen": {}}

    since = parse_since(args.since)
    horizon = datetime.now(timezone.utc) - timedelta(minutes=args.min_age_minutes)
    candidates = [path for path in sessions_dir.glob("*.jsonl") if path.is_file()]
    if args.id:
        candidates = [path for path in candidates if path.stem in args.id]
    candidates = [
        path
        for path in candidates
        if path.stat().st_size >= args.min_bytes
        and since <= datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) <= horizon
    ]
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    if args.limit:
        candidates = candidates[: args.limit]
    if not candidates:
        print(f"No sessions to export from {sessions_dir} (since {since.isoformat()}).")
        return

    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out_dir = store / ".dream" / "transcripts" / run_id
    plan = []
    for path in candidates:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        known = state["seen"].get(path.stem, {}).get("sha256")
        status = "new" if known is None else ("changed" if known != digest else "unchanged")
        plan.append((path, digest, status))
    counts = {
        status: sum(record_status == status for _, _, record_status in plan)
        for status in ("new", "changed", "unchanged")
    }
    todo = [item for item in plan if item[2] != "unchanged" or args.include_unchanged]
    if not todo:
        print(f"store: {store}")
        print(f"transcripts: {counts['new']} new, {counts['changed']} changed, {counts['unchanged']} unchanged")
        print("nothing to export")
        return

    suffix = 1
    while out_dir.exists():
        suffix += 1
        out_dir = store / ".dream" / "transcripts" / f"{run_id}-{suffix}"
    out_dir.mkdir(mode=0o700, parents=True, exist_ok=True)

    transcripts = []
    for path, digest, status in plan:
        record = {
            "id": path.stem,
            "title": "",
            "path": "",
            "bytes": 0,
            "sha256": digest,
            "status": status,
            "written": False,
            "bad_lines": 0,
        }
        if status != "unchanged" or args.include_unchanged:
            text, title, bad = export_session(path, args.max_tool_chars, args.max_session_chars, args.with_subagents)
            out_path = out_dir / f"{path.stem}.txt"
            private_write(out_path, text)
            record.update(title=title, path=str(out_path), bytes=len(text), written=True, bad_lines=bad)
        transcripts.append(record)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": str(args.project.resolve()),
        "store": str(store),
        "since": since.isoformat(),
        "counts": counts,
        "transcripts": transcripts,
    }
    manifest_path = out_dir / "manifest.json"
    private_write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2))

    exported = [record for record in transcripts if record["written"]]
    total_bytes = sum(record["bytes"] for record in exported)
    print(f"store: {store}")
    print(f"transcripts: {counts['new']} new, {counts['changed']} changed, {counts['unchanged']} unchanged")
    print(f"exported {len(exported)} files, {total_bytes / 1024:.0f} KB -> {out_dir}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
