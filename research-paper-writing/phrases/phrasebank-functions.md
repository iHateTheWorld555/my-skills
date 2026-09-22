# ML/CV/NLP Paper Writing Phrasebank — Organized by Language Function

> `[...]` marks a replaceable slot. Entries are indexed by the "speech act" you need while writing; pair with the section-organized `phrasebank.md`.
> Sources listed at the end.

---

## 1. Hedging (cautious language)

### Strength scale (strong → weak)

| Strength | Claim verb / phrase | Use case |
|---|---|---|
| ★★★★★ Strongest | "we demonstrate that..." / "clearly show" / "establish" | overwhelming evidence; main-result claims |
| ★★★★ Strong | "show" / "indicate that" / "confirm" | solid evidence, short of decisive |
| ★★★ Medium | "suggest (that)" / "provide evidence that" | clear tendency but confounds possible |
| ★★ Weak | "appear to" / "seem to" / "may support the hypothesis that" | preliminary observations, exploratory findings |
| ★ Weakest | "may indicate" / "possibly / potentially" / "cannot be ruled out" | pure speculation, needs follow-up validation |

**Templates:**

1. "Recent research has suggested that [...]." — weakens a claim by attributing it to others (Manchester)
2. "There is some evidence to suggest that [...]." — "some evidence" caps the evidence amount (Manchester)
3. "It is likely / possible / probable that [...]." — modal adverbs graded by strength (Manchester)
4. "[...] may be / could be / might be due to [...]." — three-level weakening for causal attribution (Manchester)
5. "A possible / likely explanation is that [...]." — downgrades an explanation to one possibility (Manchester)
6. "These data must be interpreted with caution because [...]." — proactively asks readers to interpret cautiously (Manchester)
7. "These results do not rule out the influence of [...]." — declares an unexcluded factor, academic honesty (Manchester)
8. "Our findings cannot be extrapolated to [...]." — bounds how far the conclusion extends (Manchester)
9. "The evidence, while preliminary, suggests that [...]." — admits preliminary status while giving direction (RhetoriLex, adapted)
10. "There is a tendency for X to [...]." — downgrades a regularity to a tendency (Manchester)
11. "X is generally assumed to [...]." — frames a claim as common assumption, not fact (Manchester)
12. "This claim is limited to [...] and may not extend to [...]." — explicitly states the boundary of validity (RhetoriLex)
13. "Although [...] supports [...], it remains compatible with [...]." — keeps alternative explanations alive (RhetoriLex)

---

## 2. Causality

### Strong causality (needs experimental support)

1. "[...] can lead to / result in / give rise to [...]." — forward causal verb chain (Manchester)
2. "[...] is driven by / can be attributed to / stems from [...]." — reverse attribution verbs (Manchester)
3. "Removing [...] leads to a drop of [...] in [...], indicating that [...]." — ML ablation causality three-step (ML)

### Contributory causality (claims only a partial role)

4. "[...] contributes to [...]." — partial attribution (Manchester)
5. "Several factors are known to affect / shape / influence [...]." — multiple concurrent causes (Manchester)
6. "[...] is associated with an increased risk of [...]." — association-not-causation phrasing, medical style (Manchester)
7. "[...] plays a role in [...]." — weak contribution claim (Manchester)

### Nominalized and sentence-level causality

8. "[...] is a key / major / dominant / underlying factor in [...]." — factor-frame sentence (Manchester)
9. "A consequence of [...] is [...]." — result-frame sentence (Manchester)
10. "Owing to / Due to / As a result of [...], [...]." — prepositional causality (Manchester)
11. "Therefore, / Consequently, / As a result, [...]." — inter-sentence causal connectives (Manchester)
12. "[...], thereby [...]ing [...]." — participial trailing cause (Manchester)

### Cautious causality (possibly correlational)

13. "[...] may be an important factor in [...]." — weak causal claim (Manchester)
14. "There is some evidence that [...] may affect [...]." — evidence-qualified causality (Manchester)
15. "It is not yet clear whether [...] is made worse by [...]." — explicitly flags causality as unconfirmed (Manchester)
16. "[...] appears to be linked to [...]." — associative wording, avoids causal misreading (Manchester)

---

## 3. Contrast / Comparison

### Introducing differences

1. "[...] differs from [...] in a number of important ways." — blanket difference statement (Manchester)
2. "There are a number of important differences between [...] and [...]." — difference opener (Manchester)
3. "In contrast to / By contrast / On the other hand, [...]." — three inter-sentence contrastives (Manchester)
4. "While / Whereas [...], [...]." — balanced contrast within one sentence (Manchester)
5. "Compared with [...], [...] [...]." — direct comparison (Manchester)
6. "Unlike prior work, our approach [...] rather than [...]." — standard ML method-contrast phrase (ML)
7. "Whereas [...] reports [...], the present analysis finds [...]." — contrasts against published findings (RhetoriLex)
8. "[...] aligns with [...] but differs from the prediction of [...]." — partial agreement, partial divergence; fine-grained (RhetoriLex)

### Introducing similarities

