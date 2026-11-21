# Using AI in this TFG: assessment and learning method

**Written:** 2026-10-06, after the first analysis session ([[2026-09-30]] task; results in `analysis/RESULTS.md`).
**Purpose:**
1. Honestly assess how AI (Claude Code) was used so far.
2. Define a working method where AI speeds up the work **while I learn, understand and own every procedure, test and decision.**

---

## Part 1. Assessment of the first session (2026-10-06)

### 1.1 What the AI did

In one session of about 1 hour, the AI did practically everything:

| Phase | Done by AI | Done by me |
|---|---|---|
| Find the dataset size, decide what to download, write a resumable MD5-checked downloader | ✅ all | Gave the goal; delegated the embeddings decision ("download what you deem necessary") |
| Design the tests (operationalisation of "position", null model, hypotheses H1–H4, statistics) | ✅ all | Approved the plan |
| Data cleaning (duplicates, NULL voters, exclusions) | ✅ all: found the problems *and* chose the fixes | none |
| Code (8 scripts, SQL + Python) | ✅ all | none |
| Running, debugging, checking | ✅ all, including finding its own bugs | none |
| Interpretation and conclusions | ✅ all | Asked for RESULTS file |

**Bottom line:** the results are probably correct and well documented. But **right now they are the AI's work, not mine.** If I were asked "why a Mantel–Haenszel odds ratio?" or "what is immortal-time bias and why does the landmark avoid it?", I would not be able to answer from understanding. For a TFG this is the main risk: the defense, the written report and future decisions all depend on me understanding it.

### 1.2 What worked well (keep)

- **Traceability.** Every decision is in `NOTES.md`, every run in `results/run.log`, every number in a CSV. That makes the work auditable and learnable after the fact.
- **Speed on mechanical work.** Downloading 28 GB with verification, converting 400M rows to Parquet, and writing plotting code took minutes. None of this is where the learning value of a TFG lies.
- **Self-checking.** The AI found and fixed real problems:
  1. 259k duplicate comments
  2. 27M votes from deleted voters, which looked like 1.3M conflicting votes
  3. a statistical bug: shrinkage that made "no data" look hostile and flipped the sign of a result
  4. a misleading pooled metric
  5. out-of-range timestamps
- **Robustness by default.** Null models, bootstrap CIs and a multiverse check over 42 specifications.

### 1.3 Risks and problems

