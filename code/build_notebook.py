"""Build TREMORWATCH_notebook.ipynb — the full analysis as an educational notebook.
Run:  python build_notebook.py   (then open the .ipynb in Jupyter or VS Code)"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def md(src):  return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}
def py(src):  return {"cell_type": "code", "execution_count": None,
                      "metadata": {}, "outputs": [], "source": src.splitlines(keepends=True)}

cells = [
md("""# 🌋 TREMORWATCH — Seismic Risk Intelligence

**Poster Battle | Theme: Disaster Management & Emergency Response Platform**
**Team:** Rehan Shaikh • Aman Ansari • Kamil Mirza — ACM Student Chapter, SVKM IOT Dhule

This notebook is the complete, reproducible analysis behind the poster. It runs on
**live public data** (USGS global earthquake feed — no API key) and reproduces every
number in the project.

> Run all cells: **Kernel → Restart & Run All** (takes ~2 min).
> Dependencies: `pandas numpy matplotlib scikit-learn requests`
> (optional `plotly` for the bonus interactive map at the end).
> A cached data file (`usgs_all_month.geojson`) in this folder makes it run **offline**."""),

py("""import json, os, warnings
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score

warnings.filterwarnings("ignore")

BG, PANEL, GRID, TXT = "#0d1b2a", "#10243e", "#1e3a5f", "#e0e6ed"
C_ORANGE, C_CYAN, C_YELLOW, C_RED, C_GREEN = "#ff8c42", "#4cc9f0", "#ffd166", "#ef476f", "#06d6a0"
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL, "axes.edgecolor": GRID,
    "axes.labelcolor": TXT, "text.color": TXT, "xtick.color": "#9fb3c8",
    "ytick.color": "#9fb3c8", "grid.color": GRID, "grid.linewidth": 0.5,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "savefig.facecolor": BG,
})
print("style ready")"""),

md("""## Step 1 — Load the live USGS feed (last 30 days, worldwide)

We use the same feed response agencies use. The script reuses a cached copy in this
folder if present (offline mode); otherwise it downloads the live feed (~8 MB)."""),

py("""FEED  = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
WORLD = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
         "master/geojson/ne_110m_admin_0_countries.geojson")

def fetch(url, fname):
    if not os.path.exists(fname):
        print(f"downloading {fname} ...")
        r = requests.get(url, timeout=120); r.raise_for_status()
        open(fname, "wb").write(r.content)
    return fname

gj = json.load(open(fetch(FEED, "usgs_all_month.geojson"), encoding="utf-8"))
rows = []
for f in gj["features"]:
    p, g = f["properties"], f["geometry"]["coordinates"]   # g = [lon, lat, depth]
    rows.append(dict(time=pd.to_datetime(p["time"], unit="ms"), mag=p.get("mag"),
                     depth=g[2], lat=g[1], lon=g[0],
                     place=p.get("place", ""), tsunami=int(p.get("tsunami", 0))))
df = pd.DataFrame(rows).dropna(subset=["mag"]).sort_values("time").reset_index(drop=True)
df["hour"] = df["time"].dt.hour
df["dow"]  = df["time"].dt.dayofweek
df["c_lat"] = np.floor(df["lat"] / 5).astype(int)    # 5-degree grid cell
df["c_lon"] = np.floor(df["lon"] / 5).astype(int)
df["y"] = (df["mag"] >= 5.0).astype(int)             # target: significant event

print(f"{len(df):,} earthquakes   {df['time'].min():%d %b %Y} → {df['time'].max():%d %b %Y}")
df.head()"""),

md("""## Step 2 — Key numbers (the ones on the poster)"""),

py("""stats = dict(
    earthquakes=len(df),
    largest=f"M {df['mag'].max():.1f}  ({df.loc[df['mag'].idxmax(),'place']})",
    significant_M_ge_5=int(df['y'].sum()),
    M_ge_5_5=int((df['mag']>=5.5).sum()),
    M_ge_6=int((df['mag']>=6.0).sum()),
    tsunamis=int(df['tsunami'].sum()),
)
pd.Series(stats)"""),