9. "Both [...] and [...] share a number of key features." — commonality summary (Manchester)
10. "[...] is similar to / comparable to that of [...]." — similarity sentence (Manchester)
11. "Similarly, / Likewise, / In the same way, [...]." — parallel inter-sentence connectives (Manchester)

### Comparative forms (for experimental numbers)

12. "[...] achieves [...] more / less [...] than [...]." — basic comparative form (Manchester)
13. "[...] tends to perform better / worse than [...] on [...]." — trend comparison (Manchester)
14. "[...] outperforms [...] by a large / significant margin." — ML dominant-win phrasing (ML)
15. "[...] is on par with / comparable to [...], while being [...]." — matched performance with another advantage (ML)

---

## 4. Emphasis

1. "Notably, / Importantly, / Strikingly, [...]." — sentence-initial emphatic adverbs, three levels (ML)
2. "The most striking result to emerge from the data is that [...]." — most surprising finding (Manchester)
3. "What stands out in the table is [...]." — points readers to the table's key entry (Manchester)
4. "It is worth noting that [...]." — medium-strength flag (Manchester)
5. "Of particular interest is [...]." — formal emphasis variant (Manchester, adapted)
6. "Notably, our method achieves this without [...]." — benefit-at-zero-cost emphasis (ML)
7. "This is a particularly [...] result, given that [...]." — evaluates a result against context (Manchester)

---

## 5. Definition

1. "[...] refers to [...]." — minimal definition (Manchester)
2. "[...] can broadly be defined as [...]." — broad definition (Manchester)
3. "In this paper, [...] is defined as [...]." — paper-specific definition (Manchester)
4. "Throughout this paper, the term '[...]' will refer to [...]." — whole-paper term convention (Manchester)
5. "Here, [...] refers specifically to [...], excluding [...]." — definition plus boundary (RhetoriLex)
6. "Following [...], we use [...] to denote [...]." — adopts someone else's definition (ML)
7. "For clarity, we distinguish between [...] and [...]." — disambiguation statement (ML)
8. "Several definitions of [...] have been proposed; in this work, we adopt [...]." — surveys competing definitions, then picks one (Manchester, adapted)
9. "We use the terms [...] and [...] interchangeably." — synonym declaration (Manchester, adapted)
10. "A generally accepted definition of [...] is lacking." — flags an undefined term; good setup for the intro (Manchester)

---

## 6. Transition

### Between sections

1. "Turning now to [...]." — moves to the next topic (Manchester)
2. "Having defined [...], we now move on to [...]." — builds on a completed step (Manchester)
3. "So far, this paper has focused on [...]. The following section will discuss [...]." — stage summary plus preview (Manchester)
4. "We next investigate / examine [...]." — short ML transition (ML)
5. "With the above setup in place, we now turn to [...]." — advances once groundwork is laid (ML)

### Within paragraphs

6. "Regarding / In terms of / With respect to [...], [...]." — topic-limiting triplet (Manchester)
7. "As discussed above / As previously stated, [...]." — back-reference to earlier text (Manchester)
8. "In addition, / Furthermore, / Moreover, [...]." — additive progression (Manchester)
9. "Despite this, [...]." — concessive contrast (Manchester)
10. "Returning to the issue of [...], [...]." — pulls back to the main thread (Manchester)

### Pointing forward (figures / equations / sections)

11. "As shown in Figure [...] / Table [...], [...]." — figure/table back-reference (Manchester)
12. "A detailed description is provided in Section [...] / the Appendix." — forward pointer (ML)
13. "This will be discussed in detail in Section [...]." — defers discussion to later (ML)

---

## 7. Example

1. "A well-known example of this is [...]." — canonical instance (Manchester)
2. "For example, / For instance, [...]." — all-purpose exemplification (Manchester)
3. "[...], such as [...] and [...]." — in-sentence examples (Manchester)
4. "[...], including [...], [...] and [...]." — multi-item enumeration (Manchester)
5. "To illustrate this, consider [...]." — constructed example (ML)
6. "Take [...] as an example." — slightly more colloquial exemplification (ML)
7. "A concrete example is [...]: given [...], [...]." — walks through a worked example, common in Method (ML)
8. "This can be illustrated briefly by [...]." — brief illustrative example (Manchester)

---

## 8. Trend / Quantity Description

### Trends

1. "[...] shows a steady / sharp / marked increase / decline in [...]." — trend plus qualifier (Manchester)
2. "[...] increased / decreased [...] from [...] to [...] over [...]." — change over an interval (Manchester)
3. "[...] peaked at [...] in [...]." — peak description (Manchester)
4. "[...] is expected to [...] in the coming [...]." — trend extrapolation (Manchester)
5. "[...] grows [...] as [...] increases, and saturates beyond [...]." — standard ML training-curve narrative (ML)

### Quantities and proportions

