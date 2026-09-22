# ML/CV/NLP Paper Writing Phrasebank — Organized by Paper Section

> `[...]` marks a replaceable slot. Each entry carries a short note on tone and use case.
> Sources listed at the end. Entries marked "(ML)" come from common usage in top ML venues; the rest follow the Manchester Phrasebank.

---

## 1. Abstract

**Opening (field + task):**
1. "Recent advances in [...] have demonstrated remarkable progress in [...]." — most universal ML opener, signals a hot field
2. "[...] is a fundamental task in [...] and plays a critical role in [...]." — task-importance opener, fits CV/NLP task papers
3. "The past decade has witnessed the rapid development of [...]." — time-span opener, more historical than "Recently"
4. "Deep learning approaches have achieved impressive performance on [...]. However, [...]." — two-sentence setup-then-break, leads straight to the problem (ML)

**Problem / gap:**
5. "However, existing methods [...] when [...]." — standard abstract pivot; states when current methods fail (ML)
6. "However, these approaches typically suffer from [...], limiting their applicability to [...]." — names a limitation plus its consequence, formal tone
7. "Despite recent progress, it remains challenging to [...] due to [...]." — restrained tone; stresses the difficulty, not prior mistakes

**Our method:**
8. "In this paper, we propose [...], a novel [...] that [...]." — standard method-introduction formula, use when naming the method (ML)
9. "We present [...], which [...] by [...]." — compact method statement for tight abstract space
10. "To address this issue, we introduce [...], which [...] without requiring [...]." — selling point first: solves pain plus removes a cost
11. "Unlike prior work, our approach [...] rather than [...]." — sharp contrast with prior work when needed (ML)

**Results claim:**
12. "Extensive experiments on [...] benchmarks demonstrate that [...] outperforms state-of-the-art methods by a large margin." — standard results sentence; "demonstrate" is a strong claim, needs data (ML)
13. "Experimental results show that our method achieves [...] while reducing [...] by [...]." — numbers-forward version, gives gains and cost together
14. "We conduct extensive experiments on [...] datasets, and the results verify the effectiveness of [...]." — conservative results sentence for non-dominant gains

**Contribution teaser:**
15. "Our code and models are publicly available at [...]." — open-source statement, now near-mandatory at ML venues (ML)

---

## 2. Introduction

### 2.1 Background and importance

1. "X is a fundamental problem in [...], with applications ranging from [...] to [...]." — standard way to establish importance via broad applications
2. "X plays a vital / critical / central role in [...]." — stresses the subject's status in a system (Manchester)
3. "There is a growing body of literature that recognises the importance of [...]." — signals momentum via volume of literature (Manchester)
4. "Recently, there has been renewed interest in [...] due to [...]." — explains why an old problem is back; suits new takes on old problems (Manchester)
5. "The past thirty years have seen increasingly rapid advances in the field of [...]." — field-level temporal narrative opener (Manchester)
6. "Driven by [...], X has attracted increasing attention from the community." — ML-style background line, attributes momentum to a driver (ML)

### 2.2 Framing the problem

7. "X is a major / challenging problem in [...]." — direct statement of problem status (Manchester)
8. "There is an urgent need to address [...], since [...]." — stresses urgency; must justify in the "since" clause (Manchester)
9. "Despite its practical importance, X remains largely under-explored / notoriously difficult because [...]." — "important yet hard" combo, sets up this paper (ML)

### 2.3 Existing work and consensus

10. "Extensive research has shown that [...]." — neutral attribution to many prior findings (Manchester)
11. "Previous research has established that [...]." — stronger than the previous entry, for accepted conclusions (Manchester)
12. "A number of studies have attempted to [...] (Smith et al., 2020; Jones et al., 2021)." — cites specific works; suits intros that front-load related work (Manchester)

### 2.4 Gap — the core pivot of the Introduction

