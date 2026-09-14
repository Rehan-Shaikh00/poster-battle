"""Light-theme charts for the standard-layout TREMORWATCH poster (navy/white).
Writes to poster-standard/charts/. Uses the cached data in ../code/."""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, "charts")
os.makedirs(CH, exist_ok=True)
CODE = os.path.abspath(os.path.join(HERE, "..", "code"))

# corporate palette: navy + white + brand accents
NAVY, NAVY2 = "#0b2545", "#13315c"
INK, MUTED = "#1d3557", "#5b7083"
GRIDC = "#d9e2ec"
ORANGE, CYAN, RED, GREEN = "#ff8c42", "#219ebc", "#e63946", "#2a9d8f"
BGW = "#ffffff"

plt.rcParams.update({
    "figure.facecolor": BGW, "axes.facecolor": BGW, "axes.edgecolor": GRIDC,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "grid.color": GRIDC, "grid.linewidth": 0.6,
    "font.size": 10.5, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlecolor": NAVY, "savefig.facecolor": BGW,
    "font.family": "DejaVu Sans",
})

# ---------------------------------------------------------------- data
gj = json.load(open(os.path.join(CODE, "usgs_all_month.geojson"), encoding="utf-8"))
rows = []
for f in gj["features"]:
    p, g = f["properties"], f["geometry"]["coordinates"]
    rows.append(dict(mag=p.get("mag"), depth=g[2], lat=g[1], lon=g[0],
                     place=p.get("place", "")))
df = pd.DataFrame(rows).dropna(subset=["mag"])
df["y"] = (df["mag"] >= 5.0).astype(int)
df["c_lat"] = np.floor(df["lat"] / 5).astype(int)
df["c_lon"] = np.floor(df["lon"] / 5).astype(int)
w = json.load(open(os.path.join(CODE, "world_110m.geojson"), encoding="utf-8"))

def draw_coast(ax, fill="#e8edf3", edge="#9db2c8"):
    for feat in w["features"]:
        gm = feat["geometry"]
        polys = gm["coordinates"] if gm["type"] == "MultiPolygon" else [gm["coordinates"]]
        for poly in polys:
            for ring in poly:
                a = np.array(ring)
                ax.fill(a[:, 0], a[:, 1], color=fill, zorder=1)
                ax.plot(a[:, 0], a[:, 1], color=edge, lw=0.4, zorder=1)

# ---------------------------------------------------------------- 1. process diagram
steps = [
    ("1  INGEST",   "USGS live global feed — every event, GeoJSON, no API key"),
    ("2  EXPLORE",  "EDA — Gutenberg–Richter (b = 1.15), depth, rates, hotspots"),
    ("3  ZONE",     "5° grid risk map — P(M ≥ 5.0) per zone, min 15 events"),
    ("4  TRIAGE",   "Random Forest scores each event, walk-forward CV, < 1 s"),
    ("5  RESPOND",  "Ranked alerts → dispatch, sheltering, resource planning"),
]
fig, ax = plt.subplots(figsize=(9.8, 6.4), dpi=200)
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
n = len(steps)
top_edge, box_h = 9.6, 1.52
gap = (9.6 - 0.4 - n * box_h) / (n - 1)
for i, (title, desc) in enumerate(steps):
    y = top_edge - i * (box_h + gap)
    col = NAVY if i < 4 else ORANGE
    ax.add_patch(FancyBboxPatch((0.55, y - box_h), 8.9, box_h,
                 boxstyle="round,pad=0.06,rounding_size=0.18",
                 fc=col, ec="none", zorder=3))
    ax.text(5.0, y - 0.42, title, ha="center", va="center",
            color="white", fontsize=12.5, fontweight="bold", zorder=4)
    ax.text(5.0, y - 1.0, desc, ha="center", va="center",
            color="white", fontsize=8.6, zorder=4, alpha=0.95)
    if i < n - 1:
        ay = y - box_h - 0.12
        ax.add_patch(FancyArrowPatch((5.0, ay), (5.0, ay - gap + 0.12),
                     arrowstyle="-|>", mutation_scale=16,
                     color=ORANGE, lw=2.0, zorder=3))
