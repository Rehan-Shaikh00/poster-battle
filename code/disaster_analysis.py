# ============================================================================
#  TREMORWATCH — Disaster Management & Emergency Response Platform
#  Technical Poster Battle  |  ACM Student Chapter, S V K M's IOT Dhule
#
#  Run:   python disaster_analysis.py
#  Deps:  pip install pandas numpy matplotlib scikit-learn requests
#          (optional) pip install plotly   -> adds an interactive map
# ----------------------------------------------------------------------------
#  WHAT THIS SCRIPT DOES
#   1. Downloads the LIVE USGS global earthquake feed (last 30 days, free,
#      no API key)  + a lightweight world coastline file.
#   2. Exploratory analysis:
#        - magnitude distribution + Gutenberg-Richter b-value
#        - daily seismic activity rate
#        - depth vs magnitude
#        - hotspot regions
#   3. HEADLINE VISUAL: a spatial RISK ZONE map. For every 5-degree grid
#      cell it computes the observed probability of a significant
#      (M >= 5.0) event -> "where should emergency resources be ready?"
#   4. ML RISK MODEL (Random Forest) that ranks each detected event by the
#      probability it is significant (M >= 5.0).
#        - features known at detection time: grid location, depth,
#          time-of-day, day-of-week  (NO leakage: magnitude/target excluded)
#        - evaluated with WALK-FORWARD time-series cross-validation
#          (5 folds: train on the past, test only on the future -> no
#           data leakage) and a fixed decision threshold.
#   5. Saves every chart to output/*.png, all numbers to output/metrics.json,
#      and prints a clean summary you can lift straight into the poster.
# ============================================================================
import json, os, warnings
import numpy as np
import pandas as pd
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score

warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------------
# 0.  Paths, style, sources
# ----------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "output")
os.makedirs(OUT, exist_ok=True)

FEED  = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
WORLD = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
         "master/geojson/ne_110m_admin_0_countries.geojson")

BG, PANEL, GRID, TXT = "#0d1b2a", "#10243e", "#1e3a5f", "#e0e6ed"
C_ORANGE, C_CYAN, C_YELLOW, C_RED, C_GREEN = "#ff8c42", "#4cc9f0", "#ffd166", "#ef476f", "#06d6a0"
DPI = 150

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL, "axes.edgecolor": GRID,
    "axes.labelcolor": TXT, "text.color": TXT, "xtick.color": "#9fb3c8",
    "ytick.color": "#9fb3c8", "grid.color": GRID, "grid.linewidth": 0.5,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "savefig.facecolor": BG, "savefig.dpi": DPI,
})

def fetch(url, fname):
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f"  downloading {fname} ...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    return path

def style_ax(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, pad=10)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.grid(alpha=0.4)
    for s in ax.spines.values(): s.set_color(GRID)

def region_label(place_series):
    """Extract the trailing country name from a USGS 'place' string."""
    m = place_series.str.extract(r",\s*([A-Z][A-Za-z .&'-]{2,40})$")
    m = m[0].dropna()
    return m.mode()[0] if len(m) else "(open ocean / remote)"

# ----------------------------------------------------------------------------
# 1.  Load + parse the live USGS feed
# ----------------------------------------------------------------------------
print("[1/6] Loading live USGS earthquake feed (last 30 days, worldwide) ...")
gj = json.load(open(fetch(FEED, "usgs_all_month.geojson")))
rows = []
for f in gj["features"]:
    p, g = f["properties"], f["geometry"]["coordinates"]   # g = [lon, lat, depth]
    rows.append(dict(
        time=pd.to_datetime(p["time"], unit="ms"), mag=p.get("mag"),
        depth=g[2], lat=g[1], lon=g[0],
        place=p.get("place", ""), tsunami=int(p.get("tsunami", 0)),
    ))
df_all = pd.DataFrame(rows)
df = df_all.dropna(subset=["mag"]).sort_values("time").reset_index(drop=True)
df["date"] = df["time"].dt.date

