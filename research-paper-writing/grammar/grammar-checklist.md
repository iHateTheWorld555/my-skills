# Academic English Grammar Checklist (ML/CV/NLP papers · agent-executable)

> When revising a paper, run every rule in the "Check Order" list at the end. Each rule states the point plus a one-line fix.
> [S]= grep/search hint · [R]= judge with context · [W]= obey while generating text.

---

## 1. Articles

1.1 Plural generics take no article. Fix: [R]scan every "the + plural noun"; drop "the" unless the referent is uniquely identifiable ("convolutional neural networks", not "the convolutional neural networks").

1.2 Use "the" only for uniquely identifiable referents. Fix: [R]for each "the", find the noun's first mention; if none and no limiting phrase (of X, in this paper) exists, drop "the" or use "a".

1.3 Appositions introducing a new name use "a", even with "novel/first": "We propose DiffNet, a novel diffusion-based network". Fix: [S]`propose [A-Za-z]+, (the|an?)`; correct the article.

1.4 Use "the" for items unique in the paper (the encoder, the loss, the ground truth). Fix: [S]bare subject nouns naming your model parts (encoder/decoder/loss/module); prepend "the".

1.5 Uncountable nouns take no article and no plural: research, evidence, information, knowledge, code, hardware, software, literature, training, inference, feedback. Fix: [S]`a (evidence|information|knowledge|research|software|hardware|code|feedback|literature)` and `(researches|informations|knowledges|evidences|feedbacks|softwares)`; rewrite.

1.6 Generic process nouns (ablation, evaluation, comparison, optimization, supervision) take no article. Fix: [R]drop it for generic use; keep "the" only for a specific experiment of this paper ("the ablation study in Table 3").

1.7 Proper model names take no "the" (ResNet, BERT, GPT-4, U-Net). Fix: [S]`the (ResNet|BERT|VGG|Transformer|CNN|GAN|ViT|U-Net)`; drop "the" (except generic "the Transformer architecture").

1.8 Own method: "our method" or "the proposed method" — always one determiner, never bare "proposed method" nor doubled determiners. Fix: [S]bare `proposed (method|framework|model|approach|network)`; prepend "the".

1.9 Dataset names: "the COCO dataset" has "the"; the bare name ("on COCO") does not. Fix: [S]`on (the )?[A-Z][a-zA-Z]+ dataset` and `the (COCO|ImageNet|CIFAR|VOC|KITTI|ADE20K|LSUN|FFHQ)\b` (not followed by "dataset"); correct each.

1.10 No "the" before "Section 3", "Figure 1", "Table 2", "Eq. (5)" (with ordinals, "the third section" is fine). Fix: [S]`the (Section|Figure|Table|Eq\.|Algorithm) \d`; drop "the".

1.11 Fixed phrase is "in this paper/work/section" — never "on/at this paper". Fix: [S]`(on|at) this (paper|work|study|section)`; change to "in".

1.12 Fields take no "the": computer vision, machine learning, natural language processing. Fix: [S]`the (computer vision|machine learning|deep learning|natural language processing)\b`; drop "the".

1.13 Ordinals and superlatives before a noun take "the": "the first method", "the best performance". Fix: [S]bare `(first|second|last|best|worst|only) `; check for a preceding "the".

1.14 Fixed pairs carry their article: "play a (key|important|vital) role", "as an alternative", "in a real-time manner"; a/an by sound (a university, an hour). Fix: [S]`plays? (key|important|crucial|vital) role` and `a (important|interesting|effective|influence)`; correct.

---

## 2. Agreement & Number

2.1 "data" may be singular or plural — pick one and stay consistent; "datas" is always wrong. Fix: [S]`datas\b` → data/data points; count "data is/are" across the paper and unify.

2.2 "the number of X is" (singular); "a number of X are" (= many); "a total of 100 images are" (plural). Fix: [S]`number of`; match the verb to the pattern.

2.3 each/every/either/neither + singular noun takes a singular verb, even with an of-phrase. Fix: [S]`(Each|Every|Either|Neither) of`; check the verb is singular.