ax.set_title("Response pipeline — data in, decisions out", pad=14)
fig.tight_layout()
fig.savefig(os.path.join(CH, "process_diagram.png"), bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 2. risk map (light)
cell = df.groupby(["c_lat", "c_lon"]).agg(n=("mag", "size"), sig=("y", "sum"))
cell["p"] = cell["sig"] / cell["n"]
cell = cell[cell["n"] >= 15]
ramp = [("#d7f0e8", 0.0), ("#ffd166", 0.45), ("#ff8c42", 0.72), ("#e63946", 1.0)]
def zone_col(p, pmax):
    t = max(0.02, p / pmax)
    for i in range(1, len(ramp)):
        c, th = ramp[i]
        if t <= th:
            return c
    return ramp[-1][0]

fig, ax = plt.subplots(figsize=(11.4, 5.2), dpi=200)
draw_coast(ax)
pmax = cell["p"].max()
for (cla, clo), r in cell.iterrows():
    ax.add_patch(plt.Rectangle((clo * 5, cla * 5), 5, 5,
               facecolor=zone_col(r["p"], pmax), edgecolor="white", lw=0.7,
               alpha=0.55 + 0.4 * min(r["n"] / 150, 1), zorder=2))
ax.scatter(df["lon"], df["lat"], s=2.2, c=NAVY, alpha=0.30, zorder=3)
from matplotlib.patches import Patch
leg = ax.legend(handles=[
    Patch(fc="#d7f0e8", label="low risk"), Patch(fc="#ffd166", label="elevated"),
    Patch(fc="#ff8c42", label="high"), Patch(fc="#e63946", label="highest"),
    Patch(fc=NAVY, label="all events")],
    loc="lower left", fontsize=8.5, frameon=True, edgecolor=GRIDC,
    facecolor="white", bbox_to_anchor=(0.005, 0.02))
leg.set_title("P(M ≥ 5.0) per 5° zone")
leg.get_title().set_fontsize(8.5)
leg.get_title().set_color(INK)
ax.set_xlim(-180, 180); ax.set_ylim(-62, 75); ax.set_aspect("equal")
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_color(GRIDC)
ax.set_title("Seismic risk zones — where significant (M ≥ 5.0) events concentrate",
             pad=10, fontsize=12.5)
fig.tight_layout()
fig.savefig(os.path.join(CH, "risk_map_light.png"), bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 3. magnitude bands
mbins = [2, 3, 4, 5, 6, 7, 8]
mlabel = ["2–3", "3–4", "4–5", "5–6", "6–7", "7–8"]
mcol = [NAVY2, NAVY2, "#486581", ORANGE, RED, "#9d0208"]
counts, _ = np.histogram(df["mag"], bins=mbins)
fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=200)
bars = ax.bar(mlabel, counts, color=mcol, edgecolor="white", width=0.74)
for b, v in zip(bars, counts):
    ax.text(b.get_x() + b.get_width() / 2, v + max(counts) * 0.02,
            f"{v:,}", ha="center", fontsize=9, color=INK)
ax.set_title("Events by magnitude band", pad=10)
ax.set_xlabel("Magnitude band (Mw)"); ax.set_ylabel("Events")
ax.set_ylim(0, max(counts) * 1.16)
ax.grid(alpha=0.5, axis="y")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(CH, "mag_bands_light.png"), bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 4. risk-zone bars
top = cell.sort_values("p", ascending=False).head(6)
labels, vals = [], []
for (cla, clo), r in top.iterrows():
    sub = df[(df["c_lat"] == cla) & (df["c_lon"] == clo)]
    m = sub["place"].str.extract(r",\s*([A-Z][A-Za-z .&'-]{2,40})$")[0].dropna()
    labels.append((m.mode()[0] if len(m) else "Open ocean") + f"  (n={int(r['n'])})")
    vals.append(float(r["p"]))
vals = np.array(vals)
fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=200)
ypos = np.arange(len(labels))[::-1]
ax.barh(ypos, vals, color=[zone_col(v, pmax) for v in vals],
        edgecolor="white", height=0.62)
for y, v in zip(ypos, vals):
    ax.text(v + 0.004, y, f"{v:.3f}", va="center", fontsize=9, color=INK)
ax.set_yticks(ypos); ax.set_yticklabels(labels, fontsize=9)
ax.set_xlim(0, max(vals) * 1.22)
ax.set_title("P(M ≥ 5.0) — top risk zones", pad=10)
ax.grid(alpha=0.5, axis="x")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(CH, "risk_zones_bars_light.png"), bbox_inches="tight")
plt.close(fig)

print("charts written to", CH)
for f in sorted(os.listdir(CH)):
    print("  ", f, os.path.getsize(os.path.join(CH, f)) // 1024, "KB")