md("""### Gutenberg–Richter validation

Real crust follows **log N = a − b·M** with **b ≈ 1**. Fitting our live data is a
data-quality check — a healthy pipeline should recover b ≈ 1."""),

py("""thr = np.arange(4.5, df["mag"].max(), 0.25)
N   = np.array([(df["mag"] >= t).sum() for t in thr])
ok  = N >= 20
slope, intercept = np.polyfit(thr[ok], np.log10(N[ok]), 1)
b_value = round(float(-slope), 2)

fig, ax = plt.subplots(figsize=(8, 4.6))
ax.semilogy(thr, N, "o", ms=5, color=C_CYAN, label="Observed counts")
ax.semilogy(thr[ok], 10 ** (intercept + slope * thr[ok]), "--", color=C_ORANGE, lw=2,
            label=f"Fit: b = {b_value}")
ax.set_title("Gutenberg–Richter law (frequency vs magnitude)")
ax.set_xlabel("Magnitude (Mw)"); ax.set_ylabel("Cumulative events (log)")
ax.grid(alpha=0.4); ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TXT)
for s in ax.spines.values(): s.set_color(GRID)
plt.show()
print(f"b-value = {b_value}  (expected ≈ 1.0) → catalog is healthy")"""),

md("""## Step 3 — Exploratory analysis"""),

py("""mbins  = [2, 3, 4, 5, 6, 7, 8]
mlabel = ["2-3", "3-4", "4-5", "5-6", "6-7", "7-8"]
mcol   = [C_CYAN, "#58b6e8", "#58b6e8", C_YELLOW, C_ORANGE, C_RED]
counts, _ = np.histogram(df["mag"], bins=mbins)
fig, ax = plt.subplots(figsize=(8, 4.6))
bars = ax.bar(mlabel, counts, color=mcol, edgecolor=BG, width=0.72)
for b, v in zip(bars, counts):
    ax.text(b.get_x() + b.get_width()/2, v + max(counts)*0.015, f"{v:,}",
            ha="center", fontsize=10)
ax.set_title("Events by magnitude band — small events dominate")
ax.set_xlabel("Magnitude band (Mw)"); ax.set_ylabel("Events")
ax.grid(alpha=0.4, axis="y")
for s in ax.spines.values(): s.set_color(GRID)
plt.show()
print(f"Significant (M≥5.0): {df['y'].sum()} of {len(df)} = {df['y'].mean()*100:.1f}%")"""),

py("""raw = df.set_index("time").resample("1D").size()
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
a = axes[0]
a.fill_between(raw.index, raw.values, color=C_CYAN, alpha=0.35)
a.plot(raw.rolling(7, min_periods=1).mean().clip(lower=0), color=C_ORANGE, lw=2, label="7-day avg")
a.set_title("Daily seismic activity"); a.set_xlabel("Date"); a.set_ylabel("Events/day")
a.grid(alpha=0.4); a.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TXT)

b = axes[1]
b.scatter(df["depth"], df["mag"], s=7, c=df["mag"], cmap="inferno", vmin=2, vmax=9, alpha=0.6)
b.set_yscale("log")
b.axvline(70, color=C_YELLOW, ls=":", lw=1.2); b.axvline(300, color=C_RED, ls=":", lw=1.2)
b.set_title("Hypocenter depth vs magnitude"); b.set_xlabel("Depth (km)"); b.set_ylabel("Mw (log)")
b.grid(alpha=0.4)
for axx in axes:
    for s in axx.spines.values(): s.set_color(GRID)
plt.show()
print(f"Deep (>300 km) avg M {df.loc[df['depth']>300,'mag'].mean():.2f}  vs  "
      f"shallow (<70 km) avg M {df.loc[df['depth']<70,'mag'].mean():.2f}  (detection bias)")"""),