2.4 Uncountable nouns — no plural, no "a": research, evidence, information, knowledge, advice, code, hardware, software, literature, equipment, progress, work, training, inference, supervision, storage, memory, computation, feedback, staff, luggage. Fix: [S]`(many|several|few|a) (researches?|evidences?|informations?|knowledges?|equipments?|softwares?|hardwares?|progresses?|advices?|literatures?)`; rewrite as much/little/a piece of.

2.5 Latin/Greek plurals: phenomenon→phenomena, criterion→criteria, medium→media, analysis→analyses, datum→data, formula→formulae/formulas, index→indices, matrix→matrices, basis→bases, hypothesis→hypotheses. Fix: [S]`(phenomenons|criterias|matrixes|indexs|basises|hypothesises)` and singular-slot `a phenomena|a criteria|a media|an analyses`; correct the form.

2.6 Collective nouns (team, committee, community) are usually singular in American usage; "the authors of [X]" is plural. Fix: [R]check collective-noun verbs and unify across the paper.

2.7 The verb agrees with the head noun, not the nearest one: "The set of images is...", "The results of the experiments show...". Fix: [R]for subjects with an of-phrase, match the verb to the noun before "of".

2.8 "there is/are" agrees with the real subject after it. Fix: [S]`There (is|are)`; match the following noun.

2.9 Percentage/fraction subjects agree with the noun after "of": "80% of the samples are". Fix: [S]`\d+% of`; match the verb.

2.10 "The following are..." and inverted subjects ("Among them is/are...") agree with the postposed real subject. Fix: [S]`The following (is|are)` and `Among .*(is|are)`; check the following/postposed noun.

---

## 3. Syntax

3.1 No comma splice: two independent clauses need a period, semicolon, or conjunction. Fix: [S]`, however,|, therefore,|, moreover,|, thus,`; if the first half is a full clause, change the comma to a semicolon or period.

3.2 however/therefore/moreover/thus/hence/consequently are adverbs, not conjunctions — they cannot join two clauses like but/and/so. Fix: same action as 3.1; prefer semicolon + adverb.

3.3 No fragments: every sentence needs subject + verb; Because/Although/While/Which/That clauses cannot stand alone. Fix: [S]`(Because|Although|While|Since|Given that) [^.]*\.` and sentence-initial `Which|That is why`; attach to a main clause.

3.4 Dangling modifiers: the logical subject of an opening participle (Using/Given/Compared with/After/By/When) must equal the main-clause subject. Fix: [S]sentence-initial `(Using|Given|Compared|Based|Following|After|Before|By) `; rewrite so the subject performs the participle, or convert to a Since/When/While clause.

3.5 "Compared with X, Y..." — Y must be the thing compared with X: "Compared with the baseline, our method reduces latency", not "the latency is reduced". Fix: [S]`Compared (with|to) `; check the main subject is comparable to X.

3.6 Parallel structure: both...and / either...or / not only...but also / neither...nor must join grammatically identical elements. Fix: [S]`(both|either|neither|not only)`; match parts of speech on both sides.

3.7 Lists (A, B, and C) must be uniform — all noun phrases, all gerunds, or all clauses. Fix: [R]for each 3+ item list, check every item's opening form.

3.8 "which" refers to the nearest noun; if ambiguous, use "this + noun" resumption or restructure. Fix: [S]`, which `; rewrite ambiguous ones ("...dataset, which improves" → "This improves...").

3.9 Restrictive clauses use "that" (no comma); non-restrictive use ", which" (American convention). Fix: [S]`, that ` → which, or drop the comma.

3.10 Cut empty it-extrapositions: "It is worth noting that", "It should be noted that", "It is obvious that", "It can be seen that". Fix: [S]`It is (worth|should be noted|important to note|obvious|clear|evident)`; rewrite as "Notably, ..." / "Note that ...".

3.11 Avoid top-heavy subjects longer than ~15 words before the verb. Fix: [R]use "it"-extraposition or split the sentence.

