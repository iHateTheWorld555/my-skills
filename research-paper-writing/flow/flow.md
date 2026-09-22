# Sentence and Paragraph Flow

Actionable rules for making paper text flow. Merged from three sources; see Provenance at the end.

Order of use: paragraph-level checks first (Part A), then sentence-level (Part B). Phrase banks live in `phrases/`.

## Part A: Paragraph-level checks

### A1. Reverse outline

Write down the thesis, each topic sentence, and each supporting point. Check that every topic sentence maps to the thesis and every point supports its topic sentence. A paragraph that cannot be mapped gets revised or cut. (Full procedure: `structure/does-my-writing-flow-source.md`.)

### A2. Topic-string test

Underline the first 7-8 words of every sentence. The underlined words should form one or two consistent topic strings. If every sentence starts a new subject, the paragraph has no story line — pick the concept that recurs but never opens a sentence, and promote it to the topic position of most sentences.

### A3. Old-new chaining

The last few words of one sentence should set up the first few words of the next: old information opens, new information closes. When rearrangement exposes a gap where a connecting sentence is missing, the argument itself has a hole — add the connecting sentence (cause or mechanism) or cut the dangling material.

### A4. Transitions

Use transition words to mark the relation between sentences: cause (therefore, consequently, as a result), contrast (however, in contrast, nevertheless), addition (furthermore, moreover), example (for instance, such as). Do not use connectives to fake logic — if every sentence connects cleanly by old-new chaining, few transitions are needed.

## Part B: Sentence-level rules (reader expectations)

These are principles, not rules: skilled writers violate them deliberately at exceptional moments. Passive voice is correct when the paragraph's story is about the patient. A sentence is too long when it has more stress-worthy items than stress positions, not when it exceeds a word count.

### B1. Subject-verb proximity

Follow the grammatical subject with its verb as soon as possible. Anything long between them reads as an interruption of lesser importance, even when important.

- Bad: `The smallest of the URF's (URFA6L), a 207-nucleotide reading frame overlapping out of phase the NH2-terminal portion of the ATPase subunit 6 gene, has been identified as ...` (subject and verb are 23 words apart)
- Fix A — if the interruption matters, give it its own clause with a semicolon: `The smallest of the URF's is URFA6L, a 207-nucleotide reading frame ...; it has been identified as ...`
- Fix B — if it is peripheral, cut it: `The smallest of the URF's (URFA6L) has been identified as ...`

### B2. Stress position

Readers emphasize what arrives at the point of syntactic closure — the end of the sentence, or just before a colon or semicolon. Put the most important new information there. Never end on a citation label, a date, or a routine qualifier if a stress-worthy item sits mid-sentence.

Fixes: trim the end; move peripheral material left; push new information right (there is/are, passive, what/it-cleft, not only X but also Y).

### B3. Topic position

The sentence opener tells the reader whose story the sentence is. Put the recurring concept there, not a fresh piece of information.

### B4. Old before new

Old information (already stated) goes in the topic position for backward linkage; new information goes in the stress position. Reversing this is the most common structural defect in scientific prose. Within the sentence, middle material may mix old and new.

### B5. Actions in verbs

Express the action of each clause in its verb. If the verbs of a paragraph are mostly is/are/has/remains, the real actions are hidden in nominalizations — reanimate them.

- Bad: `The utilization of the proposed regularization leads to an improvement in alignment stability and a reduction in WER.`
- Good: `The proposed regularization stabilizes alignment and reduces WER.`

### B6. Context before novelty

Give the reader context before asking them to absorb anything new — within sentences, paragraphs, and sections alike. Avoid opening a paragraph with a new claim and closing it with background.

### B7. Structural emphasis matches substantive emphasis

The places the structure marks as important must be the places the content is important. Mismatch is the most reliable source of misreading.

## Part C: Concision and coherence (Williams)

### C1. Characters as subjects, actions as verbs

Keep the subject for the main character and the verb for the key action. Watch for nominalization chains (`analysis`, `evaluation`, `utilization`), weak verbs (is, have, occur, result in, is based on), and characters buried in possessives or prepositional phrases.

### C2. Concision

Cut: words that add nothing (kind of, actually, particular, really, various, virtually, basically); paired synonyms (each and every, first and foremost); words implied by their neighbors (terrible tragedy, final outcome, free gift); category redundancies (large in size, period of time). Replace phrases with words (make an assumption → assume) and negatives with positives (not different → similar) unless the negation itself is the point. Keep hedging (suggest, appear, may) — confident writing hedges more and intensifies less.

### C3. Cohesion and coherence

Cohesion is sentence-to-sentence meshing (old-new chaining, A3). Coherence is a consistent set of subjects across the paragraph (A2). When the two conflict, old-new information wins over per-sentence clarity. Do not vary subjects for the sake of variety — repeat the key term; substitute a pronoun only when the same word in the same position turns mechanical.

### C4. Long sentences

A long sentence is fine when its shape is clear. Fix openers first: get to the subject fast, get from subject to verb fast. Fix sprawl with four moves: compress (who/that/which + be → phrase), separate into sentences, convert to resumptive/summative/free modifiers, or coordinate — with short elements before long ones.

### C5. Emphasis placement

Sentence endings carry the most weight; put heavy words, pairs of heavy words, or the key term at the close. The paragraph's organizing concept should appear at the stress position of the first sentence — readers look there for the keywords the rest of the paragraph will develop.

## Part D: Revision checklist

Run in order:

1. Reverse-outline the passage; map every paragraph to a claim.
2. Scan topic positions down the paragraph for a consistent story line (A2).
3. Check old-new chaining across sentence boundaries (A3, B4).
4. For each sentence, measure subject-verb distance; decide per interruption: own clause or cut (B1).
5. Inventory stress positions; count stress-worthy items; split or trim when the count exceeds the positions (B2).
6. Audit verbs for nominalizations; reanimate (B5, C1).
7. Cut concision violations (C2).
8. Verify every new term has context before first use (B6).
9. Flag argument gaps exposed by restructuring — these are content problems to report, not style problems (A3).

## Science-meaning guard

Restructuring can change scientific content: claim strength, scope qualifiers, causal direction. Before/after, verify sentence by sentence; revert any sentence where meaning shifted. If a rewrite requires new technical claims, stop and ask the author.

## Provenance

- Part B: G. Gopen & J. Swan, "The Science of Scientific Writing," American Scientist 78(6):550-558 (1990). Examples in B1 are from the original; examples in B5 were added for ML-paper style.
- Parts A, C, D: J. M. Williams & J. Bizup, *Style: Lessons in Clarity and Grace*, 11th ed. (Pearson, 2013). A1 adapted from a writing-center handout bundled as `structure/does-my-writing-flow-source.md`.