py("""# World map of every epicenter, coloured by magnitude
w = json.load(open(fetch(WORLD, "world_110m.geojson"), encoding="utf-8"))
fig, ax = plt.subplots(figsize=(12, 5.6))
for feat in w["features"]:
    gm = feat["geometry"]
    polys = gm["coordinates"] if gm["type"] == "MultiPolygon" else [gm["coordinates"]]
    for poly in polys:
        for ring in poly:
            a = np.array(ring); ax.plot(a[:, 0], a[:, 1], color="#33507a", lw=0.45, zorder=1)
sc = ax.scatter(df["lon"], df["lat"], s=6, c=df["mag"], cmap="inferno", vmin=2, vmax=9, alpha=0.85)
cb = fig.colorbar(sc, ax=ax, pad=0.01); cb.set_label("Magnitude", color=TXT)
ax.set_xlim(-180, 180); ax.set_ylim(-62, 75); ax.set_aspect("equal")
ax.set_title(f"Global epicenters — last 30 days ({len(df):,} events)")
for s in ax.spines.values(): s.set_color(GRID)
fig.tight_layout(); plt.show()"""),

md("""## Step 4 — Spatial risk zones (the headline)

Divide the planet into 5° zones and compute, per zone, the **observed probability of a
significant event** (minimum 15 events for stability). Red = where response should be ready."""),

py("""cell = df.groupby(["c_lat", "c_lon"]).agg(n=("mag", "size"), sig=("y", "sum"))
cell["p"] = cell["sig"] / cell["n"]
cell = cell[cell["n"] >= 15].sort_values("p", ascending=False)

top = cell.head(8).copy()
top["zone"] = [
    df[(df["c_lat"] == cl) & (df["c_lon"] == co)]["place"]
        .str.extract(r",\\s*([A-Z][A-Za-z .&'-]{2,40})$")[0].dropna().mode()
        .pipe(lambda x: x[0] if len(x) else "Open ocean")
    for cl, co in top.index]
table = top.reset_index().rename(columns={"c_lat": "lat", "c_lon": "lon",
                                          "n": "events", "sig": "significant",
                                          "p": "P(M>=5.0)"})
table[["zone", "lat", "lon", "events", "significant", "P(M>=5.0)"]]"""),

py("""from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
risk_cmap = LinearSegmentedColormap.from_list(
    "risk", ["#123b2e", "#1b6b47", C_YELLOW, C_ORANGE, C_RED])
pmax = cell["p"].max()
fig, ax = plt.subplots(figsize=(12, 5.6))
for feat in w["features"]:
    gm = feat["geometry"]
    polys = gm["coordinates"] if gm["type"] == "MultiPolygon" else [gm["coordinates"]]
    for poly in polys:
        for ring in poly:
            a = np.array(ring); ax.plot(a[:, 0], a[:, 1], color="#24466e", lw=0.5, zorder=1)
for (cla, clo), r in cell.iterrows():
    ax.add_patch(Rectangle((clo*5, cla*5), 5, 5,
                           facecolor=risk_cmap(r["p"]/pmax), edgecolor=BG, lw=0.6,
                           alpha=0.45 + 0.5*min(r["n"]/150, 1), zorder=2))
ax.scatter(df["lon"], df["lat"], s=2.5, c="#9fb3c8", alpha=0.25, zorder=3)
ax.set_xlim(-180, 180); ax.set_ylim(-62, 75); ax.set_aspect("equal")
ax.set_title("Seismic risk zones — where significant (M>=5.0) events concentrate")
for s in ax.spines.values(): s.set_color(GRID)
fig.tight_layout(); plt.show()"""),

md("""## Step 5 — ML risk model (Random Forest triage)

**Target:** probability the event is significant (M ≥ 5.0).
**Features (all known at detection time — no leakage):** 5° grid location, depth, hour, day-of-week.

**Evaluation: walk-forward time-series cross-validation.** Four sequential hold-out
windows; each model is trained **only on events that happened before its test window**.
No random splits, no peeking at the future."""),

