# Code review of experiment 01 (2026-11-02)

**Reviewer:** Claude (the same model family that wrote most of the code, so this is a second reading, not an independent audit; the `[AI, not yet reviewed]` tags stay until *you* have gone through the items below).
**Scope:** every script in `code/_obsoleto/01-reply-opposition-lifetime/`: `common.py`, `00`–`09`, `h4.py`, `plotstyle.py` (not reviewed beyond a read), `check_duplicate_comments.py`, `check_self_votes.py`. Read line by line; logic re-derived against the plan, the papers in [[PAPERS-SUMMARY]] and the logged numbers in `results/run.log`.
**What I ran for the review (nothing in the pipeline was modified):**
1. A voter-stratified version of H1 (scratch script, not in the repo; results below).
2. A sanity query on `edges_stance.parquet`: after removing A's vote on the replied comment, no dyad vote count goes negative (0 of 44,350,672 true edges, 0 of 44,349,679 null edges), and no edge where A voted on the parent lacks dyad votes. The "excl" variant is internally consistent.
3. Checked the constants in `common.py` (see 1.1).

**Bottom line.** I found **no coding bug that changes a headline number.** The pipeline does what the notes say. The risks are in *what the measures mean*: 3 high-severity validity issues (selection, look-ahead, and my own top-10% definition), 6 medium design issues, and a few low items. Details and suggested fixes follow. I have not changed any analysis code in response to this review; decisions are listed in section 5.

---

## 1. Checked and found correct

### 1.1 Constants and conventions (`common.py`)
- `T_START`=2013-01-01, `T_END`=2023-01-01, `RIGHT_CENSOR`=2022-07-01, `LEFT_CENSOR`=2013-07-01 (decoded from the epoch values; all UTC midnight).
- `hexid` casts the 16-hex id to `UBIGINT` (`'0x'||id`); NULL stays NULL.

### 1.2 `00_to_parquet.py`
- Votes: `sign = Pos − Neg`; log confirms **0 votes with sign 0** (`run.log`: 412,511,165 total = 319,154,131 positive + 93,357,034 negative), so no ambiguous votes. Year/month taken from the file name (`votes_file_MM_YY`), 2000+YY.
- `votes_clean`: one row per (comment, voter), NULL voters dropped (27,122,483), pairs with two signs dropped (0 found). `any_value(author_id)` keeps a non-NULL author if any duplicate has one.
- Comments `DISTINCT` is lossless: `check_duplicate_comments.py` shows distinct comment ids = distinct full rows = 75,385,329 (259,521 exact duplicates).
- Users: `First_Comment = 0` → NULL (never commented), same for the other timestamps.
- **Skip-if-exists** (lines 63–66) is a stale-data risk if cleaning rules change (see L-7).

### 1.3 `01_reply_edges.py`
- Self-join on `parent_id`; the funnel categories are mutually exclusive and add up exactly: 53,427,803 − 326,643 − 11 − 7,976,578 − 773,899 = 44,350,672 final edges (verified by hand). Exclusion list includes **both** types in `inconsistent_comment_metadata` ("Article deleted" 382,167 comments and "Inconsistent timestamp" 1,208, per the dataset paper), matching the dataset authors' recommendation.
- `tenure_*_days` uses first activity of either kind; correct handling of NULL first comment/vote.

### 1.4 `02_null_pairs.py`
- `k` = rank of the comment among eligible (non-NULL author, non-inconsistent) comments of the article by `(ts, comment_id)`. `k_null = 1 + floor(U·(k−1))` with `U = hash/2^64 ∈ [0,1)` → uniform on `1..k−1`; deterministic via `hash(comment_id, SEED+draw)`; first valid draw (author ≠ A) kept. Logged checks: 0 null comments after the reply, 0 in a different article, 0 self; 993 replies without a null (0.002%); null equals true target in 1,760,319 cases (4.0%).

### 1.5 `03_dyads.py`
- `pairs` covers real and null targets in both directions; `dyads` joins on `(voter, author)` through a semi-join; `edges_stance` joins are 1:1 (unique `(comment, voter)` in `votes_clean`; unique `(u,v)` in `dyads`), so no row multiplication (row count stays 44,350,672).

### 1.6 `04_h1_comment_level.py`
- 2×2 cell definitions: `a` = replier & downvote, `b` = replier & upvote, `c` = other & downvote, `d_` = other & upvote → OR = ad/bc ✓. The Mantel–Haenszel estimator `ΣR/ΣS` with `R=ad/n`, `S=bc/n` and the Robins–Breslow–Greenland variance `ΣPR/(2ΣR²) + Σ(PS+QR)/(2ΣRΣS) + ΣQS/(2ΣS²)` match the standard formulas. `repl` uses `DISTINCT (parent_id, a)` so the left join cannot duplicate votes.

