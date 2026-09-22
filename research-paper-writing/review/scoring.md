# Scoring

The scoring agent scores revised text against **this skill's own reference files** — no separate rubric.

- Read the reference files for the task dimension being scored (structure/flow/grammar per `SKILL.md`).
- Score the revised text **0-10** (integers or 0.5 steps). 8+ = publication-ready polish level; below 5 = structural problems remain.
- Compare against the original text only to detect meaning drift: flag any change to claim strength, scope qualifiers, causal direction, numbers, or hedging as `MEANING-DRIFT` (must be fixed; does not count toward the score).
- Score in the requested dimension(s); full-paper review averages structure, flow, grammar.

Output format:

```
Score: NN/10
Issues:
  - <quoted fragment> — <which rule it violates, one line>
Verdict: <one line>
```

No vague comments; every issue quotes the text and names the rule.
