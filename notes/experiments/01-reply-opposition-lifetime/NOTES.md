# Replies × stance × lifetime: decision log and results (2026-10-06)

Task from [[2026-09-30]]: *Analyze who replies to whom and whether their positions are opposed, complemented with an analysis of users' lifetime* (due 2026-10-19).
Plan: `PLAN.md` (approved 2026-10-06). Download log: `../dataset-download/NOTES.md`.
Code: `code/_obsoleto/01-reply-opposition-lifetime/00…07_*.py` (run in order with `uv run python <script>` from that folder). Derived data: `data/derstandard/derived/`. Every table and figure is in `results/`, and every run is logged with timings and row counts in `results/run.log`.

## Headline results

| # | Question | Test | Result |
|---|---|---|---|
| H1 | Do people downvote the comment they reply to? | Same comment: repliers vs other voters, Mantel–Haenszel over 8.1M comments | **53.3% vs 30.1% downvotes; OR = 4.43 [4.42, 4.44]**. Stable every year (4.1–4.7) and topic (3.5–4.9). |
| H1b | Escalation | OR by depth of the replied comment | OR **3.5 (root) → 5.7 → 6.9 → 7.8 → 8.2 → 9.0 (depth ≥5)** |
| H2 | Do people reply to users they are generally against? | A's dataset-wide votes toward B vs toward a co-present null (random earlier commenter in the same article); A's vote on that specific comment excluded; bootstrap clustered by replier | Negative edges (≥5 votes, E[p]<0.4): **31.4% vs 18.1%** (diff +13.3 pp [12.6, 14.0]). FAULTANA strict edges: 9.4% vs 3.8%. Mean E[p] 0.53 vs 0.59. |
| H2-robust | 24 specs (prior, thresholds, min votes, incl/excl) | Specification curve | diff ∈ **[+11.7, +20.6] pp, positive in 24/24** |
| H3 | Are replies cross-faction? (14.8k FAULTANA-labelled users) | Cross share vs null vs random mixing | **26.0% observed vs 23.2% null vs 46.8% random mixing**. Exposure is strongly segregated, and within that exposure people pick slightly more out-group targets. The excess comes from faction 1 (16.7% vs 13.7%); faction 2 users reply to faction 1 about 84% of the time, the same as their null. |
| H3b | Are cross-faction replies hostile? | P(replier downvoted parent) | **64.6% cross vs 37.0% same faction**; dyad downvote share 53% vs 2.5% |
| Reply-back | Does hostility keep the exchange going? | P(B replies to A's reply) | **31.8% if A downvoted B's comment, 16.6% if A upvoted it**, 29.8% if A didn't vote |
| Tenure | Who is hostile to whom? | P(downvoted parent) by tenure of replier × target (2016+) | Veterans (3y+) → newcomers (<30d): **68%**; veteran ↔ veteran: 48% |
| Life | Lifetime descriptives (247,863 users) | KM, CCDF | 26.7% active <1 day, 37.9% <30 days, 20% wrote a single comment. KM median lifetime falls by cohort: **2014: 1.36 y → 2016: 0.81 → 2018: 0.41 → 2020: 0.39 y**; 1-year survival 53% → 41% |
| H4 | Does early opposition predict leaving? | Cox PH, 30-day landmark, stratified by cohort, 98,670 new commenters (59% events) | HR per SD: **downvote share received 1.11 [1.10, 1.12]; hostile replies received 1.06 [1.05, 1.07]**; hostile replies written 1.04; got any reply 0.95; early comments (log) 1.23. PH assumption OK (all p > 0.05 on a 20k sample). |
| H4-robust | 18 specs (churn buffer 3/6/12 m × window 14/30/60 d × shrinkage 2/10) | Specification curve | downvote share HR ∈ [1.10, 1.12]; hostile received ∈ [1.05, 1.08]; CI excludes 1 in **18/18** for all three hostility measures |

Figures: `04_h1_by_year.png`, `05_h2_dyad.png`, `06_lifetime_ccdf_km.png`, `06_h4_cox.png`, `07_multiverse.png`.

## Data decisions (all logged in run.log)
1. **Duplicate comments:** 259,521 comment IDs appear twice with identical rows → `DISTINCT` (75,644,850 → 75,385,329). The official summary counts include the duplicates.
2. **Votes:**
   - 27.1M votes have a NULL (deleted) voter → dropped. They can't be used for anything dyadic.
   - Exact duplicate rows were collapsed to one vote per (comment, voter).
   - Excluding NULL voters, there are **0** (comment, voter) pairs with conflicting signs. The 1.33M "conflicts" seen at first were NULL-voter rows grouping together.
   - Clean total: 383,858,436 votes.
3. **Reply edges** (53.43M replies → **44,350,672 edges**):
   - dropped 326,643 flagged in `inconsistent_comment_metadata`
   - dropped 11 with a missing parent
   - dropped 7.98M with a deleted author on either side
   - dropped 773,899 self-replies
   - 26 edges have parent_ts > reply_ts; kept (negligible)
4. **Null model:** for each reply, the null target is the author of a uniformly random *earlier* comment in the same article, excluding A. Draws are deterministic hash-based (seed 20261006, up to 5 draws). Coverage is 99.998%. Verified: 0 null comments come after the reply, 0 are in a different article, 0 are self. The null equals the true target in 4% of cases; that's legitimate.
5. **Votes have no timestamp** (only file month), so dyad stance is measured over the whole dataset, and H1 can't tell whether the downvote came before or after the reply.
6. **21 users** have votes dated 2007–2012 (old articles still open) → first activity clipped to 2013-01-01 for lifetime.
7. **Pooled dyad downvote share is misleading** (7% overall, with spikes to 40% in 2013 and 20% in 2022). It's dominated by a few mega-dyads with thousands of mutual upvotes (median 1–2 votes per dyad, mean ~110). Headlines use per-edge measures instead (negative-edge share, mean E[p]).
8. **H4 shrinkage bug found and fixed.** The first version shrank shares with a Beta(1,1) prior, which put users with no replies at 0.5, well above the real base rate. "No data" looked hostile, and the sign flipped between univariate and adjusted fits. Fix: shrink toward the population rate (pseudo-count M = 2; M = 10 in the multiverse). `log_articles` was dropped (r = 0.95 with `log_comments`).
9. **Faction projection to unlabelled users is weak** (in-sample AUC 0.63, accuracy 0.68), so it's **not used in conclusions**. With it, cross share is 29.7% vs 24.5% null, the same direction (`05_h3_projected_factions.csv`).
10. **Deviations from the plan:**
    - Skipped the 2019 prototype, because full-data steps run in seconds to minutes.
    - The H4 multiverse uses a 14/30/60-day window grid instead of "30 days vs first 10 comments", so one feature builder (`h4.py`) serves every spec.

11. **Positive votes and top-10% lifetime (2026-11-02, [AI, not yet reviewed]).** Scripts 08 and 09 (see RESULTS §8).
    - Positive edge = E[p] > 0.6, the mirror of the negative edge, with the same prior, thresholds and null.
    - The H1 upvote OR is exactly 1 / the downvote OR (same 2×2 table), so it isn't independent evidence.
    - "Long-lived" has four definitions: top 10% overall, top 10% within entry cohort (preferred, since it removes the cohort-length effect), >2y, >3y. The population is the H4 landmark one (survived 30 days).
    - `h4.py` now also returns `n_*_friendly`, `upvote_share_recv`, `friendly_reply_share_*`; `X` and the old results are unchanged.

## Caveats for the meeting
- **"Opposed position" here means vote-based disapproval, not measured ideology.** Factions are the closest thing to ideology, but they exist for only 14.8k stable users. Those users are survivors by construction, and their partition was built from these same votes, so H3b is partly circular.
- **H1/H2/H3 are associations, not causal effects.** Whether the vote came first is unknown.
- **H4 is observational.** Reverse causation is possible: users already on their way out may attract or produce hostility. "Leaving" can't be told apart from being banned. Heavy early commenters (>30 comments in 30 days) leave much faster (71% events, median 0.95 y; `06_h4_by_early_activity.csv`). These may be burst, banned or sockpuppet accounts, which is worth a separate look.
- **2022 data volume:** comments and votes per month drop about 45% from February 2022 while active users stay flat (no ID migration). This looks like a collection or platform change; ask Andreas/Emma.
- **With N in the millions, p-values carry no information.** Report effect sizes and specification curves.

## Limitaciones de los datos para el planteamiento del 2026-11-19
Apuntadas en el repaso del 2026-11-21 [AI, a petición mía]. Son hechos de los datos, no decisiones.
- **Los votos no tienen fecha** (decisión 5). No se puede saber si un voto es anterior o posterior a la respuesta del mismo usuario. Afecta a cómo se formula la pregunta de los votos negativos al responder.
- **Usuarios borrados.** Se excluyen 7.976.578 respuestas (14,9 %) y 27,1M de votos. No se ha comprobado si se comportan distinto del resto; si eran más conflictivos, el foro parecerá más tranquilo de lo que fue.
- **26 respuestas con el padre posterior a la respuesta** (decisión 3). El filtro de `inconsistent_comment_metadata` («Inconsistent timestamp», 1.208 comentarios) no las detecta. Se mantienen.
- **Año 2023 en `reply_edges`.** El dataset va hasta el 2022-12-31, pero el año máximo de las aristas es 2023.
- **Facciones.** `faction_users.tsv` tiene 14.817 usuarios (9.278 en la facción 1, 5.539 en la 2), el 6,0 % de los 247.863 del fichero de usuarios (que incluye usuarios que solo votan).

## Possible next steps
- **Bridging users:** an open idea from the meeting. Users who reply across factions without hostility. Who are they, and do they live longer?
- **Escalation as a sequence model:** P(hostile at depth k+1 | hostile at depth k) within threads.
- **Separate bans from voluntary exits:** heavy-burst accounts, plus the 2022 volume drop.
- **Topic-level H2/H3:** politics vs sport. H1 by topic is already in `04_h1_comment_level.csv`.