3.12 Split sentences over 45 words (over 60 words: always). Fix: [R]find clause/parenthetical boundaries; split into 2-3 sentences.

3.13 Avoid stacking "There is/are" openers; prefer direct subject-verb ("Two issues remain."). Fix: [S]multiple `There (is|are)` in a passage; rewrite half into direct statements.

3.14 English clauses never omit the subject: "When training the model, we found..." is fine; "When train the model..." is not. Fix: [S]`When (training|evaluating|testing|comparing), `; check the main-clause subject (and see 3.4 for dangling cases).

---

## 4. Prepositions & Collocations

4.1 High-frequency fixed collocations (memorize, never substitute):
depend **on** / rely **on** / based **on** / focus **on** / concentrate **on** / insist **on** · different **from** · consist **of** / be composed **of** / be made up **of** · compare **with** (like-for-like) / compare **to** (metaphor) · in contrast **to** / with respect **to** / with regard **to** · result **in** (cause) / result **from** (originate) · attribute **to** / be attributed **to** · lead **to** / contribute **to** / be related **to** / be associated **with** · substitute **for** / replace **with** (A with B, not "replace by") · be aware **of** / be capable **of** / be suitable **for** / be responsible **for** · in accordance **with** / in terms **of** / on behalf **of** · be superior **to** / be inferior **to** / prior **to** / subsequent **to**.
Fix: [S]`results? to|depends? of|different (with|than)|replace(d)? by|substitute with|capable to|aware about`; correct per the list above.

4.2 compare A with B = compare (experiments always use "with"); compare A to B = liken. Fix: [S]`compare (our|the) .* to `; change to "with" in experimental comparisons.

4.3 research **on** X; study **of/on** X; investigation **into** X. Fix: [S]`research (about|for) ` → on; `researches` → research.

4.4 experiment **on** a task/dataset; experiment **with** a method/idea. Fix: [R]match the preposition to the object type ("Experiments on ImageNet", not "about").

4.5 discuss, emphasize, mention, consider, investigate, stress are transitive — no preposition ("We discuss the limitations"). Fix: [S]`(discuss|emphasize|mention|consider|investigate|stress) (about|on|upon)`; delete the preposition.

4.6 **in** the paper/figure/table/section; **on** the dataset/benchmark/task; **at** the beginning/end, at 300 epochs. Fix: [S]`on (Figure|Table|Eq)` → in; `in (epoch|step|iteration) \d` → at.

4.7 by + gerund/means ("by adding noise"); with + tool/component ("with a residual connection"). Fix: [R]"with + -ing" → "by + -ing".

4.8 increase **by** X (amount) / **to** X (final value) / **from** A **to** B. Fix: [S]`(increase|decrease|improve|drop|reduce|gain)s? \d`; insert by/to.

4.9 Chain of/on: "the performance of our method on COCO" — never "performance on ... of ...". Fix: [R]reorder inverted chains to "of X on Y".

4.10 Trim wordiness: "has the ability to" → can; "in order to" → to. Fix: [S]`has the (ability|capability) to ` → can; `In order to` → To.

---

## 5. Word Choice

5.1 which vs that: no comma before "that"; non-restrictive ", which" needs the comma. Fix: same as 3.9.

5.2 fewer for countables (fewer parameters, fewer samples); less for uncountables (less memory, less noise). Fix: [S]`less (parameters|samples|images|epochs|layers|steps|tokens)` → fewer; `fewer (memory|computation|noise|data|information|time)` → less.

5.3 affect = verb; effect = noun; effectively = adverb. Fix: [S]`effects? (the )?(performance|accuracy|results)` in verb position; correct the part of speech.

5.4 principal = main ("the principal contribution", "principal component analysis"); principle = rule ("the principle behind our design"). Fix: [S]`(principles?|principals?)`; check each by meaning.

5.5 A comprises B (no "of"); B is composed of A; A consists of B (safest). Fix: [S]`comprise(s|d)? of|composes? |is comprised`; rewrite as consist(s) of or is composed of.

