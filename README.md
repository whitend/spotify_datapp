# Spotify Catalogue Promotion Dashboard

**BANA409 — Data App In-Class Group Exercise**

---

## 1. Who the dashboard is for, and what decision it supports

**The person.** The Streaming Promotion Manager at a record label or distributor. One role, not a
team and not "leadership": this is the person who owns the weekly promotion budget and decides
which releases and catalogue tracks get paid exposure — editorial playlist pitches, Marquee
placements, Discovery Mode. They look at it **every Monday morning** while planning that week's
push, for five to twenty minutes. Not the artists, not A&R (who decide what gets made), not "the
marketing function".

**The decision.**

> *If the promotion manager sees that one genre's tracks break out far more often than the
> catalogue average, they will shift the coming week's budget toward it; and if they see tracks
> that already reached above-median streams but left the chart faster than the median, they will
> put those tracks on the re-promotion list.*

**Why a dashboard and not something simpler.** The same three questions come back every week, but
the answers move as tracks age (streams accumulate, weeks-on-chart creep upward), so the view has
to be re-cut *while* the decision is being made. A weekly email is one frozen picture and cannot
answer *"compared with what?"* — which is exactly what this decision rests on. An alert watches one
threshold well but cannot answer *"where should the money go?"*.

**What it replaces.** Today the manager either hand-builds an Excel pivot from three separate CSV
exports every Monday (two to three hours) or, more realistically, repeats last week's split
unchanged. The cost is not the hours: it is a full promo cycle of delay before any reallocation,
budget that keeps flowing to genres whose tracks would break out anyway, and re-promotion
candidates missed entirely — picking "high reach, short life" titles out of 1,200 rows is precisely
the task nobody redoes weekly from a stale pivot.

---

## 2. What I showed

A **promotion allocation dashboard**: three numbers at the top, two charts that explain them, one
table at the bottom for whoever has to name actual titles.

```
Title                                        ← "Spotify Catalogue Promotion Dashboard — Team …"
Who it is for + the decision                 ← one line
Data period + production refresh             ← one line
┌────────────────────┬────────────────────┬────────────────────┐
│ Streams per track  │  Breakout rate     │ Weeks on Top 100   │   st.columns + st.metric
│ 305 M (+0 vs cat)  │ 29%    (−8 vs cat) │ 18    (+0 vs cat)  │   delta vs whole catalogue
└────────────────────┴────────────────────┴────────────────────┘
┌─ Chart 1a: streams per track by genre ─┐ ┌─ Chart 1b: breakout rate ─┐
│ dashed line = catalogue average        │ │ dashed line = average     │  why the KPIs look so
└────────────────────────────────────────┘ └───────────────────────────┘
┌─ Chart 2: streams × weeks on chart, cut at the medians ─────────────┐
│                     │ high reach, short life → re-promotion list   │  the chart the decision
└─────────────────────┴──────────────────────────────────────────────┘  is actually made on
Track table with a Stage column (Re-promote / Breaking out / Slow burn / Low priority)
Sidebar: genre multiselect · release-year window
```

**Why each element sits where it does.** People read downward and many never scroll, so the order
is the order of importance.

- **Three KPIs, five-second read.** Streams per track, breakout rate, median weeks on Top 100 —
  reach, success rate, durability: three angles that do not repeat each other. Each carries a
  **delta against the whole catalogue**, because a bare number never answers the reader's real
  question, *"compared with what?"*. Exactly three, because a row of seven headline numbers is a
  row nobody reads.
- **Chart 1 explains the KPIs.** Two genre panels side by side, both against a dashed catalogue
  average. One EDA finding decided this layout: genre barely moves streams per title (Rock 276.6 M
  to Pop 318.7 M, ±7%) but clearly moves how often a title breaks out (Rock 20.2% to R&B 33.6%).
  The right panel is the informative one, and the caption says so instead of leaving the reader to
  guess.
- **Chart 2 is the decision.** Streams against weeks on chart, cut at the current medians, so the
  re-promotion candidates are physically one corner of the picture. That population is large and
  currently unmanaged: **293 tracks reached above-median streams but left fast, with a 0% breakout
  rate**. They found an audience and failed to hold it — the strongest case for buying a second
  push. The count is stated right under the chart.
