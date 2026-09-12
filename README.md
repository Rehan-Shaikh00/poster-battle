# TREMORWATCH — Poster Battle Submission

**Theme:** Disaster Management & Emergency Response Platform
**Event:** Poster Battle, ACM Student Chapter, SVKM IOT Dhule — 15 Sept 2026, 10:30 a.m.
**Team:** Rehan Shaikh • Aman Ansari • Kamil Mirza

An AI-powered seismic risk-intelligence platform: live USGS earthquake data →
exploratory analysis → spatial risk zones → ML triage of new events → response workflow.

## What's inside

```
poster-battle/
├── poster/
│   ├── poster.html             ← THE digital poster (self-contained; opens offline)
│   ├── poster.pdf              ← print-ready A4 landscape (same content)
│   ├── poster_template.html    ← editable source (names are in here)
│   └── build_poster.py         ← rebuild HTML/PDF after edits
├── dashboard.html              ← ⭐ SINGLE-FILE dashboard: double-click to open,
│                                 zero setup, works offline (the safest event-day demo)
├── build_dashboard.py          ← rebuilds dashboard.html from code/output/
├── app/
│   └── streamlit_dashboard.py  ← ⭐ INTERACTIVE live app (filters, hover, live map)
├── code/
│   ├── disaster_analysis.py    ← the core analysis: live USGS data, EDA,
│   │                             risk zones, walk-forward CV ML model, charts
│   ├── TREMORWATCH_notebook.ipynb ← ⭐ Jupyter notebook: the full analysis cell by
│   │                                 cell, pre-run with outputs (shows the work)
│   ├── build_notebook.py       ← regenerate the notebook
│   ├── requirements.txt
│   └── output/                 ← all charts, metrics.json, interactive_map.html
└── presentation/
    └── script_and_qa.md        ← 10-min time-coded script + 18 Q&A answers
                                  + numbers cheat-sheet + day-of checklist
```

## Run it (three ways)

### 1) The core analysis script
```bash
cd code
pip install -r requirements.txt        # pandas numpy matplotlib scikit-learn requests
python disaster_analysis.py            # ~2 min: downloads/reuses live USGS data,
                                       # trains model, prints poster-ready summary
```
Works **offline** thanks to the cached `.geojson` files (exact poster numbers).

### 2) Interactive Streamlit dashboard (the "wow" live demo)
```bash
pip install streamlit pandas numpy matplotlib scikit-learn requests plotly
cd app
streamlit run streamlit_dashboard.py   # opens in your browser automatically
```
Sidebar filters (min magnitude, depth band, map view), live world map with hover
details, risk-zone map with tooltips, EDA charts, model metrics + top-8 alerts.

### 3) Jupyter notebook (show the work in Q&A)
Open `code/TREMORWATCH_notebook.ipynb` in **VS Code** (just press "Run All") or
with `pip install notebook` → `jupyter notebook`. It comes **pre-run** — every cell
shows its chart/number — and re-running it regenerates everything from live data.

### 4) Single-file dashboard (no Python at all)
Double-click **`dashboard.html`** — opens in any browser, fully offline.
This is your bulletproof fallback for event day.

## Honest-science notes (know these before Q&A)

- The model does **not predict earthquakes**. It *triages detected events*
  (probability of being significant, M ≥ 5.0) and flags zones for pre-positioning.
- Evaluation is **walk-forward time-series CV** (8,912 unseen future events,
  4 sequential hold-out windows) — no leakage, no random splits.
- Headline numbers (verified with scikit-learn 1.9.1): precision 19.6%, recall 78.6%,
  F1 0.314, **13.3× lift** over the 1.5% base rate; top-8 future alerts: 3/8 verified.
  Note: model metrics vary slightly across scikit-learn versions — requirements.txt
  pins scikit-learn>=1.9, which reproduces these numbers exactly.
- Deep-quake magnitude effect is flagged as **detection bias**, not a discovery.
- Windows note: all file reads use `encoding="utf-8"` — required on Windows
  (cp1252 default chokes on non-ASCII USGS place names like "Gjøvik, Norway").
