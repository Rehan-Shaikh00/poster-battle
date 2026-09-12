# TREMORWATCH — 10-Minute Presentation Script + Q&A Prep

**Event:** Poster Battle — Technical Poster Presentation
**Theme:** Disaster Management and Emergency Response Platform
**When:** 15 September 2026, competition starts **10:30 a.m. sharp**
**Team format:** 3 members, 10 minutes + Q&A

---

## 1. Role split (decide this at your first rehearsal)

| Role | Owns | Sections |
|------|------|----------|
| **Speaker A** (front-runner) | Hook, problem, data, EDA | 01–03, 05, 06 |
| **Speaker B** (the data scientist) | Risk zones + ML model — the core | 04, 07, 08 |
| **Speaker C** (the closer) | Platform design, India context, demo | 09, closing, leads Q&A |

Transitions should be one sentence ("…which brings us to the model that turns these zones into alerts — Speaker B will take it").
**If you can't rehearse enough for 3 speakers, one person presents everything** — consistency beats awkward handoffs.

---

## 2. The script (time-coded, 10:00 total)

Numbers in **bold** are the ones to memorize. Point at the matching poster section (its number) while talking.

### 0:00–0:40 — Hook & problem  *(poster 01)*
> "When the M7.8 struck near Ende, Indonesia on 10 September, emergency services had to answer three questions in the first minutes: *how bad is it, where is it, and what do we send?* Today we'll show you a system that answers all three using data science.
> Our poster, **TREMORWATCH**, is a seismic risk-intelligence platform for disaster management and emergency response. Earthquakes can't be predicted with certainty — but their *where* and *likelihood* are strongly patterned, and every minute of the response gap costs lives. That's the problem we attacked."

### 0:40–1:30 — The data  *(poster 02)*
> "We built this on **live, public, real** data — the USGS global earthquake feed. In the 30 days before our analysis we had **11,143 earthquakes** worldwide: a maximum of **M7.8**, **189 significant events** above M5.0, and **7 tsunamis triggered**. No synthetic data, no API key — the same feed response agencies actually use. That scale and freshness is what makes a risk model possible."

### 1:30–3:00 — What the data told us  *(poster 05, 06)*
> "Three findings from the exploratory analysis:
> **One —** the data obeys the **Gutenberg–Richter law**: we fitted it and got a **b-value of 1.15**, right at the theoretical 1.0 for Earth's crust. That's our validation that the pipeline and catalog are healthy.
> **Two —** small events dominate: only **1.7%** of all earthquakes are significant, yet those alone drive the response.
> **Three —** depth carries a signal: deep quakes below 300 km average **M4.5 versus M1.6** for shallow ones — we see large deep events precisely because small deep ones never reach our sensors.
> But the pattern that matters for emergency response is spatial — and that's the headline."

### 3:00–4:30 — Headline: risk zones  *(poster 04)*
> "This is the risk-zone map. We divided the planet into 5-degree zones and computed, for each, the observed probability of a significant event. **Red = ready.** Significant earthquakes concentrate in a handful of zones: **Indonesia and the Banda Sea — 333 events, 54 of them significant; Timor Leste at P = 0.31; the Philippines at 0.23; Mexico at 0.15.**
> For an emergency-management body, this is the pre-positioning layer: place caches, drills, and rapid-response teams *before* the event, exactly where the statistics say the risk lives. It's the same logic behind national hazard maps — but regenerated from live data in minutes."

