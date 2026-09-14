# TREMORWATCH — 10-Minute Script (EASY LANGUAGE)

> Written to be **spoken**, not read. Short sentences. No jargon left
> unexplained. Numbers in **bold** are the only ones you must remember.
> You have 10:00. If you're running long at 7:00, cut the demo line.

---

## Part A — What our solution actually does (say this in plain words)

Keep this in your head. It answers the question *"so, what does it do?"*
in about 30 seconds.

**One line:**
> "TREMORWATCH watches the live global earthquake feed, and the second an
> earthquake is detected, it tells emergency teams — in under one second —
> *how serious this is, and should we act on it.* It also tells them *where
> to keep help ready* before any earthquake happens."

**The problem it solves:**
> "When a big earthquake is detected, responders have a few minutes to answer
> three questions: **how bad is it, where is it, and what do we send?**
> The catch: in 30 days there were **11,143 earthquakes**, but only **1.7%**
> were serious. If you react to all of them, you drown in false alarms. If
> you react to a few, you might miss the one that matters. There's no fast,
> data-driven way to pick the right ones. That gap is exactly what we built."

**What it does (two layers):**
> "Layer 1 — **where to be ready** (the slow layer): from real data we build
> a risk map showing *where serious quakes actually happen*, so teams,
> supplies and drills are placed there in advance.
> Layer 2 — **what to act on** (the fast layer): a machine-learning model
> scores every *new* earthquake in under a second — *'how likely is this to
> be serious?'* — and only the top-confidence, in-risk-zone events actually
> page a responder."

**The result:**
> "Flagged events are **13.3×** more likely to be serious than picking at
> random, and the system still **catches 79%** of all serious earthquakes.
> Less noise, faster correct action."

**Best analogy to use anywhere (Q&A included):**
> "Think of a hospital emergency room. The nurse doesn't treat everyone at
> once — she **triages**: who is critical, who can wait. TREMORWATCH is that
> triage nurse for earthquakes. And the risk map is like knowing which
> roads have the most accidents, so you park the ambulances there first."

---

## Part B — The 10-minute script (time-coded, easy language)

### 0:00–0:40 — Hook & the problem
> "Imagine this. A **7.8** earthquake just struck near Ende, Indonesia. The
> emergency team has a few minutes, and three questions burning:
> *how bad is it, where is it, and what do we send?* Get these wrong and
> lives are lost. Today we'll show you a system that answers all three using
> data science. We call it **TREMORWATCH** — it turns raw earthquake data
> into fast, smart decisions for disaster response."

### 0:40–1:30 — The data (real, not fake)
> "We did not use made-up data. We used the **real, live, public** earthquake
> feed from the USGS — the same one the actual disaster agencies use. In just
> **30 days** there were **11,143 earthquakes** worldwide. The biggest was
> **M7.8**. Only **189 — 1.7 percent** — were serious, M5.0 or above. And
> **7** of them caused tsunamis. No API key, no fake data — it's real, live,
> and at scale. That's what makes a risk model possible."

### 1:30–3:00 — What the data told us
> "The data taught us three things.
> **One — it makes sense.** Earthquakes follow a known rule called
> Gutenberg–Richter. In plain words: small quakes are very common, big ones
> are rare. We checked our data against that rule and it matched — we got a
> **b-value of 1.15**, and the textbook value is about 1.0. So our data is
> clean and we can trust it.
> **Two — a tiny share causes all the trouble.** Only **1.7%** are serious,
> but those are the only ones we need to act on. So the real question is:
> *how do we quickly find that 1.7% inside 11,000 events?*
> **Three — where it happens matters most.** And that's the heart of our work."

### 3:00–4:30 — The risk map (the headline)
> "This is the risk map. We split the planet into 5-degree boxes and asked:
> *where do serious earthquakes actually happen?* They cluster in a few
> places — **Indonesia and the surrounding seas: 333 events, 54 of them
> serious**; East Timor; the Philippines; Mexico. These are our **red zones**.
> Think of it like a map of accident-prone junctions. If you know which
> junctions have the most crashes, you park your traffic police and safety
> gear there *before* the next one. Emergency teams can do exactly that —
> place supplies, drills and rapid teams in the red zones in advance. That's
> our **pre-positioning layer**."