1. **I didn't learn the procedures.** I can't yet reproduce or defend any step without the AI.
2. **The AI made methodological decisions that should be mine** (list in 1.4). Many are reasonable defaults, but *reasonable* ≠ *the one I would choose and can justify*.
3. **The AI's errors were caught by the AI.** That worked this time, but I couldn't have caught them myself. Several of them (the shrinkage bug, the misleading pooled metric) would have produced **wrong conclusions in the opposite direction** if they had gone unnoticed. I need to be able to catch errors like these myself.
4. **Plan approval without understanding.** I approved a plan full of terms (Mantel–Haenszel, landmark Cox, Beta posterior, co-present null) whose meaning and alternatives I didn't evaluate.
5. **Interpretation risk.** Some conclusions are causal-sounding (e.g. "hostility predicts churn → gatekeeping dynamic"). An AI writes persuasive prose easily; I have to judge whether the evidence supports it.
6. **Academic integrity and disclosure.** I need to know UPF's / my degree's rules on AI use in the TFG and declare it properly. **To do:** ask the TFG coordinator (I'm already asking her about cluster access) and Andreas.

### 1.4 Decisions made by the AI that I must review and own

For each one: understand it, look at the alternatives, then **endorse or change it** and write a one-line justification in my own words.

| #   | Decision                                                                                                  | Where                       | Alternatives                                                                     | My verdict (endorse / change + why)                                                                                                                                                                                                                             |
| --- | --------------------------------------------------------------------------------------------------------- | --------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | Skip the 508 GB of text embeddings                                                                        | `dataset-download/NOTES.md` | Download all / a sample; use embeddings as a stance proxy                        |                                                                                                                                                                                                                                                                 |
| D2  | "Position" = vote-based disapproval, at 3 levels (comment, user pair, faction)                            | `PLAN.md`                   | Text stance (embeddings), only factions, sentiment…                              |                                                                                                                                                                                                                                                                 |
| D3  | Null model = author of a random *earlier* comment in the same article                                     | `02_null_pairs.py`          | Random user; same thread only; degree-preserving rewiring; time-window           | **Endorse** [me], 2026-10-16. Keep the null uniform over *comments* ("a random message", not "a random author"): replies attach to comments, and the risk set is the earlier comments of the same article. Sensitivity: repeat with a null uniform over authors. No minimum risk-set size for now (it would change the population); only k >= 2 so that an earlier comment exists. See [[PLAN]]. |
| D4  | H1 = within-comment Mantel–Haenszel odds ratio                                                            | `04_h1_comment_level.py`    | Logistic regression with comment fixed effects; simple difference in proportions |                                                                                                                                                                                                                                                                 |
| D5  | Beta prior (1,2) and thresholds 0.6/0.4 from FAULTANA; "≥5 votes" relaxed definition                      | `05_…py`, `07_…py`          | Other priors and thresholds; continuous E[p] only                                |                                                                                                                                                                                                                                                                 |
| D6  | Excluding the vote on the specific comment in H2                                                          | `03_dyads.py`               | Include it; exclude all votes in the same thread                                 |                                                                                                                                                                                                                                                                 |
| D7  | Cleaning: comment DISTINCT, drop NULL voters, drop self-replies, deleted authors and inconsistent records | `00_…py`, `01_…py`          | Keep deleted authors as a category; keep self-replies                            | Drop duplicates with DISTINCT.<br><br>Drop NULL voters since they are all collapsed into a single NULL user that may have voted both +1 or -1 in the same comment. <br><br>Deleted authors won't be traceable along the dataset.<br><br>Inconsistent records () |
| D8  | Lifetime = last − first activity (comments + votes); right-censor at 2022-07, left at 2013-07             | `06_lifetime.py`            | Comments only; other cutoffs; activity-gap definition of "leaving"               |                                                                                                                                                                                                                                                                 |
| D9  | H4 design: 30-day landmark, Cox stratified by cohort, these covariates                                    | `h4.py`, `06_…py`           | Logistic "left within 1 year"; time-varying Cox; other windows                   |                                                                                                                                                                                                                                                                 |
| D10 | Shrink shares toward the population rate (M = 2); drop log_articles                                       | `h4.py`                     | No shrinkage + minimum-count filter; hierarchical model                          |                                                                                                                                                                                                                                                                 |
| D11 | Faction projection method, then judged unreliable (AUC 0.63)                                              | `05_…py`                    | Signed spectral embedding; label propagation; don't extend                       |                                                                                                                                                                                                                                                                 |
| D12 | Multiverse grids (and the deviation from the plan)                                                        | `07_multiverse.py`          | Larger or different grids                                                        |                                                                                                                                                                                                                                                                 |
| D13 | Headline metrics: per-edge, not pooled                                                                    | `NOTES.md` §7               | — (understand why pooled misleads)                                               |                                                                                                                                                                                                                                                                 |
| D14 | Tenure analysis only for replies from 2016-07                                                             | `06_…py`                    | Other cutoffs                                                                    |                                                                                                                                                                                                                                                                 |

---

## Part 2. The method: "AI as tutor and reviewer, me as author"

### 2.1 Principle

> **I make every methodological decision and can explain every line that produces a result in my TFG. The AI may do mechanical work, propose options, teach, and review, but it doesn't decide for me and I don't accept what I can't explain.**

### 2.2 Delegation levels by type of task

| Level | Type of task | Examples | AI role | My role |
|---|---|---|---|---|
| **L0. Delegate** | Mechanical, no research judgement | downloads, file conversion, plot styling, boilerplate, environment setup | Does it | Reviews the result, knows *what* it did |
| **L1. Assisted** | Technical with a correct answer | SQL joins, writing a bootstrap, fitting a Cox model | Writes it **and explains it**, or reviews my version | Must be able to explain every line (teach-back) |
| **L2. Mine, AI as tutor** | Methodological decisions | null model, which test, thresholds, exclusions, operationalisations | Gives **options + trade-offs + references, without recommending** until I've chosen | Decides and writes the justification in the decision log |
| **L3. Mine only** | Interpretation and claims | conclusions, causal language, what goes in the report | Challenges, acts as devil's advocate, checks numbers | Writes first, in my own words |

**Rule:** if I'm unsure of a task's level, treat it as one level higher.

### 2.3 Workflow for each analysis step

1. **Predict.** Before any code, I write in the step's NOTES: the question, my hypothesis, *what result I expect* and why. Five lines, my words.
2. **Explore options (L2).** I ask the AI: *"Give me 2–4 ways to test this, with trade-offs and the key concept I need to understand for each. Don't recommend yet."*
3. **Learn the concept.** For anything I can't explain, the AI teaches it with a **toy example I compute by hand or in a notebook** (e.g. an odds ratio on a 2×2 table).
4. **Decide and justify.** I choose, then write the decision, alternatives and reasons in the log. *Then* I can ask the AI to critique my choice.
5. **Implement (L1).** Either I write the code and the AI reviews it, or the AI writes it and I do a **teach-back**: I explain each block in my words and the AI corrects me. Over time, I write more of the code myself.
6. **Check.** I predefine the sanity checks (row counts, a known value, a spot-check). I run them myself.
7. **Interpret (L3).** I write the interpretation first. The AI then challenges it: alternative explanations, confounders, overclaiming.
8. **Comprehension gate.** The step only counts as done when I can answer its questions (see 2.6) **without AI help**.

### 2.4 Prompts / modes to use with Claude

Copy these at the start of a session or a step:

- **Tutor mode:** *"Act as a tutor. Don't write code or make decisions. Ask me questions to guide me, and explain concepts with small examples when I'm stuck."*
- **Options mode:** *"Give me the options with trade-offs and what each assumes. Don't recommend until I've chosen."*
- **Teach-back:** *"I'll explain what this script does block by block. Correct my mistakes and tell me what I missed."*
- **Reviewer mode:** *"Review my code/analysis. Point to lines and explain the problem, but don't fix it. Let me fix it."*
- **Devil's advocate:** *"Here is my interpretation. Give me the strongest alternative explanations and what evidence would distinguish them."*
- **Quiz me:** *"Ask me 5 questions about [concept/step], one at a time, and evaluate my answers."*
- **Explain a decision:** *"Why did you choose X? What would change if we chose Y? Show me on a small example."*

> Optional: I can add a `CLAUDE.md` to the repo so every session starts in this mode. For example: "The user is learning. For methodological decisions present options without recommending; explain every piece of code you write; ask before making any analysis choice; log decisions in notes/experiments/<experiment>/NOTES.md."

### 2.5 Logging AI use (for transparency and the final report)

- I keep an **AI-use log** in the NOTES of each topic, with one line per session: date, what the AI did, its level (L0–L3), what I decided, what I learned.
- Every decision in a decision log is tagged **[me]**, **[AI, reviewed]** or **[AI, not yet reviewed]**.
- For the TFG report, I prepare an AI-use declaration from this log, following UPF's / the degree's rules (to confirm with the coordinator and Andreas).

### 2.6 Learning metrics: how I know I understand

- I can explain any decision D1–D14 and its alternatives in 2 minutes, without notes.
- I can **reproduce one step from scratch without AI** (e.g. rewrite `04_h1_comment_level.py` from a blank file).
- I can **predict** what happens if a choice changes (e.g. "if I used a random user instead of a co-present one as the null, the gap in H2 would be larger/smaller because…") and then verify it.
- I can **find a planted bug**. I ask the AI to introduce a subtle error into a copy of a script, and I find it.

---

## Part 3. Plan to catch up on the work already done

**Goal:** turn the 2026-10-06 analysis from "AI's work" into "my work" **before the 2026-10-19 meeting**. One block per pipeline step. For each step:
- read the script
- learn the concepts (references in `papers/` where available)
- do the exercises
- answer the questions without help
- fill in the decision table (1.4)

| Block | Script(s) | Concepts to learn | Exercises (hands-on) | Questions I must answer |
|---|---|---|---|---|
| 0. Data | `00_to_parquet.py`, `common.py` | TSV vs Parquet; DuckDB; types; NULL; deduplication | Find a duplicated comment ID in the raw TSV with `grep`; count NULL voters in one month file | Why were there "1.3M conflicting votes" and why weren't they real? Why convert hex IDs to integers? |
| 1. Reply edges | `01_reply_edges.py` | Self-join, LEFT JOIN, exclusion funnel | Reconstruct one reply edge by hand from the TSV (child → parent → author) | Which replies are lost and why? Could excluding deleted authors bias the results? |
| 2. Null model | `02_null_pairs.py` | Null models; exposure / confounding; deterministic random sampling (hashing) | On one small article, list the earlier commenters and draw a null by hand | What does the co-present null control for that a random-user null doesn't? What does it *not* control for? |
| 3. Pair stance | `03_dyads.py` | Signed networks; structural balance (`Heider1946`, `CartwrightHarary1956`); FAULTANA (`Fraxanet2024`) | Compute A→B pos/neg counts for one pair by hand | Why exclude the vote on the specific comment? |
| 4. H1 | `04_h1_comment_level.py` | 2×2 tables, odds ratio, stratification, Mantel–Haenszel, confounding by comment; bootstrap | Compute the OR on a toy 2×2 table; build 3 toy strata where the pooled OR and the MH OR differ | Why stratify by comment instead of pooling all votes? What does OR = 4.43 mean in words? |
| 5. H2 / H3 | `05_h2_h3_dyad_faction.py` | Beta–binomial posterior; prior choice; cluster bootstrap; random mixing; the AUC metric | Compute E[p] and Var[p] for pos=3, neg=1 with prior (1,2); see why the FAULTANA threshold needs many votes | Why bootstrap by replier, not by edge? Why is the pooled downvote share misleading? Why is the faction result partly circular? |
| 6. Lifetime / H4 | `06_lifetime.py`, `h4.py` | Censoring (left/right); Kaplan–Meier; Cox PH and hazard ratios; immortal-time bias and landmarking; Schoenfeld test; shrinkage / empirical Bayes; collinearity | Fit KM and Cox on a 5k sample in a notebook; **re-introduce the Beta(1,1) shrinkage bug and watch the sign flip** | What does HR = 1.11 per SD mean? Why measure exposures *before* the landmark? Why did the old shrinkage flip the sign? |
| 7. Robustness | `07_multiverse.py` | Multiverse analysis (`Steegen2016`); specification curve (`Simonsohn2020`); effect size vs p-value at huge N | Add one new specification to the grid myself | Which specification choices matter most, and why? |
| 8. Results | `RESULTS.md` | Association vs causation; overclaiming | Rewrite the Conclusions in my own words, then compare with the AI's version | Which conclusions are causal-sounding but only associational? |

**Suggested pacing:** about 2 blocks per working day leaves time to spare before 2026-10-19. Do blocks 4 and 6 (the core statistics) with the most care.

---

## Part 4. Going forward (next tasks)

- **New analyses** (e.g. bridging users, escalation): start at step 1 of the workflow (2.3), with me writing the prediction and choosing the method.
- **Mechanical support** (downloads, environment, plot polish): delegate freely (L0).
- **Each meeting:** I present only what I can defend. Anything still tagged **[AI, not yet reviewed]** is either reviewed first or explicitly labelled as preliminary.
- **Review this document monthly:** is the AI still doing L2/L3 work for me? Am I writing more of the code myself?