### 4:30–7:00 — The ML triage model  *(poster 07, 08)*
> "Pre-positioning is the slow layer. The fast layer is triage: when any earthquake is detected, score in under a second — *how likely is this to be significant?*
> We trained a **Random Forest** on features known **at detection time**: grid location, depth, hour, day of week — magnitude is the target, never an input, so no leakage.
> Evaluation is the part most projects fudge, so we were strict: **walk-forward time-series cross-validation** — four sequential holdout windows, **8,912 unseen future events**, every model trained only on data that had already happened.
> Results: **precision 19.6%, recall 78.6%, F1 0.314.** The headline number is the **13.3× lift**: if you alerted on every earthquake, 1.5% would be significant; the events our model flags are **13 times more likely** to be significant, and it still **caught 79%** of them.
> Look at the feature importances — **location and depth carry about 90% of the signal**. The algorithm, fed only numbers, independently learned the **Ring of Fire**. That's a sanity check we love: the model understood plate tectonics.
> And here is the model working on actual future events — its eight highest-confidence alerts. **Three of the eight were verified significant — 37.5%, versus a 1.5% base rate, 25× better than random.** The misses cluster just below M5.0, exactly where magnitude estimates are least stable. We show the misses on purpose — an honest model earns trust."

### 7:00–8:30 — The response platform  *(poster 09) + live demo*
> "The platform closes the loop: **detect** from the live feed, **score** with the model, **zone** lookup against the risk map, **alert** on-call responders via SMS or app — and **dispatch** pre-positioned resources. Only top-confidence, in-risk-zone events page a human, which cuts alert fatigue while keeping a 79% catch rate.
> *(Speaker C stands, opens the interactive map on the laptop)*
> And this isn't a screenshot — this is the live dashboard we generated from the same pipeline. You can see every event from the last 30 days, colour-coded by magnitude. *(If demoing)* The full code is on our drive — it downloads the feed, runs the analysis, trains the model, and reproduces every number on this poster in under two minutes."

### 8:30–9:20 — Why it matters (India)  *(footer chips)*
> "Why should we care here in India? We sit on some of the most active tectonic geometry on Earth — Zone-V regions in the north, the 2001 Bhuj M7.6, the 2015 Nepal M7.8 whose effects reached our whole region. National response — NDMA, district administration, hospitals — runs on exactly the question our system answers: *severity, fast, and in priority order.* Whether or not Dhule is a high-risk district, the pipeline generalises: swap the earthquake feed for IMD cyclone data or flood-gauge streams, and the zone–triage–alert architecture stays the same."

### 9:20–10:00 — Close
> "To sum up: **11,143 real earthquakes, one honest model, a 13.3× lift, and a response pipeline that turns raw seismic data into minutes saved.** We chose to show our misses as proudly as our hits, because in disaster management, trust is the deliverable. Thank you — we're happy to take questions."

**Timing discipline:** if you're running long at 7:00, cut the demo line and jump to the close. Never end the 10 minutes mid-thought — the Q&A clock starts immediately.

---

## 3. Numbers cheat-sheet (memorize these)

| Stat | Value |
|------|-------|
| Earthquakes in window | **11,143** (13 Aug – 12 Sept 2026) |
| Largest event | **M7.8**, NNW of Ende, Indonesia |
| Significant (M≥5.0) | **189** = **1.7%** |
| Tsunamis triggered | **7** |
| Gutenberg–Richter b-value | **1.15** (theory ≈ 1.0) |
| Top risk zones | Indonesia/Banda Sea (333 ev, 54 sig), Timor Leste P=0.31, Philippines P=0.23, Mexico P=0.15 |
| Model | Random Forest, 5 features, walk-forward CV, **8,912** future events |
| Precision / Recall / F1 | **19.6% / 78.6% / 0.314** |
| Lift vs 1.5% baseline | **13.3×** |
| Feature importance | Location **75.9%**, Depth **16.0%**, Hour 5.3%, Day 2.7% |
| Top-8 alerts verified | **3 of 8** (37.5% vs 1.5% base → 25×) |
| Depth insight | Deep (>300 km) avg **M4.5** vs shallow **M1.6** (detection bias) |

---

## 4. Q&A — likely judge questions & model answers

**Q1. "Can this actually predict earthquakes?"**
"No — and we deliberately don't claim it can. Nobody can predict an individual earthquake. What we built is *risk triage*: the moment an event is detected, it's scored in under a second on how likely it is to be significant, so response teams can prioritize. We're not predicting *when* — we're answering *how much should we mobilize, and where should we already be ready.*"