n_total  = len(df_all); n_used = len(df)
max_mag  = df["mag"].max(); max_ev = df.loc[df["mag"].idxmax(), "place"]
n_ge55   = int((df["mag"] >= 5.5).sum()); n_ge60 = int((df["mag"] >= 6.0).sum())
n_tsum   = int(df["tsunami"].sum())
d_min, d_max = df["time"].min().strftime("%d %b %Y"), df["time"].max().strftime("%d %b %Y")
print(f"      {n_total:,} events ({n_used:,} with magnitude)   {d_min} -> {d_max}")
print(f"      largest: M{max_mag:.1f}  ({max_ev})")

# features used by the model (all available at detection time)
df["hour"] = df["time"].dt.hour
df["dow"]  = df["time"].dt.dayofweek
df["c_lat"] = np.floor(df["lat"] / 5).astype(int)     # 5-degree grid cell
df["c_lon"] = np.floor(df["lon"] / 5).astype(int)
SIGNIFICANT = 5.0
df["y"] = (df["mag"] >= SIGNIFICANT).astype(int)
FEATURES = ["c_lat", "c_lon", "depth", "hour", "dow"]
THRESH = 0.30

# daily rate + Gutenberg-Richter + hotspots + depth bands
raw_daily = df.set_index("time").resample("1D").size()
daily_avg = raw_daily.rolling(7, min_periods=1).mean().clip(lower=0)
thr = np.arange(4.5, max_mag, 0.25)
N_cum = np.array([(df["mag"] >= t).sum() for t in thr])
ok = N_cum >= 20
slope, intercept = np.polyfit(thr[ok], np.log10(N_cum[ok]), 1)
b_value = round(float(-slope), 2)
place_cty = df["place"].str.extract(r",\s*([A-Z][A-Za-z .&'-]{2,40})$")[0]
top_regions = (place_cty.value_counts().head(6)
               .rename_axis("region").reset_index(name="events").to_dict("records"))
bands = pd.cut(df["depth"], [0, 70, 300, 999],
               labels=["Shallow (<70 km)", "Intermediate (70-300 km)", "Deep (>300 km)"])
depth_tab = (df.assign(band=bands).groupby("band", observed=True)
               .agg(events=("mag", "size"), mean_mag=("mag", "mean"),
                    max_mag=("mag", "max")).round(2).reset_index()
               .to_dict("records"))

# ----------------------------------------------------------------------------
# 2.  EDA charts
# ----------------------------------------------------------------------------
print("[2/6] Rendering charts ...")

# --- (a) world map of all epicenters ----------------------------------------
fig, ax = plt.subplots(figsize=(12, 5.6))
w = json.load(open(fetch(WORLD, "world_110m.geojson")))
for feat in w["features"]:
    gm = feat["geometry"]
    polys = gm["coordinates"] if gm["type"] == "MultiPolygon" else [gm["coordinates"]]
    for poly in polys:
        for ring in poly:
            a = np.array(ring); ax.plot(a[:, 0], a[:, 1], color="#33507a", lw=0.45, zorder=1)
sc = ax.scatter(df["lon"], df["lat"], s=6, c=df["mag"], cmap="inferno",
                vmin=2, vmax=9, alpha=0.85, zorder=2)
cb = fig.colorbar(sc, ax=ax, pad=0.01); cb.set_label("Magnitude", color=TXT)
cb.outline.set_edgecolor(GRID); cb.ax.tick_params(colors="#9fb3c8")
ax.set_xlim(-180, 180); ax.set_ylim(-62, 75); ax.set_aspect("equal")
ax.set_xlabel(""); ax.set_ylabel("")
ax.set_title(f"Global Epicenters - last 30 days  ({n_used:,} events, live USGS feed)", pad=10)
for s in ax.spines.values(): s.set_color(GRID)
ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "epicenter_map.png")); plt.close(fig)

