---
name: citation-bfs-survey
description: Breadth-first citation-graph literature survey driven by an on-disk queue. Use when the user names a research topic (optionally with seed papers) and wants a broad, systematic sweep of the literature — recording each paper's contribution, citation count, open-source status and star count, then expanding through its citations and references. Runs sub-agents in parallel and uses an external gate so the loop cannot early-stop. Triggers include 调研这个方向的文献 / 广度调研 / 滚雪球 / snowball / citation graph survey / 把相关论文都找出来 / literature sweep.
description_zh: 引文图广度优先文献调研
description_en: Citation-graph BFS literature survey
disable: false
agent_created: true
---

# citation-bfs-survey

BFS over the citation graph from a set of seed papers, with all state on disk so
the loop is resumable, parallelizable, and cannot be silently abandoned.

Complement to `frontier-survey`: that skill is about *judgment* (evidence
grading, counter-evidence, route comparison). This one is about *coverage*
(enumerate the neighborhood exhaustively). For a deliverable that argues a
conclusion, run this first for coverage, then apply `frontier-survey`'s grading
and adversarial passes to the collected set.

## The one rule

**You do not decide when the survey ends. `paperq.py gate` does.**

Never conclude "I have enough papers" or "the main work is covered". Call `gate`;
it exits 3 only when the queue is drained, every candidate is triaged, and the
paper target is met. Anything else means keep going.

