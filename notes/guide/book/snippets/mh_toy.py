# Mantel-Haenszel by hand. One 2x2 table per comment:
# a = replier downvoted, b = replier upvoted, c = other voter downvoted, d = other voter upvoted
tables = {"X": (6, 2, 24, 16), "Y": (1, 9, 4, 36)}

R = S = 0.0
A = B = C = D = 0
for name, (a, b, c, d) in tables.items():
    n = a + b + c + d
    R += a * d / n          # numerator term of this comment
    S += b * c / n          # denominator term of this comment
    A, B, C, D = A + a, B + b, C + c, D + d
    print(name, "odds ratio inside this comment:", a * d / (b * c))

print("crude OR (tables stacked):", round(A * D / (B * C), 2))
print("Mantel-Haenszel OR      :", round(R / S, 2))
