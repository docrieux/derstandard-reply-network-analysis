"""H4 landmark dataset: early-life (first `window_days`) exposures of new commenters and their exit times."""
import numpy as np
import pandas as pd

from common import DERIVED, LEFT_CENSOR, RIGHT_CENSOR

DAY = 86400
X = ["downvote_share_recv", "hostile_reply_share_recv", "hostile_reply_share_sent", "got_any_reply", "log_comments"]


def h4_frame(con, window_days=30, right_censor=RIGHT_CENSOR, M=2):
    """Return (h, Z, info). h = raw per-user frame; Z = standardised model frame (T_years, E, cohort + X).

    Population: users whose first comment is in [2013-07-01, right_censor - 2*window) and who are still
    active at the landmark (t0 + window). Event E = last activity < right_censor.
    Shares are shrunk toward the population rate with pseudo-count M (users with no events sit at the mean).
    """
    d, W = DERIVED.as_posix(), window_days * DAY
    con.execute(f"""
    CREATE OR REPLACE TEMP TABLE pop AS
      SELECT user_id AS uid, first_comment AS t0,
             greatest(coalesce(last_comment, last_vote), coalesce(last_vote, last_comment)) AS t_last
      FROM '{d}/users.parquet'
      WHERE first_comment IS NOT NULL AND first_comment >= {LEFT_CENSOR} AND first_comment < {right_censor - 2 * W};
    CREATE OR REPLACE TEMP TABLE own AS   -- own early comments and votes received on them
      SELECT p.uid, count(*) AS n_comments, sum(c.votes_pos) AS rpos, sum(c.votes_neg) AS rneg
      FROM pop p JOIN '{d}/comments.parquet' c ON c.author_id = p.uid AND c.ts < p.t0 + {W}
      GROUP BY 1;
    CREATE OR REPLACE TEMP TABLE recv AS  -- replies received early; hostile = replier downvoted the comment
      SELECT p.uid, count(*) AS n_recv, sum((e.vote_true = -1)::INT) AS n_recv_hostile,
             sum((e.vote_true = 1)::INT) AS n_recv_friendly
      FROM pop p JOIN '{d}/edges_stance.parquet' e ON e.b = p.uid AND e.ts < p.t0 + {W}
      GROUP BY 1;
    CREATE OR REPLACE TEMP TABLE sent AS  -- replies written early; hostile = user downvoted the parent
      SELECT p.uid, count(*) AS n_sent, sum((e.vote_true = -1)::INT) AS n_sent_hostile,
             sum((e.vote_true = 1)::INT) AS n_sent_friendly
      FROM pop p JOIN '{d}/edges_stance.parquet' e ON e.a = p.uid AND e.ts < p.t0 + {W}
      GROUP BY 1;
    """)
    h = con.sql("""
      SELECT p.*, coalesce(o.n_comments, 0) AS n_comments, coalesce(o.rpos, 0) AS rpos, coalesce(o.rneg, 0) AS rneg,
             coalesce(r.n_recv, 0) AS n_recv, coalesce(r.n_recv_hostile, 0) AS n_recv_hostile, coalesce(r.n_recv_friendly, 0) AS n_recv_friendly,
             coalesce(s.n_sent, 0) AS n_sent, coalesce(s.n_sent_hostile, 0) AS n_sent_hostile, coalesce(s.n_sent_friendly, 0) AS n_sent_friendly
      FROM pop p LEFT JOIN own o USING (uid) LEFT JOIN recv r USING (uid) LEFT JOIN sent s USING (uid)""").df()
    h["cohort"] = pd.to_datetime(h.t0, unit="s").dt.year
    info = dict(n_entered=len(h), share_gone_before_landmark=(h.t_last < h.t0 + W).mean())
    h = h[h.t_last >= h.t0 + W].copy()
    h["T_years"] = (h.t_last - (h.t0 + W)) / (365.25 * DAY) + 1e-6
    h["E"] = (h.t_last < right_censor).astype(int)

    # Shrink toward the POPULATION rate: a Beta(1,1) prior put users with no replies at 0.5 and made
    # "no data" look hostile (sign flip between univariate and adjusted fits; see NOTES.md).
    def shrunk(k, n):
        return (k + M * k.sum() / n.sum()) / (n + M)

    h["downvote_share_recv"] = shrunk(h.rneg, h.rpos + h.rneg)
    h["hostile_reply_share_recv"] = shrunk(h.n_recv_hostile, h.n_recv)
    h["hostile_reply_share_sent"] = shrunk(h.n_sent_hostile, h.n_sent)
    # positive-vote mirrors (friendly = replier upvoted the comment); not part of X, used by 08/09
    h["upvote_share_recv"] = shrunk(h.rpos, h.rpos + h.rneg)
    h["friendly_reply_share_recv"] = shrunk(h.n_recv_friendly, h.n_recv)
    h["friendly_reply_share_sent"] = shrunk(h.n_sent_friendly, h.n_sent)
    h["got_any_reply"] = (h.n_recv > 0).astype(int)
    h["log_comments"] = np.log1p(h.n_comments)  # (n distinct articles dropped: r = 0.95 with this)
    Z = h[X + ["T_years", "E", "cohort"]].copy()
    for c in X:
        if c != "got_any_reply":
            Z[c] = (Z[c] - Z[c].mean()) / Z[c].std()
    info.update(n_landmark=len(Z), event_share=Z.E.mean())
    return h, Z, info