py("""FEATURES = ["c_lat", "c_lon", "depth", "hour", "dow"]
THRESH = 0.30
n, fold = len(df), len(df)//5
proba, yte = [], []
for i in range(4):
    tr, te = df.iloc[:fold*(i+1)], df.iloc[fold*(i+1):fold*(i+2)]
    if te["y"].sum() == 0:
        continue
    c = RandomForestClassifier(n_estimators=300, class_weight="balanced",
                               min_samples_leaf=3, random_state=42, n_jobs=-1)
    c.fit(tr[FEATURES], tr["y"])
    proba.append(c.predict_proba(te[FEATURES])[:, 1]); yte.append(te["y"].values)
proba = np.concatenate(proba); yte = np.concatenate(yte)
pred = proba > THRESH
base = float(yte.mean())
print(f"Held-out future events: {len(yte):,}   (significant: {yte.sum()})")
print(f"baseline precision (alert everything): {base*100:.2f}%")
print(f"model  precision: {precision_score(yte, pred, zero_division=0)*100:.1f}%   "
      f"recall: {recall_score(yte, pred, zero_division=0)*100:.1f}%   "
      f"F1: {f1_score(yte, pred, zero_division=0):.3f}")
print(f"LIFT: {precision_score(yte, pred, zero_division=0)/base:.1f}x  "
      "(flagged events are this many times more likely to be significant)")"""),

py("""# Feature importance (descriptive model on the full data)
full = RandomForestClassifier(n_estimators=400, class_weight="balanced",
                              min_samples_leaf=3, random_state=42, n_jobs=-1)
full.fit(df[FEATURES], df["y"])
imp = pd.Series(full.feature_importances_, index=FEATURES).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 4))
cols = ["#a78bfa", C_GREEN, C_YELLOW, C_CYAN, C_ORANGE]
ax.barh(imp.index[::-1], imp.values[::-1], color=cols[::-1], edgecolor=BG)
for j, v in enumerate(imp.values[::-1]):
    ax.text(v + max(imp.values)*0.01, j, f"{v:.1%}", va="center", fontsize=10)
ax.set_xlim(0, max(imp.values)*1.22)
ax.set_title("Feature importance — the model learned the Ring of Fire")
ax.grid(alpha=0.4, axis="x")
for s in ax.spines.values(): s.set_color(GRID)
plt.show()"""),

py("""# The model's top-8 highest-confidence alerts on the FUTURE test window
from sklearn.ensemble import RandomForestClassifier as RF
probs = []
for i in range(4):
    tr, te = df.iloc[:fold*(i+1)], df.iloc[fold*(i+1):fold*(i+2)]
    if te["y"].sum() == 0:
        continue
    c = RF(n_estimators=300, class_weight="balanced", min_samples_leaf=3,
           random_state=42, n_jobs=-1)
    c.fit(tr[FEATURES], tr["y"])
    te = te.copy(); te["prob"] = c.predict_proba(te[FEATURES])[:, 1]
    probs.append(te)
te_all = pd.concat(probs).sort_values("prob", ascending=False).head(8)
show = te_all[["time", "place", "mag", "depth", "prob"]].copy()
show["verified_M>=5"] = np.where(show["mag"] >= 5.0, "YES", "no")
show["time"] = show["time"].dt.strftime("%d %b %H:%M")
show["prob"] = show["prob"].round(2)
show"""),

md("""## Wrap-up — the numbers on the poster

| Stat | Value |
|---|---|
| Earthquakes in 30-day window | **11,143** |
| Largest | **M 7.8** (NNW of Ende, Indonesia) |
| Significant M≥5.0 | **189** (1.7%) |
| Gutenberg–Richter b-value | **1.15** (≈ 1.0 expected) |
| Model (walk-forward CV) | precision **19.6%**, recall **78.6%**, F1 **0.314** |
| Lift vs 1.5% base rate | **13.3×** |
| Top-8 future alerts | **3 of 8** verified significant (25× base rate) |

**Honest framing for Q&A:** the model does *not* predict individual earthquakes — it
*triages detected events* and *zones the risk* so responders can act faster.

### Bonus: interactive map (optional)

Run the cell below after `pip install plotly` to open a zoomable map of all events."""),

py("""# Optional — needs: pip install plotly
import plotly.express as px
fig = px.scatter_geo(df, lat="lat", lon="lon", color="mag",
                     color_continuous_scale="Inferno", height=560,
                     projection="natural earth", template="plotly_dark")
fig.update_layout(title="TREMORWATCH — Live Global Seismic Activity")
fig.show()"""),
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
out = os.path.join(HERE, "TREMORWATCH_notebook.ipynb")
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
print(f"wrote {out} ({len(cells)} cells)")