# --- (b) events by magnitude band ---------------------------------------------
mbins  = [2, 3, 4, 5, 6, 7, 8]
mlabel = ["2-3", "3-4", "4-5", "5-6", "6-7", "7-8"]
mcol   = [C_CYAN, "#58b6e8", "#58b6e8", C_YELLOW, C_ORANGE, C_RED]
counts, _ = np.histogram(df["mag"], bins=mbins)
fig, ax = plt.subplots(figsize=(6.2, 4.3))
bars = ax.bar(mlabel, counts, color=mcol, edgecolor=BG, width=0.72)
for b, v in zip(bars, counts):
    ax.text(b.get_x() + b.get_width()/2, v + max(counts)*0.015, f"{v:,}",
            ha="center", fontsize=9.5, color=TXT)
ymax = max(counts)
ax.annotate(f"significant  M>={SIGNIFICANT:.0f}:  {int(df['y'].sum())} events\n"
            f"({df['y'].mean()*100:.1f}% of all)",
            xy=(3.0, ymax*0.9), ha="center", fontsize=9, color=C_YELLOW,
            bbox=dict(boxstyle="round,pad=0.3", fc=PANEL, ec=C_YELLOW, lw=0.8))
style_ax(ax, "Events by Magnitude Band  (small events dominate)",
         "Magnitude band (Mw)", "Events")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "mag_distribution.png")); plt.close(fig)

# --- (c) Gutenberg-Richter ----------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.3))
ax.semilogy(thr, N_cum, "o", ms=4, color=C_CYAN, label="Observed counts")
ax.semilogy(thr[ok], 10 ** (intercept + slope * thr[ok]), "--", color=C_ORANGE, lw=1.6,
            label=f"Fit  log N = a - b.M   (b = {b_value})")
style_ax(ax, "Gutenberg-Richter  (frequency vs magnitude)",
         "Magnitude (Mw)", "Cumulative events (log)")
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TXT, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "gutenberg_richter.png")); plt.close(fig)

# --- (d) daily rate ------------------------------------------------------------
import matplotlib.dates as mdates
fig, ax = plt.subplots(figsize=(6.2, 3.9))
ax.fill_between(raw_daily.index, raw_daily.values, color=C_CYAN, alpha=0.35)
ax.plot(daily_avg.index, daily_avg.values, color=C_ORANGE, lw=1.8, label="7-day avg")
ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
style_ax(ax, "Daily Seismic Activity (30-day window)", "Date", "Events / day")
ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TXT, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "daily_rate.png")); plt.close(fig)

# --- (e) depth vs magnitude ----------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.3))
ax.scatter(df["depth"], df["mag"], s=6, c=df["mag"], cmap="inferno",
           vmin=2, vmax=9, alpha=0.6)
ax.set_yscale("log")
for edge, col in [(70, C_YELLOW), (300, C_RED)]:
    ax.axvline(edge, color=col, ls=":", lw=1.2, alpha=0.8)
style_ax(ax, "Hypocenter Depth vs Magnitude", "Depth (km)", "Magnitude (log)")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "depth_vs_mag.png")); plt.close(fig)

# ----------------------------------------------------------------------------
# 3.  HEADLINE: spatial risk-zone map (posterior P(significant) per cell)
# ----------------------------------------------------------------------------
print("[3/6] Computing spatial risk zones ...")
cell = df.groupby(["c_lat", "c_lon"]).agg(n=("mag", "size"), sig=("y", "sum"))
cell["p"] = cell["sig"] / cell["n"]
cell = cell[cell["n"] >= 15]                       # stability floor
risk_cmap = LinearSegmentedColormap.from_list(
    "risk", ["#123b2e", "#1b6b47", C_YELLOW, C_ORANGE, C_RED])

fig, ax = plt.subplots(figsize=(12, 5.6))
for feat in w["features"]:
    gm = feat["geometry"]
    polys = gm["coordinates"] if gm["type"] == "MultiPolygon" else [gm["coordinates"]]
    for poly in polys:
        for ring in poly:
            a = np.array(ring); ax.plot(a[:, 0], a[:, 1], color="#24466e", lw=0.5, zorder=1)
pmax = cell["p"].max()
for (cla, clo), r in cell.iterrows():
    col = risk_cmap(r["p"] / pmax)
    ax.add_patch(Rectangle((clo * 5, cla * 5), 5, 5, facecolor=col,
                           edgecolor=BG, lw=0.6,
                           alpha=0.45 + 0.5 * min(r["n"] / 150, 1), zorder=2))
