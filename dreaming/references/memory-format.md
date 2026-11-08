# Memory format

A dream produces a **wiki-style memory directory**: many small Markdown files that link to each other, plus `_index.md` as the catalog a future session reads first.

## Layout

```
<store>/
  _index.md              # the catalog; always read this first
  <slug>.md              # one topic per file
  <subdir>/<slug>.md     # optional grouping once the store is large
  .dream/                # bookkeeping: exports, manifest, state (never memory)
```

Memory files live at the root or in subdirectories. Anything under `.dream/` is run bookkeeping, not memory: never count it, index it, or cite it.

## File frontmatter

Every memory file starts on line 1 with:

```markdown
---
name: <slug>
description: <what this file covers and when to read it>
metadata: <freeform, optional>
---
```

- `name` equals the filename stem, lowercase and hyphen-separated.
- `description` says what is inside **and when to open it**; it is what a future agent scans.
- `metadata` is optional and free-form (dates, sources, confidence).

## Body rules

- Facts are current understanding, in plain statements: `Integration tests need FOO=1`, not `the agent then tried to run the tests`.
- Keep the concrete: exact commands, flags, paths, versions, identifiers, values, error strings, causal mechanisms. These are what a future agent greps for.
- Date facts that can go stale, and say how they were verified: `As of 2026-10-30 (verified by running make test): ...`.
- Supersede rather than delete. When a later session corrects an earlier fact, keep the current value and note what it replaced and when.
- When two sources genuinely conflict and neither is plainly later, keep both and mark it: `CONFLICT: <source A, date> says ...; <source B, date> says ...`.
- Process observations are facts worth keeping: what was tried and why it failed, which approach burned turns, what looked like a bug but was configuration.
- Drop first-person narration, dead-end hypotheses, and re-tellings of the session.
- Never copy credentials, API keys, tokens or passwords. Refer to them by role (`the deploy token`).
- Link a related topic inline as `[[other-slug]]` the first time it comes up.
- Keep each file under 100 KB; split by sub-topic when it grows.
- A retired file keeps exactly one line: `MOVED TO [[slug]]`. It gets no index entry.

## `_index.md`

One line per live memory file, grouped under `## <domain>` headings:

```markdown
## Project

- [[build-and-test]] — how to build, run the test suite, and the flags CI sets.
- [[release-process]] — version bump, changelog, tagging, and the publish step.
```

No entries for stubs, for `.dream/`, or for files that no longer exist. No live file without an entry. `_index.md` itself needs no entry and no frontmatter — but a short `# <store name>` heading and a one-line purpose at the top help.
