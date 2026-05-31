"""Bokeh layout for the Quarto data story (auto-generated).

Regenerate from project root: ``uv run python scripts/generate_viz_notebook.py``
"""

_STORY_SECTIONS = None
_EMBED_CACHE = None
_STORY_SECTION_ORDER = ("sec1", "sec2", "sec3", "sec4", "sec5", "slider")


def build_story_layout():
    from pathlib import Path
    import numpy as np
    import pandas as pd

    def _find_project_root() -> Path:
        """Return the folder that contains ``data/dataset.csv`` (repo root).

        VS Code / Jupyter often start the kernel with **cwd = workspace root** (e.g. a folder
        *above* ``Part 2/Untitled``) or with **cwd = notebooks/**. Walking only parents misses
        that, so we also check **subfolders one level** (and **two levels** under cwd).
        """
        here = Path.cwd().resolve()
        seen = set()

        def try_base(base: Path):
            b = base.resolve()
            if b in seen:
                return None
            seen.add(b)
            if (b / "data" / "dataset.csv").is_file():
                return b
            return None

        for base in [here, *here.parents]:
            r = try_base(base)
            if r is not None:
                return r

        if here.name == "notebooks":
            r = try_base(here.parent)
            if r is not None:
                return r

        try:
            for child in sorted(here.iterdir(), key=lambda p: str(p).lower()):
                if not child.is_dir() or child.name.startswith("."):
                    continue
                r = try_base(child)
                if r is not None:
                    return r
                try:
                    for sub in sorted(child.iterdir(), key=lambda p: str(p).lower()):
                        if sub.is_dir() and not sub.name.startswith("."):
                            r = try_base(sub)
                            if r is not None:
                                return r
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError):
            pass

        raise FileNotFoundError(
            "Could not find data/dataset.csv.\n"
            f"  Current working directory: {here}\n"
            "  (1) Download dataset.csv into <project>/data/: see README / SwitchDrive.\n"
            "  (2) Start Jupyter / VS Code from the project folder that contains `data/`, "
            "or set the kernel cwd there (File → Open Folder → …/Untitled).\n"
            "  (3) If the repo lives inside a parent workspace, keep this notebook inside "
            "that project tree so the search can find `data/dataset.csv`."
        )


    ROOT = _find_project_root()
    DATA = ROOT / "data"

    def _need(path: Path, what: str) -> None:
        if not path.is_file():
            raise FileNotFoundError(f"Missing {what}: {path}")

    _need(DATA / "dataset.csv", "raw Spotify export")
    for name in (
        "chart1_popularity_distribution.csv",
        "chart3_genre_radar.csv",
        "chart4_hits_vs_nonhits.csv",
        "chart5_mood_map.csv",
        "slider_lookup.csv",
    ):
        _need(DATA / name, f"prepared data ({name})")

    df = pd.read_csv(DATA / "dataset.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    df = df.drop_duplicates(subset="track_id")

    tmin, tmax = float(df["tempo"].min()), float(df["tempo"].max())

    c1 = pd.read_csv(DATA / "chart1_popularity_distribution.csv").copy()
    c1.columns = [str(c).strip().lstrip("\ufeff") for c in c1.columns]
    if "number_of_songs" not in c1.columns:
        if "popularity" in c1.columns and "count" in c1.columns:
            c1 = c1.rename(columns={"popularity": "popularity_score", "count": "number_of_songs"})
        elif len(c1.columns) >= 2:
            c1 = c1.rename(
                columns={c1.columns[0]: "popularity_score", c1.columns[1]: "number_of_songs"}
            )

    c1["popularity_score"] = pd.to_numeric(c1["popularity_score"], errors="coerce")
    c1["number_of_songs"] = pd.to_numeric(c1["number_of_songs"], errors="coerce")
    c1["bin_lo"] = (c1["popularity_score"] // 10 * 10).astype(int)
    c1 = (
        c1.groupby("bin_lo", as_index=False)["number_of_songs"]
        .sum()
        .sort_values("bin_lo")
        .reset_index(drop=True)
    )
    c1["bin_label"] = c1["bin_lo"].astype(str) + "–" + (c1["bin_lo"] + 9).astype(str)
    c1["bin_center"] = c1["bin_lo"] + 4.5

    c3 = pd.read_csv(DATA / "chart3_genre_radar.csv").copy()
    c3.columns = [str(c).strip().lstrip("\ufeff") for c in c3.columns]
    if "track_genre" not in c3.columns:
        c3 = c3.rename(columns={c3.columns[0]: "track_genre"})
    if "tempo" in c3.columns:
        denom = (tmax - tmin) if (np.isfinite(tmax) and np.isfinite(tmin) and tmax > tmin) else None
        if denom:
            c3["tempo_norm"] = ((c3["tempo"].astype(float) - tmin) / denom).clip(0, 1)
        else:
            c3["tempo_norm"] = 0.5
    elif "tempo_norm" in c3.columns:
        pass
    else:
        raise ValueError(
            "chart3_genre_radar.csv must include `tempo` (BPM) or `tempo_norm`. "
            f"Found: {list(c3.columns)}"
        )

    c5 = pd.read_csv(DATA / "chart5_mood_map.csv").copy()
    c5.columns = [str(c).strip().lstrip("\ufeff") for c in c5.columns]
    if "genre" not in c5.columns and len(c5.columns) >= 3:
        c5 = c5.rename(columns={c5.columns[0]: "genre"})

    lookup = pd.read_csv(DATA / "slider_lookup.csv")
    lookup["tempo_bin"] = lookup["tempo_bin"].astype(int)

    BINS_01 = np.arange(0, 1.1, 0.1)
    # slider_lookup.csv must use the SAME tempo bin edges as when it was built.
    # Repo file was built with 0–100 BPM in 10 BPM steps (bin indices 0–9); newer runs may use 0–250.
    _lt_tb_max = int(lookup["tempo_bin"].max())
    if _lt_tb_max <= 11:
        TEMPO_BINS_LOOKUP = np.arange(0, 110, 10)
    else:
        TEMPO_BINS_LOOKUP = np.arange(0, 250, 10)


    def bins01_series(s: pd.Series) -> pd.Series:
        return pd.cut(s, bins=BINS_01, labels=False, include_lowest=True)


    def tempo_bin_series_lookup(s: pd.Series) -> pd.Series:
        return pd.cut(s, bins=TEMPO_BINS_LOOKUP, labels=False, include_lowest=True)


    def bin01_scalar(x: float) -> int:
        s = bins01_series(pd.Series([float(np.clip(x, 0, 1))]))
        v = s.iloc[0]
        if pd.isna(v):
            return int(min(9, max(0, round(float(x) * 10 - 1e-9))))
        return int(v)


    def tempo_bin_lookup_scalar(bpm: float) -> int:
        # Clip to last histogram edge so pd.cut matches rows in slider_lookup (legacy file tops out at 100 BPM).
        hi_edge = float(TEMPO_BINS_LOOKUP[-1])
        bpm_c = float(np.clip(bpm, 0.0, hi_edge))
        s = tempo_bin_series_lookup(pd.Series([bpm_c]))
        v = s.iloc[0]
        if pd.isna(v):
            return int(_lt_tb_max)
        return int(v)


    def lookup_popularity(lookup: pd.DataFrame, d, e, v, a, tempo) -> float | None:
        db, eb, vb, ab = bin01_scalar(d), bin01_scalar(e), bin01_scalar(v), bin01_scalar(a)
        tb = tempo_bin_lookup_scalar(tempo)
        m = (
            (lookup["danceability_bin"] == db)
            & (lookup["energy_bin"] == eb)
            & (lookup["valence_bin"] == vb)
            & (lookup["acousticness_bin"] == ab)
            & (lookup["tempo_bin"].astype(int) == tb)
        )
        if not m.any():
            return None
        return float(lookup.loc[m, "popularity"].iloc[0])


    def tempo_to_norm(bpm: float) -> float:
        if tmax <= tmin or not (np.isfinite(tmin) and np.isfinite(tmax)):
            return 0.5
        return float(np.clip((bpm - tmin) / (tmax - tmin), 0, 1))


    import numpy as np
    import pandas as pd
    from bokeh.plotting import figure, show
    from bokeh.resources import INLINE
    from bokeh.models import (
        ColumnDataSource,
        Slider,
        Div,
        Range1d,
        LinearColorMapper,
        ColorBar,
        HoverTool,
        FactorRange,
        CustomJS,
        CheckboxGroup,
        InlineStyleSheet,
        Label,
        Spacer,
        FixedTicker,
    )
    from bokeh.layouts import column, row
    from bokeh.transform import dodge, transform, factor_cmap
    from bokeh.core.property.vectorization import value

    FOCUS_GENRES = ["classical", "hip-hop", "jazz", "metal", "pop", "rock"]
    FOCUS_LABELS = {
        "classical": "Classical",
        "hip-hop": "Hip-Hop",
        "jazz": "Jazz",
        "metal": "Metal",
        "pop": "Pop",
        "rock": "Rock",
    }

    PLAIN = {
        "danceability": "Easy to dance to (0–1)",
        "energy": "Intense / energetic (0–1)",
        "valence": "Sounds happy / positive (0–1)",
        "acousticness": "Acoustic, not electronic (0–1)",
        "instrumentalness": "Instrumental (little vocals)",
        "speechiness": "Spoken-word / rap-like",
        "liveness": "Live-audience feel",
        "loudness": "Typical volume (Spotify dB)",
        "tempo": "Tempo (BPM)",
        "tempo_norm": "Tempo (relative, 0–1)",
        "popularity": "Popularity (0–100)",
    }

    # Canva-inspired palette: dark canvas, neon green / purple / sky blue
    C = {
        "bg": "#14141f",
        "panel": "#1e1e2c",
        "text": "#f4f4f8",
        "muted": "#9ca3b8",
        "grid": "#2e2e42",
        "green": "#1DB954",
        "green_hi": "#1ed760",
        "purple": "#9B5DE5",
        "purple_dim": "#5c4d8a",
        "blue": "#56CFE1",
        "silver": "#e8e8ff",
        "dot": "#4a4a62",
    }
    GENRE_COLOR = {
        "classical": "#9B5DE5",  # purple
        "hip-hop": "#1DB954",  # green
        "jazz": "#56CFE1",  # sky blue
        "metal": "#E8E8FF",  # silver
        "pop": "#FFB703",  # gold
        "rock": "#FF6B9D",  # coral pink
    }
    _GENRE_PALETTE = [GENRE_COLOR[g] for g in FOCUS_GENRES]
    _GENRE_CMAP = factor_cmap("genre", palette=_GENRE_PALETTE, factors=FOCUS_GENRES)

    def _hex_rgb(hex_color: str) -> tuple[int, int, int]:
        h = hex_color.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def _genre_checkbox_css() -> str:
        rules = [
            ":host { display: block; width: 100%; max-width: 100%; box-sizing: border-box; }",
            ".bk-input-group { display: flex !important; flex-wrap: wrap; gap: 0.45rem 0.55rem; margin: 0; max-width: 100%; }",
            "label { display: inline-flex !important; align-items: center; gap: 0.4rem; margin: 0 !important;",
            " padding: 0.35rem 0.6rem !important; border-radius: 999px !important;",
            " border: 1px solid #2e2e42 !important; background: rgba(30, 30, 44, 0.9) !important; cursor: pointer; }",
            "label span { font-family: Figtree, system-ui, sans-serif !important; font-size: 0.82rem !important;",
            " font-weight: 600 !important; }",
            "label input { width: 1rem; height: 1rem; margin: 0; cursor: pointer; }",
        ]
        for i, gkey in enumerate(FOCUS_GENRES, start=1):
            col = GENRE_COLOR[gkey]
            r, gb, b = _hex_rgb(col)
            rules.append(f"label:nth-child({i}) span {{ color: {col} !important; }}")
            rules.append(f"label:nth-child({i}) input {{ accent-color: {col}; }}")
            rules.append(
                f"label:nth-child({i}):has(input:checked) {{"
                f" border-color: rgba({r}, {gb}, {b}, 0.65) !important;"
                f" background: rgba({r}, {gb}, {b}, 0.16) !important;"
                f" box-shadow: 0 0 12px rgba({r}, {gb}, {b}, 0.28); }}"
            )
        return "\n".join(rules)
    def _lerp_hex(c1: str, c2: str, t: float) -> str:
        r1, g1, b1 = _hex_rgb(c1)
        r2, g2, b2 = _hex_rgb(c2)
        t = max(0.0, min(1.0, t))
        return f"#{int(r1 + (r2 - r1) * t):02x}{int(g1 + (g2 - g1) * t):02x}{int(b1 + (b2 - b1) * t):02x}"

    def _build_corr_palette(steps: int = 256) -> list[str]:
        stops = [
            (-1.0, "#7B2CBF"),
            (-0.5, "#9B5DE5"),
            (-0.2, "#5c5578"),
            (0.0, "#2e2e42"),
            (0.2, "#3d5248"),
            (0.5, "#1DB954"),
            (1.0, "#56CFE1"),
        ]
        out: list[str] = []
        for i in range(steps):
            v = -1 + 2 * i / max(steps - 1, 1)
            for j in range(len(stops) - 1):
                v0, c0 = stops[j]
                v1, c1 = stops[j + 1]
                if v <= v1 or j == len(stops) - 2:
                    t = (v - v0) / (v1 - v0) if v1 != v0 else 0.0
                    out.append(_lerp_hex(c0, c1, t))
                    break
        return out

    CORR_PALETTE = _build_corr_palette()
    _FONT = "Figtree"
    _FONT_CANVAS = "Helvetica"

    def _apply_theme(fig, *, grid: bool = True) -> None:
        fig.background_fill_color = C["bg"]
        fig.border_fill_color = C["bg"]
        fig.outline_line_color = None
        fig.title.text_color = C["text"]
        fig.title.text_font = _FONT_CANVAS
        fig.title.text_font_size = "13pt"
        fig.title.text_font_style = "bold"
        for axis in (fig.xaxis, fig.yaxis):
            axis.axis_label_text_color = C["muted"]
            axis.major_label_text_color = C["muted"]
            axis.axis_label_text_font = _FONT_CANVAS
            axis.major_label_text_font = _FONT_CANVAS
            axis.axis_line_color = C["grid"]
            axis.major_tick_line_color = C["grid"]
            axis.minor_tick_line_color = C["grid"]
        fig.grid.visible = grid
        if grid:
            fig.grid.grid_line_color = C["grid"]
            fig.grid.grid_line_alpha = 0.55
        if fig.legend:
            fig.legend.background_fill_color = C["panel"]
            fig.legend.background_fill_alpha = 0.94
            fig.legend.border_line_color = C["grid"]
            fig.legend.label_text_color = C["text"]
            fig.legend.label_text_font = _FONT_CANVAS
        fig.toolbar.logo = None
        fig.toolbar.autohide = True
        if fig.toolbar_location is not None:
            fig.toolbar_location = "above"

    def _style_colorbar(cb) -> None:
        cb.title = None
        cb.major_label_text_color = C["muted"]
        cb.major_label_text_font = _FONT_CANVAS
        cb.major_label_text_font_size = "9pt"
        cb.background_fill_color = None
        cb.background_fill_alpha = 0
        cb.border_line_color = None

    def _corr_text_color(v: float) -> str:
        if v >= 0.45:
            return "#14141f"
        if v <= -0.45:
            return "#f4f4f8"
        if v >= 0.2:
            return "#14141f"
        return "#e8e8ff"

    # Charts and slider content: 640px default; sec2/slider use 736px inside 800px cards
    FIG_W = 640
    SLIDER_PANEL_W = 736  # fills 800px section card minus horizontal padding
    SEC2_W = SLIDER_PANEL_W
    _SLIDER_PANEL_PAD = 56  # matches 1.75rem horizontal padding × 2
    _SLIDER_HANDLE_PAD = 16  # handle bleed past track edges
    SLIDER_W = SLIDER_PANEL_W - _SLIDER_PANEL_PAD - _SLIDER_HANDLE_PAD
    _SLIDER_GAP = 20
    SLIDER_COL_W = (SLIDER_W - _SLIDER_GAP) // 2
    W_MAIN = FIG_W
    _SCATTER_GAP = 12  # matches _center_row_ss gap
    W_SCATTER = (SEC2_W - _SCATTER_GAP) // 2
    SCATTER_H = 400
    W_HEAT_PLOT = FIG_W - 64  # leave room for colorbar so total width ≈ FIG_W
    W_HEAT = FIG_W
    W_BOX = FIG_W

    # Bokeh 3 widgets use shadow DOM: page CSS cannot reach them; use InlineStyleSheet.
    _genre_panel_ss = InlineStyleSheet(
        css="""
:host {
  display: block;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  margin: 0 auto 1.25rem auto;
  padding: 1rem 1rem 0.9rem;
  border-radius: 14px;
  border: 1px solid #2e2e42;
  background: linear-gradient(135deg, rgba(86,207,225,0.12) 0%, #14141f 45%, rgba(155,93,229,0.14) 100%);
  box-shadow: 0 10px 32px rgba(0,0,0,0.35);
  overflow: hidden;
}
"""
    )
    _story_layout_ss = InlineStyleSheet(
        css="""
:host {
  width: 100% !important;
  max-width: 100% !important;
  margin-left: auto !important;
  margin-right: auto !important;
  box-sizing: border-box;
}
"""
    )
    _sec2_layout_ss = InlineStyleSheet(
        css=f"""
:host {{
  width: {SEC2_W}px !important;
  max-width: 100% !important;
  margin-left: auto !important;
  margin-right: auto !important;
  box-sizing: border-box;
}}
"""
    )
    _center_row_ss = InlineStyleSheet(
        css="""
:host {
  display: flex !important;
  flex-direction: row !important;
  justify-content: center !important;
  align-items: flex-start !important;
  gap: 12px !important;
  width: 100% !important;
  max-width: 100% !important;
  margin-left: auto !important;
  margin-right: auto !important;
  box-sizing: border-box;
}
"""
    )

    def _center_section(layout, *, width: int = FIG_W):
        """Wrap chart blocks to fill the same column as section text."""
        return column(
            layout,
            align="center",
            sizing_mode="stretch_width",
            width=width,
            stylesheets=[_story_layout_ss],
        )

    _genre_cb_ss = InlineStyleSheet(css=_genre_checkbox_css())
    _slider_panel_ss = InlineStyleSheet(
        css="""
:host {
  display: block;
  margin: 0;
  padding: 1.75rem 1.75rem 1.5rem;
  border-radius: 18px;
  border: 1px solid #2e2e42;
  background: linear-gradient(145deg, rgba(155,93,229,0.14) 0%, #14141f 40%, rgba(29,185,84,0.12) 100%);
  box-shadow: 0 16px 48px rgba(0,0,0,0.4);
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box;
  overflow: hidden;
}
"""
    )

    _slider_stack_ss = InlineStyleSheet(
        css="""
:host {
  display: block;
  width: 100% !important;
  max-width: 100% !important;
  margin: 0 0 0.5rem 0;
  box-sizing: border-box;
  overflow: hidden;
}
"""
    )

    _slider_row_ss = InlineStyleSheet(
        css="""
:host {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.25rem;
  width: 100% !important;
  max-width: 100% !important;
  margin-bottom: 0.35rem;
  box-sizing: border-box;
  overflow: hidden;
}
:host > * {
  flex: 0 1 auto;
  min-width: 0;
  max-width: calc(50% - 0.625rem);
}
"""
    )

    _results_stack_ss = InlineStyleSheet(
        css="""
:host {
  display: block;
  width: 100% !important;
  max-width: 100% !important;
  margin: 0.35rem 0 0 0;
  box-sizing: border-box;
}
"""
    )

    _panel_block_ss = InlineStyleSheet(
        css="""
:host {
  display: block;
  width: 100% !important;
  max-width: 100% !important;
  margin: 0;
  box-sizing: border-box;
}
"""
    )

    def _slider_ss(title_color: str, handle_border: str, handle_glow: str) -> InlineStyleSheet:
        return InlineStyleSheet(
            css=f"""
:host {{ display: block; margin-bottom: 0.5rem; width: {SLIDER_COL_W}px !important; max-width: 100% !important; box-sizing: border-box; overflow: hidden; }}
.bk-input-group {{
  width: 100% !important;
  max-width: 100% !important;
  margin-bottom: 0.15rem !important;
  box-sizing: border-box;
  overflow: hidden;
}}
.bk-slider {{
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box;
}}
.bk-slider-title {{
  color: {title_color} !important;
  font-weight: 700 !important;
  font-family: Figtree, system-ui, sans-serif !important;
  font-size: 0.82rem !important;
  white-space: normal !important;
  line-height: 1.3 !important;
  margin-bottom: 0.3rem !important;
  min-height: 1.9rem;
  overflow-wrap: anywhere;
}}
.bk-slider-track {{
  background: #2e2e42 !important;
  border-radius: 6px !important;
  height: 8px !important;
  max-width: 100% !important;
}}
.bk-slider-handle {{
  background: #f4f4f8 !important;
  border: 2px solid {handle_border} !important;
  border-radius: 6px !important;
  box-shadow: 0 0 12px {handle_glow} !important;
}}
"""
        )

    # ========== Chart 1 ==========
    src1 = ColumnDataSource(c1)
    p1 = figure(
        title="How popular are most songs, really?",
        x_axis_label="Number of tracks",
        y_axis_label="Popularity score (10-point bands; 0 = almost unheard, 100 = huge)",
        width=W_MAIN,
        height=480,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p1.hbar(
        y="bin_center",
        right="number_of_songs",
        height=8,
        source=src1,
        fill_color=C["green"],
        line_color=None,
        fill_alpha=0.92,
    )
    p1.add_tools(
        HoverTool(tooltips=[("Score range", "@bin_label"), ("Tracks", "@number_of_songs{0,0}")])
    )
    _apply_theme(p1)

    # ========== Chart 2a / 2b scatter (focus genres only so genre filter is meaningful) ==========
    rng = np.random.default_rng(42)
    _foc_mask = df["track_genre"].astype(str).str.lower().isin(FOCUS_GENRES)
    foc_df = df.loc[_foc_mask]
    n = min(6000, len(foc_df))
    if len(foc_df) == 0:
        raise ValueError("No tracks in focus genres: check track_genre values in dataset.csv")
    idx = rng.choice(len(foc_df), size=n, replace=False)
    sub = foc_df.iloc[idx].copy()
    _genre = sub["track_genre"].astype(str).str.lower().values

    _scatter_d = dict(
        x=sub["danceability"].values,
        y=sub["popularity"].values,
        track_name=sub["track_name"].astype(str).values,
        artists=sub["artists"].astype(str).values,
        genre=_genre,
    )
    src_d = ColumnDataSource(_scatter_d)
    src_d_all = ColumnDataSource({k: np.asarray(v).copy() for k, v in _scatter_d.items()})
    p2a = figure(
        title="Danceability vs popularity",
        x_axis_label=PLAIN["danceability"],
        y_axis_label=PLAIN["popularity"],
        width=W_SCATTER,
        height=SCATTER_H,
        tools="pan,wheel_zoom,box_zoom,reset,save",
        toolbar_location="above",
    )
    p2a.scatter(
        "x",
        "y",
        size=7,
        source=src_d,
        color=_GENRE_CMAP,
        alpha=0.55,
        line_color=None,
        marker="circle",
    )
    p2a.add_tools(
        HoverTool(
            tooltips=[
                ("Track", "@track_name"),
                ("Artist(s)", "@artists"),
                ("Danceability", "$x{0.00}"),
                ("Popularity", "$y{0}"),
            ]
        )
    )
    _apply_theme(p2a)

    _scatter_e = dict(
        x=sub["energy"].values,
        y=sub["popularity"].values,
        track_name=sub["track_name"].astype(str).values,
        artists=sub["artists"].astype(str).values,
        genre=_genre,
    )
    src_e = ColumnDataSource(_scatter_e)
    src_e_all = ColumnDataSource({k: np.asarray(v).copy() for k, v in _scatter_e.items()})
    p2b = figure(
        title="Energy vs popularity",
        x_axis_label=PLAIN["energy"],
        y_axis_label=PLAIN["popularity"],
        width=W_SCATTER,
        height=SCATTER_H,
        y_range=p2a.y_range,
        tools="pan,wheel_zoom,box_zoom,reset,save",
        toolbar_location="above",
    )
    p2b.scatter(
        "x",
        "y",
        size=7,
        source=src_e,
        color=_GENRE_CMAP,
        alpha=0.55,
        line_color=None,
        marker="circle",
    )
    p2b.add_tools(
        HoverTool(
            tooltips=[
                ("Track", "@track_name"),
                ("Artist(s)", "@artists"),
                ("Energy", "$x{0.00}"),
                ("Popularity", "$y{0}"),
            ]
        )
    )
    _apply_theme(p2b)

    # ========== Chart 2c correlation heatmap ==========
    feat_cols = ["danceability", "energy", "valence", "acousticness", "instrumentalness", "tempo"]
    cm = df[feat_cols].corr().reindex(feat_cols).T.reindex(feat_cols).T
    z = cm.values.flatten()
    xf, yf, labs, text_colors = [], [], [], []
    for ri in feat_cols:
        for cj in feat_cols:
            xf.append(cj)
            yf.append(ri)
    for v in z:
        labs.append(f"{v:.2f}")
        text_colors.append(_corr_text_color(float(v)))
    src_hm = ColumnDataSource(dict(x=xf, y=yf, v=z, lab=labs, text_color=text_colors))
    mapper = LinearColorMapper(palette=CORR_PALETTE, low=-1, high=1)
    cats = feat_cols
    p2c = figure(
        title="How audio features correlate with each other",
        x_range=FactorRange(*cats),
        y_range=FactorRange(*reversed(cats)),
        width=SEC2_W - 56,
        height=460,
        tools="hover,save,reset",
        toolbar_location="above",
        x_axis_location="above",
    )
    p2c.rect(
        x="x",
        y="y",
        width=0.92,
        height=0.92,
        source=src_hm,
        fill_color=transform("v", mapper),
        line_color=None,
        fill_alpha=0.97,
    )
    p2c.text(
        x="x",
        y="y",
        text="lab",
        text_align="center",
        text_baseline="middle",
        text_font_size="9pt",
        text_font_style="bold",
        text_color="text_color",
        text_font=value(_FONT),
        source=src_hm,
    )
    p2c.add_tools(HoverTool(tooltips=[("Pair", "@x vs @y"), ("Correlation (r)", "@lab")]))
    _cb = ColorBar(
        color_mapper=mapper,
        location=(0, 0),
        height=280,
        width=10,
        margin=10,
        border_line_color=None,
        background_fill_alpha=0,
    )
    _cb.ticker = FixedTicker(ticks=[-1, -0.5, 0, 0.5, 1])
    _style_colorbar(_cb)
    p2c.add_layout(_cb, "right")
    _apply_theme(p2c, grid=False)
    p2c.xaxis.major_label_text_font_size = "10pt"
    p2c.yaxis.major_label_text_font_size = "10pt"
    p2c.outline_line_color = C["grid"]
    p2c.outline_line_alpha = 0.35

    # ========== Chart 3 radar ==========
    RADAR_FEATURES = ["danceability", "energy", "valence", "acousticness", "tempo_norm"]
    RADAR_LABELS = [
        "Danceable",
        "Energetic",
        "Happy-sounding",
        "Acoustic",
        "Tempo",
    ]
    N = len(RADAR_FEATURES)
    # Start at top (12 o'clock) so Danceability sits centered above the chart
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False) - np.pi / 2


    def radar_xy(vals: list) -> tuple:
        vals = list(vals) + [vals[0]]
        ang = np.append(angles, angles[0])
        r = np.array(vals)
        x = r * np.cos(ang)
        y = r * np.sin(ang)
        return x, y


    RADAR_W = SEC2_W - 56

    def _radar_backdrop(fig, angles_arr) -> None:
        """Faint rings + spokes so the radar reads at a glance."""
        ring_angles = np.append(angles_arr, angles_arr[0])
        for lvl in (0.25, 0.5, 0.75, 1.0):
            fig.line(
                lvl * np.cos(ring_angles),
                lvl * np.sin(ring_angles),
                color=C["grid"],
                line_width=0.6,
                line_alpha=0.45 if lvl < 1.0 else 0.65,
            )
        for ang in angles_arr:
            fig.line(
                [0, np.cos(ang)],
                [0, np.sin(ang)],
                color=C["grid"],
                line_width=0.5,
                line_alpha=0.28,
            )

    p3 = figure(
        title="Average profile by genre (focus genres)",
        width=RADAR_W,
        height=RADAR_W,
        tools="pan,wheel_zoom,box_zoom,reset,save",
        match_aspect=True,
        x_range=Range1d(-1.42, 1.42),
        y_range=Range1d(-1.42, 1.42),
        min_border_left=36,
        min_border_right=36,
        min_border_top=36,
        min_border_bottom=28,
    )
    p3.axis.visible = False
    p3.grid.visible = False
    _radar_backdrop(p3, angles)
    for i, g in enumerate(c3["track_genre"]):
        gmean = c3[c3["track_genre"] == g].iloc[0]
        vals = [float(gmean[f]) for f in RADAR_FEATURES]
        xs, ys = radar_xy(vals)
        cds = ColumnDataSource(dict(x=xs, y=ys))
        lab = FOCUS_LABELS.get(str(g), str(g))
        gkey = str(g).lower()
        col = GENRE_COLOR.get(gkey, list(GENRE_COLOR.values())[i % len(GENRE_COLOR)])
        p3.line("x", "y", source=cds, color=col, line_width=3, alpha=0.92, legend_label=lab)
        p3.scatter(
            "x",
            "y",
            source=cds,
            color=col,
            size=10,
            alpha=0.98,
            line_color=C["text"],
            line_width=0.8,
            marker="circle",
        )

    label_r = 1.14

    def _radar_label_anchor(ang: float) -> tuple[str, str]:
        c, s = np.cos(ang), np.sin(ang)
        if s > 0.45:
            return "center", "bottom"
        if s < -0.45:
            return "center", "bottom"
        if c > 0:
            return "right", "middle"
        return "left", "middle"

    for ang, lab in zip(angles, RADAR_LABELS):
        align, baseline = _radar_label_anchor(ang)
        p3.add_layout(
            Label(
                x=float(label_r * np.cos(ang)),
                y=float(label_r * np.sin(ang)),
                text=lab,
                text_align=align,
                text_baseline=baseline,
                text_font_size="10pt",
                text_font_style="bold",
                text_color=C["text"],
                text_font=_FONT,
            )
        )

    init_vals = [0.55, 0.55, 0.55, 0.3, tempo_to_norm(75.0)]
    jx, jy = radar_xy(init_vals)
    jonas_radar = ColumnDataSource(dict(x=jx, y=jy))
    p3.line(
        "x",
        "y",
        source=jonas_radar,
        color=C["text"],
        line_width=3.5,
        line_dash="dashed",
        line_alpha=0.95,
        legend_label="Your track (sliders)",
    )
    p3.legend.location = "top_left"
    p3.legend.orientation = "vertical"
    p3.legend.click_policy = "hide"
    p3.legend.label_text_font = _FONT_CANVAS
    p3.legend.label_text_font_size = "8pt"
    p3.legend.label_text_color = C["text"]
    p3.legend.spacing = 6
    p3.legend.padding = 8
    p3.legend.margin = 6
    p3.legend.background_fill_color = C["panel"]
    p3.legend.background_fill_alpha = 0.92
    p3.legend.border_line_color = C["grid"]
    p3.legend.border_line_alpha = 0.7
    _apply_theme(p3, grid=False)
    p3.add_layout(p3.legend[0], "right")
    p3.outline_line_color = C["grid"]
    p3.outline_line_alpha = 0.35
    p3.min_border_right = 108

    # --- Chart 3b: spread of energy within each focus genre (median + quartiles) ---
    FOCUS = ["classical", "hip-hop", "jazz", "metal", "pop", "rock"]
    gdf = df[df["track_genre"].astype(str).str.lower().isin(FOCUS)]
    rows = []
    for g in FOCUS:
        s = gdf.loc[gdf["track_genre"].astype(str).str.lower() == g, "energy"]
        rows.append(
            dict(
                genre_key=g,
                genre=FOCUS_LABELS[g],
                color=GENRE_COLOR[g],
                q1=float(s.quantile(0.25)),
                q2=float(s.median()),
                q3=float(s.quantile(0.75)),
            )
        )
    src_box = ColumnDataSource(pd.DataFrame(rows))
    p3b = figure(
        title="How consistent is each genre’s energy?",
        y_range=FactorRange(*[r["genre"] for r in rows]),
        width=SEC2_W,
        height=380,
        min_border_left=88,
        min_border_right=28,
        tools="hover,save,reset",
        toolbar_location="above",
        x_axis_label=PLAIN["energy"],
    )
    p3b.hbar(
        y="genre",
        left="q1",
        right="q3",
        height=0.52,
        source=src_box,
        fill_color="color",
        fill_alpha=0.38,
        line_color="color",
        line_alpha=0.95,
        line_width=1.5,
    )
    p3b.scatter(
        x="q2",
        y="genre",
        source=src_box,
        size=14,
        color="color",
        line_color=C["text"],
        line_width=1.25,
        fill_alpha=1,
    )
    p3b.add_tools(HoverTool(tooltips=[("Genre", "@genre"), ("Median energy", "@q2{0.00}"), ("25–75% range", "@q1{0.00} – @q3{0.00}")]))
    _apply_theme(p3b)
    p3b.grid.grid_line_alpha = 0.35
    p3b.xaxis.major_label_text_font_size = "10pt"
    p3b.yaxis.major_label_text_font_size = "10pt"
    p3b.outline_line_color = C["grid"]
    p3b.outline_line_alpha = 0.35

    sec3_radar_row = row(
        p3,
        align="center",
        sizing_mode="fixed",
        width=SEC2_W,
        stylesheets=[_center_row_ss],
    )
    sec3_box_row = row(
        p3b,
        align="center",
        sizing_mode="fixed",
        width=SEC2_W,
        stylesheets=[_center_row_ss],
    )
    sec3_block = column(
        sec3_radar_row,
        Spacer(height=32, sizing_mode="fixed"),
        sec3_box_row,
        align="center",
        sizing_mode="fixed",
        width=SEC2_W,
        stylesheets=[_sec2_layout_ss],
    )

    genre_filter_help = Div(
        text=(
            '<p style="margin:0 0 0.75rem 0;font-size:0.92rem;line-height:1.55;color:#9ca3b8;">'
            '<span style="color:#1DB954;font-weight:700;">Genres shown</span>: tick styles to filter the '
            '<b style="color:#f4f4f8;">scatter plots</b> below and to highlight matching genres on the '
            '<b style="color:#f4f4f8;">mood map</b> (Section 5).'
            "</p>"
        ),
    )
    genre_cb = CheckboxGroup(
        labels=["Classical", "Hip-Hop", "Jazz", "Metal", "Pop", "Rock"],
        active=[0, 1, 2, 3, 4, 5],
        inline=True,
        stylesheets=[_genre_cb_ss],
    )
    _genre_filter_js = CustomJS(
        args=dict(src_d=src_d, src_e=src_e, src_d_all=src_d_all, src_e_all=src_e_all),
        code="""
    if (!cb_obj.active || cb_obj.active.length === 0) {
      cb_obj.active = [0, 1, 2, 3, 4, 5];
    }
    const keys = ["classical", "hip-hop", "jazz", "metal", "pop", "rock"];
    const active = new Set(cb_obj.active.map(i => keys[i]));

    function filtScatter(src, full) {
      const x = [], y = [], track_name = [], artists = [], genre = [];
      const G = full.data.genre, X = full.data.x, Y = full.data.y;
      const T = full.data.track_name, A = full.data.artists;
      for (let i = 0; i < G.length; i++) {
        if (active.has(G[i])) {
          x.push(X[i]); y.push(Y[i]); track_name.push(T[i]); artists.push(A[i]); genre.push(G[i]);
        }
      }
      src.data = {x: x, y: y, track_name: track_name, artists: artists, genre: genre};
      src.change.emit();
    }
    filtScatter(src_d, src_d_all);
    filtScatter(src_e, src_e_all);
    """,
    )
    genre_cb.js_on_change("active", _genre_filter_js)

    genre_filter_panel = column(
        genre_filter_help,
        genre_cb,
        align="start",
        sizing_mode="fixed",
        width=SEC2_W,
        stylesheets=[_genre_panel_ss],
    )
    sec2_heatmap_gap = Spacer(height=44, sizing_mode="fixed")
    sec2_scatter_note = Div(
        text=(
            '<p style="margin:0 0 0.65rem 0;font-size:0.82rem;line-height:1.45;color:#9ca3b8;text-align:center;">'
            f"Random sample of up to {n:,} tracks from the six focus genres (same songs in both charts)."
            "</p>"
        ),
        stylesheets=[_panel_block_ss],
    )
    sec2_scatter_row = row(
        p2a,
        p2b,
        align="center",
        sizing_mode="fixed",
        width=SEC2_W,
        stylesheets=[_center_row_ss],
    )
    sec2_heatmap_row = row(
        p2c,
        align="center",
        sizing_mode="fixed",
        width=SEC2_W,
        stylesheets=[_center_row_ss],
    )
    sec2_block = column(
        genre_filter_panel,
        sec2_scatter_row,
        sec2_scatter_note,
        sec2_heatmap_gap,
        sec2_heatmap_row,
        align="center",
        sizing_mode="fixed",
        width=SEC2_W,
        stylesheets=[_sec2_layout_ss],
    )

    # ========== Chart 4: hits vs non-hits (split scales so 0–1 traits stay visible) ==========
    p90 = float(df["popularity"].quantile(0.90))
    p10 = float(df["popularity"].quantile(0.10))
    hits = df[df["popularity"] >= p90]
    nonhits = df[df["popularity"] <= p10]

    def _hits_vs_nonhits_bar(
        features: list[str],
        *,
        title: str,
        y_axis_label: str,
        width: int,
        height: int = 380,
        y_range: Range1d | None = None,
        show_legend: bool = True,
    ):
        x = features
        src_hit = ColumnDataSource(
            dict(x=x, v=[float(hits[f].mean()) for f in features])
        )
        src_miss = ColumnDataSource(
            dict(x=x, v=[float(nonhits[f].mean()) for f in features])
        )
        fig = figure(
            title=title,
            x_range=FactorRange(*x),
            width=width,
            height=height,
            tools="pan,wheel_zoom,box_zoom,reset,save",
            toolbar_location=None,
        )
        if y_range is not None:
            fig.y_range = y_range
        bar_w = 0.35
        hit_kw = dict(
            x=dodge("x", -bar_w / 2, range=fig.x_range),
            top="v",
            width=bar_w,
            source=src_hit,
            color=C["green"],
            line_color=None,
        )
        miss_kw = dict(
            x=dodge("x", bar_w / 2, range=fig.x_range),
            top="v",
            width=bar_w,
            source=src_miss,
            color=C["purple_dim"],
            line_color=None,
            fill_alpha=0.85,
        )
        if show_legend:
            hit_kw["legend_label"] = "Top 10% popularity"
            miss_kw["legend_label"] = "Bottom 10% popularity"
        r_hit = fig.vbar(**hit_kw)
        r_miss = fig.vbar(**miss_kw)
        fig.x_range.range_padding = 0.12
        fig.yaxis.axis_label = y_axis_label
        fig.add_tools(
            HoverTool(
                renderers=[r_hit],
                tooltips=[("Group", "Top 10%"), ("Feature", "@x"), ("Average", "@v{0.000}")],
            )
        )
        fig.add_tools(
            HoverTool(
                renderers=[r_miss],
                tooltips=[("Group", "Bottom 10%"), ("Feature", "@x"), ("Average", "@v{0.000}")],
            )
        )
        if show_legend:
            fig.legend.background_fill_alpha = 0.0
            fig.legend.border_line_alpha = 0.0
            fig.add_layout(fig.legend[0], "right")
        fig.xaxis.major_label_orientation = 0.8
        fig.xaxis.major_label_overrides = {
            k: (PLAIN[k].split("(")[0].strip() if k in PLAIN else k) for k in x
        }
        _apply_theme(fig)
        return fig

    p4a = _hits_vs_nonhits_bar(
        ["danceability", "energy", "valence", "acousticness", "instrumentalness"],
        title="Top 10% vs bottom 10%: audio traits (0–1 scale)",
        y_axis_label="Average (0 = low, 1 = high)",
        width=W_MAIN,
        height=400,
        y_range=Range1d(0, 0.85),
    )
    _p4_half = (FIG_W - 16) // 2
    p4b = _hits_vs_nonhits_bar(
        ["loudness"],
        title="Loudness",
        y_axis_label=PLAIN["loudness"],
        width=_p4_half,
        height=340,
        y_range=Range1d(-10.5, -6.5),
        show_legend=False,
    )
    p4c = _hits_vs_nonhits_bar(
        ["tempo"],
        title="Tempo",
        y_axis_label=PLAIN["tempo"],
        width=_p4_half,
        height=340,
        y_range=Range1d(118, 123),
        show_legend=False,
    )
    sec4_block = column(
        p4a,
        row(
            p4b,
            p4c,
            align="center",
            sizing_mode="fixed",
            width=FIG_W,
            stylesheets=[_center_row_ss],
        ),
        align="center",
        sizing_mode="fixed",
        width=FIG_W,
        stylesheets=[_story_layout_ss],
    )

    # ========== Chart 5 mood map ==========
    c5 = c5.copy()
    c5["is_focus"] = c5["genre"].isin(FOCUS_GENRES)
    c5["genre_disp"] = c5["genre"].map(lambda g: FOCUS_LABELS.get(g, g.replace("-", " ").title()))
    c5["dot_color"] = c5["genre"].astype(str).str.lower().map(
        lambda g: GENRE_COLOR.get(g, C["green"])
    )
    c5_fg = c5[c5["is_focus"]].copy()
    _fg_n = len(c5_fg)
    src_fg = ColumnDataSource(
        dict(
            valence=c5_fg["valence"].values,
            energy=c5_fg["energy"].values,
            genre_disp=c5_fg["genre_disp"].values,
            dot_color=c5_fg["dot_color"].values,
            mean_popularity=c5_fg["mean_popularity"].values,
            genre=c5_fg["genre"].astype(str).str.lower().values,
            alpha=np.full(_fg_n, 0.95),
        )
    )
    src_fg_all = ColumnDataSource({k: np.asarray(v).copy() for k, v in src_fg.data.items()})
    c5_bg = c5[~c5["is_focus"]]
    _bg_n = len(c5_bg)
    src_bg = ColumnDataSource(
        dict(
            valence=c5_bg["valence"].values,
            energy=c5_bg["energy"].values,
            genre_disp=c5_bg["genre_disp"].values,
            mean_popularity=c5_bg["mean_popularity"].values,
            alpha=np.full(_bg_n, 0.35),
        )
    )
    src_bg_all = ColumnDataSource({k: np.asarray(v).copy() for k, v in src_bg.data.items()})

    p5 = figure(
        title="Where genres sit: happy ↔ sad, calm ↔ intense",
        x_axis_label="Sounds more sad ← → more happy / positive",
        y_axis_label="Sounds calmer ← → more intense",
        width=W_MAIN,
        height=540,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p5.scatter(
        "valence",
        "energy",
        source=src_bg,
        size=7,
        color=C["dot"],
        alpha="alpha",
        line_color=None,
        marker="circle",
    )
    p5.scatter(
        "valence",
        "energy",
        source=src_fg,
        size=16,
        color="dot_color",
        alpha="alpha",
        line_color=C["text"],
        line_width=0.8,
        legend_field="genre_disp",
        marker="circle",
    )
    p5.add_tools(
        HoverTool(
            tooltips=[
                ("Genre", "@genre_disp"),
                ("Valence", "@valence{0.00}"),
                ("Energy", "@energy{0.00}"),
                ("Avg. popularity", "@mean_popularity{0.0}"),
            ]
        )
    )
    jonas_mood = ColumnDataSource(dict(x=[0.55], y=[0.55]))
    p5.scatter(
        "x",
        "y",
        source=jonas_mood,
        size=24,
        color=C["text"],
        line_color=C["green"],
        line_width=2,
        legend_label="Your track",
        marker="star",
    )
    p5.legend.location = "bottom_center"
    p5.legend.label_text_font_size = "9pt"
    p5.legend.background_fill_alpha = 0.94
    p5.legend.border_line_alpha = 0.0
    p5.legend.orientation = "horizontal"
    p5.legend.spacing = 14
    p5.legend.margin = 12
    p5.legend.padding = 8
    p5.add_layout(p5.legend[0], "below")
    p5.min_border_bottom = 52
    _apply_theme(p5)

    _genre_mood_js = CustomJS(
        args=dict(src_fg=src_fg, src_fg_all=src_fg_all, src_bg=src_bg, src_bg_all=src_bg_all),
        code="""
    if (!cb_obj.active || cb_obj.active.length === 0) {
      cb_obj.active = [0, 1, 2, 3, 4, 5];
    }
    const keys = ["classical", "hip-hop", "jazz", "metal", "pop", "rock"];
    const active = new Set(cb_obj.active.map(i => keys[i]));
    const G = src_fg_all.data.genre;
    const alpha = [];
    for (let i = 0; i < G.length; i++) {
      alpha.push(active.has(G[i]) ? 0.95 : 0.12);
    }
    src_fg.data = Object.assign({}, src_fg_all.data, {alpha: alpha});
    src_fg.change.emit();
    const bgA = active.size < 6 ? 0.12 : 0.35;
    const n = src_bg_all.data.valence.length;
    src_bg.data = Object.assign({}, src_bg_all.data, {alpha: Array(n).fill(bgA)});
    src_bg.change.emit();
    """,
    )
    genre_cb.js_on_change("active", _genre_mood_js)

    # ========== Jonas panel ==========
    def _readout_html(value_html: str) -> str:
        return (
            '<div style="width:100%;box-sizing:border-box;margin-top:0.5rem;padding:1rem 1.25rem;border-radius:12px;'
            "border:1px solid #2e2e42;"
            "background:linear-gradient(90deg,rgba(29,185,84,0.18),rgba(155,93,229,0.14),rgba(86,207,225,0.12));"
            'font-size:1rem;line-height:1.5;">'
            '<span style="color:#9ca3b8;font-weight:600;">Average popularity of similar tracks:</span> '
            f'<span style="color:#1DB954;font-size:1.45rem;font-weight:800;margin:0 0.15rem;">{value_html}</span>'
            '<span style="color:#9ca3b8;font-weight:600;"> / 100</span>'
            "</div>"
        )

    _genre_moods = []
    for _gk in FOCUS_GENRES:
        _row = c5[c5["genre"].astype(str).str.lower() == _gk]
        if len(_row) == 0:
            continue
        _genre_moods.append(
            dict(
                key=_gk,
                label=FOCUS_LABELS[_gk],
                v=float(_row.iloc[0]["valence"]),
                e=float(_row.iloc[0]["energy"]),
                color=GENRE_COLOR[_gk],
            )
        )

    def _closest_genre_mood(valence: float, energy: float) -> dict:
        best = _genre_moods[0]
        best_d = 1e9
        for gm in _genre_moods:
            d = (valence - gm["v"]) ** 2 + (energy - gm["e"]) ** 2
            if d < best_d:
                best_d = d
                best = gm
        return best

    def _closest_genre_html(
        d: float, e: float, v: float, a: float, bpm: float
    ) -> str:
        mood = _closest_genre_mood(v, e)
        feat = _closest_genre_features(d, e, v, a, tempo_to_norm(bpm))
        return (
            '<p style="margin:0.45rem 0 0;font-size:0.92rem;line-height:1.5;color:#9ca3b8;">'
            "All sliders: "
            f'<b style="color:{feat["color"]}">{feat["label"]}</b>'
            " · Mood map: "
            f'<b style="color:{mood["color"]}">{mood["label"]}</b>'
            "</p>"
        )

    _sim_cols = [
        "track_name",
        "artists",
        "track_genre",
        "danceability",
        "energy",
        "valence",
        "acousticness",
        "tempo",
        "popularity",
    ]
    _missing_sim = [c for c in _sim_cols if c not in df.columns]
    if _missing_sim:
        raise ValueError(f"dataset.csv missing columns needed for similar-track matching: {_missing_sim}")
    _sim = df[_sim_cols].copy()
    _sim["track_genre"] = _sim["track_genre"].astype(str).str.lower()
    _sim = _sim[_sim["track_genre"].isin(FOCUS_GENRES)]
    if len(_sim) == 0:
        raise ValueError("No focus-genre tracks in dataset.csv for similar-track matching")
    for _c in ("danceability", "energy", "valence", "acousticness", "tempo", "popularity"):
        _sim[_c] = pd.to_numeric(_sim[_c], errors="coerce")
    _sim["track_name"] = _sim["track_name"].astype(str).replace({"nan": "Unknown track"})
    _sim["artists"] = _sim["artists"].astype(str).replace({"nan": "Unknown artist"})
    _sim = _sim.dropna(subset=["danceability", "energy", "valence", "acousticness", "tempo", "popularity"])
    _sim = _sim.reset_index(drop=True)
    _sim["genre_key"] = _sim["track_genre"]
    _sim["genre_label"] = _sim["genre_key"].map(FOCUS_LABELS)
    _sim["genre_color"] = _sim["genre_key"].map(GENRE_COLOR)
    _sim_cap = 6000
    if len(_sim) > _sim_cap:
        _sim = _sim.sample(_sim_cap, random_state=42).reset_index(drop=True)
    _sim_t_denom = (tmax - tmin) if (np.isfinite(tmax) and np.isfinite(tmin) and tmax > tmin) else 1.0
    _sim["tempo_norm"] = ((_sim["tempo"] - tmin) / _sim_t_denom).clip(0, 1)
    _sim_data = dict(
        track_name=_sim["track_name"].tolist(),
        artists=_sim["artists"].tolist(),
        genre_key=_sim["genre_key"].tolist(),
        genre_label=_sim["genre_label"].tolist(),
        genre_color=_sim["genre_color"].tolist(),
        d=_sim["danceability"].astype(float).tolist(),
        e=_sim["energy"].astype(float).tolist(),
        v=_sim["valence"].astype(float).tolist(),
        a=_sim["acousticness"].astype(float).tolist(),
        t=_sim["tempo_norm"].astype(float).tolist(),
        p=_sim["popularity"].astype(float).tolist(),
    )
    _feat_w = np.array([1.0, 1.0, 1.0, 1.0, 0.75], dtype=float)
    _genre_profiles = []
    for _gk in FOCUS_GENRES:
        _sub = _sim[_sim["genre_key"] == _gk]
        if len(_sub) == 0:
            continue
        _genre_profiles.append(
            dict(
                key=_gk,
                label=FOCUS_LABELS[_gk],
                color=GENRE_COLOR[_gk],
                d=float(_sub["danceability"].mean()),
                e=float(_sub["energy"].mean()),
                v=float(_sub["valence"].mean()),
                a=float(_sub["acousticness"].mean()),
                t=float(_sub["tempo_norm"].mean()),
            )
        )

    def _closest_genre_features(d: float, e: float, v: float, a: float, tn: float) -> dict:
        best = _genre_profiles[0]
        best_d = 1e9
        q = np.array([d, e, v, a, tn], dtype=float)
        for gp in _genre_profiles:
            g = np.array([gp["d"], gp["e"], gp["v"], gp["a"], gp["t"]], dtype=float)
            dist = float((_feat_w * (q - g) ** 2).sum())
            if dist < best_d:
                best_d = dist
                best = gp
        return best

    def _feature_distances(d: float, e: float, v: float, a: float, tn: float) -> np.ndarray:
        _w = np.array([1.0, 1.0, 1.0, 1.0, 0.75], dtype=float)
        _arr = _sim[["danceability", "energy", "valence", "acousticness", "tempo_norm"]].to_numpy(dtype=float)
        _q = np.array([d, e, v, a, tn], dtype=float)
        return ((_arr - _q) ** 2 * _w).sum(axis=1)

    def _pick_similar_indices(d: float, e: float, v: float, a: float, bpm: float, *, n: int = 3) -> tuple[dict, list[int]]:
        tn = tempo_to_norm(bpm)
        pool_g = _closest_genre_features(d, e, v, a, tn)
        dist = _feature_distances(d, e, v, a, tn)
        same = np.flatnonzero(_sim["genre_key"].values == pool_g["key"])
        pool = same if len(same) else np.arange(len(_sim))
        order = pool[np.argsort(dist[pool])]
        return pool_g, order[:n].astype(int).tolist()

    def _closest_tracks_html(d: float, e: float, v: float, a: float, bpm: float) -> str:
        best_g, _top_idx = _pick_similar_indices(d, e, v, a, bpm)
        _rows = [_sim.iloc[int(_i)] for _i in _top_idx]
        _show_genre = len({_r["genre_key"] for _r in _rows}) > 1
        _items = []
        for _row in _rows:
            _genre_bit = ""
            if _show_genre:
                _genre_bit = (
                    f' <span style="color:{_row["genre_color"]};font-size:0.82rem;font-weight:600;">'
                    f'{_row["genre_label"]}</span>'
                )
            _items.append(
                '<li style="margin:0.2rem 0;color:#f4f4f8;">'
                f'{_row["track_name"]} <span style="color:#9ca3b8;">({_row["artists"]})</span>'
                f"{_genre_bit}"
                "</li>"
            )
        return (
            '<div style="width:100%;box-sizing:border-box;margin-top:0.55rem;padding:0.75rem 1rem;border-radius:10px;'
            'border:1px solid #2e2e42;background:rgba(20,20,31,0.7);">'
            f'<p style="margin:0 0 0.35rem 0;font-size:0.88rem;color:#9ca3b8;">'
            f'Closest <strong style="color:{best_g["color"]}">{best_g["label"]}</strong> tracks:</p>'
            '<ul style="margin:0;padding-left:1rem;line-height:1.35;">'
            + "".join(_items)
            + "</ul>"
            "</div>"
        )

    explain = Div(
        text=(
            '<p style="margin:0 0 0.5rem 0;font-size:0.95rem;line-height:1.55;color:#9ca3b8;">'
            '<span style="color:#1DB954;font-weight:700;">Drag the sliders</span> to mirror your track, a demo, or a song you know. '
            'Scroll up to see the '
            '<a href="#sec-moodmap" style="color:#1ed760;text-decoration:none;font-weight:600;">mood map star</a> '
            'and '
            '<a href="#sec-genres" style="color:#1ed760;text-decoration:none;font-weight:600;">genre radar</a> '
            "move."
            "</p>"
            '<p style="margin:0 0 0.65rem 0;font-size:0.9rem;line-height:1.5;color:#9ca3b8;">'
            "The green score is the average popularity of similar tracks in the dataset. "
            "The three songs below are the closest matches using "
            "<strong style=\"color:#f4f4f8;\">all five sliders</strong> "
            "(same genre as the “All sliders” line)."
            "</p>"
            '<p class="story-slider-jumps" style="margin:0;display:flex;flex-wrap:wrap;gap:0.65rem;">'
            '<a href="#sec-moodmap" class="story-slider-jump" '
            'style="color:#c8ceda !important;text-decoration:none !important;font-size:0.82rem;font-weight:600;">'
            '↑ Mood map &amp; star</a>'
            '<a href="#sec-genres" class="story-slider-jump" '
            'style="color:#c8ceda !important;text-decoration:none !important;font-size:0.82rem;font-weight:600;">'
            '↑ Genre radar</a>'
            "</p>"
        ),
        stylesheets=[_panel_block_ss],
    )
    readout = Div(text=_readout_html("…"), stylesheets=[_panel_block_ss])
    genre_match = Div(text=_closest_genre_html(0.55, 0.55, 0.55, 0.30, 75.0), stylesheets=[_panel_block_ss])
    similar_tracks = Div(text=_closest_tracks_html(0.55, 0.55, 0.55, 0.30, 75.0), stylesheets=[_panel_block_ss])
    disclaimer = Div(
        text=(
            '<p style="margin:0.55rem 0 0;font-size:0.8rem;color:#9ca3b8;font-style:italic;">'
            "<i>Score and genres come from the dataset; tags can be imperfect.</i>"
            "</p>"
        ),
        stylesheets=[_panel_block_ss],
    )

    sd = Slider(
        start=0, end=1, value=0.55, step=0.01, title="How danceable?",
        width=SLIDER_COL_W,
        sizing_mode="fixed",
        bar_color=C["green"],
        stylesheets=[_slider_ss(C["green"], C["green"], "rgba(29,185,84,0.45)")],
    )
    se = Slider(
        start=0, end=1, value=0.55, step=0.01, title="How intense / energetic?",
        width=SLIDER_COL_W,
        sizing_mode="fixed",
        bar_color=C["purple"],
        stylesheets=[_slider_ss(C["purple"], C["purple"], "rgba(155,93,229,0.45)")],
    )
    sv = Slider(
        start=0, end=1, value=0.55, step=0.01, title="How happy / positive?",
        width=SLIDER_COL_W,
        sizing_mode="fixed",
        bar_color=C["blue"],
        stylesheets=[_slider_ss(C["blue"], C["blue"], "rgba(86,207,225,0.45)")],
    )
    sa = Slider(
        start=0, end=1, value=0.30, step=0.01, title="How acoustic?",
        width=SLIDER_COL_W,
        sizing_mode="fixed",
        bar_color=C["silver"],
        stylesheets=[_slider_ss(C["silver"], C["silver"], "rgba(232,232,255,0.35)")],
    )
    _bpm_lo = max(40, int(np.floor(tmin)))
    _bpm_hi = min(260, int(np.ceil(tmax)))
    # Default BPM chosen so (d,e,v,a,tempo_bin) exists in slider_lookup for typical slider defaults.
    _st_mid = int(np.clip(75, _bpm_lo, _bpm_hi))
    st = Slider(
        start=_bpm_lo,
        end=_bpm_hi,
        value=_st_mid,
        step=1,
        title="Tempo (BPM)",
        width=SLIDER_COL_W,
        sizing_mode="fixed",
        bar_color=C["green_hi"],
        stylesheets=[_slider_ss(C["green_hi"], C["green_hi"], "rgba(30,215,96,0.45)")],
    )

    _lut = {}
    for _, __r in lookup.iterrows():
        _k = f"{int(__r.danceability_bin)}_{int(__r.energy_bin)}_{int(__r.valence_bin)}_{int(__r.acousticness_bin)}_{int(__r.tempo_bin)}"
        _lut[_k] = float(__r.popularity)

    _angles = (np.linspace(0, 2 * np.pi, N, endpoint=False) - np.pi / 2).tolist()
    _tempo_edges = [float(x) for x in TEMPO_BINS_LOOKUP]
    _tb_js_max = int(lookup["tempo_bin"].max())

    _jonas_cb = CustomJS(
        args=dict(
            sd=sd,
            se=se,
            sv=sv,
            sa=sa,
            st=st,
            jonas_radar=jonas_radar,
            jonas_mood=jonas_mood,
            readout=readout,
            genre_match=genre_match,
            similar_tracks=similar_tracks,
            genre_moods=_genre_moods,
            genre_profiles=_genre_profiles,
            lut=_lut,
            sim_data=_sim_data,
            tempo_edges=_tempo_edges,
            tempo_tb_max=_tb_js_max,
            tmin=float(tmin),
            tmax=float(tmax),
            angles=_angles,
        ),
        code="""
    function bin01(x) {
      x = Math.max(0, Math.min(1, x));
      for (let i = 0; i < 10; i++) {
        const lo = i * 0.1, hi = (i + 1) * 0.1;
        if (i === 0) { if (x >= lo && x <= hi + 1e-12) return i; }
        else { if (x > lo && x <= hi + 1e-12) return i; }
      }
      return 9;
    }
    function tempoBin(bpm, edges, tbmax) {
      const hi = edges[edges.length - 1];
      bpm = Math.max(0, Math.min(bpm, hi));
      for (let i = 0; i < edges.length - 1; i++) {
        const lo = edges[i], hi2 = edges[i + 1];
        if (i === 0) { if (bpm >= lo && bpm <= hi2 + 1e-9) return i; }
        else { if (bpm > lo && bpm <= hi2 + 1e-9) return i; }
      }
      return tbmax;
    }
    const d = sd.value, e = se.value, v = sv.value, a = sa.value, bpm = st.value;
    const db = bin01(d), eb = bin01(e), vb = bin01(v), ab = bin01(a);
    const tb = tempoBin(bpm, tempo_edges, tempo_tb_max);
    const k = db + "_" + eb + "_" + vb + "_" + ab + "_" + tb;
    const pop = lut[k];
    const span = (tmax - tmin) || 1.0;
    const tn = Math.max(0, Math.min(1, (bpm - tmin) / span));
    const vals2 = [d, e, v, a, tn, d];
    const ang2 = angles.concat([angles[0]]);
    const xs = [], ys = [];
    for (let i = 0; i < ang2.length; i++) {
      const r = vals2[i];
      const ang = ang2[i];
      xs.push(r * Math.cos(ang));
      ys.push(r * Math.sin(ang));
    }
    jonas_radar.data = {x: xs, y: ys};
    jonas_mood.data = {x: [v], y: [e]};
    jonas_radar.change.emit();
    jonas_mood.change.emit();
    let moodBest = genre_moods[0];
    let moodBestD = 1e20;
    for (let i = 0; i < genre_moods.length; i++) {
      const g = genre_moods[i];
      const dx = v - g.v, dy = e - g.e;
      const dist = dx * dx + dy * dy;
      if (dist < moodBestD) { moodBestD = dist; moodBest = g; }
    }
    const wFeat = [1.0, 1.0, 1.0, 1.0, 0.75];
    let featBest = genre_profiles[0];
    let featBestD = 1e20;
    for (let i = 0; i < genre_profiles.length; i++) {
      const g = genre_profiles[i];
      const dd = d - g.d, de = e - g.e, dv = v - g.v, da = a - g.a, dt = tn - g.t;
      const dist = wFeat[0]*dd*dd + wFeat[1]*de*de + wFeat[2]*dv*dv + wFeat[3]*da*da + wFeat[4]*dt*dt;
      if (dist < featBestD) { featBestD = dist; featBest = g; }
    }
    const listGenre = featBest;
    genre_match.text = '<p style="margin:0.45rem 0 0;font-size:0.92rem;line-height:1.5;color:#9ca3b8;">All sliders: <b style="color:' + featBest.color + '">' + featBest.label + '</b> · Mood map: <b style="color:' + moodBest.color + '">' + moodBest.label + '</b></p>';
    const SN = sim_data.track_name;
    const SA = sim_data.artists;
    const Sg = sim_data.genre_key;
    const Sgl = sim_data.genre_label;
    const Sgc = sim_data.genre_color;
    const Sp = sim_data.p;
    const Sd = sim_data.d, Se = sim_data.e, Sv = sim_data.v, Sa = sim_data.a, St = sim_data.t;
    const wT = 0.75;
    const bestI = [-1, -1, -1];
    const bestD2 = [1e20, 1e20, 1e20];
    let poolLen = 0;
    for (let i = 0; i < SN.length; i++) {
      if (Sg[i] === listGenre.key) poolLen++;
    }
    const useGenreFilter = poolLen > 0;
    for (let i = 0; i < SN.length; i++) {
      if (useGenreFilter && Sg[i] !== listGenre.key) continue;
      const dd = d - Sd[i], de = e - Se[i], dv = v - Sv[i], da = a - Sa[i], dt = tn - St[i];
      const dist2 = dd * dd + de * de + dv * dv + da * da + wT * dt * dt;
      if (dist2 < bestD2[0]) {
        bestD2[2] = bestD2[1]; bestI[2] = bestI[1];
        bestD2[1] = bestD2[0]; bestI[1] = bestI[0];
        bestD2[0] = dist2; bestI[0] = i;
      } else if (dist2 < bestD2[1]) {
        bestD2[2] = bestD2[1]; bestI[2] = bestI[1];
        bestD2[1] = dist2; bestI[1] = i;
      } else if (dist2 < bestD2[2]) {
        bestD2[2] = dist2; bestI[2] = i;
      }
    }
    let listHtml = '';
    let popSum = 0.0;
    let popN = 0;
    const pickedGenres = new Set();
    for (let j = 0; j < bestI.length; j++) {
      if (bestI[j] < 0) continue;
      pickedGenres.add(Sg[bestI[j]]);
    }
    const showTrackGenre = pickedGenres.size > 1;
    for (let j = 0; j < bestI.length; j++) {
      if (bestI[j] < 0) continue;
      const idx = bestI[j];
      let genreBit = '';
      if (showTrackGenre) {
        genreBit = ' <span style="color:' + Sgc[idx] + ';font-size:0.82rem;font-weight:600;">' + Sgl[idx] + '</span>';
      }
      listHtml += '<li style="margin:0.2rem 0;color:#f4f4f8;">' + SN[idx] + ' <span style="color:#9ca3b8;">(' + SA[idx] + ')</span>' + genreBit + '</li>';
      popSum += Number(Sp[idx]);
      popN += 1;
    }
    similar_tracks.text = '<div style="width:100%;box-sizing:border-box;margin-top:0.55rem;padding:0.75rem 1rem;border-radius:10px;border:1px solid #2e2e42;background:rgba(20,20,31,0.7);"><p style="margin:0 0 0.35rem 0;font-size:0.88rem;color:#9ca3b8;">Closest <strong style="color:' + listGenre.color + '">' + listGenre.label + '</strong> tracks:</p><ul style="margin:0;padding-left:1rem;line-height:1.35;">' + listHtml + '</ul></div>';
    const popNear = popN > 0 ? (popSum / popN) : undefined;
    const popShow = (pop !== undefined) ? Number(pop) : popNear;
    if (popShow === undefined || Number.isNaN(popShow)) {
      readout.text = '<div class="slider-readout slider-readout-empty" style="width:100%;box-sizing:border-box;margin-top:0.5rem;"><span class="slider-readout-label">Average popularity of similar tracks:</span> <span class="slider-readout-value"><i>score unavailable</i></span></div>';
    } else {
      readout.text = '<div style="width:100%;box-sizing:border-box;margin-top:0.5rem;padding:1rem 1.25rem;border-radius:12px;border:1px solid #2e2e42;background:linear-gradient(90deg,rgba(29,185,84,0.18),rgba(155,93,229,0.14),rgba(86,207,225,0.12));font-size:1rem;"><span style="color:#9ca3b8;font-weight:600;">Average popularity of similar tracks:</span> <span style="color:#1DB954;font-size:1.45rem;font-weight:800;">' + Number(popShow).toFixed(1) + '</span><span style="color:#9ca3b8;font-weight:600;"> / 100</span></div>';
    }
    """,
    )

    for _w in (sd, se, sv, sa, st):
        _w.js_on_change("value", _jonas_cb)

    slider_stack = column(
        row(sd, se, sizing_mode="stretch_width", stylesheets=[_slider_row_ss]),
        row(sv, sa, sizing_mode="stretch_width", stylesheets=[_slider_row_ss]),
        row(st, sizing_mode="stretch_width", stylesheets=[_slider_row_ss]),
        align="center",
        sizing_mode="stretch_width",
        stylesheets=[_slider_stack_ss],
    )

    results_stack = column(
        readout,
        genre_match,
        similar_tracks,
        disclaimer,
        align="center",
        sizing_mode="stretch_width",
        stylesheets=[_results_stack_ss],
    )

    panel = column(
        explain,
        slider_stack,
        results_stack,
        align="center",
        sizing_mode="stretch_width",
        width=SLIDER_PANEL_W,
        stylesheets=[_slider_panel_ss, _story_layout_ss],
    )

    _pop0 = lookup_popularity(lookup, sd.value, se.value, sv.value, sa.value, st.value)
    if _pop0 is None:
        readout.text = _readout_html("<i>no tracks in this exact bin combo</i>; nudge a slider.")
        readout.css_classes = ["slider-readout-wrap", "slider-readout-empty"]
    else:
        readout.text = _readout_html(f"{_pop0:.1f}")
        readout.css_classes = ["slider-readout-wrap"]
    genre_match.text = _closest_genre_html(
        float(sd.value), float(se.value), float(sv.value), float(sa.value), float(st.value)
    )
    similar_tracks.text = _closest_tracks_html(float(sd.value), float(se.value), float(sv.value), float(sa.value), float(st.value))

    global _STORY_SECTIONS
    _STORY_SECTIONS = {
        "sec1": _center_section(p1),
        "sec2": sec2_block,
        "sec3": sec3_block,
        "sec4": _center_section(sec4_block),
        "sec5": _center_section(p5),
        "slider": panel,
    }
    return column(*_STORY_SECTIONS.values())


def _ensure_embed_cache() -> None:
    global _EMBED_CACHE
    if _STORY_SECTIONS is None:
        build_story_layout()
    if _EMBED_CACHE is not None:
        return
    from bokeh.embed import components

    roots = [_STORY_SECTIONS[sid] for sid in _STORY_SECTION_ORDER]
    script, divs = components(roots)
    _EMBED_CACHE = (script, divs)


def story_figure_html(section_id: str, *, centered: bool = True) -> str:
    """Return the embeddable HTML div for one story section (shared Bokeh document)."""
    _ensure_embed_cache()
    idx = _STORY_SECTION_ORDER.index(section_id)
    html = _EMBED_CACHE[1][idx]
    classes = ["story-figure-wide", "story-figure-center"]
    if section_id == "sec2":
        classes.append("story-figure-sec2")
    if section_id == "sec3":
        classes.append("story-figure-sec3")
    if section_id == "sec5":
        classes.append("story-figure-sec5")
    if not centered:
        classes.remove("story-figure-center")
    return (
        f'<div class="story-viz-rail">'
        f'<div class="{" ".join(classes)}">{html}</div>'
        f"</div>"
    )


def story_scripts_html() -> str:
    """Bokeh JS library + embed script (call once, after all section divs)."""
    from bokeh.resources import INLINE

    _ensure_embed_cache()
    tooltip_css = """
<style id="story-bokeh-tooltip-vars">
[popover="manual"] {
  --background-color: #1e1e2c;
  --color: #f4f4f8;
  --divider-color: #2e2e42;
  --icon-color: #2e2e42;
  --tooltip-arrow-color: #1e1e2c;
}
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@600;700&display=swap">
"""
    return INLINE.render_css() + INLINE.render_js() + tooltip_css + _EMBED_CACHE[0]


def story_page_extras_html() -> str:
    """Deprecated: scroll/reveal loaded via story.qmd include-after-body."""
    return ""