### 1.7 `05_h2_h3_dyad_faction.py`
- Beta posterior `E[p]=(pos+α)/(pos+neg+α+β)`, variance `E(1−E)/(n+α+β+1)` ✓ (FAULTANA, see PAPERS-SUMMARY B2). Per-edge metrics, ratio estimators and **paired** Poisson bootstrap by replier (same weights for real and null) ✓. Reply-back logic: `back` = (comment, replier), joined on `(A's reply comment, B)` → "B replied directly to A's reply" ✓. H3 cross-faction and random-mixing `2p(1−p)` ✓.

### 1.8 `06_lifetime.py`, `h4.py`, `07_multiverse.py`
- Lifetime: first activity clipped to the dataset start (21 users with 2007–2012 votes), censoring flags, KM per cohort with `event = not censored` ✓. Landmark logic ✓: exposures from `ts < t0 + W`, survivors `t_last ≥ t0 + W`, time from the landmark. **Censoring times for non-events are `t_last`, which can exceed `right_censor`; this does not change the Cox hazard ratios** (events only occur before `right_censor − landmark`, and every censored user is in the risk set at every event time either way). Cosmetic only.
- Shrinkage toward the population rate ✓ (the Beta(1,1) bug of the first version is fixed and documented). Multiverse H2 formulae reproduce the main spec (diff +13.3 pp at prior (1,2), 0.6/0.4, ≥5 votes, excl).

### 1.9 My own additions (`08`, `09`, `h4.py` extension)
- `08` swaps the 2×2 roles for the up-vote mirror (new `a`=replier & up, `b`=replier & down, `c`=other & up, `d_`=other & down): OR_up = 1/OR_down. Numerical check: 1/4.428 = 0.2258 vs reported 0.23 ✓.
- `h4.py` only *added* columns; `X` and the existing outputs are unchanged. The positive-edge definition mirrors the negative one. `09`: `life_years = T_years + 30/365.25` = lifetime from the first comment ✓.

---

## 2. Findings: validity issues (not coding bugs)

### High

**H-1. Deleted users are invisible, so exits by deletion or ban cannot be analysed.** (`00_to_parquet.py` users; `01_reply_edges.py:27`; dataset paper "Internal Consistency")
Comments, votes and replies by deleted accounts have `Author_Id`/`Voter_Id = NA` (8.46% of comment authors, 8.33% of vote authors, 7.27% of voters). They cannot be linked to a user, so **they are not in the users file and not in the lifetime or H4 populations**. We drop 14.9% of replies because either side is deleted, and this is selective: it is the accounts that left in the most drastic way. Consequences: (i) the lifetime/survival results describe users who *kept* their account; (ii) hostility → exit via ban/deletion is outside the data, so the H4 hazard ratios could be biased in an unknown direction (probably toward under-estimating the effect of hostility, if hostile users are the ones banned); (iii) "hostile replies received from deleted repliers" are lost from the exposure. **Suggested action:** state this in the limitations of the thesis; optionally bound it with a sensitivity analysis (e.g. compare the share of NA authors by year and by thread depth/topic; check whether replies with a deleted party are more often at deep levels).

**H-2. The "top 10% by lifetime" group is mostly "still active at the end", ordered by last-activity date, and the fixed-threshold profiles are contaminated by cohort.** (`09_top_decile_lifetime.py:32–36`, my code)
Lifetime is right-censored, and in `top10_cohort` **100% of the group is censored**. Among censored users the observed lifetime only reflects *when they last happened to be active before the data end*, so the group is partly selected by recent activity (and so favours people who are active more often), not by true duration. For `gt2y`/`gt3y`, the "rest" group includes cohorts that entered too recently to reach 2 or 3 years, so the early-profile comparison mixes calendar years (hostility levels also vary by year). The logit uses cohort fixed effects and, for `gt2y`, restricts to cohorts ≤ 2020, which is right, but the profile table and the tenure table do not. **Suggested fixes:** (a) compare within cohort (stratify, or standardise by cohort); (b) use fixed thresholds only for cohorts that can reach them (≤ 2019-07 for 3 y) and report them as "survived to ≥ 3 y"; (c) add a survivor flag "active after 2022-07" as an explicit alternative group; (d) add a volume covariate (activity in the last months) to check that "recently active" is not driving it. The existing result (long-lived users start less hostile) is qualitatively plausible because the difference does not come from early volume (median early comments 2 vs 2), but should be re-stated after (a)–(b).