**Q2. "The risk map just uses past data — isn't that circular?"**
"Partly, and that's by design — it's two different tools. The risk map is *posterior*: observed frequencies, exactly how FEMA or NDMA hazard maps work, used for slow decisions like pre-positioning. The ML triage is the fast tool: it scores each *new* event using only features available at detection time, and we evaluated it strictly on future events. One tells you where to be ready; the other tells you how to react."

**Q3. "Explain the 13.3× lift."**
"Precision math. Alert on everything → 1.5% of alerts are real. Our model's alerts → 19.6% are real. 19.6 ÷ 1.5 ≈ 13. So a flagged event is about 13× more likely to be significant than a random one — and we still caught 79% of all significant events. Lift is the fairest single number for imbalanced problems like this."

**Q4. "Why location is the top feature — isn't that cheating?"**
"No leakage: the USGS publishes the epicenter *before* the final magnitude, so location is genuinely known at detection time. And it's physically meaningful — large quakes happen at plate boundaries and subduction zones. The model learned the Ring of Fire on its own from raw coordinates. A model that *doesn't* find that signal is the one to worry about."

**Q5. "Why walk-forward CV instead of a normal train/test split?"**
"Because time has a direction. A random split would let the model learn from the *future* — 2030 quakes teaching it about 2025. We used walk-forward cross-validation: four sequential holdout windows, each model trained only on events before its test window. The 8,912 test events were genuinely unseen future. That's the only evaluation an operations team would trust."

**Q6. "Only 1.7% positives — how did you handle class imbalance?"**
"Three things: `class_weight='balanced'` in the forest so it doesn't just predict 'minor'; a tuned probability threshold (0.30) instead of the default 0.5; and we report precision/recall/lift, never accuracy — at 98.5% majority, accuracy would make a useless model look perfect. In production you'd set the threshold by cost: a missed M6.5 costs lives, a false alarm costs minutes."

**Q7. "Why a Random Forest? What about a neural network or XGBoost?"**
"Right tool for the job: ~11k rows of tabular data with mixed feature types. RF trains in seconds, is robust to outliers, and gives interpretable feature importances — which a responder can trust. XGBoost or LightGBM would be our next benchmark; a deep net would be overkill and a black box at this data scale."

**Q8. "What's the b-value and why does it matter?"**
"Gutenberg–Richter: log N = a − bM — the number of earthquakes drops exponentially with magnitude, with b ≈ 1 for Earth's crust. We fitted **b = 1.15** on our live data. It matters because it's a *data-quality check*: if the fit were broken, our whole pipeline would be suspect. We validated the sensor before trusting the model."

**Q9. "Why earthquakes instead of floods or cyclones, which hit India more often?"**
"Pragmatic MVP choice: earthquakes give a clean, standardized, *live* global feed with a well-defined significance threshold (magnitude) and a 30-day window rich enough to evaluate a model honestly. Cyclones and floods have messier, sparser signals. But the architecture is feed-agnostic — swap in IMD cyclone data or flood-gauge streams and the zone–triage–alert pipeline is unchanged. That generalizability is the point."

**Q10. "Deep quakes average M4.5 vs M1.6 shallow — real effect or bias?"**
"Honest answer: mostly detection bias, and we said so on the poster. Small deep quakes never reach surface sensors, so the deep sample only contains big ones. There's also a real subduction-slab physics component. Good catch — that's exactly why the poster labels it."

**Q11. "What's the real latency in production?"**
"The USGS feed updates within about a minute of detection; Random Forest inference on one event is under 10 milliseconds; the full loop — poll, parse, score, page — runs in seconds on a laptop, and as a small always-on service (Flask or Streamlit) on any cheap VPS. The alerting leg (SMS/Telegram) adds a few seconds. Total: well under a minute after detection."

