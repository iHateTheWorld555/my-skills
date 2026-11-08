#!/usr/bin/env python3
"""Check a dream store against the memory-format rules.

Reports missing or mismatched frontmatter, oversized files, a missing or
incomplete _index.md, entries for files that do not exist, and broken links.
Exit status is 1 when any problem is found.
"""

import argparse
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.S)
LINK = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
INDEX_ENTRY = re.compile(r"^\s*-\s*\[\[([^\]]+)\]\]", re.M)
MAX_BYTES = 100 * 1024


def memory_files(store):
    return sorted(
        path
        for path in store.rglob("*.md")
        if not any(part.startswith(".") for part in path.relative_to(store).parts)
    )


def parse_frontmatter(text):
    match = FRONTMATTER.match(text)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            name, value = line.split(":", 1)
            fields[name.strip()] = value.strip()
    return fields


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("store", type=Path, help="memory store root")
    args = parser.parse_args()
    store = args.store.resolve()
    if not store.is_dir():
        sys.exit(f"No memory store at {store}")

    problems = []
    live = {}
    stubs = set()
    for path in memory_files(store):
        if path.name == "_index.md":
            continue
        text = path.read_text(encoding="utf-8")
        slug = path.stem
        if text.strip().startswith("MOVED TO"):
            stubs.add(slug)
            continue
        live[slug] = text
        if path.stat().st_size > MAX_BYTES:
            problems.append(f"{path.relative_to(store)}: {path.stat().st_size} bytes, over the 100 KB limit")
        fields = parse_frontmatter(text)
        if fields is None:
            problems.append(f"{path.relative_to(store)}: missing frontmatter block")
            continue
        if fields.get("name") != slug:
            problems.append(f"{path.relative_to(store)}: frontmatter name {fields.get('name')!r} != filename {slug!r}")
        if not fields.get("description"):
            problems.append(f"{path.relative_to(store)}: missing description")

    index_path = store / "_index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    entries = INDEX_ENTRY.findall(index_text)
    if not index_path.exists():
        problems.append("_index.md: missing")
    for slug in sorted(set(entries)):
        if entries.count(slug) > 1:
            problems.append(f"_index.md: duplicate entry [[{slug}]]")
        if slug not in live:
            problems.append(f"_index.md: entry [[{slug}]] has no live file")
    for slug in sorted(live):
        if slug not in entries:
            problems.append(f"_index.md: live file [[{slug}]] has no entry")

    known = set(live) | stubs | {"_index"}
    for slug, text in sorted(live.items()):
        body = FRONTMATTER.sub("", text, count=1)
        for target in sorted(set(LINK.findall(body))):
            if target not in known:
                problems.append(f"{slug}.md: link [[{target}]] points at no file")

    print(f"store: {store}")
    print(f"files: {len(live)} live, {len(stubs)} stubs, {len(entries)} index entries")
    if problems:
        print(f"problems: {len(problems)}")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)
    print("problems: 0")


if __name__ == "__main__":
    main()