ax.scatter(df["lon"], df["lat"], s=2.5, c="#9fb3c8", alpha=0.25, zorder=3)
sm = plt.cm.ScalarMappable(cmap=risk_cmap,
                           norm=matplotlib.colors.Normalize(vmin=0, vmax=pmax))
cb = fig.colorbar(sm, ax=ax, pad=0.01)
cb.set_label(f"P(M >= {SIGNIFICANT}) per 5-degree zone  (min 15 events)", color=TXT)
cb.outline.set_edgecolor(GRID); cb.ax.tick_params(colors="#9fb3c8")
ax.set_xlim(-180, 180); ax.set_ylim(-62, 75); ax.set_aspect("equal")
ax.set_xlabel(""); ax.set_ylabel("")
ax.set_title("Seismic Risk Zones - where significant (M>=5.0) events concentrate", pad=10)
for s in ax.spines.values(): s.set_color(GRID)
ax.grid(alpha=0.2)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "risk_map.png")); plt.close(fig)

# risk zone table (top by posterior probability) with data-driven labels
risk_rows = []
for (cla, clo), r in cell.sort_values("p", ascending=False).head(6).iterrows():
    sub = df[(df["c_lat"] == cla) & (df["c_lon"] == clo)]
    risk_rows.append(dict(
        zone=region_label(sub["place"]),
        lat=f"{cla*5} to {cla*5+5} N" if cla >= 0 else f"{-cla*5} to {-cla*5+5} S",
        lon=f"{(clo*5+180)%360-180} deg",
        events=int(r["n"]), significant=int(r["sig"]),
        p_posterior=round(float(r["p"]), 3)))

# ----------------------------------------------------------------------------
# 4.  ML risk model - walk-forward time-series cross-validation
# ----------------------------------------------------------------------------
print(f"[4/6] Training ML risk model (walk-forward CV, target M>={SIGNIFICANT}) ...")
n = len(df); fold = n // 5
proba_list, y_list, idx_list, fold_imp = [], [], [], []
for i in range(4):                                  # 4 hold-out future windows
    tr = df.iloc[:fold * (i + 1)]
    te = df.iloc[fold * (i + 1): fold * (i + 2)]
    if te["y"].sum() == 0:
        continue
    c = RandomForestClassifier(n_estimators=300, class_weight="balanced",
                               min_samples_leaf=3, random_state=42, n_jobs=-1)
    c.fit(tr[FEATURES], tr["y"])
    proba_list.append(c.predict_proba(te[FEATURES])[:, 1])
    y_list.append(te["y"].values); idx_list.append(te.index.values)
    fold_imp.append(c.feature_importances_)
proba = np.concatenate(proba_list); yte = np.concatenate(y_list)
test_idx = np.concatenate(idx_list); pred = proba > THRESH

base   = float(yte.mean())
prec   = precision_score(yte, pred, zero_division=0)
rec    = recall_score(yte, pred, zero_division=0)
f1     = f1_score(yte, pred, zero_division=0)
lift   = prec / base if base else 0.0
imp    = np.mean(fold_imp, axis=0)
imp_df = (pd.Series(imp, index=FEATURES).sort_values(ascending=False)
            .round(3).reset_index().rename(columns={"index": "feature", 0: "importance"})
            .to_dict("records"))
print(f"      test (future) events: {len(yte):,}  significant: {int(yte.sum())}")
print(f"      precision {prec:.3f}  recall {rec:.3f}  F1 {f1:.3f}  "
      f"lift {lift:.1f}x  (baseline {base:.4f})")

# final full-data model -> feature-importance chart (descriptive)
full = RandomForestClassifier(n_estimators=400, class_weight="balanced",
                              min_samples_leaf=3, random_state=42, n_jobs=-1)
full.fit(df[FEATURES], df["y"])
full_imp = (pd.Series(full.feature_importances_, index=FEATURES)
            .sort_values(ascending=False).reset_index()
            .rename(columns={"index": "feature", 0: "v"}))

