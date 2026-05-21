"""Export static chart PNGs for presentation finding slides (same data as the story)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent / "presentation-media" / "findings"
OUT.mkdir(parents=True, exist_ok=True)

BG = "#14141f"
CARD = "#1c1c28"
TEXT = "#f4f4f8"
MUTED = "#9ca3b8"
GREEN = "#1DB954"
GREEN_H = "#1ed760"
PURPLE = "#9B5DE5"
GRID = "#2e2e42"

FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
    "loudness",
    "tempo",
]

FOCUS_GENRES = ["pop", "rock", "hip-hop", "classical", "metal", "jazz"]


def _style_axes(ax):
    ax.set_facecolor(CARD)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)
    ax.grid(True, axis="y", color=GRID, alpha=0.45, linewidth=0.6)


def export_finding_01() -> None:
    c1 = pd.read_csv(DATA / "chart1_popularity_distribution.csv")
    c1.columns = [str(c).strip().lstrip("\ufeff") for c in c1.columns]
    x = c1.iloc[:, 0].astype(int)
    y = c1.iloc[:, 1]

    fig, ax = plt.subplots(figsize=(6.4, 3.6), facecolor=BG)
    ax.bar(x, y, width=0.92, color=GREEN, alpha=0.85, edgecolor="none")
    ax.set_xlabel("Popularity score", fontsize=10)
    ax.set_ylabel("Number of tracks", fontsize=10)
    ax.set_title("Most tracks pile up at low popularity", fontsize=11, fontweight="bold", pad=10)
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(OUT / "finding-01-popularity.png", dpi=160, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def export_finding_02() -> None:
    df = pd.read_csv(DATA / "dataset.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    df = df.drop_duplicates(subset="track_id")
    corr = df[FEATURES + ["popularity"]].corr()["popularity"].drop("popularity")
    corr = corr.reindex(corr.abs().sort_values(ascending=True).index)

    fig, ax = plt.subplots(figsize=(6.4, 3.6), facecolor=BG)
    colors = [GREEN_H if v >= 0 else PURPLE for v in corr.values]
    ax.barh(corr.index, corr.values, color=colors, alpha=0.9, height=0.65)
    ax.axvline(0, color=GRID, linewidth=1)
    ax.set_xlim(-0.12, 0.12)
    ax.set_xlabel("Correlation with popularity", fontsize=10)
    ax.set_title("All correlations are weak", fontsize=11, fontweight="bold", pad=10)
    _style_axes(ax)
    ax.grid(True, axis="x", color=GRID, alpha=0.45, linewidth=0.6)
    ax.grid(False, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "finding-02-correlations.png", dpi=160, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def export_finding_03() -> None:
    radar = pd.read_csv(DATA / "chart3_genre_radar.csv", index_col=0)
    radar = radar.loc[[g for g in FOCUS_GENRES if g in radar.index]]
    labels = list(radar.columns)
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    angles = np.concatenate([angles, [angles[0]]])

    fig, ax = plt.subplots(figsize=(5.2, 5.2), subplot_kw=dict(polar=True), facecolor=BG)
    ax.set_facecolor(CARD)
    palette = [GREEN, PURPLE, "#56CFE1", "#F72585", "#FFC300", "#4CC9F0"]
    for i, (genre, row) in enumerate(radar.iterrows()):
        vals = np.concatenate([row.values, [row.values[0]]])
        ax.plot(angles, vals, color=palette[i % len(palette)], linewidth=1.8, label=genre)
        ax.fill(angles, vals, color=palette[i % len(palette)], alpha=0.08)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=MUTED, fontsize=7)
    ax.tick_params(colors=MUTED, labelsize=7)
    ax.grid(color=GRID, alpha=0.5)
    ax.set_title("Genres have distinct audio profiles", fontsize=11, fontweight="bold", color=TEXT, pad=18)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.12), fontsize=8, framealpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "finding-03-genre-radar.png", dpi=160, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def export_finding_04() -> None:
    hits = pd.read_csv(DATA / "chart4_hits_vs_nonhits.csv", index_col=0)
    show = [c for c in ["danceability", "energy", "valence", "acousticness", "tempo"] if c in hits.columns]
    x = np.arange(len(show))
    w = 0.35
    top = hits.loc["Top 10%", show].astype(float).values
    bot = hits.loc["Bottom 10%", show].astype(float).values

    fig, ax = plt.subplots(figsize=(6.4, 3.6), facecolor=BG)
    ax.bar(x - w / 2, top, width=w, label="Top 10%", color=GREEN, alpha=0.9)
    ax.bar(x + w / 2, bot, width=w, label="Bottom 10%", color=MUTED, alpha=0.75)
    ax.set_xticks(x)
    ax.set_xticklabels(show, rotation=25, ha="right")
    ax.set_ylabel("Mean feature value", fontsize=10)
    ax.set_title("Hits vs non-hits: small gaps, large overlap", fontsize=11, fontweight="bold", pad=10)
    _style_axes(ax)
    leg = ax.legend(frameon=True, fontsize=9)
    leg.get_frame().set_facecolor(CARD)
    leg.get_frame().set_edgecolor(GRID)
    for t in leg.get_texts():
        t.set_color(TEXT)
    fig.tight_layout()
    fig.savefig(OUT / "finding-04-hits.png", dpi=160, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    export_finding_01()
    export_finding_02()
    export_finding_03()
    export_finding_04()
    print(f"Saved 4 charts to {OUT}/")


if __name__ == "__main__":
    main()
