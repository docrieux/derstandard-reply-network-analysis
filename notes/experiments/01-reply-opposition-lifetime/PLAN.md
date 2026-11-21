> **Diseño antiguo (2026-10-06), escrito por la IA. Se conserva como registro del planteamiento inicial.** Sus afirmaciones no están verificadas; sus problemas y las decisiones sobre cada uno están en `notes/method/BASE-VERIFICADA.md`, §4. El planteamiento actual es el del 2026-11-19 (`WORKLOG.md`).

# Plan — Testing "who replies to whom & opposed positions" + "user lifetime" (DerStandard)

## Context
Meeting 2026-09-30 task (due 2026-10-19): *Analyze who replies to whom and whether their positions are opposed, complemented with an analysis of users' lifetime.* Data are downloaded to `data/derstandard/` (28 GB, MD5-verified): 75.6M comments (53.6M replies), 412M votes (22.6% negative), 587k articles, users file, `faction_users.tsv`.

There is no comment text, so **"position" has to be inferred from signed votes**. Three operationalisations, from most local to most global:
1. **Comment-level:** did the replier up- or downvote the comment they replied to?
2. **Dyad-level:** A's overall vote balance toward B across the whole dataset (Beta posterior, as in FAULTANA: prior α=1, β=2; positive edge if E[p] > 0.6, negative if E[p] < 0.4).
3. **Faction-level:** are A and B in opposite FAULTANA factions? `faction_users.tsv` covers 14.8k "stable" users who voted every year 2014–2021: faction 1 has 9,278 users, faction 2 has 5,539.

Novelty versus prior group work: Lan Ceqin (2026) studied reply/vote *reciprocity* and new-user shares. FAULTANA studied vote-network factions. Neither crosses **reply structure × stance × lifetime**.

Resources: 32 GB RAM, 16 threads, 751 GB free, uv 0.12.7, Python 3.11 (`code/`). Engine: **DuckDB** (out-of-core SQL over Parquet). Stats: scipy, statsmodels, lifelines. Plots: matplotlib.

## Objective 1 — Who replies to whom, and are their positions opposed?

**Reply edge** = comment with `Is_Reply=1`, joined on `Parent_Id` to the parent's author → (replier A, target B, comment ids, ts, article, depth). Drop self-replies, `NA` authors, and IDs in `inconsistent_comment_metadata.tsv`.

**Descriptives (who → whom):** reply-graph degree distributions and concentration (Gini; share of replies received by the top 1% of users); reciprocity; newcomer↔veteran mixing (A's and B's tenure at reply time); breakdown by year, `Topic_1` and thread depth.

**Hypotheses and tests** (each against a null that controls for exposure):
- **H1 (comment level):** voters who reply to comment c downvote c more often than voters who don't reply.
  - Test: within-comment comparison over comments that have both reply-voters and non-reply voters.
  - Statistics: Mantel–Haenszel pooled odds ratio stratified by comment, plus a cluster bootstrap by voter.
- **H2 (dyad level):** reply pairs (A→B) have a more negative dyadic vote balance than **co-present null pairs**.
  - Null construction: for each reply, B is replaced by the author of a uniformly random earlier comment in the same article. In SQL: rank comments per article by timestamp; for a reply at rank r, pick rank ⌊U·(r−1)⌋+1. This keeps article, time and exposure fixed.
  - Robustness: compute dyad balance **excluding** votes on the parent comment, so H2 doesn't re-count H1.
  - Report P(negative edge), mean E[p], and the difference with a bootstrap CI.
- **H3 (faction level):** among replies where both users have a faction label, the cross-faction share exceeds (a) random mixing given faction sizes and (b) the same co-present null as H2. Also split into cohesive vs divisive replies (in-group vs out-group).
- **Follow-ups:**
  - Does opposition rise with thread depth (escalation)?
  - Does B reply back more often when A is opposed?
  - Year and topic heterogeneity, e.g. politics vs sport.

**Faction extension (for Objective 2 and coverage):** project unlabeled users onto the fault line using their vote balance toward each faction. Score = net vote toward F1 members − net vote toward F2 members, with a Beta-shrunk confidence. Validate on held-out labeled users (accuracy/AUC) before using it.