**H-3. Votes have no timestamp, so "early-life exposure" in H4 includes votes cast after the landmark.** (`h4.py:26–27` received votes `comments.votes_pos/neg`; `h4.py:31–37` hostile = `vote_true = −1`)
The 30-day window restricts *when the comment or reply was written*, not *when the vote was cast*. A downvote on a day-3 comment cast at month 6 counts as "early" while survival starts at day 30: a mild look-ahead. Most votes arrive within days, so the bias should be small, but it cannot be bounded with the data. Also, the dataset paper notes that the comment-file vote counts are sometimes one lower than the votes files (the authors overwrote them with the votes-file aggregates); H4 uses the comment-file counts for received votes. **Suggested action:** state the limitation; recompute `rpos/rneg` from `votes_clean` for consistency; as a sanity check restrict to comments whose votes mostly arrive early (e.g. comments with ≥ X votes) or use only the hostile/friendly *reply* measures (which do not depend on the received-vote counts).

### Medium

**M-1. H1 compares different voters, and the CI is too narrow.** (`04_h1_comment_level.py:32–68`)
The within-comment design removes comment effects, but repliers can be systematically heavier or more negative voters. **I tested this** (voter-stratified MH, strata = 103,984 voters; each voter's votes on comments they replied to vs their votes on other comments that received at least one reply): **OR = 3.49 [3.48, 3.49]** (vs 4.43 by comment); P(down | replied) = 52.3% vs 25.3%; and **89% of voters with ≥ 10 votes on both sides downvote more on the comments they reply to** (median difference +23.4 pp). So the result is robust to voter heterogeneity, but part of the 4.43 (about 16% of it on the log scale: ln 3.49 = 1.25 vs ln 4.43 = 1.49) is who the repliers are. Also, the plan promised a *cluster bootstrap by voter*; the code bootstraps over comments with Poisson weights, and the MH interval (4.42–4.44) assumes independent votes. Both CIs understate uncertainty (votes of the same voter are correlated). **Suggested action:** report both ORs (comment strata 4.43, voter strata 3.49) and a voter-cluster bootstrap CI, and describe the CI as conditional on independence.

**M-2. H2 compares "defined edges" among subsets that differ between real and null.** (`05_h2_h3_dyad_faction.py:21–35, 61–83`)
`p_negedge5 = negative edges / (edges with ≥ 5 votes and E[p] outside [0.4,0.6])`: the denominator is conditioned on having a vote history, and real pairs have more shared history than null pairs (any vote: 59.4% vs 55.6%; strict-edge counts 1,510,420 vs 1,197,429). The headline +13.3 pp is a difference between shares computed on different, selected subsets. The multiverse shows the sign is stable (+11.7 to +20.6 pp), but the *size* is partly a coverage effect. Also, dyad votes cover the whole dataset period, so they include votes made *after* the reply and possibly *because* of the reply (the "excl" variant removes only the vote on the replied comment). **Suggested action:** add a version that conditions on equal coverage (e.g. restrict to replies where both the real and the null pair have ≥ 5 votes), report the shares with both denominators, and keep the "association, not cause" wording.

**M-3. The null is article-level and comment-weighted, not thread-level or visibility-matched.** (`02_null_pairs.py:19–28`)
The null chooses an author of a random earlier comment in the article; real replies are directed to comments the replier has *seen*, which are concentrated in the replier's own thread and in more visible/popular comments. So "real − null" mixes stance with exposure to the specific thread and comment popularity. The null controls for article and time, as designed, but not for thread. **Suggested action:** add a second null restricted to the same thread (`root_id`) and, if possible, matched on the parent's depth or vote count; report both. This also matters for how the claim "people reply to users they are generally against" is worded: "more than to a random co-present commenter in the article".

**M-4. The escalation-by-depth numbers for H2 use the pooled downvote share.** (`05_h2_h3_dyad_faction.py:86–93`)
`NOTES.md` item 7 says the pooled dyad downvote share is dominated by mega-dyads and that headlines use per-edge measures; the depth and year breakdowns (`by`) nevertheless use `sum(neg)/sum(tot)`. The RESULTS statement "11.4% vs 6.2% at depth 6+" therefore rests on the measure the notes call misleading. **Suggested action:** recompute by depth with the per-edge metrics.

**M-5. "Hostile share" mixes hostility with the propensity to vote.** (`h4.py:56–58`)
Only 25.5% of replies have an A-vote on the parent (`run.log`). `hostile_reply_share_*` = hostile replies / *all* replies, so a user who votes a lot has higher hostile *and* friendly shares. This is why friendly replies have HR ≈ 1 but both can be driven by voting activity. **Suggested action:** define the share among replies with an observed vote (and include `n_voted` as a covariate), or add a covariate for the user's early voting volume.

**M-6. The multiverse is descriptive.** (`07_multiverse.py`)
Matches Steegen et al. (descriptive multiverse) but not Simonsohn et al.'s step 3 (joint inference under the null). The H4 multiverse varies buffer, window and shrinkage, not the model (e.g. covariate set, no stratification). **Suggested action:** word the claim as "the estimate has the same sign and similar magnitude across 24/18 specifications", and mention that no joint test was run.

### Low

- **L-1. Time zones.** `year(to_timestamp(ts))` (`01_reply_edges.py:40`, `04_h1_comment_level.py:46`, `08_positive_votes.py:56`) uses the DuckDB session time zone, while `pd.to_datetime(..., unit="s")` (`06_lifetime.py:31`, `h4.py:45`) is UTC. Year boundaries differ by hours. Add `SET TimeZone='UTC'` in `common.connect()`.
- **L-2. PH test on a 20k sample** (`06_lifetime.py:106–110`). A non-significant test on a subsample is weak evidence for proportionality; plot Schoenfeld residuals or fit a time-interaction on the full 98,670 users.
- **L-3. Faction projection validation is in-sample** (`05:151–155`, AUC 0.63). Already marked "not used" in the notes.
- **L-4. Penalizer** `0.001` in all Cox fits (small shrinkage). Say so in the methods.
- **L-5. Users with "Inconsistent timestamp" comments** (1,208 comments, < 0.15% of users per the dataset paper) are excluded from reply edges but their first/last activity stays in the users file used for lifetimes. Negligible, but the dataset authors recommend excluding them for lifespan analysis.
- **L-6. `run.log` appends across runs** (it mixes the first and later runs). Add a run header, or write one log per run.
- **L-7. Skip-if-exists in `00_to_parquet.py`.** If the cleaning rules change, the old Parquet files are silently reused. Store a version/hash of the query in a sidecar file.
- **L-8. Bootstrap replicates** are 200 (H1, H2). Enough for a percentile CI on millions of rows, but say so, and note it is a Poisson (not multinomial) bootstrap.
- **L-9. `check_self_votes.py`** has an unfinished comment ("My prediction ... No self votes or all self votes", lines 30–31). The result is recorded in `data-treatment.md` (no self-votes).
- **L-10. Entry = first comment** (`h4.py:24`). Users who voted for months before their first comment are "new commenters" but not new users. Fine for a comment-exposure design; say so, or add `first_vote` before `first_comment` as a covariate.

---

## 3. Things not checked

- The raw TSV → Parquet step was verified through its logs and the checks in the script, not by re-running it.
- `plotstyle.py` and the figures were not inspected for visual correctness.
- I did not re-derive the dataset-level numbers in `RESULTS.md` independently; I only checked those that the scripts reproduce and those I used in `08`/`09`.
- Statistical choices (Cox specification, penalizer, standardisation) were checked for coherence, not against alternative software.

## 4. Link with the literature (see [[PAPERS-SUMMARY]])
- FAULTANA edges and the Beta prior: our implementation matches the paper (prior (1,2), thresholds 0.6/0.4, variance < 1e-4). The FAULTANA network uses 17% negative interactions for the stable users; our whole-dataset share is 23%, so factions-level stance levels are not comparable with platform-wide levels.
- Dataset paper: our exclusions match its warnings, with the two gaps noted in L-5 and H-3 (vote counts).
- Cartwright–Harary: absence of a vote ≠ a negative tie; our "hostile" requires an observed downvote (M-5).

## 5. Suggested next actions (for you to approve)
Ordered by value for the thesis:
1. Re-define the long-lived group (H-2) and re-run `09` (about 10 s); update RESULTS §8.
2. Add the voter-stratified H1 and the thread-level null to the analysis (M-1, M-3) as robustness checks (about 10 minutes of compute).
3. Recompute H2 by depth with per-edge metrics, and the equal-coverage version of H2 (M-4, M-2).
4. Write the limitations on deleted users and vote timing (H-1, H-3) into RESULTS §6 and the thesis.
5. Small fixes: time zone, log header, Schoenfeld plot (L-1, L-2, L-6).
