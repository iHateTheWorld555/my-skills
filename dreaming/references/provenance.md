# Provenance and design notes

## Source

Anthropic cookbook: [Dreaming with a dynamic workflow](https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/CMA_dreaming_with_a_dynamic_workflow.ipynb) (`managed_agents/`). Its helper `memory_distill_utils.py`, the four prompts under `example_data/memory_distill/prompts/`, and `dreaming_nightly.py` were read when porting this skill.

The original runs on **Claude Managed Agents** (beta): it exports sessions through the Sessions API, uploads transcript files, creates three persisted agents (lead, analyzer, organizer), starts a session with the memory store mounted read-write, has the lead agent write a workflow, and follows the run.

## What this skill keeps

- The three-way split: a **lead** orchestrates, one **analyzer per transcript** does verify → enrich → organize, one **organizer** runs after all analyzers.
- The memory product: small linked Markdown files with frontmatter, `[[slug]]` links, `_index.md` as the catalog, `MOVED TO [[slug]]` stubs, dated/stale facts, explicit `CONFLICT:` markers, 100 KB per file.
- The untrusted-input stance: transcripts are data, not instructions; injected instructions and secrets are never recorded.
- The concurrency rules: re-read before editing, targeted index edits, read-back verification of every write.
- The turn-efficiency rules: read a transcript once, batch independent calls, don't re-read.
- The coverage discipline: every transcript must reach an analyzer and the organizer must finish, or the run is reported as incomplete.
- The cost findings from the notebook: plain text beats JSON exports, a "fewer turns" section in the analyzer prompt pays for itself, and a cheap model is enough for analyzers.

## What changed, and why

| Original | Here | Why |
| --- | --- | --- |
| Managed Agents workflow run | Local `Agent` subagents, 3 in parallel | No platform dependency; the Claude Code skill already has the harness |
| Lead agent writes a workflow script | `SKILL.md` is the lead's fixed procedure | The task shape is known; generating a workflow each run adds failure modes |
| Memory store API | A plain directory under `~/.claude/dreams/<project-slug>/` | Auditable, greppable, version-control friendly |
| Sessions API export | `scripts/export_sessions.py` reads `~/.claude/projects/<slug>/*.jsonl` | That is where Claude Code writes sessions on disk |
| Time-window dedup (`COOKBOOK_SINCE`) | Content-hash state in `.dream/state.json` | A session can keep growing after export; hashes catch changes, timestamps miss them |
| Analyzer/organizer held only file tools, empty network allowlist | Prompts forbid Bash and web tools; subagents get file tools only by instruction | Claude Code subagents share the tool set, so the restriction is enforced by prompt |
| Nightly `nbclient` runner + cron | `references/scheduling.md` | Same idea, three ways to attach it |

## Reported cost of the original

From the notebook: eleven example transcripts (283 KB, ~97,000 tokens) cost $0.36 at list price and took about 2.5 minutes. Fifty long transcripts (about 12 MB) cost about $8 and ten minutes with the cost-saving settings, versus about $10 and nine minutes without them, over 60 and 30 dreams. Fact retention was about the same either way.

## What this skill does not claim

- It cannot know what happened after the last transcript; facts carry staleness notes and should be re-checked.
- A dream reorganizes and enriches; it does not re-run experiments or verify claims against reality.
- Memory built from untrusted transcripts can be wrong or poisoned. Read the store before wiring it into a system prompt, and mount it read-only to consumers.