5.6 Capitalization: "Figure 1", "Section 3", "Table 2", "Algorithm 1", "Eq. (5)" capitalized in-text; keep official casing of model names (BERT, GPT-3, ResNet-50, Swin Transformer, U-Net) and datasets (COCO, ImageNet, CIFAR-10); "our method" is lowercase — no "the Proposed Method". Fix: [S]`\bfigure \d|table \d|section \d|algorithm \d|equation \d` and lowercase model names; correct.

5.7 Numbers and units: words under 10, numerals 10+ and all technical quantities; no sentence-initial numerals ("Fifteen images..."); space before units ("3.2 GB", "10 ms", "5 kHz"), consistent "%"-spacing; en-dash ranges ("100--200"); leading zero ("0.85"); "batch size" (two words). Fix: [S]`batchsize|batch-size`, `\s\.\d`; check %-spacing consistency.

5.8 Define every acronym at first use: "convolutional neural network (CNN)", then acronym only; define separately in Abstract and body; avoid acronyms in the title unless field-standard. Fix: [R]search each acronym's first occurrence for a definition; search for duplicate definitions.

5.9 Hyphenate attributive compounds: "state-of-the-art method", "end-to-end training", "real-time inference", "large-scale dataset"; no hyphen predicatively ("trained end to end") and none after -ly adverbs ("highly effective"; but "well-known"). Fix: [S]`(end to end|real time|state of the art|large scale|high resolution|multi [a-z]|cross [a-z]) `; hyphenate when attributive; check "a/an state-of-the-art".

5.10 Replace nominalizations with verbs: perform an analysis of → analyze; make a comparison → compare; conduct an investigation → investigate; is able to → can. Fix: [S]`perform(s|ed)? an? (analysis|comparison|evaluation|investigation|examination) of` and `is able to|are able to`; rewrite.

5.11 Delete filler with no information: "It is well known that", "As we all know", "obviously", "in fact", "very" (use a precise adjective), "really". Fix: [S]`As we all know|It is well known|obviously|in fact, |very (good|large|small|important|effective)`; delete or replace.

5.12 Ban colloquialisms: basically, actually, literally, totally, huge, a lot of. Fix: [S]`\b(basically|actually|literally|totally|huge)\b|a lot of`; replace (substantial, many).

---

## 6. Academic Conventions

6.1 Prefer active "we" (modern ML convention); passive for generic procedures/objective facts; do not switch mid-section; avoid "we" for non-author acts. Fix: [S]`we can see|we can observe|it can be seen` → "Figure X shows" or a direct statement.

6.2 Place "only" next to what it limits; misplaced "not" changes scope: "Our method uses only 25%..." vs "Only our method uses...". Fix: [S]`\bonly\b`; check adjacency to the limited element.

6.3 "respectively" requires two equal-length parallel lists: "A and B are X and Y, respectively". Fix: [S]`respectively`; delete or rewrite when the lists do not correspond.

6.4 Abbreviation dots: "et al." (one dot, no extra period at sentence end), "i.e.", "e.g.", "cf.", "viz.", "w.r.t.", "a.k.a."; American style puts a comma after i.e./e.g. ("..., e.g., images"); "et al." for 3+ authors, "A and B" for two. Fix: [S]`et\. al|et al[^.]` and `\b(e\.g\.|i\.e\.) `; fix dots and commas consistently.

6.5 Citation style: "X et al. [12] proposed..." or "... (He et al., 2016)"; avoid "In [12], the authors propose" and unclear "they"; in LaTeX use `~\cite{}`. Fix: [R]check citation subjects for clear reference; add `~` before `\cite`.

6.6 a/an for acronyms by sound: an SVM, an LSTM, a U-Net, a CNN. Fix: [S]`a (SVM|LSTM|SQL|SOTA|FCN|RNN|MLP)` → an; `an (U-Net|UNet|UNI|VIP)` → a.

6.7 No absolute claims: "proves" only for mathematical proof (else demonstrates/shows); no "solves/completely solves"; "the first" only if verifiable; "significant" only with a statistical test (else substantial/considerable). Fix: [S]`prove(s|d)? (that|the effectiveness)` and unqualified `significant`; downgrade.