6. "Over half / Nearly half of [...] [...]." — proportion sentence (Manchester)
7. "[...] accounts for [...]% of [...]." — share-of-total sentence (Manchester, adapted)
8. "The number of [...] ranges from [...] to [...]." — range sentence (Manchester)
9. "[...] achieved [...]%, outperforming [...] by [...] points." — ML metric plus delta (ML)
10. "The improvement is statistically significant (p < 0.05)." — statistical significance statement (Manchester, adapted)
11. "The mean [...] was [...] (±[...]) across [...] runs." — mean ± std reporting, ML multi-seed convention (ML)

---

## 9. Criticism

### Criticizing the field as a whole

1. "Previous studies of [...] have not dealt with [...]." — names an uncovered aspect (Manchester)
2. "Most studies in the field of [...] have only focused on [...]." — too-narrow scope (Manchester)
3. "Such approaches, however, have failed to address [...]." — failure statement (Manchester)
4. "However, all the previously mentioned methods suffer from [...]." — blanket rejection (Manchester)
5. "Results of previous studies have proved inconclusive." — prior conclusions unreliable (Manchester / Wordvice)

### Criticizing a single work

6. "[...] fails to fully define / distinguish between / address [...]." — specific defect (Manchester)
7. "[...] does not take [...] into account." — omitted factor (Manchester, adapted)
8. "The main limitation of this technique, however, is [...]." — technique limitation (Manchester)
9. "A major problem with the [...] method is that [...]." — method problem (Manchester)
10. "[...] makes the strong assumption that [...], which limits [...]." — criticizes a hidden assumption (ML)
11. "[...] was later shown to [...], suggesting that [...]." — criticizes via later evidence (ML)

### Constructive criticism

12. "[...] would have been more [...] if it had [...]." — hypothetical-improvement form, the mildest (Manchester)
13. "While [...] is effective for [...], it is less suitable for [...]." — grants merit first, then bounds it; recommended for Related Work (ML)

---

## 10. Listing / Classification

1. "[...] can be classified / divided into [...] categories: [...] and [...]." — classification skeleton (Manchester)
2. "There are two basic approaches currently being adopted in [...]: [...] and [...]." — dichotomy (Manchester)
3. "[...] can be broadly categorized into [...]-based methods and [...]-based methods." — standard ML Related-Work dichotomy (ML)
4. "The key aspects of [...] can be listed as follows: [...], [...] and [...]." — enumeration lead-in (Manchester)
5. "This topic can best be treated under three headings: [...], [...] and [...]." — structured sub-topics (Manchester)
6. "Firstly, [...]. Secondly, [...]. Thirdly, [...]." — ordinal enumeration (Manchester)
7. "First, [...]. Then, [...]. Finally, [...]." — procedural enumeration (Manchester, adapted)
8. "[...] draws a distinction between [...] and [...]." — cites someone else's taxonomy (Manchester)
9. "We group existing methods along two axes: [...] and [...]." — ML-style two-axis organization (ML)

---

## 11. Evidence-safe Claiming (RhetoriLex patterns)

1. "The available evidence suggests but does not establish that [...]." — states explicitly that evidence falls short of proof (RhetoriLex)
2. "Given [...], the more defensible interpretation is that [...]." — picks the most defensible reading among alternatives (RhetoriLex)
3. "Because [...] remains imprecise, the evidence does not distinguish between [...] and [...]." — declares limited discriminating power (RhetoriLex)
4. "Since [...] does not rule out [...], [...] should not be read as causal evidence." — declares the evidence non-causal (RhetoriLex)
5. "If [...] holds, [...] is consistent with [...]." — conditional claim (RhetoriLex)
6. "Because the sample excludes [...], [...] should be generalized only to [...]." — bounds the scope of generalization (RhetoriLex)
7. "The measure captures [...] through [...], which may omit [...]." — honest disclosure of a metric's blind spots (RhetoriLex)
8. "Across [...], the evidence converges on [...], particularly under [...]." — converging-evidence claim from multiple sources (RhetoriLex)
9. "The literature divides over [...]: [...] supports [...], whereas [...] supports [...]." — describes a scholarly disagreement (RhetoriLex)
10. "Until [...] is resolved, a proportionate step is to [...]." — conservative recommendation under uncertainty (RhetoriLex)

---

## Sources

- **Manchester Academic Phrasebank** (11 of the 12 language-function pages, all but Writing about the past):
  using-cautious-language / being-critical / classifying-and-listing / compare-and-contrast / writing-definitions / describing-trends / describing-quantities / explaining-cause-and-effect / giving-examples / signalling-transition / writing-about-the-past-2
  https://www.phrasebank.manchester.ac.uk/
- **shengmincui/Academic_Phrasebank_note**: https://github.com/shengmincui/Academic_Phrasebank_note (contributed the hedging strength-scale material and additional variants)
- **rezaprama/RhetoriLex** (`data/canonical/catalog.v1.jsonl`, 48 evidence-graded patterns; most of Section 11 is taken directly from it): https://github.com/rezaprama/RhetoriLex
- **Wordvice "Academic Writing Cheat Sheet" PDF**: https://wordvice.com/blog/useful-phrases-for-writing-academic-papers/
- **ML conventional phrases**: summarized from common usage in top ML venue papers; each is marked "(ML)"