13. "However, previous studies of X have not dealt with [...]." — directly names what has not been covered (Manchester)
14. "However, most existing methods [...] and thus fail to [...]." — mainstream-practice-then-failure causal chain (ML)
15. "However, these methods are built on the assumption that [...], which often does not hold in practice." — attacks a hidden assumption, deeper than surface flaws (ML)
16. "While some research has been carried out on X, no previous study has investigated [...]." — classic "some work exists, but not this" formula (Manchester)
17. "There is little published data / a paucity of research on [...]." — points out research scarcity (Manchester)
18. "It is still not known whether [...]." — knowledge-gap type of gap statement (Manchester)
19. "The mechanisms / factors that underpin X are not fully understood." — understanding gap; suits analysis-oriented work (Manchester)
20. "A much debated question is whether [...]." — opens from a contested question in the field (Manchester)
21. "The existing accounts fail to resolve the contradiction between X and Y." — unresolved contradiction; suits work proposing a unified account (Manchester)
22. "However, far too little attention has been paid to [...]." — classic understudied-area sentence (Manchester)

### 2.5 Purpose, contributions, significance

23. "In this paper, we propose / present / introduce [...]." — all-purpose opener for contribution statements (ML)
24. "To fill this gap / To bridge this gap, we [...]." — standard bridge after a gap sentence (ML)
25. "The main contributions of this paper are summarized as follows: (1) ... (2) ... (3) ..." — standard lead-in for ML contribution bullets (ML)
26. "We further propose [...] to [...], which [...] for the first time." — "for the first time" priority claim; verify before using (ML)
27. "To the best of our knowledge, this is the first work to [...]." — hedged first-work claim with self-protection (ML)
28. "This study provides new insights into [...]." — stresses conceptual over performance contribution (Manchester)
29. "We demonstrate that [...] can be achieved with [...], challenging the prevailing assumption that [...]." — counter-intuitive result challenging consensus; high-risk claim (ML)

### 2.6 Roadmap

30. "The remaining part of this paper proceeds as follows / is organized as follows. Section 2 reviews [...]. Section 3 describes [...]." — standard structure paragraph (Manchester)
31. "This paper begins by [...]. It will then go on to [...]." — non-numbered roadmap variant (Manchester)

---

## 3. Related Work

### 3.1 Surveying the literature

1. "A large and growing body of literature has investigated [...]." — conveys the scale of the literature (Manchester)
2. "The literature on X has highlighted several [...]." — introduces several themes in the literature (Manchester)
3. "Much of the current literature on X pays particular attention to [...]." — names the field's current focus (Manchester)
4. "There is a relatively small body of literature that is concerned with [...]." — sparse sub-area, leaves room for this paper (Manchester)
5. "Different methods have been proposed to address [...]. These can be roughly divided into two categories: [...] and [...]." — taxonomy skeleton, the standard ML organizing move (ML)

### 3.2 Historical development

6. "Research into X has a long history, dating back to [...]." — traces an old problem to its origins (Manchester)
7. "Early approaches relied on [...]. Over the past decade, most research in X has shifted toward [...]." — paradigm-shift narrative from early to recent (Manchester, adapted for ML)
8. "Only in the past ten years have studies of X directly addressed [...]." — stresses that a problem was faced only recently (Manchester)
9. "It is only since the work of Smith (2015) that the study of X has gained momentum." — credits a seminal paper for momentum (Manchester)

### 3.3 Citing individual works (three subject positions)

10. "Smith et al. (2020) proposed [...] and demonstrated [...]." — researcher as subject, the most common citation format (Manchester)
11. "Smith et al. (2020) were among the first to [...]." — attributes pioneering status (Manchester, adapted)
12. "In 2017, Smith et al. introduced [...], which has since become a standard baseline." — time as subject plus status assessment (Manchester)
13. "A seminal study in this area is the work of [...]." — flags a foundational paper (Manchester)
14. "To address X, Jones et al. (2019) compared [...]." — purpose as subject; foregrounds motive over author (Manchester)
15. "It has been shown that [...] (Smith et al., 2019; Jones et al., 2020)." — research as subject, weak-author citation for multiple sources (Manchester)

### 3.4 Synthesis: agreement and contrast

16. "Similarly, Jones (2015) found that [...]." — groups a parallel finding (Manchester)
17. "This view is supported by Jones (2015), who [...]." — supportive continuation (Manchester)
18. "In contrast to Smith, Jones (2013) argues that [...]." — juxtaposes opposing views (Manchester)
19. "While Smith (2008) focuses on X, Jones (2009) is more concerned with [...]." — division-of-labor contrast in one sentence, common for closing (Manchester)
20. "Other studies, however, have concluded that [...]." — introduces inconsistent conclusions (Manchester)

### 3.5 Closing summary (end of Related Work)

