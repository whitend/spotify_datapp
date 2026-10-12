"""
Spotify Catalogue Promotion Dashboard
-------------------------------------
In-Class Group Exercise (BANA409) — Data App lecture.

Audience : the label's Streaming Promotion Manager.
Decision : where next week's promotion budget goes, and which tracks need a second push.

Run locally :  uv run streamlit run app.py
Deploy      :  Streamlit Cloud, main file path `app.py`, Python 3.14.
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

DATA_FILE = "spotify_tracks.csv"
SPOTIFY_GREEN = "#1DB954"
BLUE = "#4C6EF5"
GREY = "#8A8A8A"
RED = "#C92A2A"

st.set_page_config(page_title="Spotify Catalogue Promotion Dashboard", layout="wide")


@st.cache_data
def load_tracks(path: str) -> pd.DataFrame:
    """Load the frozen Kaggle snapshot (3 original files merged into one CSV)."""
    df = pd.read_csv(path, parse_dates=["release_date"])
    return df


df_all = load_tracks(DATA_FILE)

# ---------------------------------------------------------------------------
# Title + the two required captions (audience/decision, and data/refresh line)
# ---------------------------------------------------------------------------
st.title("Spotify Catalogue Promotion Dashboard — Team [Your Team Name]")

st.caption(
    "**Who it is for:** the label's Streaming Promotion Manager. "
    "**Decision it supports:** where next week's promotion budget goes — and which individual "
    "tracks deserve a second push."
)
st.caption(
    "**Data:** 1,200 charting tracks, releases Jan 2018 – Jun 2026 (Kaggle snapshot, synthetic). "
    "**Refresh in production:** nightly from the streaming platforms · "
    "**Reviewed:** weekly, in the Monday promotion meeting."
)

# ---------------------------------------------------------------------------
# Filters — only the two this decision-maker actually uses
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    st.caption("Start with the genre the budget is being split across.")
    all_genres = sorted(df_all["genre"].unique())
    genre_filter = st.multiselect("Genre", all_genres, all_genres)

    st.caption("Then narrow to the release window the promo push is targeting.")
    min_year = int(df_all["release_year"].min())
    max_year = int(df_all["release_year"].max())
    year_filter = st.slider("Release year", min_year, max_year, (min_year, max_year))

df = df_all[
    df_all["genre"].isin(genre_filter)
    & df_all["release_year"].between(year_filter[0], year_filter[1])
]

if df.empty:
    st.warning(
        "No tracks match the current filters. Select at least one genre and widen the "
        "release-year window."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Headline metrics — three numbers, five-second read, always vs the catalogue
# ---------------------------------------------------------------------------
catalogue_spt = df_all["total_streams_mil"].mean()
catalogue_breakout = df_all["is_viral_hit"].mean()
catalogue_weeks = df_all["weeks_on_top_100"].median()

sel_spt = df["total_streams_mil"].mean()
sel_breakout = df["is_viral_hit"].mean()
sel_weeks = df["weeks_on_top_100"].median()

col1, col2, col3 = st.columns(3)
col1.metric(
    "Streams per track",
    f"{sel_spt:,.0f} M",
    f"{sel_spt - catalogue_spt:+,.0f} M vs catalogue",
)
col2.metric(
    "Breakout rate",
    f"{sel_breakout:.0%}",
    f"{(sel_breakout - catalogue_breakout) * 100:+.0f} pts vs catalogue",
)
col3.metric(
    "Median weeks on Top 100",
    f"{sel_weeks:.0f}",
    f"{sel_weeks - catalogue_weeks:+.0f} weeks vs catalogue",
)

# ---------------------------------------------------------------------------
# Supporting chart 1 — breakdown by segment, compared against the catalogue
# ---------------------------------------------------------------------------
by_genre = (
    df.groupby("genre")
    .agg(
        streams_per_track=("total_streams_mil", "mean"),
        breakout_rate=("is_viral_hit", "mean"),
    )
    .sort_values("streams_per_track")
)

st.subheader("Why the headline numbers look the way they do")

fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
ax1.barh(by_genre.index, by_genre["streams_per_track"], color=SPOTIFY_GREEN)
ax1.axvline(catalogue_spt, color=GREY, ls="--", lw=1)
ax1.set_title("Streams per track (M)")
ax1.set_xlabel("millions")

ax2.barh(by_genre.index, by_genre["breakout_rate"] * 100, color=BLUE)
ax2.axvline(catalogue_breakout * 100, color=GREY, ls="--", lw=1)
ax2.set_title("Breakout rate (% of tracks)")
ax2.set_xlabel("% breaking out")
ax2.tick_params(labelleft=False)

fig1.tight_layout()
st.pyplot(fig1)

st.caption(
    f"Dashed line = the whole-catalogue average ({catalogue_spt:,.0f} M streams per track, "
    f"{catalogue_breakout:.0%} breakout rate). Genre barely moves streams per title, but it does "
    "move how often a title breaks out — so use the right-hand panel, not the left, when the "
    "question is *where the next push is most likely to land*."
)

# ---------------------------------------------------------------------------
# Supporting chart 2 — the chart that actually drives the weekly decision
# ---------------------------------------------------------------------------
st.subheader("What to do about it: high reach, short life")

median_streams = df["total_streams_mil"].median()
median_weeks = df["weeks_on_top_100"].median()

fig2, ax = plt.subplots(figsize=(9, 5))
for genre, sub in df.groupby("genre"):
    ax.scatter(
        sub["total_streams_mil"],
        sub["weeks_on_top_100"],
        s=18,
        alpha=0.6,
        edgecolors="none",
        label=genre,
    )
ax.axvline(median_streams, color=GREY, ls="--", lw=1)
ax.axhline(median_weeks, color=GREY, ls="--", lw=1)
ax.set_xlabel("Total streams (millions)")
ax.set_ylabel("Weeks on Top 100")
ax.text(
    0.99,
    0.03,
    "high reach, short life\n→ second push can still extend these",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=8,
    color=RED,
)
ax.legend(fontsize=7, ncol=2, loc="upper left", frameon=False)
fig2.tight_layout()
st.pyplot(fig2)

shortlist = df[
    (df["total_streams_mil"] >= median_streams) & (df["weeks_on_top_100"] < median_weeks)
]
st.caption(
    f"Dashed lines are the medians of the current selection ({median_streams:,.0f} M streams, "
    f"{median_weeks:.0f} weeks). The **{len(shortlist)} tracks in the lower-right quadrant** "
    "reached an audience but did not stay on the chart — that is the re-promotion shortlist. "
    "Tracks in the upper right are already breaking out on their own; extra spend there buys less."
)

# ---------------------------------------------------------------------------
# Bottom: detail for whoever wants to dig in
# ---------------------------------------------------------------------------
st.subheader("Track detail")

detail = df.sort_values("total_streams_mil", ascending=False).copy()
detail["Stage"] = "Low priority"
detail.loc[
    (detail["total_streams_mil"] >= median_streams)
    & (detail["weeks_on_top_100"] < median_weeks),
    "Stage",
] = "Re-promote"
detail.loc[
    (detail["total_streams_mil"] >= median_streams)
    & (detail["weeks_on_top_100"] >= median_weeks),
    "Stage",
] = "Already breaking out"
detail.loc[
    (detail["total_streams_mil"] < median_streams)
    & (detail["weeks_on_top_100"] >= median_weeks),
    "Stage",
] = "Slow burn"

show = detail[
    [
        "track_title",
        "artist_name",
        "genre",
        "release_year",
        "total_streams_mil",
        "weeks_on_top_100",
        "peak_chart_rank",
        "Stage",
    ]
].rename(
    columns={
        "track_title": "Track",
        "artist_name": "Artist",
        "genre": "Genre",
        "release_year": "Released",
        "total_streams_mil": "Streams (M)",
        "weeks_on_top_100": "Weeks on chart",
        "peak_chart_rank": "Peak rank",
    }
)
st.dataframe(show, hide_index=True)