**Never self-impose paper-count caps or iteration limits** ("stop after N
papers", "10 iterations is enough"). The only legitimate stop conditions are
gate rc3, the user's explicit instruction, or a hard external timeout. A
self-imposed cap leaves landmark works sitting in frontier/deferred while the
report ships without them — measured: a capped run reported 11/38 landmarks
that the same queue had 37/38 of at discovery time.

## Screening protocol (adopted from ARS deep-research)

Discovery (BFS) and relevance judgment are separate concerns. The queue's job
is to be *complete*; the screening protocol's job is to be *precise*. Neither
alone was sufficient — measured on DiT-based TTS: keyword-search skills (ARS,
agent-research-skills) recalled 19–30% of landmark works, BFS recalled 95% raw
but flooded the queue without LLM screening.

1. **Criteria before screening** (PRISMA discipline): at `init` or via
   `paperq.py criteria --text "..."`, write down what the user actually wants.
   Two parts: (a) *core class* — the papers the deliverable is about
   (e.g. "DiT/flow-matching/latent-diffusion 大规模零样本 TTS 系统");
   (b) *exclusions* — whole domains that are out no matter how cited (SSL
   encoders, codecs, speaker verification, ASR, metrics, toolkits, historical
   diffusion/vocoder lineage, other-domain methodology ancestors).
   Criteria live in DB meta and are surfaced in every `claim` response, so all
   parallel workers judge consistently.
   **If the user has not stated criteria, ask once and wait — never invent
   core-class boundaries on their behalf.** An agent-guessed criteria is how a
   blind-test run wrongly excluded Seed-TTS (an AR-LM system the user wanted)
   while looking internally consistent.
2. **Two-pass screening**: title pass bulk-rejects obvious outs (cheap);
   abstract pass only for borderline cases. Never re-read what is already
   rejected.
3. **Tier tagging on accept**: `accept <id> --why "..." --tier core` for
   papers matching the core class; `--tier ring2` for relevant-but-peripheral
   (same-era zero-shot TTS outside the core architecture, TTS corpora, etc.).
   Stored in `relevance` as a `[core]`/`[ring2]` prefix.
4. **Report by tier**: `report --tier core` produces the deliverable the user
   reads; `--tier ring2` / `--tier all` for the appendix. A survey without
   criteria gets a loud warning at init — do not skip them.
5. **Verify code claims**: `search_guess` repos are GitHub title-search hits —
   confirm via the paper's page before citing a repo.

## Setup

```bash
PQ=~/.claude/skills/citation-bfs-survey/scripts/paperq.py
O=survey-<topic-slug>      # one dir per survey; holds sqlite state + cache
```

Optional but strongly recommended — removes the main bottleneck:
```bash
export S2_API_KEY=...      # free: semanticscholar.org/product/api#api-key-form
export GITHUB_TOKEN=...    # raises GitHub search limit 10/min -> 30/min
```

## Phase 1 — seed

```bash
python3 $PQ --outdir $O init --topic "<topic>" \
    --min-year 2024 --max-depth 2 --target-papers 40 --min-seed-queries 6
python3 $PQ --outdir $O add 2211.17192 2401.10774        # user's seed papers, if any
python3 $PQ --outdir $O seed "speculative decoding" "draft model verification" \
    --sources arxiv,crossref,gscholar
```

**Query several engines per phrase.** Their blind spots are structural, not
random — arXiv indexes only preprints, Crossref and DBLP only published venue
work, Google Scholar reaches work that never touched arXiv. Measured on one
`"speculative decoding"` query at limit 8: all 7 Crossref hits and 5 of 8
Google Scholar hits had **no arXiv ID at all**, i.e. an arXiv-only survey
misses them entirely. Same-paper hits across engines collapse onto one row via
normalized-title dedup.

`seed` takes bare phrases (auto-wrapped into `abs:"..." OR ti:"..."`) or raw
arXiv field syntax (`cat:cs.CL AND abs:"..."`). Run **≥6 queries from different
angles** — the gate enforces this. Vary along: synonyms, the method name vs the
problem name, adjacent subfields, benchmark names, and a `survey OR review`
query (survey classification tables hand you a batch of names for free).

Check `silent_engines` in the output. A silent engine means that channel is
down, **not** that no such papers exist — run `probe` to tell the two apart.

## Phase 2 — the BFS loop

Each iteration:

```bash
python3 $PQ --outdir $O gate --batch 4     # rc 0 = continue, rc 3 = done
python3 $PQ --outdir $O claim --n 4        # hands out frontier papers
```

Then **dispatch one sub-agent per claimed paper, all in a single message** so
they run concurrently. Each sub-agent does, for its one paper:

1. `expand <id>` — queries every available citation-graph backend, pre-filters
   by year/influence **and a topic lexicon** (`--require-words`, word-boundary
   regex over title+abstract), writes candidates to the DB and prints them with
   abstracts and a `found_by` channel tag. The lexicon exists because expanding
   any seed drags in its whole generic-ML neighbourhood — measured: one
   flow-matching seed parked 1000+ irrelevant papers in deferred. Tune it per
   survey; `--keep-cites` (default 0) lets high-cited papers bypass it, but the
   user corrected this: methodology ancestors (DiT/LDM/CFG for a TTS survey)
   must NOT bypass — they are out of scope even at 10k+ citations.
2. Triage **every** candidate:
   `accept <id> --why "<one line tying it to the topic>"` or
   `reject <id1> <id2> ... --why "<reason>"`.
   **Acceptance = the paper itself belongs to the topic domain.** For a
   DiT-based-TTS survey: TTS/speech-synthesis papers only. "Supports the
   technical route" is NOT acceptance grounds for a paper from another domain.
   Borderline domains (ASR, codecs, deepfake detection, audio understanding,
   text-to-audio) default to reject.
   Check nothing was missed with `pending --parent <id>` — `list` truncates,
   `pending` does not. `reject-rest <id> --why "..."` clears a long off-topic
   tail in one call (read them first).
   Accepted papers become frontier at depth+1.
3. `record <id> --summary "<3-5 sentences: problem, method, headline result>"`
   Add `--code-url <repo>` when the paper states one (exact repo lookup);
   otherwise the script guesses via GitHub search — mark those `search_guess`
   results as unverified. `--no-code` if the paper releases nothing.

`record` refuses to run while that paper still has untriaged candidates, and
refuses summaries under 80 chars. Both are deliberate.

Existing queues can be retro-swept when the acceptance policy changes:
`sweep [--status deferred,candidate,frontier,in_progress,done] [--keep-cites 0]`
applies the same lexicon rule and moves failures to rejected (reversible via
SQL). Dry-run first and eyeball the kill list before applying.

Sub-agent prompts must state: the topic, the paper id, `--outdir`, the full
`expand → triage → record` sequence, and "do not decide the survey is finished".

Loop back to `gate`. Repeat until rc 3.

## Phase 3 — report

```bash
python3 $PQ --outdir $O report --out survey.md
```

Emits an overview table (title, year, citations, repo, stars, depth, discovery
path) plus per-paper notes. Then write the analysis yourself — the generated file
is a structured record, not a narrative.

## Unattended mode (ralph loop)

To run the whole thing without supervision, each iteration in a **fresh agent
process** (no context accumulation, no drift):

```bash
~/.claude/skills/citation-bfs-survey/scripts/ralph.sh --outdir $O --max-iters 30
```

It calls `gate`, injects the verdict into a new `claude -p` invocation, and
repeats until rc 3 or the iteration cap. Progress lives in the sqlite file, so
killing it mid-run loses nothing — just rerun. Override the driver with
`--agent "codex exec"` or `RALPH_AGENT`.

Inside Claude Code, `/survey-loop <outdir>` runs one iteration under the same
contract. Any `/loop`-style wrapper works, as long as the per-turn instruction
is "advance the queue, then stop" and the continue/stop decision comes from
`gate`'s exit code rather than your own judgment.

## Queue states

`frontier` (waiting to expand) → `in_progress` (claimed) → `done` (recorded).
Candidates land in `candidate` (awaiting triage) and leave via `accept`
(→ frontier) or `reject`. Over-budget candidates are parked in `deferred`, not
deleted — when the frontier dries up while the paper target is unmet, `gate`
automatically revives the newest deferred batch. That is the mechanism that
makes early stopping impossible; `list --status deferred` shows the reserve.

## Discovery channels

Two orthogonal axes. Coverage comes from combining them, not from any one being
good.

**Discovery sources** (`seed --sources`), keyword search:

| source | state (measured 2026-09) | unique value |
|---|---|---|
| `arxiv` | reliable, newest-first | preprints; the only channel that reliably surfaces last-month work |
| `crossref` | reliable | published/peer-reviewed work, DOI-native — no arXiv ID needed |
| `gscholar` | works, HTML scrape | indexes venue/journal work with no arXiv version; yields cluster ids |
| `s2` | often 429 without a key | relevance ranking |
| `dblp` | intermittent (`http=000` on repeat calls) | CS venue records |

**Citation-graph backends** (`expand --backends`):

| backend | state | unique value |
|---|---|---|
| `s2` | reliable, both directions | the BFS engine; arXiv-native |
| `s2rec` | reliable | S2 recommendations — reaches papers with **no citation-graph link** to the seed |
| `gscholar` | works, needs a cluster id | citing work that never reached arXiv or S2 |
| `opencit` | works, DOI-only | independent index; weak on preprints (measured: 5 citations vs S2's 1959 on the same paper) |

`s2rec` earns its slot: it returned `SpecLA: Efficient Speculative Decoding for
Linear Attention` and other on-topic 2026 work that pure BFS from the seed does
not reach, including papers with no arXiv ID.

Run `probe` any time coverage looks thin — it live-checks all 8 backends in
~20s and separates "no such papers" from "this channel is down". That confusion
is the most common cause of a survey silently under-covering its topic.

```bash
python3 $PQ --outdir $O probe
```

Dead ends, do not reinvent: **OpenAlex** is now metered and returns 429 at $0
budget; **paperswithcode**'s API is retired (302). Both appear in older
tutorials as free options.

## API reality (measured, 2026-09)

- **arXiv must be `https://`.** `http://export.arxiv.org` returns 301 with an
  empty body; curl without `-L` then looks exactly like "the paper does not
  exist". This false negative has previously been misread as fabricated IDs.
- **Google Scholar is scraped, not an API.** Measured: 5 consecutive queries
  plus a `cites=` page all returned 200 with no CAPTCHA, and 10/10 result blocks
  exposed a cluster id and cited-by count. But `scholarly`'s own README warns
  that `search_pubs`/`citedby` will get your IP blocked, so treat it as a
  low-volume supplement: every response is cached, and a CAPTCHA response makes
  the backend return empty rather than retry.
- All fetches are cached under `$O/.cache/`, so retries and reruns are cheap.
  Delete that dir to force-refresh citation counts.
- 429/5xx are retried with exponential backoff (4s → 90s) inside the script.
  Do not wrap it in your own retry loop. `s2` keyword search is deliberately
  single-attempt — retrying it stalls seeding for minutes.
- If `expand` reports `degraded_backends`, that channel failed after all
  retries. Re-run `expand` later; the cache keeps whatever succeeded.

No pip installs. Everything is stdlib `urllib` against public endpoints, so
there is nothing to break in a fresh environment. `scholarly`,
`semanticscholar` and the various paper-search MCP servers were evaluated and
rejected: they add a dependency and an abstraction layer without adding a single
data source this doesn't already reach, and `scholarly` specifically requires
paid proxies for exactly the two calls that matter here.

## Pitfalls

- **Do not paraphrase from search-result snippets.** A summary must come from the
  abstract or the paper body. For full text use `arxiv.org/html/<id>` or
  `ar5iv.labs.arxiv.org/html/<id>` — never the PDF (binary garbage through
  web-fetch tools).
- **A seminal paper's references are mostly background, not neighbours.** Expanding
  the 2022 speculative-decoding paper returns Attention / BERT / GPT-3 / GELU —
  the whole ML canon. `expand` drops pre-`min-year` papers above
  `--generic-cites` (default 8000) and splits the candidate budget **per
  channel** (cited_by / cites / recommended). Without the per-channel split the
  biggest channel starves the rest: measured, 200+ `cited_by` items pushed all
  30 recommendations into `deferred`, silently discarding the one channel that
  reaches non-graph-connected work.
- **Citation counts are a discovery signal, not a quality verdict.** Recent
  strong work has near-zero citations; `expand` keeps low-cite recent papers on
  purpose and only applies the citation floor to pre-`min-year` work. Counts
  also differ per source — the DB keeps the max seen, so a Crossref count does
  not overwrite a larger S2 count.
- **Cross-source dedup is by normalized title.** Same paper, three ids (arXiv id,
  DOI, GS cluster). If two genuinely different papers share a title, they will
  merge — rare, but check `list` output if a row looks wrong.
- **`code_status: search_guess` is unverified.** GitHub search matches on title
  words and will happily return a reimplementation or an unrelated repo.
  Measured: the seminal speculative-decoding paper resolved to
  `NVIDIA/Model-Optimizer` (3.7k stars), which is not its repo. Verify before any
  repo appears in a deliverable.
- **Depth 2 from a good seed set is usually plenty**; depth 3 explodes and drags
  in the whole field. Widen with new seed queries before raising `--max-depth`.
- **Rejections are permanent within a run.** They are logged with a reason —
  check `list --status rejected` before concluding an area is absent.
- Two workers claiming the same paper is prevented by the DB; stale claims are
  auto-reclaimed after 30 min, so a crashed sub-agent never blocks the queue.