- **The table is last** because only the person who has to name titles needs it. It sits at the
  bottom rather than competing with the charts.
- **Two filters only**: genre (all selected by default, so the first view is the whole catalogue)
  and a release-year window — the two cuts this manager actually makes.

Every number shown is computed from the data at load time; only the labels are hard-coded.

---

## 3. What I cut, and why

Each element was tested against one question: *if this disappeared, would the decision-maker
notice?* These failed.

**1. Every audio-feature chart (tempo, danceability, valence, energy, acousticness).** This is what
the dataset's own description recommends as the project, and it is the most tempting thing in the
file. It is out because no audio feature correlates with a business outcome above |r| = 0.22 — the
strongest, danceability, explains under 5% of the variation in chart life. There is no line in this
data from "the song sounds like this" to "promote it", so the chart would quietly imply a decision
that does not exist.

**2. Total streams by genre.** The first chart anyone would draw, and a trap. Pop totals 101.4 B
streams against Rock's 30.2 B — a 3× gap — but that is mostly 318 Pop tracks versus 109 Rock
tracks. Per track the gap is 318.7 M against 276.6 M. A totals chart sends budget to whichever
genre happens to be released most often, which is a fact about the catalogue, not about audience.
This is also why the first KPI is an average and not a sum.

**3. A streams-by-release-year trend line.** Looks like the natural second chart, but 2018–2025 sits
flat at 291–323 M per track and 2026 appears to collapse to 265 M — a "collapse" that is nothing
but the partial year (64 tracks, Jan–Jun). No decision value, one certain misreading. I kept the
release-year *filter* (the manager does use it to focus the active window) and dropped the trend.

**4. Per-track audio detail in the table.** The table answers "which exact titles", which needs
title, artist, genre, streams, weeks on chart and a stage label — not nine audio columns nobody
acts on.

**Two inputs I also refused to use**, because they would have produced confident numbers that mean
nothing:

- **`longevity_score`** — correlates **−0.92** with peak rank; it is a re-scaled inverse of a column
  already on the page, not a second opinion.
- **`is_viral_hit` as a per-track filter** — no documented definition, and I could not reproduce it:
  all 344 flagged tracks spent ≥ 21 weeks on the chart, but so did 187 tracks that are *not*
  flagged. It appears only as an aggregate "breakout rate", never as a filter.

**What could mislead the reader, and how the page handles it.**

| Risk | Handling |
|---|---|
| Data is **synthetic** (`Hit Song 1`, `Artist 164`) | Said in the page caption; this demonstrates a method, not a market finding |
| **Survivorship bias** — every row already charted | Said in the caption. The page works the catalogue you already charted; it cannot say what makes a song chart |
| `is_viral_hit` definition unreproducible (344 flagged vs 187 unflagged, all at ≥ 21 weeks) | Never shown as a formula, never used as a filter |
| Streams are estimates, and **2026 is a partial year** | Labelled "(M)" and treated as relative; the year filter runs to Jun 2026, and the trend chart was cut |
| KPIs are **means over a selection**, thin for K-Pop (59 tracks) or Latin (66) | The table exposes those 59–66 rows, and the default view is the whole catalogue |
| Chart rank is **inverted** (1 = best) | Named "Peak rank", kept out of the KPIs, never used as a "higher is better" axis |

---

## 4. How often the data should be refreshed

**Refresh: nightly.** Platforms publish streams and positions daily; the one action this page
supports happens weekly. Hourly refresh would add pipeline cost and change no decision, because
there is no intra-week lever anyway. Daily is the slowest cadence that still makes Monday's picture
current.

**Review: weekly, Monday 09:00 — a deliberately different number.** The manager reads it in the
meeting that already sets the week's push. Nightly refresh means the reviewed version is at most a
day old, and nobody has to remember to "go and look".

**What is tracked, and what triggers action.**

- **Tracked:** streams per track, week over week, by genre — the KPI at the top of the page.
- **Allocation trigger:** a genre's streams per track more than **10% below its own 4-week average
  in two consecutive weeks** → move budget out of it at the next Monday meeting. Two weeks, not
  one, because single-week streaming numbers are noisy.
