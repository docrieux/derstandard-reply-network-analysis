# Results: who replies to whom, opposed positions, and user lifetime

**Task:** [[2026-09-30]]. Analyze who replies to whom and whether their positions are opposed, complemented with an analysis of users' lifetime.
**Data:** DerStandard forum, 2013–2022 (doi:10.82201/RVQGUG): 75.4M unique comments, 383.9M usable votes, 247,863 users.
**Method and decisions:** see `PLAN.md` and `NOTES.md`. Code: `code/_obsoleto/01-reply-opposition-lifetime/00…07`. Tables and figures: `results/`.
**Date:** 2026-10-06

---

## 1. Summary

1. **People reply to those they disagree with.** A user who replies to a comment is about **4.4 times more likely (in odds)** to downvote it than other users who voted on that same comment. They also hold a more negative overall stance toward the person they reply to than toward other people in the same discussion.
2. **Disagreement escalates down the thread.** The deeper the exchange, the more hostile it gets: the odds ratio goes from 3.5 at the top of a thread to 9.0 at depth 5 or more.
3. **Hostility keeps conversations going.** A downvoted author replies back about twice as often as an upvoted one (31.8% vs 16.6%).
4. **Factions rarely meet, but when they do it's hostile.** Only 26% of replies cross the faction line, vs 47% if people mixed at random. When they cross, the replier downvotes the comment 65% of the time.
5. **Most users don't stay, and newer cohorts leave faster.** 27% are active for less than a day. Median lifetime drops from 1.4 years (2014 cohort) to 0.4 years (2020 cohort).
6. **Early hostility predicts leaving.** New commenters who receive more downvotes or hostile replies in their first month leave sooner. This holds across all 18 robustness specifications.

---

## 2. What "opposed position" means here

The dataset has **no comment text**, so a position is inferred from **votes**, at three levels:

| Level | Measure | Question |
|---|---|---|
| Comment | Did the replier up- or downvote the comment they replied to? | Do I disagree with *this* comment? |
| Pair of users | The replier's overall vote balance toward the target, across the whole dataset (Beta posterior, FAULTANA prior α=1, β=2) | Am I generally against *this person*? |
| Faction | Are the two users in opposite FAULTANA factions? (14.8k labelled users) | Are we on *opposite sides* of the platform's fault line? |

**Baseline (null model).** For each real reply, the null pairs the same replier with the author of a random **earlier comment in the same article**. Same discussion, same moment, same exposure; only *who was chosen* changes. Every comparison below is real vs null, so it isn't explained by who simply happens to be in the same place.

**Analysis set:** 44,350,672 reply edges (replier → author of the parent comment) among about 160k users. Deleted authors, self-replies and records flagged as inconsistent are excluded.

---

## 3. Objective 1: who replies to whom, and are they opposed?

### 3.1 Comment level (H1): repliers downvote what they answer

Design: within each comment, compare voters who replied to it with voters who didn't. Mantel–Haenszel odds ratio pooled over 8,117,960 comments.

| | Downvote share |
|---|---|
| Voters who **replied** to the comment | **53.3%** |
| Other voters on the **same** comment | 30.1% |
| **Odds ratio (MH)** | **4.43** [95% CI 4.42–4.44; bootstrap over comments 4.42–4.44] |

- **Stable over time:** the OR is between 4.1 and 4.7 in every year from 2013 to 2022.
- **Stable across topics:** the OR is between 3.5 (sport) and 4.9 (economy). It is above 4.5 in international, panorama and op-ed (diskurs).
- **Escalation with depth:**

| Depth of the replied comment | 0 (top level) | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|---|
| OR (MH) | 3.48 | 5.73 | 6.89 | 7.77 | 8.20 | **9.00** |
| Downvote share, repliers | 49.0% | 56.1% | 61.3% | 62.0% | 64.2% | 63.3% |

![[results/04_h1_by_year.png]]

### 3.2 User-pair level (H2): people reply to users they are generally against

The replier's votes toward the target over the whole dataset, minus the vote on the specific comment so this doesn't re-count H1. Compared with the null target. Bootstrap CIs are clustered by replier.

| Measure | Replied-to user | Null (co-present) | Difference [95% CI] |
|---|---|---|---|
| Negative relationships among user pairs with ≥5 votes (E[p] < 0.4) | **31.4%** | 18.1% | **+13.3 pp** [12.6, 14.0] |
| Negative relationships, FAULTANA strict definition | 9.4% | 3.8% | +5.6 pp [4.2, 7.6] |
| Mean posterior approval E[p] (pairs with any vote) | 0.53 | 0.59 | −0.058 [−0.061, −0.056] |
| Any vote history between the two users | 59.4% | 55.6% | +3.8 pp |