6.8 Hedge and scope claims: qualify with "on the benchmarks we tested" / "in our experiments"; avoid all, every, always, never. Fix: [S]`\b(always|never|all existing|every)\b`; add scope or soften (usually, most).

6.9 Every Figure/Table is numbered continuously and cited at least once in the text; captions are complete sentences. Fix: [R]cross-check `\ref{fig:...}` against figure numbers and caption completeness.

6.10 Punctuation consistency: use the Oxford comma (A, B, and C) uniformly; commas on both sides of mid-sentence adverbs ("The model, however, fails to..."). Fix: [R]sample 3-5 lists for the Oxford comma; check however pairs.

6.11 No contractions: don't → do not, can't → cannot (one word), won't → will not, it's → it is, doesn't → does not; "can not" is wrong. Fix: [S]`n't\b|it's\b|can not\b`; write formal forms.

6.12 Expand or avoid case-sensitive abbreviations: prefer "with respect to" over "w.r.t." (some venues ban it). Fix: [S]`w\.r\.t\.|resp\.`; expand per the target venue.

---

## Check Order (agent execution sequence)

Ordered by error frequency × fix payoff. Run each search, then apply that rule's fix. Record hit and fix counts per item; for [R]items, judge with context — never guess.

1. **Article sweep** (1.1-1.10): search `the ` and verify each; `propose .*, (the|an?)` (1.3); `on (COCO|ImageNet|...)|the (COCO|...)` (1.9); `the (Figure|Table|Section|Eq\.|Algorithm) \d` (1.10).
2. **Dangling modifiers** (3.4, 3.5, 3.14): search sentence-initial `Using|Given|Compared|Based|Following|When ...ing`; verify each main-clause subject.
3. **Uncountable nouns** (1.5, 2.4): search `researches|informations|evidences|knowledges|a evidence|a research|a software`; rewrite all hits.
4. **Adverb splices** (3.1, 3.2): search `, however,|, therefore,|, moreover,|, thus,`; check whether the clause before the comma is complete.
5. **Subject-verb agreement** (2.2, 2.3, 2.7, 2.8): search `number of|Each of|There (is|are)`; verify each.
6. **Preposition collocations** (4.1, 4.5, 4.8): search `results? to|depends? of|different with|discuss about|emphasize on|increases? \d`; fix each.
7. **respectively** (6.3): search `respectively`; check the parallel lists.
8. **Latin plurals** (2.5): search `phenomenons|criterias|matrixes`; correct the forms.
9. **Parallel structure** (3.6, 3.7): search `both|not only|either` plus 3+ item lists; check uniformity.
10. **which reference** (3.8, 3.9): search `, which` for ambiguous antecedents; search `, that` and rewrite.
11. **it-extraposition & wordiness** (3.10, 5.10, 5.11): search `It is (worth|obvious|important)|perform an analysis|As we all know|in order to`; rewrite.
12. **Abbreviations** (5.8, 6.6, 6.12): check each acronym's first-use definition; search `a (SVM|LSTM)` for a/an.
13. **Capitalization & typography** (5.6, 5.7): search `\bfigure \d|table \d|section \d`; unify %-spacing, leading zeros, unit spacing.
14. **Hyphens** (5.9): search `end to end|real time|state of the art`; hyphenate attributive uses.
15. **Word swaps** (5.2, 5.3, 5.4, 5.5, 5.12): search `less (parameters|samples)`, affect/effect parts of speech, `comprise of|is comprised`, colloquialisms.
16. **Absolute claims & hedging** (6.7, 6.8): search `prove|significant|always|never|all existing`; qualify or downgrade.
17. **we vs passive & register** (6.1, 6.11): search `we can see|it can be seen|can't|don't|can not`; rewrite.
18. **Punctuation** (6.10): sample-check the Oxford comma and however comma pairs.
19. **Figure/table completeness** (6.9): verify each Figure/Table is cited at least once, numbering is continuous, and captions are complete sentences.