fig, ax = plt.subplots(figsize=(6.2, 4.0))
cols = ["#a78bfa", C_GREEN, C_YELLOW, C_CYAN, C_ORANGE]
ax.barh(full_imp["feature"][::-1], full_imp["v"][::-1],
        color=cols[::-1], edgecolor=BG)
for ylab, v in zip(full_imp["feature"][::-1], full_imp["v"][::-1]):
    ax.text(v + max(full_imp["v"])*0.01, ylab, f"{v:.1%}",
            va="center", ha="left", fontsize=9)
ax.set_xlim(0, max(full_imp["v"]) * 1.22)
style_ax(ax, "Model Feature Importance (Random Forest)", "Importance", "")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "feature_importance.png")); plt.close(fig)

# top model alerts on the held-out FUTURE test set (honest demo)
tst = (df.loc[test_idx][["time", "place", "mag", "depth"]]
         .assign(prob=proba).sort_values("prob", ascending=False).head(8).copy())
tst["flag"] = np.where(tst["prob"] > THRESH, "ALERT", "-")
tst["actual_sig"] = np.where(tst["mag"] >= SIGNIFICANT, "YES", "no")
tst_out = tst.assign(time=tst["time"].dt.strftime("%d %b %H:%M")).to_dict("records")

# ----------------------------------------------------------------------------
# 5.  Save metrics + print poster-ready summary
# ----------------------------------------------------------------------------
metrics = dict(
    n_total=n_total, n_used=n_used, date_min=d_min, date_max=d_max,
    max_mag=float(max_mag), max_ev=max_ev, n_ge55=n_ge55, n_ge60=n_ge60,
    n_tsum=n_tsum, b_value=b_value, top_regions=top_regions, depth_tab=depth_tab,
    significant_threshold=float(SIGNIFICANT), threshold=THRESH,
    model=dict(test_n=int(len(yte)), test_pos=int(yte.sum()), baseline=round(base, 4),
               precision=round(float(prec), 3), recall=round(float(rec), 3),
               f1=round(float(f1), 3), lift=round(float(lift), 1),
               importance=imp_df),
    risk_zones=risk_rows, top_alerts=tst_out,
)
with open(os.path.join(OUT, "metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2, default=str)
print("[5/6] metrics.json saved.")

print("[6/6] Poster-ready summary")
print("=" * 64)
print(f"Dataset : USGS live feed, {n_used:,} earthquakes, {d_min} -> {d_max}")
print(f"Significant (M>={SIGNIFICANT:.0f}) events in window : {int(df['y'].sum())}")
print(f"Gutenberg-Richter b-value : {b_value}  (typical crust = 1.0)")
print(f"Top risk zone : {risk_rows[0]['zone']}  P(sig)={risk_rows[0]['p_posterior']}")
print(f"MODEL (walk-forward CV, threshold {THRESH}) :")
print(f"   precision {prec:.3f}  |  recall {rec:.3f}  |  F1 {f1:.3f}  |  LIFT {lift:.1f}x")
print(f"   -> flagged events are {lift:.0f}x more likely to be significant")
print(f"   -> model catches {rec*100:.0f}% of significant events in the future")
print("=" * 64)
print("Charts in:  output/*.png   (risk_map.png is the headline)")

# ----------------------------------------------------------------------------
# 6.  OPTIONAL interactive map (browser) - needs: pip install plotly
# ----------------------------------------------------------------------------
try:
    import plotly.express as px
    f2 = px.scatter_geo(df, lat="lat", lon="lon", color="mag",
                        color_continuous_scale="Inferno", height=520,
                        projection="natural earth", template="plotly_dark")
    f2.update_layout(title="TREMORWATCH - Live Global Seismic Activity")
    f2.write_html(os.path.join(OUT, "interactive_map.html"), include_plotlyjs="cdn")
    print("Bonus: interactive map -> output/interactive_map.html")
except Exception as e:
    print(f"(skipped interactive map: {e.__class__.__name__})")