- The gap also grows with thread depth, and is largest at depth 6+ (11.4% vs 6.2% downvote share).
- **Robustness:** across 24 specifications, the gap stays between **+11.7 and +20.6 pp**, and is positive in all 24. The specifications vary the prior, the thresholds (0.6/0.4 vs 0.7/0.3), the minimum votes per pair (1/5/20), and whether the specific vote is included.

![[results/05_h2_dyad.png]]

### 3.3 Faction level (H3): factions rarely meet; when they do, it's hostile

Restricted to replies where both users have a FAULTANA faction label (11.3M edges).

| | Share of cross-faction replies |
|---|---|
| Random mixing (by faction size, 63% / 37%) | 46.8% |
| **Co-present null** (who is actually in the same discussions) | 23.2% |
| **Observed replies** | **26.0%** |

- **Exposure is strongly segregated.** Users mostly share discussions with their own faction (23% vs 47%).
- **Within that exposure, people choose out-group targets slightly more often than chance** (+2.8 pp, +12% relative). The excess comes from faction 1, the majority (16.7% observed vs 13.7% null). Faction 2 users reply to faction 1 about 84% of the time, which is what their null predicts. As the minority, they already share most discussions with faction 1.
- **Cross-faction replies are much more hostile:**

| Reply type | Replier downvoted the parent | Downvote share between the two users |
|---|---|---|
| Same faction | 37.0% | 2.5% |
| **Cross faction** | **64.6%** | **53.1%** |

> Note: an attempt to extend faction labels to all users was too weak to rely on (AUC 0.63). It points the same way (29.7% vs 24.5% cross-faction).

### 3.4 Reply-back: hostility keeps the exchange going

| Replier A's vote on B's comment | P(B replies back to A) |
|---|---|
| Upvoted | 16.6% |
| No vote | 29.8% |
| **Downvoted** | **31.8%** |

### 3.5 Who is hostile to whom (tenure)

Share of replies where the replier downvoted the parent, by tenure (replies from 2016-07 on, so tenure is not distorted by the dataset start):

| Replier \ target | < 30 days | 30 d – 1 y | 1 – 3 y | 3 y + |
|---|---|---|---|---|
| < 30 days | 59% | 62% | 62% | 62% |
| 30 d – 1 y | 62% | 57% | 56% | 53% |
| 1 – 3 y | 65% | 60% | 57% | 52% |
| **3 y +** | **68%** | 61% | 57% | **48%** |

Veterans are the most hostile toward newcomers (68%) and the least hostile toward each other (48%).

---

## 4. Objective 2: user lifetime

### 4.1 Descriptives

Lifetime = last activity − first activity, counting comments and votes.

| | Value |
|---|---|
| Users | 247,863 (211,108 commenters, 36,755 vote-only) |
| Active for **less than 1 day** | **26.7%** |
| Active for less than 30 days | 37.9% |
| Wrote exactly one comment | 20.3% |
| Still active at the end (last activity ≥ 2022-07; right-censored) | 30.3% |
| May predate the dataset (first activity < 2013-07; left-censored) | 16.6% |

**Survival by entry cohort** (Kaplan–Meier, commenters; time from first activity):

| Cohort | n | Median lifetime | Still active after 1 year | After 3 years |
|---|---|---|---|---|
| 2014 | 20,274 | **1.36 y** | 53% | 41% |
| 2016 | 16,018 | 0.81 y | 48% | 36% |
| 2018 | 14,752 | 0.41 y | 44% | 30% |
| 2020 | 21,462 | **0.39 y** | 41% | 28% |

Each newer cohort leaves faster. All curves drop steeply in the first weeks and then decline slowly: users who make it past the first months tend to stay for years.

![[results/06_lifetime_ccdf_km.png]]

### 4.2 Linking the two objectives (H4): early hostility → earlier exit

**Design:**
- Population: new commenters from 2013-07 to 2022-04 who are still active after their first 30 days. That's 98,670 users, of whom 59% leave before 2022-07.
- Exposures are measured in the first 30 days. Survival is counted from day 30 on, a "landmark" design that avoids immortal-time bias.
- Cox proportional hazards model, stratified by cohort. Shares are shrunk toward the population rate.

