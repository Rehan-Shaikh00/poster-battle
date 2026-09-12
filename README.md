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
│   ├── poster_preview.png      ← quick visual check
│   ├── poster_template.html    ← editable source (add team names here)
│   └── build_poster.py         ← rebuild HTML/PDF after edits
├── code/
│   ├── disaster_analysis.py    ← the analysis: downloads live data, EDA,
│   │                             risk zones, walk-forward CV ML model, charts
│   ├── requirements.txt
│   └── output/
│       ├── *.png               ← all charts (dark theme, poster-ready)
│       ├── metrics.json        ← every number used in the poster
│       └── interactive_map.html← bonus live dashboard for the laptop demo
└── presentation/
    └── script_and_qa.md        ← 10-min time-coded script + 18 Q&A answers
                                  + numbers cheat-sheet + day-of checklist
```

## Run it yourself (takes ~2 min)

```bash
cd code
pip install -r requirements.txt        # pandas numpy matplotlib scikit-learn requests
python disaster_analysis.py            # downloads live USGS data, trains model,
                                       # prints poster-ready summary, saves charts
```

Everything is reproducible from public data — no API keys, no synthetic data.
If you re-run on the day of the event, the numbers update to the latest 30-day
window (the cached `.geojson` files make it also run fully offline).

## Edit the poster (e.g., add your names)

1. Open `poster/poster_template.html` → replace `[Name 1] • [Name 2] • [Name 3]`.
2. `python poster/build_poster.py` → regenerates `poster.html` + `poster.pdf`.

## Honest-science notes (know these before Q&A)

- The model does **not predict earthquakes**. It *triages detected events*
  (probability of being significant, M ≥ 5.0) and flags zones for pre-positioning.
- Evaluation is **walk-forward time-series CV** (8,912 unseen future events,
  4 sequential hold-out windows) — no leakage, no random splits.
- Headline numbers: precision 24.8%, recall 57.3%, F1 0.346, **16.8× lift**
  over the 1.5% base rate; top-8 future alerts: 4/8 verified significant.
- Deep-quake magnitude effect is flagged as **detection bias**, not a discovery.