21. "Taken together, these studies support the notion that [...]." — synthesizing summary (Manchester)
22. "Overall, these studies highlight the need for [...]." — slides from survey to "what is still needed", sets up this paper (Manchester)
23. "However, such studies remain narrow in focus, dealing only with [...]." — names a collective blind spot (Manchester)
24. "There remain several aspects of X about which relatively little is known." — leaves-open sentence, paves the way below (Manchester)
25. "Unlike these works, our method [...] [...]. A detailed comparison is provided in Section [...]." — ML-style close: claim difference and point to a comparison table (ML)

---

## 4. Method

### 4.1 Motivation and design philosophy

1. "Motivated by this observation, we design [...]." — observation-to-design pivot, standard Method opener (ML)
2. "A natural question arises: [...]. To answer this, we [...]." — question-driven advance; suits intuition-first methods (ML)
3. "Our key insight is that [...]." — states the core insight, justifies the design in one line (ML)
4. "The intuition behind [...] is that [...]." — softer version of "key insight", humbler tone (ML)
5. "We draw inspiration from [...], and adapt it to [...]." — honest attribution when borrowing across fields (ML)
6. "This design choice is guided by the following consideration: [...]." — formal statement of design rationale (ML)

### 4.2 Justifying design choices

7. "A major advantage of this approach is that [...]." — standard Manchester advantage sentence (Manchester)
8. "This method is particularly useful for [...], since [...]." — use case plus reason (Manchester)
9. "X was selected for its [...] and [...]." — compact choice rationale (Manchester)
10. "We adopt [...] rather than [...], because [...]." — A-or-B choice sentence; pre-answers a reviewer question (ML)
11. "One advantage of [...] is that it avoids the problem of [...]." — defines advantage by what it avoids (Manchester)
12. "The benefit of this formulation is twofold: [...] and [...]." — two-item benefit summary (Manchester, adapted)

### 4.3 Describing the procedure

13. "Our framework consists of two / three main components: [...], [...] and [...]." — overview-then-parts opener (ML)
14. "The overall pipeline is illustrated in Figure 2. Given [...], our model first [...], then [...], and finally [...]." — figure-text pairing plus flow narration (ML)
15. "Formally, given [...], we define [...] as [...]." — equation lead-in (ML)
16. "To this end, we formulate the task as [...]." — transition into a mathematical formulation (ML)
17. "Specifically, [...] is computed by [...]." — detail-expansion sentence (ML)
18. "The first step in this process is to [...]. Once [...], [...] is performed." — sequential-step description (Manchester)
19. "In order to [...], we [...] ." — purpose-led process description (Manchester)
20. "We train [...] end-to-end with [...], using [...]." — training setup in one line (ML)

### 4.4 Relation to existing methods

21. "Our approach builds upon [...], but differs in that [...]." — stands on prior work while drawing a boundary (ML)
22. "Compared with [...], our method replaces [...] with [...], thereby [...]." — difference plus causal benefit (ML)
23. "Following common practice [...], we [...]." — declares inherited conventions, defuses reviewer challenges (ML)

### 4.5 Limitations (honest disclosure, optional)

24. "Note that our method assumes [...], which may not hold when [...]." — proactively states the applicability condition (ML)
25. "A limitation of the proposed approach is its reliance on [...]." — Manchester limitation formula ported to ML (Manchester)

---

## 5. Experiments

### 5.1 Setup

1. "We evaluate our method on [...] benchmarks / datasets." — dataset declaration (ML)
2. "We compare our approach against [...] strong baselines, including [...]." — baseline declaration with "strong" qualifier (ML)
3. "Following previous work [...], we adopt [...] as the evaluation metric." — metric declaration citing convention (ML)
4. "All experiments are conducted on [...] with [...]." — hardware/implementation statement (ML)
5. "Implementation details are provided in the Appendix / supplementary material." — defers details to supplementary (ML)
6. "For a fair comparison, all methods are trained / evaluated under the same setting." — fairness statement, preempts reviewer doubts (ML)

### 5.2 Main results

7. "Table 1 shows / presents / summarizes the results of [...]." — table lead-in (Manchester)
8. "As shown in Table 2, our method outperforms all baselines on [...]." — main-result statement (Manchester, adapted)
9. "Our approach achieves [...] on [...], surpassing the previous best method [...] by [...]." — numeric-comparison version (ML)
10. "Notably, our method achieves this improvement without additional [...]." — zero-cost improvement, efficiency selling point (ML)
11. "What stands out in the table is [...]." — directs the reader to the table's highlight (Manchester)
12. "It can be observed that [...]." — neutral observation, formal version of "we can see that" (ML)