## Objective 2 — User lifetime
- **Lifetime** = last − first activity, computed for comments only and for any activity (comments + votes), from `users_file`.
  - Right-censoring: last activity on or after 2022-07-01 counts as censored ("still active").
  - Left-censoring: first activity before 2013-07-01 is flagged left-censored. Excluded from cohort analyses.
- **Descriptives:** lifetime CCDF (log-log); share of one-shot users; Kaplan–Meier survival by entry-year cohort; survival of commenters vs voter-only users.
- **Link to Objective 1, H4:** users who receive more opposition early in life leave sooner.
  - For each user's first 30 days (and, alternatively, first 10 comments): share of replies received from opposed users (H2 dyad sign), downvote share received, and share of own replies that are antagonistic.
  - Model: Cox proportional hazards. Covariates: early activity volume, cohort year, topic mix, and whether the user's early replies got any response at all.
  - Check the proportional-hazards assumption (Schoenfeld residuals). Use a landmark at day 30 to avoid immortal-time bias.
- **Caveat:** `faction_users` are survivors by construction. They are never used as the population for lifetime estimates, only for the extended faction scores.

## Robustness (multiverse-lite, following the Steegen/Simonsohn papers in `papers/`)
Vary:
- Beta prior: (1,2) vs (1,1)
- Edge thresholds: 0.6/0.4 vs 0.7/0.3
- Minimum interactions per dyad
- Churn buffer: 3 / 6 / 12 months
- Early window: 30 days vs 10 comments

Report how each headline effect behaves across these specifications.

## Implementation (staged; every stage checkpoints to disk so work can stop cleanly at any point)
Analysis scripts go in `code/_obsoleto/01-reply-opposition-lifetime/`, numbered and run with `uv run`. The existing package is named `code`, which clashes with Python's stdlib module of the same name, so don't import it. Deps are added to `code/pyproject.toml`: duckdb, pyarrow, pandas, numpy, scipy, statsmodels, lifelines, matplotlib.

| Step | Script | Output (`data/derstandard/derived/`) |
|---|---|---|
| 0 | `00_to_parquet.py` — TSV→Parquet with explicit types; hex IDs → `UBIGINT`; `NA`→NULL | `comments.parquet`, `votes.parquet` (partitioned by year), `users`, `articles`, `factions` |
| 1 | `01_reply_edges.py` | `reply_edges.parquet` (+ tenure of A and B at reply time) |
| 2 | `02_null_pairs.py` — co-present random earlier commenter per reply, fixed seed | `null_edges.parquet` |
| 3 | `03_dyads.py` — vote aggregates only for (A,B) pairs in reply ∪ null edges (semi-join keeps it small), both directions, with and without the parent comment | `dyads.parquet` |
| 4 | `04_h1_comment_level.py` | tables + figs |
| 5 | `05_h2_h3_dyad_faction.py` (+ faction projection and validation) | tables + figs |
| 6 | `06_lifetime.py` (KM, CCDF, Cox H4) | tables + figs |
| 7 | `07_multiverse.py` | spec-curve fig |

- **Prototype every step on a single year (2019) first** to check runtimes and sanity, then run the full 2013–2022 data.
- Traceability: `notes/experiments/01-reply-opposition-lifetime/NOTES.md` (decision log, linked from `[[2026-09-30]]`) plus `notes/experiments/01-reply-opposition-lifetime/results/` (CSV tables + PNG figures + run logs with row counts and timings).

## Verification
- Row counts after each step match `summary_comments.tsv` / `summary_votes.tsv` (75,644,850 comments; 53,617,134 replies; 412,511,165 votes), minus documented exclusions.
- Spot-check five random reply edges against the raw TSVs by grep.
- Null sanity: the null target's timestamp is always earlier than the reply, in the same article, and never equal to A.
- Faction check: the dyad network restricted to `faction_users` should reproduce FAULTANA's pattern (mostly positive edges within factions, negative across).
- Survival sanity: Kaplan–Meier median lifetime vs the raw CCDF; the censoring share is reported.
- Deliverable for 2026-10-19: a short results note with ~6 figures (reply concentration, H1 odds ratio, H2/H3 observed vs null, opposition × depth, Kaplan–Meier by cohort, Cox hazard ratios).
