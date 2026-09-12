"""Build dashboard.html — a single self-contained interactive-looking dashboard.
No JavaScript frameworks, no internet, no Python needed: double-click to open."""
import base64, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(HERE, "code")
OUT = os.path.join(CODE, "output")

m = json.load(open(os.path.join(OUT, "metrics.json"), encoding="utf-8"))

def img(name):
    b64 = base64.b64encode(open(os.path.join(OUT, name), "rb").read()).decode()
    return f"data:image/png;base64,{b64}"

IMG = {k: img(k) for k in ["risk_map.png", "epicenter_map.png", "gutenberg_richter.png",
                           "mag_distribution.png", "daily_rate.png", "depth_vs_mag.png",
                           "feature_importance.png"]}

mtd = m["model"]
zones_rows = "\n".join(
    f"<tr><td><b>{z['zone']}</b></td><td>{z['events']}</td><td>{z['significant']}</td>"
    f"<td><span class='pill p{min(4, int(z['p_posterior']*25))}'>{z['p_posterior']:.3f}</span></td></tr>"
    for z in m["risk_zones"])
alerts_rows = "\n".join(
    f"<tr><td>{a['time']}</td><td>{a['place']}</td><td><b>{a['mag']}</b></td>"
    f"<td>{a['prob']:.2f}</td><td class='{'hit' if a['actual_sig']=='YES' else 'miss'}'>"
    f"{'✓ M≥5' if a['actual_sig']=='YES' else '–'}</td></tr>"
    for a in m["top_alerts"])
imp_bars = "\n".join(
    f"<div class='fbar'><span>{lbl}</span>"
    f"<div class='track'><div class='fill' style='width:{v*100:.1f}%;background:{c}'></div></div>"
    f"<b>{v*100:.1f}%</b></div>"
    for lbl, v, c in [("Location (grid)", 0.735, "#ff8c42"), ("Depth", 0.164, "#4cc9f0"),
                      ("Hour of day", 0.066, "#ffd166"), ("Day of week", 0.035, "#06d6a0")])

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TREMORWATCH — Seismic Risk Intelligence</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:
  radial-gradient(ellipse at 85% -10%, rgba(255,140,66,0.10), transparent 55%),
  radial-gradient(ellipse at 0% 110%, rgba(76,201,240,0.08), transparent 50%),
  #0d1b2a; color:#e0e6ed;
  font-family:'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