- **Alert trigger, separate from the dashboard:** a single track's weekly streams below **50% of its
  own 4-week average while still on the chart** raises an alert the same day. That is a phone call,
  not a dashboard visit: a second push has to be bought before the decay finishes, and waiting until
  Monday wastes the money.
- **Reviewed weekly, never alerted on:** breakout rate and median weeks on chart. Both move slowly;
  alerting on them would be pure noise.

**What stale data costs.** A full promo cycle: one week of spend aimed at a genre whose velocity has
already turned, one week of delay before a decaying track is rescued, and a Monday meeting arguing
over a picture that no longer exists. The real point is not that fresher is better — it is that the
*allocation* decision tolerates a day of staleness while the *decay* signal does not. That asymmetry
is why decay became an alert and everything else stayed a weekly read.

**On the page.** Because the data is a frozen Kaggle snapshot, the caption states the data period
(Jan 2018 – Jun 2026) and the production refresh (nightly, reviewed weekly).

---

## 5. The data and the EDA behind these choices

**Dataset.** *Global Spotify Hits & Audio Dynamics (2018–2026)*, CC0 —
<https://www.kaggle.com/datasets/vedauv/global-spotify-hits-and-audio-dynamics-20182026>.
Three CSVs sharing a `track_id` (`track_metadata`, `audio_features`, `chart_longevity_panel`),
merged one-to-one (1,200 rows, no duplicate ids) into the single `spotify_tracks.csv` the app reads:
**1,200 × 21, 156 KB**, inside the 25 MB limit. Nothing sampled or aggregated.

- **One row** = one song that reached the Top 100, with its audio profile and what it did on the
  charts. **Period** = 7 Jan 2018 – 27 Jun 2026.
- **Synthetic, and obviously so**: titles are `Hit Song 1`, `Hit Song 2`, …; artists are
  `Artist 164`, `Artist 29`, … over 200 artists. Treated as a realistically shaped stand-in for a
  label's catalogue report, not as market evidence.

| Finding | Number |
|---|---|
| Catalogue | 1,200 tracks · 8 genres · 200 placeholder artists |
| Streams per track | mean **304.6 M**, median 281 M, range 9.99 M – 1,467 M |
| Breakout rate (`is_viral_hit`) | **28.7%** (344 / 1,200) |
| Weeks on Top 100 | median **18**, range 5 – 102 |
| Genre → streams per title | near flat: Rock 276.6 M … Pop 318.7 M (**±7%**) |
| Genre → breakout rate | clearly different: Rock **20.2%** … R&B **33.6%** |
| Audio features → outcomes | danceability r = 0.22; energy −0.02; valence −0.02; tempo −0.02; duration −0.02 |
| `longevity_score` vs peak rank | r = **−0.92** |
| Reach × longevity quadrants | high reach + short life: **293 tracks, 0% breakout** · high reach + long life: 307, 78% |
| 2026 coverage | **64 tracks, Jan–Jun only** |

Two findings decided the page: genre moves breakout rate far more than streams per title, and
"high reach, short life" is a large, unmanaged block of the catalogue.

---

## 6. Build and deploy

```
spotify-dashboard/
├── app.py               # the dashboard
├── spotify_tracks.csv   # the three Kaggle files merged into one (1,200 × 21, 156 KB)
├── requirements.txt     # streamlit, pandas, matplotlib
└── README.md            # this file
```

Run locally: `uv run streamlit run app.py`

Deploy: these four files at the root of a **public** GitHub repository, then a Streamlit Cloud app
with main file path **`app.py`** and, under **Advanced settings**, Python version **3.14**. No
`uv.lock` or `pyproject.toml` is committed, so `requirements.txt` is the only dependency mechanism
in play.

**With real data I would** pull the file nightly from the platform APIs; add a `week` column, since
the snapshot has one row per track and no time series — the biggest gap between this prototype and
the refresh design in §4; replace the placeholder names; and add a market dimension so budget can be
split by territory as well as by genre.

---

## 7. Repository and app

| |      |
|---|------|
| **Team** | `[14]` |
| **Deployed app** | `[https://spotifydatapp-fa4afycec4upyqisms3vln.streamlit.app]` |
| **Repository** | `[https://github.com/whitend/spotify_datapp]` |
