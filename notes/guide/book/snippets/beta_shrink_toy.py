# (1) Beta posterior for "A votes positively on B", prior Beta(1, 2); (2) shrinkage of a share
al, be = 1, 2
print("pos neg  E[p]   edge")
for pos, neg in [(1, 3), (2, 8), (50, 50), (400, 100), (0, 1), (1, 0)]:
    e = (pos + al) / (pos + neg + al + be)
    edge = "negative" if e < 0.4 else "positive" if e > 0.6 else "none"
    print(f"{pos:3d} {neg:3d}  {e:.3f}  {edge}")

M, p = 2, 0.17      # pseudo-count and population share
print("hostile k of n  ->  shrunk share")
for k, n in [(0, 0), (1, 1), (0, 1), (5, 10), (50, 100)]:
    print(f"{k:3d} of {n:3d}      {(k + M * p) / (n + M):.3f}")