### 5.3 Ablation

13. "To investigate the contribution of each component, we conduct ablation studies on [...]." — standard ablation opener (ML)
14. "We ablate [...] by removing / replacing it with [...]." — declares the ablation procedure (ML)
15. "As shown in Table 3, removing [...] leads to a drop of [...] in [...], indicating that [...]." — remove-drop-prove-necessary three-step (ML)
16. "The performance gain mainly comes from [...], rather than [...]." — attribution analysis, rebuts "just better tuning" doubts (ML)

### 5.4 Analysis and interpretation

17. "Interestingly, [...]." — introduces a surprising observation (Manchester)
18. "The most striking result to emerge from the data is that [...]." — foregrounds the most surprising finding (Manchester)
19. "A possible explanation for this is that [...]." — explains an observation with a weak claim (Manchester)
20. "We attribute this improvement to [...]." — attribution sentence, medium claim strength (ML)
21. "This result suggests that [...] rather than [...]." — uses the result to adjudicate between two options (ML)
22. "Figure 3 visualizes [...] and illustrates how [...]." — visualization analysis lead-in (ML)
23. "Contrary to expectations, [...]." — introduces a counter-intuitive result (Manchester)
24. "These results are in line with those of previous studies [...]." — mutual corroboration with the literature (Manchester)

### 5.5 Generalization and robustness

25. "To assess the generalization ability of [...], we further evaluate [...] on [...]." — generalization-experiment opener (ML)
26. "Our method remains robust across [...], whereas baselines degrade significantly when [...]." — robustness contrast (ML)
27. "These findings cannot be extrapolated to [...]; further validation is needed for [...]." — proactively bounds the conclusion's scope (Manchester)

---

## 6. Conclusion

### 6.1 Restating the work

1. "In this paper, we proposed [...], which [...]." — standard conclusion opener (ML)
2. "This study set out to examine [...]." — loops back to the stated research aim (Manchester)
3. "We presented a novel approach to [...] that [...]." — "novel" claim plus one-line method (ML)

### 6.2 Summarizing findings

4. "Our experimental results demonstrate that [...]." — medium-strong results summary (Manchester, adapted)
5. "This study has identified [...]." — findings as subject (Manchester)
6. "Taken together, our results suggest that [...]." — synthesized summary with mild hedging (Manchester)

### 6.3 Significance and contribution

7. "We believe this work sheds light on [...]." — stresses inspirational value, common in ML conclusions (ML)
8. "The findings reported here provide new insights into [...]." — conceptual-contribution statement (Manchester)
9. "Our approach lays the groundwork for future research into [...]." — foundational-contribution framing (Manchester)
10. "Beyond [...], the proposed framework can be readily extended to [...]." — extends applicability outlook (ML)

### 6.4 Limitations and future work

11. "A limitation of this work is that [...]." — direct admission of a limitation (Manchester)
12. "Despite these promising results, [...] remains an open problem." — acknowledges unfinished ground (ML)
13. "In future work, we plan to explore [...]." — planned item (ML)
14. "Further work is needed to determine whether [...]." — to-be-validated item (Manchester)
15. "An interesting direction for future research would be to investigate [...]." — outlook-style future work (Manchester)
16. "It would be worthwhile to extend our method to [...] settings." — generalization suggestion (Manchester, adapted)

---

## Sources

- **Manchester Academic Phrasebank** (all category pages): https://www.phrasebank.manchester.ac.uk/ — 12 pages across section categories (introducing-work / referring-to-sources / describing-methods / reporting-results / discussing-findings / writing-conclusions) and language-function categories
- **shengmincui/Academic_Phrasebank_note** (bilingual Manchester notes): https://github.com/shengmincui/Academic_Phrasebank_note
- **rezaprama/RhetoriLex** (evidence-graded writing pattern library): https://github.com/rezaprama/RhetoriLex
- **Wordvice "Useful Phrases for Academic Papers" cheat sheet**: https://wordvice.com/blog/useful-phrases-for-writing-academic-papers/
- **ML conventional phrases**: summarized from common usage in top ML venue papers (NeurIPS/ICML/ICLR/CVPR/ACL); each is marked "(ML)"