**Q12. "What did you actually build — is it a working app?"**
"The complete analysis pipeline is working code — it downloads the live feed and reproduces every number on this poster in under two minutes. The risk map and the trained model are live artifacts. The bonus interactive dashboard is a real running app — that's what we're demoing from the laptop. The 'platform' box (SMS dispatch, resource layer) is the designed extension; the core triage logic works today."

**Q13. "What would you build next?"**
"Four things: (1) decades of historical data from NEIC/EM-DAT instead of 30 days — the risk map gets sharper; (2) more disaster types on the same architecture; (3) an actual alerting channel — a Telegram/SMS bot for a local disaster cell; (4) aftershock awareness — the model currently scores each event independently, so adding 'recent large quake nearby' as a feature is our clearest upgrade."

**Q14. "Is any of this copied?"**
"The *data* is public — USGS feeds are a shared global sensor, like a weather station. Everything else is ours: the analysis, the model, the evaluation, the charts, and this poster. The code is on our pendrive and we'll gladly walk through any line during Q&A."

**Q15. "Explain precision and recall to a non-technical person."**
"Precision: of the alarms we raise, how many are real — **about 1 in 5**. Recall: of the real significant earthquakes, how many we sounded the alarm for — **79%**. For a fire alarm you'd want both near 100%; here we deliberately accept 4 false alarms per real one, because missing a real M6.5 is catastrophic while a false alarm just costs a few minutes of checking."

**Q16. "What about aftershocks? An M5.5 right after an M7.8 is normal."**
"Correct — and that's a limitation we'd fix next. Right now the model scores each event on its own features; in production we'd add context features: a large event within 100 km in the last 24–48 h raises the prior for the follow-ups. That turns 'each quake in isolation' into 'understand the sequence' — which is how real early-warning systems like CEA-IP working in India operate."

**Q17. "How bad is M5.5 actually? Why that threshold?"**
"Each whole magnitude step is ~32× the energy. M5.5 is felt strongly within ~100 km and can damage older buildings; M6.5 can destroy urban infrastructure — which is why response agencies treat M5–5.5 as the 'assess now' line. Our M5.0 target is deliberately slightly below that line: better to triage a few extra events than to under-alert."

**Q18. "What's Maharashtra's risk, honestly?"
"Low-to-moderate — we're not on a major plate boundary, and historical events in the region are generally M4–5. But the poster isn't 'Dhule is dangerous' — it's a *method* for converting a live hazard feed into response decisions. That method works identically for Zone-V districts, for cyclones in coastal districts, or for a national dashboard."

**If asked something you don't know:** *"That's a fair question and I'd rather be honest than invent a number — here's what we do know, and here's how we'd find out."* Then hand the rest to a teammate. Never bluff numbers in front of judges.

---

## 5. Day-of checklist

**Pendrive (two copies, one on each of two drives):**
- [ ] `poster.pdf` — the digital poster (A4 landscape) — **this is your submission format**
- [ ] `poster.html` — same poster as a web page (opens offline, self-contained)
- [ ] `code/disaster_analysis.py` + `code/output/` (all charts, `metrics.json`, `interactive_map.html`)
- [ ] `code/usgs_all_month.geojson` + `world_110m.geojson` (cached data → code runs **offline** if the venue Wi-Fi fails)

**Laptop (rules allow your own laptop/pendrive — use them):**
- [ ] Charged + charger packed; close all background updates
- [ ] Open `interactive_map.html` in Chrome **before** the slot, keep it warm
- [ ] Run `python disaster_analysis.py` once at home beforehand so the code's first run is proven
- [ ] Browser bookmarks: USGS live feed page (backup live view)

**Team:**
- [ ] Rehearse the full 10 minutes **twice with a stopwatch** before the event
- [ ] Agree on transitions + who leads Q&A (Speaker C) and the handoff rule ("Speaker B, the model?")
- [ ] Reach the venue so you're registered and seated before **10:30 a.m. sharp** — the competition starts on time