| Early-life exposure (first 30 days) | HR per SD [95% CI] | Interpretation |
|---|---|---|
| **Downvote share received** | **1.11** [1.10, 1.12] | more downvoted → leaves sooner |
| **Hostile replies received** (replier downvoted the user's comment) | **1.06** [1.05, 1.07] | more hostile replies → leaves sooner |
| Hostile replies written | 1.04 [1.03, 1.05] | being hostile also predicts leaving, weakly |
| Got any reply (yes/no) | 0.95 [0.93, 0.96] | getting a response → stays slightly longer |
| Early comments (log) | 1.23 [1.22, 1.24] | see note below |

- **Proportional hazards** holds for every covariate (Schoenfeld test, p > 0.05 on a 20k sample).
- **Robustness:** across 18 specifications (churn buffer 3/6/12 months × early window 14/30/60 days × shrinkage 2/10), HR(downvote share) ranges from 1.10 to 1.12 and HR(hostile replies received) from 1.05 to 1.08. The CI excludes 1 in **18/18** specifications for all three hostility measures.
- **Note on early activity:** users with more than 30 comments in their first month leave much faster (71% leave, median 0.95 years remaining, vs 57% and 2.35 years for users with 1–2 comments). These are probably burst, banned or sockpuppet accounts rather than engaged newcomers.

![[results/06_h4_cox.png]]

![[results/07_multiverse.png]]

---

## 5. Conclusions

1. **Replies are an antagonistic channel.**
   - Disagreement is the main reason people reply: on the same comment, repliers are far more likely to downvote it than other voters (OR 4.4).
   - It is also personal: people reply to users they are against overall, more than to others in the same discussion (+13 pp more negative relationships).
2. **Conversations escalate.** Antagonism grows with depth (OR 3.5 → 9.0), and being downvoted doubles the chance of answering back. Long threads are mostly back-and-forth between users who disagree.
3. **The fault line shapes who meets whom, not only how they interact.** Factions mostly discuss separately (23% cross-faction exposure vs 47% at random). When they do meet, the exchange is hostile in two-thirds of replies. The majority faction seeks out the minority slightly more than chance.
4. **The platform loses most newcomers quickly, and increasingly so.** Median lifetime fell from 1.4 years (2014 cohort) to 0.4 years (2020 cohort).
5. **Hostility and churn are linked.** Newcomers who receive more downvotes and hostile replies in their first month leave sooner, by about 6–11% higher hazard per SD, robust to every specification tried. Veterans are the most hostile toward newcomers (68% downvote rate), which suggests a gatekeeping dynamic.

## 6. Limitations

- **"Position" means vote-based disapproval, not measured ideology.** Faction labels exist only for 14.8k long-lived users (survivors by construction), and that partition was built from these same votes, so the faction hostility result (3.3) is partly circular.
- **Votes have no timestamps.** We can't tell whether the downvote came before or after the reply. All of Objective 1 is association, not cause.
- **H4 is observational.** Users already disengaging may attract or produce hostility, and bans can't be told apart from voluntary exits.
- **2022 data volume:** comments and votes per month drop about 45% from February 2022 while active users stay flat. This could be a collection or platform change; to check with Andreas/Emma.
- **With millions of observations, p-values are uninformative.** Conclusions rest on effect sizes and the robustness checks.

## 7. Suggested next steps

- **Bridging users** (open idea from the meeting): users who reply across factions without hostility. Who are they, and do they stay longer?
- **Escalation as a sequence:** P(hostile at depth k+1 | hostile at depth k) within a thread.
- **Separate bans from voluntary exits:** heavy-burst accounts and the 2022 volume drop.
- **Pair-level and faction results by topic:** politics vs sport. The comment-level results by topic are already in `results/04_h1_comment_level.csv`.

---

### Source tables (`results/`)

| Section | Files |
|---|---|
| 3.1 | `04_h1_comment_level.csv` |
| 3.2 | `05_h2_dyad.csv`, `05_h2_by_depth_year.csv`, `07_multiverse_h2.csv` |
| 3.3 | `05_h3_factions.csv`, `05_h3_stance_by_faction_relation.csv`, `05_h3_projected_factions.csv`, `05_projection_validation.csv` |
| 3.4 | `05_reply_back.csv` |
| 3.5 | `06_opposition_by_tenure.csv` |
| 4.1 | `06_lifetime_descriptives.csv`, `06_km_by_cohort.csv` |
| 4.2 | `06_h4_cox.csv`, `06_h4_cox_univariate.csv`, `06_h4_ph_test.csv`, `06_h4_by_early_activity.csv`, `07_multiverse_h4.csv` |
| Reply-set exclusions | `01_reply_funnel.csv` |
| Full run log | `run.log` |

## 8. Update 2026-11-02 (meeting #2 follow-ups)
Scripts `08_positive_votes.py` and `09_top_decile_lifetime.py`; h4.py gained the "friendly" (replier upvoted) features. Existing results are unchanged.

### 8.1 Positive votes (same levels as the negative ones)
- **H1:** repliers upvote the comment they answer much less. P(up | replier) = 46.7% vs 69.9% for other voters on the same comment. OR_up = 0.23 [0.23, 0.23], exactly 1 / the downvote OR (4.43), because up and down are the two halves of the same 2×2 table. It is not independent evidence (`08_h1_positive.csv`).
- **H2** (votes on the replied comment excluded; `08_h2_positive.csv`):

  | Metric | Replied-to user | Co-present null | Difference |
  |---|---|---|---|
  | Upvote share of A's votes to target | 93.1% | 95.6% | −2.5 pp [−4.0, −1.5] |
  | Mean E[p] | 0.529 | 0.587 | −5.8 pp |
  | Positive-edge share (≥5 votes) | 68.6% | 81.9% | −13.3 pp [−13.9, −12.6] |
  | Positive-edge share (FAULTANA-style) | 90.6% | 96.2% | −5.6 pp |

  Across the 24 specifications the gap is between −20.6 and −11.7 pp, negative in all 24 (`08_multiverse_h2_positive.csv`). It is the mirror image of the negative-edge result (+11.7 to +20.6 pp). People reply less to users they generally support, and more to users they are against.
- **H3 (stance by faction relation):** within the same faction A upvotes the parent in 63.0% of replies (dyad upvote share 97.5%). Across factions it is 35.4% (dyad 46.9%).
- **H4:** early *positive* exposure is mildly protective, but friendly replies add nothing once hostility is controlled for (`08_h4_positive_cox.csv`).
  - Positive-only model: upvote share received HR 0.87 per SD [0.87, 0.88]; got any reply 0.93; friendly replies received 0.99 (n.s.); friendly replies written 1.00 (n.s.).
  - Joint model: downvote share received 1.11, hostile replies received 1.06, hostile replies written 1.04 all stay > 1. Friendly replies received 1.00 and written 1.01 are n.s.
  - Reading: it is the absence of hostility that matters, not the presence of friendliness. The upvote share received is the complement of the downvote share, so it carries the same information.

### 8.2 The longest-living users (top 10% by lifetime)
Population: the H4 landmark population (98,670 commenters who entered 2013-07 to 2022-04 and were still active 30 days later). Four definitions of "long-lived" (`09_top_decile_*.csv`):
- top 10% overall: lifetime ≥ 7.35 years (9,867 users, 83% right-censored);
- top 10% within entry-year cohort (removes the "older cohorts had more time" effect; 9,870 users, all of them still active in 2022);
- more than 2 years (52%);
- more than 3 years (40%).

**Early profile (first 30 days), top 10% within cohort vs the rest:**

| | Top 10% | Rest |
|---|---|---|
| Downvote share received | 20.4% | 30.0% |
| Hostile replies received | 11.8% | 16.9% |
| Hostile replies written | 12.2% | 17.1% |
| Friendly replies received | 14.0% | 9.8% |
| Got any reply | 62.6% | 62.8% |
| Median early comments | 2 | 2 |

Long-lived users were treated and behaved less negatively from the start, with the same amount of early activity and the same chance of getting a reply. The other three definitions give the same direction.

**Early negativity predicts being long-lived** (logit with cohort fixed effects, odds ratio per SD; `09_top_decile_logit.csv`, top 10% within cohort): downvote share received 0.87 [0.85, 0.89], hostile replies received 0.94, hostile replies written 0.96. Early friendly replies received are slightly positive (1.02). For ">2 years" the pattern is the same (0.86 / 0.93 / 0.94).

**Inside the group**, early negativity barely relates to how long they stay (Spearman ρ between 0.03 and 0.07 for the within-cohort group, ≈0.02 for the overall group; `09_top_decile_within_group.csv`). The difference is between the long-lived group and the rest, not within it.

**Whole life, by tenure** (`09_top_decile_by_tenure.csv`): at every tenure the long-lived group downvotes the parent less when replying (46.6–50.3% vs 52.4–54.4%) and receives fewer hostile replies (46.5–50.2% vs 52.8–61.0%). The group's own hostility is roughly flat over time. The rest become less hostile with tenure, plausibly because the more hostile members have already left (untested).

**Caveats:** (i) lifetime is right-censored at 2022-07-01, so "top 10%" partly means "still active in 2022"; (ii) early hostility is measured after the fact for a group selected on survival, so this is association, not cause, and says nothing about bans vs voluntary exit; (iii) with N ≈ 99k, p-values carry no information, so use the effect sizes.