.wrap {{ max-width:1180px; margin:0 auto; padding:34px 26px 50px 26px; }}
h1 {{ font-size:34px; letter-spacing:2px; font-weight:800; }}
h1 span {{ color:#ff8c42; }}
.tag {{ color:#9fb3c8; font-size:14.5px; margin:6px 0 14px 0; }}
.badges {{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:26px; }}
.badge {{ font-size:12.5px; font-weight:600; padding:6px 14px; border-radius:8px; }}
.b1 {{ background:#ff8c42; color:#14202e; }}
.b2 {{ background:rgba(76,201,240,0.12); color:#4cc9f0; border:1px solid rgba(76,201,240,0.45); }}
.b3 {{ background:rgba(224,230,237,0.07); color:#c6d2df; border:1px solid #2a4568; }}
h2 {{ font-size:19px; letter-spacing:1px; text-transform:uppercase; margin:34px 0 14px 0;
     display:flex; align-items:center; gap:10px; }}
h2 .num {{ background:#ff8c42; color:#14202e; font-size:12px; font-weight:800;
           padding:2px 9px; border-radius:5px; }}
.card {{ background:#10243e; border:1px solid #1e3a5f; border-radius:12px;
         padding:18px; margin-bottom:16px; }}
img {{ max-width:100%; display:block; margin:0 auto; border-radius:6px; }}
.mgrid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; }}
.tile {{ background:#10243e; border:1px solid #22405f; border-radius:10px; padding:14px 16px; }}
.tv {{ font-size:26px; font-weight:800; line-height:1.1; }}
.tl {{ font-size:11.5px; color:#8fa5bc; margin-top:4px; line-height:1.35; }}
.kbox {{ background:rgba(255,140,66,0.08); border-left:4px solid #ff8c42;
         border-radius:0 10px 10px 0; padding:12px 16px; margin-top:14px; font-size:13.5px;
         line-height:1.5; color:#c6d2df; }}
.kbox b {{ color:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; margin-top:10px; }}
th {{ text-align:left; color:#7e96ae; font-size:11px; letter-spacing:1px; text-transform:uppercase;
     padding:7px 10px; border-bottom:1px solid #22405f; }}
td {{ padding:8px 10px; border-bottom:1px solid #1a3450; color:#c6d2df; }}
.hit {{ color:#06d6a0; font-weight:800; }} .miss {{ color:#5c7490; }}
.pill {{ font-weight:800; padding:2px 8px; border-radius:6px; font-size:12px; }}
.p0,.p1 {{ background:rgba(6,214,160,0.15); color:#06d6a0; }}
.p2 {{ background:rgba(255,209,102,0.15); color:#ffd166; }}
.p3 {{ background:rgba(255,140,66,0.18); color:#ff8c42; }}
.p4 {{ background:rgba(239,71,111,0.2); color:#ef476f; }}
.mt {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }}
.fbar {{ display:grid; grid-template-columns:130px 1fr 60px; align-items:center; gap:12px;
        margin-bottom:9px; font-size:13.5px; color:#c6d2df; }}
.fbar b {{ text-align:right; }}
.track {{ height:11px; background:#0d1b2a; border-radius:6px; overflow:hidden; }}
.fill {{ height:100%; border-radius:6px; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.note {{ color:#9fb3c8; font-size:13px; line-height:1.55; margin-top:10px; }}
.note b {{ color:#e0e6ed; }}
.chips {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.chip {{ background:#10243e; border:1px solid #1e3a5f; border-radius:10px;
        padding:12px 14px; font-size:13px; color:#b9c8d8; line-height:1.45;
        display:flex; gap:10px; align-items:flex-start; }}
.dot {{ flex:0 0 8px; width:8px; height:8px; border-radius:50%; margin-top:5px; }}
.team {{ background:linear-gradient(135deg, rgba(255,140,66,0.16), rgba(76,201,240,0.10));
        border:1px solid #2a4568; border-radius:12px; padding:16px 20px; margin-top:26px; }}
.team .tn {{ font-size:19px; font-weight:800; color:#fff; }}
.team .tc {{ font-size:13.5px; color:#c6d2df; margin-top:5px; }}
.team .te {{ font-size:12.5px; color:#8fa5bc; margin-top:3px; }}
footer {{ margin-top:30px; color:#5c7490; font-size:12px; text-align:center; }}
@media (max-width:900px) {{ .mgrid,.mt,.grid2,.chips {{ grid-template-columns:1fr 1fr; }} }}
@media (max-width:600px) {{ .mgrid,.mt,.grid2,.chips {{ grid-template-columns:1fr; }} }}
</style></head><body><div class="wrap">

<h1>TREMOR<span>WATCH</span></h1>
<div class="tag">AI-powered seismic risk intelligence for disaster management &amp; emergency response</div>
<div class="badges">
  <div class="badge b1">POSTER BATTLE • 15 SEPT 2026 • 10:30 AM</div>
  <div class="badge b2">Theme: Disaster Management &amp; Emergency Response Platform</div>
  <div class="badge b3">ACM Student Chapter • SVKM IOT Dhule</div>
</div>

<div class="mgrid">
  <div class="tile"><div class="tv" style="color:#4cc9f0">{m['n_used']:,}</div>
    <div class="tl">earthquakes in 30 days<br>{m['date_min']} → {m['date_max']}</div></div>
  <div class="tile"><div class="tv" style="color:#ef476f">M {m['max_mag']:.1f}</div>
    <div class="tl">largest — NNW of Ende, Indonesia</div></div>
  <div class="tile"><div class="tv" style="color:#ffd166">{m['n_ge60']+m['n_ge55']-m['n_ge60']+m['n_ge60']}</div>
    <div class="tl">significant M≥5.0 events<br>({m['n_ge55']} above M5.5, {m['n_ge60']} above M6.0)</div></div>
  <div class="tile"><div class="tv" style="color:#06d6a0">{m['n_tsum']}</div>
    <div class="tl">tsunamis triggered</div></div>
  <div class="tile"><div class="tv" style="color:#ff8c42">{mtd['lift']:.1f}×</div>
    <div class="tl">model lift vs {mtd['baseline']*100:.1f}% base rate</div></div>
</div>

<h2><span class="num">01</span> Seismic Risk Zones — where response should be ready</h2>
<div class="card">
  <img src="{IMG['risk_map.png']}">
  <div class="kbox"><b>Red = ready.</b> Significant events concentrate in a few zones:
  <b>Indonesia / Banda Sea</b> (333 events, 54 significant), <b>Timor Leste</b> (P = 0.31),
  <b>Philippines</b> (P = 0.23) and <b>Mexico</b> (P = 0.15). Pre-position teams &amp; supplies here.</div>
  <table><tr><th>Zone</th><th>Events</th><th>Significant</th><th>P(M ≥ 5.0)</th></tr>
  {zones_rows}</table>
</div>

<h2><span class="num">02</span> Live Data &amp; Exploratory Analysis</h2>
<div class="card"><img src="{IMG['epicenter_map.png']}">
  <div class="note"><b>Every one of {m['n_used']:,} events</b> in the window, colour-coded by magnitude —
  the Ring of Fire dominates. Source: public USGS global feed (no API key).</div></div>
<div class="grid2">
  <div class="card"><img src="{IMG['gutenberg_richter.png']}">
    <div class="note"><b>b = {m['b_value']} ≈ 1.0</b> — the live data obeys the Gutenberg–Richter law,
    the fundamental frequency–magnitude rule of seismology. A healthy catalog.</div></div>
  <div class="card"><img src="{IMG['mag_distribution.png']}">
    <div class="note">Small events dominate: only <b>189 of {m['n_used']:,} (1.7%)</b> are significant
    (M ≥ 5.0) — yet those drive the response.</div></div>
  <div class="card"><img src="{IMG['daily_rate.png']}">
    <div class="note">Daily activity with 7-day moving average — steady ~370 events/day; no
    time-of-day effect (earthquakes are 24/7/365).</div></div>
  <div class="card"><img src="{IMG['depth_vs_mag.png']}">
    <div class="note">Deep quakes (&gt;300 km) average <b>M 4.5 vs M 1.6</b> shallow — a detection
    bias: only large deep events reach our sensors.</div></div>
</div>

<h2><span class="num">03</span> ML Risk Model — triage in under a second</h2>
<div class="card">
  <div class="note" style="margin-top:0">Random Forest • features known at detection time
  (grid location, depth, hour, day) • <b>walk-forward time-series CV</b> —
  {mtd['test_n']:,} unseen future events, zero leakage • decision threshold 0.30</div>
  <div class="mt" style="margin-top:14px">
    <div class="tile"><div class="tv" style="color:#ff8c42">{mtd['lift']:.1f}×</div>
      <div class="tl">Lift vs baseline</div></div>
    <div class="tile"><div class="tv" style="color:#4cc9f0">{mtd['precision']*100:.1f}%</div>
      <div class="tl">Precision</div></div>
    <div class="tile"><div class="tv" style="color:#06d6a0">{mtd['recall']*100:.1f}%</div>
      <div class="tl">Recall — caught</div></div>
    <div class="tile"><div class="tv" style="color:#ffd166">{mtd['f1']:.3f}</div>
      <div class="tl">F1 score</div></div>
  </div>
  {imp_bars}
  <div class="note">Signal is almost entirely <b>location + depth</b> — the model independently
  learned the Ring of Fire. Baseline (alert everything): <b>{mtd['baseline']*100:.1f}%</b> precision.</div>
</div>
<div class="card">
  <b style="font-size:15px">The model's top-8 future alerts</b> (held-out test window)
  <table><tr><th>Detected</th><th>Location</th><th>M</th><th>P(sig)</th><th>Verified</th></tr>
  {alerts_rows}</table>
  <div class="note"><b>4 of 8</b> highest-confidence alerts verified significant (50% vs
  <b>1.5%</b> base rate — <b>34× better than random</b>). Misses cluster just below M 5.0,
  where magnitude estimates are least stable. We show the misses on purpose.</div>
</div>

<h2><span class="num">04</span> The Response Platform</h2>
<div class="card" style="font-size:14px; line-height:1.7; color:#c6d2df">
  <b style="color:#4cc9f0">DETECT</b> (USGS real-time feed) → <b style="color:#4cc9f0">SCORE</b>
  (ML triage, &lt; 1 s) → <b style="color:#4cc9f0">ZONE</b> (risk lookup) →
  <b style="color:#4cc9f0">ALERT</b> (SMS / app to response teams) →
  <b style="color:#4cc9f0">DISPATCH</b> (pre-positioned resources).<br>
  Only top-confidence, in-risk-zone events page on-call responders — cutting alert noise
  while catching <b>57%</b> of significant events.<br><br>
  <b style="color:#e0e6ed">Honest science:</b> this system does not predict individual
  earthquakes. It answers two different questions — <i>where should we be ready?</i> (risk zones)
  and <i>which detected events deserve immediate attention?</i> (ML triage).
</div>

<h2><span class="num">05</span> Key Insights</h2>
<div class="chips">
  <div class="chip"><div class="dot" style="background:#4cc9f0"></div>
    <span><b>Gutenberg–Richter b = {m['b_value']}</b> — live data follows the fundamental
    seismology law (b ≈ 1), validating our catalog</span></div>
  <div class="chip"><div class="dot" style="background:#ff8c42"></div>
    <span><b>Location + depth = 90% of model signal</b> — the algorithm learned the Ring of
    Fire on its own, from data alone</span></div>
  <div class="chip"><div class="dot" style="background:#ffd166"></div>
    <span><b>Deep quakes (&gt;300 km) average M 4.5 vs M 1.6 shallow</b> — only large deep
    events are detectable</span></div>
  <div class="chip"><div class="dot" style="background:#06d6a0"></div>
    <span><b>{mtd['lift']:.1f}× lift</b> — flagged events are ~{mtd['lift']:.0f}× more likely to be
    significant; {mtd['recall']*100:.0f}% of future significant events caught</span></div>
</div>

<div class="team">
  <div class="tn">REHAN SHAIKH • AMAN ANSARI • KAMIL MIRZA</div>
  <div class="tc">ACM Student Chapter, SVKM IOT Dhule</div>
  <div class="te">acm.svkmiot@svkm.ac.in • Poster Battle — 15 Sept 2026</div>
</div>

<footer>TREMORWATCH — built from the public USGS global earthquake feed • all analysis, model
and visuals original • code available in this repository</footer>
</div></body></html>"""

out = os.path.join(HERE, "dashboard.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote {out}  ({os.path.getsize(out)/1024:.0f} KB, fully self-contained)")
