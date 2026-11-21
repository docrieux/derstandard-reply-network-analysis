"""Matplotlib style for static thesis figures (reference palette, light mode)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OBS = "#2a78d6"  # observed / real reply edges (categorical slot 1)
ALT = "#eb6834"  # second series when needed (slot 2)
NULL = "#9a9890"  # null / reference baseline (neutral)
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.axisbelow": True,
    "lines.linewidth": 2, "lines.markersize": 6, "font.size": 10, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False,
    "figure.dpi": 110, "savefig.dpi": 160, "savefig.bbox": "tight",
})
