---
name: research-paper-writing
description: Improve academic paper writing quality for ML/CV/NLP papers. Use when drafting or revising Abstract, Introduction, Related Work, Method, Experiments, or Conclusion; fixing paragraph or sentence flow; upgrading academic phrasing; checking grammar (articles, agreement, syntax, collocations); or doing a pre-submission review. Four task types (structure, flow, grammar, review), each routed to its own reference folder and closed by an independent scoring agent that must score the edit 8+ out of 10.
agent_created: true
---

# Research Paper Writing

## Overview

Improve ML/CV/NLP paper writing. Four task types; every edit is closed by an independent scoring agent. All reference files are in English; prose examples inside them are English.

## Task routing

Decide the task type first (mixed tasks route per part and merge at the end). When unclear, ask.

| Request | Type | Read |
|---|---|---|
| Rewrite a section (Abstract / Introduction / Related Work / Method / Experiments / Conclusion) or the paper's overall architecture | **structure** | `structure/<section>.md`; for whole-paper architecture also the logic map in `structure/introduction.md` |
| Fix flow of a paragraph/sentence; upgrade wording or phrasing | **flow** | `flow/flow.md`; phrase banks in `phrases/` |
| Grammar check (articles, agreement, syntax, collocations) | **grammar** | `grammar/grammar-checklist.md` |
| Pre-submission review, reject-risk audit | **review** | `review/paper-review.md` |

Load only the files for the current task.

## Common workflow

1. Read the reference files for the task.
2. Save the original text before editing (keep before/after).
3. Edit according to the rules.
4. Launch a scoring agent (below). Mandatory.
5. Done only when the score is **8+ / 10**; otherwise iterate or report why it cannot pass.

## Scoring loop

The scorer must be a freshly launched agent that sees only the text, not the editing process. Launch a general-purpose agent with:

```
You are an academic writing reviewer. Read <skill-path>/review/scoring.md, then
score the TEXT below on the dimension(s) requested. Compare against the ORIGINAL
(for meaning drift only, not scored).

TEXT (revised):
<revised text>

ORIGINAL (reference only):
<original text>

Output: score NN/10; issues found (quote + one line each); one-line verdict.
```

- **Score 8+**: pass. Report score and main changes.
- **Score < 8**: fix per the scorer's issues and resubmit. Also check whether the edit changed scientific meaning; revert any sentence where it did.
- **Max 5 rounds.** After that, report the score, remaining issues, and why further editing has no return (usually a logic or evidence problem in the original, not wording).

`review/scoring.md` is one page: score against this skill's rules, 10-point scale, no separate rubric.

## structure

Files: `structure/abstract.md`, `structure/introduction.md`, `structure/related-work.md`, `structure/method.md`, `structure/experiments.md`, `structure/conclusion.md`, example bank `structure/examples/index.md`.

1. Logic before prose: use the backward-reasoning questions in `structure/introduction.md`.
2. One section guide at a time.
3. Every major claim must map to experimental evidence; weaken or remove unsupported claims.
4. Reverse-outline before submitting to the scorer.

## flow

Files: `flow/flow.md` (all rules), `phrases/phrasebank.md` (by paper section), `phrases/phrasebank-functions.md` (by language function; includes hedging-strength table).

1. Paragraph checks first (Part A of `flow/flow.md`), then sentence rules (Part B).
2. For phrasing, pick from `phrases/`; match hedging strength to the evidence.
3. Hard constraint: flow edits must not change scientific meaning — claim strength, scope qualifiers, causal direction. Revert on drift.
4. Submit to the scorer (flow).

## grammar

File: `grammar/grammar-checklist.md` (~72 rules, ordered by the checklist's scan sequence).

1. Scan per the checklist's ordering; report each hit as rule number + original + fix.
2. Ambiguous cases: list and ask the user; do not guess.
3. Contested usage (e.g., data is/are): follow mainstream academic convention and note the decision.
4. Submit to the scorer (grammar).

## review

File: `review/paper-review.md` — five-dimension question list; adversarial reviewer stance; claim-evidence alignment is a hard constraint. Full-paper edits are scored on all three dimensions and averaged.

## Rules

1. One paragraph per message; one message per paragraph.
2. One message per paragraph, stated in the first sentence.
3. Nouns self-contained; define terms before reuse; keep terminology stable (no elegant variation).
4. Figures/tables/layout are content, not decoration.
5. Keep the original text; report before/after.

## Output contract

Report to the user: changes (before/after per paragraph); score; scorer issues and their handling (fixed / reverted as meaning drift / left for the user); claim-evidence map (`Claim: ... | Evidence: ... | Status: supported/needs evidence`).
