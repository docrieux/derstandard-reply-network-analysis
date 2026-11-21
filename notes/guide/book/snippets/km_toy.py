# Kaplan-Meier by hand. (time in years, 1 = left / 0 = still active when observation ended)
data = [(1, 1), (2, 1), (2, 0), (4, 1), (5, 0), (6, 0)]

S = 1.0
for t in sorted({t for t, left in data if left}):
    at_risk = sum(1 for u, _ in data if u >= t)
    leaving = sum(1 for u, left in data if u == t and left)
    S *= 1 - leaving / at_risk
    print(f"t={t}: at risk {at_risk}, leave {leaving}, S(t) = {S:.3f}")