### 4:30–7:00 — The machine-learning triage (the core)
> "Now the fast layer. When a *new* earthquake is detected, we need an answer
> in **under one second**: *is this serious?*
> We trained a machine-learning model — a **Random Forest**, which is just a
> team of many simple decision-trees that vote together. It looks only at
> things we already know at the moment of detection: **where** it happened,
> **how deep**, and the **time of day**. It never sees the magnitude first —
> the magnitude is what it's trying to guess. And it gives out one number:
> *the chance this quake is serious.*
> Now — how do we know the model is good? This is where most projects cut
> corners, so we did it the hard way. We didn't test on random data. We
> tested it **on the future**: we train on the past, and let it predict
> events that had not happened yet — **8,912 events it had never seen**.
> That's called **walk-forward**, and it's the most honest way to test a
> time-based model.
> The result: when our model raises the flag, that event is **13.3× more
> likely** to be serious than picking at random — and it still **caught 79%**
> of all serious earthquakes.
> And here's what we love: we asked the model what mattered most. It said
> **location and depth — about 90%**. The machine, fed only numbers, taught
> itself the **Ring of Fire**. That's our confidence check — the model
> understood the same geography that scientists do."

### 7:00–8:30 — How it fits together (the platform) + demo
> "Here's how it all connects. The system **watches** the live feed. It
> **scores** each new quake. It **checks** the risk map. And only the
> important, high-confidence events **page** a responder. Everything else is
> ignored — so no noise, no alert fatigue, yet 79% of the serious ones are
> still caught.
> And this isn't just a poster. This is the **live dashboard** we built from
> the same pipeline — you can see every quake from the last 30 days on
> screen, coloured by size."

### 8:30–9:20 — Why it matters (India)
> "Why should we care here in India? We sit on some of the most active
> ground on Earth — the **2001 Bhuj** quake was 7.6, and the **2015 Nepal**
> 7.8 was felt across our region. National response teams answer exactly the
> same questions our system answers: *how serious, how fast, in what order.*
> And the same system can be reused — swap earthquakes for cyclone or flood
> data and it still works. So this isn't just about earthquakes."

### 9:20–10:00 — Close
> "To sum up: **11,143 real earthquakes, one honest model, a 13.3× edge over
> random, and a system that turns raw earthquake data into minutes saved.**
> We show the model's misses as proudly as its hits — because in disaster
> management, **trust is the real product.** Thank you. We're happy to take
> questions."

---

## Part C — The only numbers you must memorize

| Say | Number |
|-----|--------|
| Earthquakes in 30 days | **11,143** |
| Biggest one | **M 7.8** |
| Serious (M5.0+) share | **1.7%** (189 events) |
| Tsunamis | **7** |
| Data-quality check (b-value) | **1.15** (book value ≈ 1.0) |
| Top risk spot | **Indonesia / Banda Sea** (333 events, 54 serious) |
| Future events the model predicted | **8,912** |
| Flagged events are this much likelier to be serious | **13.3×** |
| Share of serious quakes we caught | **79%** |
| What the model learned matters most | **location + depth ≈ 90%** |

That's it. Everything else is on the poster — just **point** at it.

---

## Part D — Three easy answers for the trickiest Q&A

**"Can you actually predict earthquakes?"**
> "No — and we don't claim to. Nobody can predict *when* a specific quake
> will happen. What we do is **triage**: the moment one is detected, we tell
> teams in under a second *how serious it's likely to be*, and we show *where
> to already be ready.* We're not predicting the future — we're making the
> response faster and smarter."

**"Explain 13.3× in simple words."**
> "If you raised the alarm on *every* quake, only **1.5%** would be serious.
> When *our* model raises the alarm, about **19.6%** are serious.
> 19.6 divided by 1.5 is about **13**. So a quake our model flags is 13 times
> more likely to be the real deal — and we still caught **79%** of them."

**"Why is location the top clue — isn't that cheating?"**
> "No. The USGS already knows *where* a quake happened the moment it's
> detected — location is genuinely known before the final size is. And it
> makes physical sense: big quakes happen at plate boundaries. The model
> finding that on its own is a good sign, not a bad one."
