"""Bokeh layout for the Quarto data story (auto-generated).

Regenerate from project root: ``uv run python docs/viz/generate_phase2_notebook.py``
"""

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
            "  (1) Download dataset.csv into <project>/data/ — see README / SwitchDrive.\n"
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

    c4 = pd.read_csv(DATA / "chart4_hits_vs_nonhits.csv").copy()
    c4.columns = [str(c).strip().lstrip("\ufeff") for c in c4.columns]
    if "group" not in c4.columns:
        c4 = c4.set_index(c4.columns[0])

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
        print(
            "NOTE: slider_lookup tempo bins look like 0–100 BPM (max bin index ≤ 9). "
            "The viz clips BPM to that range for the lookup table only. "
            "Re-export slider_lookup with np.arange(0, 250, 10) if you want full-range bins."
        )
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


    print("Project:", ROOT)
    print("Tracks:", len(df), "| lookup bins:", len(lookup))
    print(
        "Tempo bin edges for slider lookup (BPM):",
        [int(x) for x in TEMPO_BINS_LOOKUP],
        "→ max bin index in file",
        _lt_tb_max,
    )
    print("Chart1 columns:", list(c1.columns))
    print("Chart3 columns:", list(c3.columns))


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
    )
    from bokeh.layouts import column, row
    from bokeh.palettes import Category10, RdBu11
    from bokeh.transform import dodge, transform

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

    # ========== Chart 1 ==========
    src1 = ColumnDataSource(c1)
    p1 = figure(
        title="How popular are most songs, really?",
        x_axis_label="Popularity score (0 = almost unheard, 100 = huge)",
        y_axis_label="Number of tracks",
        width=760,
        height=380,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p1.vbar(
        x="popularity_score",
        width=0.85,
        top="number_of_songs",
        source=src1,
        fill_color="#6b7aa6",
        line_color="#333",
    )
    p1.add_tools(
        HoverTool(tooltips=[("Popularity", "@popularity_score"), ("Tracks", "@number_of_songs{0,0}")])
    )

    # ========== Chart 2a / 2b scatter (focus genres only so genre filter is meaningful) ==========
    rng = np.random.default_rng(42)
    _foc_mask = df["track_genre"].astype(str).str.lower().isin(FOCUS_GENRES)
    foc_df = df.loc[_foc_mask]
    n = min(6000, len(foc_df))
    if len(foc_df) == 0:
        raise ValueError("No tracks in focus genres — check track_genre values in dataset.csv")
    idx = rng.choice(len(foc_df), size=n, replace=False)
    sub = foc_df.iloc[idx].copy()
    _genre = sub["track_genre"].astype(str).str.lower().values

    src_d = ColumnDataSource(
        dict(
            x=sub["danceability"].values,
            y=sub["popularity"].values,
            track_name=sub["track_name"].astype(str).values,
            artists=sub["artists"].astype(str).values,
            genre=_genre,
        )
    )
    p2a = figure(
        title="Danceability vs popularity (random sample)",
        x_axis_label=PLAIN["danceability"],
        y_axis_label=PLAIN["popularity"],
        width=380,
        height=340,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p2a.scatter("x", "y", size=5, source=src_d, color="#1f77b4", alpha=0.35, marker="circle")
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

    src_e = ColumnDataSource(
        dict(
            x=sub["energy"].values,
            y=sub["popularity"].values,
            track_name=sub["track_name"].astype(str).values,
            artists=sub["artists"].astype(str).values,
            genre=_genre,
        )
    )
    p2b = figure(
        title="Energy vs popularity (same sample)",
        x_axis_label=PLAIN["energy"],
        y_axis_label=PLAIN["popularity"],
        width=380,
        height=340,
        y_range=p2a.y_range,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p2b.scatter("x", "y", size=5, source=src_e, color="#d62728", alpha=0.35, marker="circle")
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

    # ========== Chart 2c correlation heatmap ==========
    feat_cols = ["danceability", "energy", "valence", "acousticness", "instrumentalness", "tempo"]
    cm = df[feat_cols].corr().reindex(feat_cols).T.reindex(feat_cols).T
    z = cm.values
    n_f = len(feat_cols)
    xf = []
    yf = []
    for i, ri in enumerate(feat_cols):
        for j, cj in enumerate(feat_cols):
            xf.append(cj)
            yf.append(ri)
    labs = [f"{v:.2f}" for v in z.flatten()]
    src_hm = ColumnDataSource(dict(x=xf, y=yf, v=z.flatten(), lab=labs))
    mapper = LinearColorMapper(palette=RdBu11, low=-1, high=1)
    cats = feat_cols
    p2c = figure(
        title="How audio features correlate with each other",
        x_range=FactorRange(*cats),
        y_range=FactorRange(*reversed(cats)),
        width=440,
        height=400,
        tools="hover,save,reset",
        toolbar_location="right",
        x_axis_location="above",
    )
    p2c.rect(
        x="x",
        y="y",
        width=1,
        height=1,
        source=src_hm,
        fill_color=transform("v", mapper),
        line_color="#333",
    )
    p2c.text(
        x="x",
        y="y",
        text="lab",
        text_align="center",
        text_baseline="middle",
        text_font_size="9pt",
        source=src_hm,
    )
    p2c.add_tools(HoverTool(tooltips=[("Pair", "@x vs @y"), ("Correlation", "@v{0.000}")]))
    p2c.add_layout(ColorBar(color_mapper=mapper, location=(0, 0), title="r"), "right")

    # ========== Chart 3 radar ==========
    RADAR_FEATURES = ["danceability", "energy", "valence", "acousticness", "tempo_norm"]
    RADAR_LABELS = [
        "Danceable",
        "Energetic",
        "Happy-sounding",
        "Acoustic",
        "Tempo (relative)",
    ]
    N = len(RADAR_FEATURES)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)


    def radar_xy(vals: list) -> tuple:
        vals = list(vals) + [vals[0]]
        ang = np.append(angles, angles[0])
        r = np.array(vals)
        x = r * np.cos(ang)
        y = r * np.sin(ang)
        return x, y


    p3 = figure(
        title="Average profile by genre (focus genres)",
        width=520,
        height=520,
        tools="pan,wheel_zoom,box_zoom,reset,save",
        match_aspect=True,
        x_range=Range1d(-1.15, 1.15),
        y_range=Range1d(-1.15, 1.15),
    )
    p3.axis.visible = False
    p3.grid.visible = False
    palette = Category10[10]
    for i, g in enumerate(c3["track_genre"]):
        gmean = c3[c3["track_genre"] == g].iloc[0]
        vals = [float(gmean[f]) for f in RADAR_FEATURES]
        xs, ys = radar_xy(vals)
        cds = ColumnDataSource(dict(x=xs, y=ys))
        lab = FOCUS_LABELS.get(str(g), str(g))
        p3.line("x", "y", source=cds, color=palette[i % 10], line_width=2, alpha=0.85, legend_label=lab)
        p3.scatter("x", "y", source=cds, color=palette[i % 10], size=8, alpha=0.9, marker="circle")

    label_r = 1.08
    for ang, lab in zip(angles, RADAR_LABELS):
        p3.text(
            x=[label_r * np.cos(ang)],
            y=[label_r * np.sin(ang)],
            text=[lab],
            text_align="center",
            text_baseline="middle",
            text_font_size="9pt",
        )

    init_vals = [0.55, 0.55, 0.55, 0.3, tempo_to_norm(75.0)]
    jx, jy = radar_xy(init_vals)
    jonas_radar = ColumnDataSource(dict(x=jx, y=jy))
    p3.line(
        "x",
        "y",
        source=jonas_radar,
        color="#111",
        line_width=3,
        line_dash="dashed",
        legend_label="Your track (sliders)",
    )
    p3.legend.location = "top_right"
    p3.legend.click_policy = "hide"

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
                q1=float(s.quantile(0.25)),
                q2=float(s.median()),
                q3=float(s.quantile(0.75)),
            )
        )
    src_box = ColumnDataSource(pd.DataFrame(rows))
    src_box_all = ColumnDataSource(pd.DataFrame(rows))
    p3b = figure(
        title="How consistent is each genre’s energy? (median and middle 50% of tracks)",
        y_range=FactorRange(*[r["genre"] for r in rows]),
        width=520,
        height=280,
        tools="hover,save,reset",
        x_axis_label=PLAIN["energy"],
    )
    p3b.hbar(
        y="genre",
        left="q1",
        right="q3",
        height=0.45,
        source=src_box,
        fill_color="#d9c7bd",
        line_color="#666",
        legend_label="Middle 50% of tracks",
    )
    p3b.scatter(x="q2", y="genre", source=src_box, size=11, color="#333", legend_label="Median")
    p3b.add_tools(HoverTool(tooltips=[("Genre", "@genre"), ("Median energy", "@q2{0.00}"), ("25–75% range", "@q1{0.00} – @q3{0.00}")]))
    p3b.legend.location = "bottom_right"

    genre_filter_help = Div(
        text=(
            '<p style="margin:0 0 6px 0;font-size:13px"><b>Genres shown</b> — tick the styles you want in the '
            "<b>danceability / energy vs popularity</b> scatters and in the <b>energy spread</b> chart.</p>"
        )
    )
    genre_cb = CheckboxGroup(
        labels=["Classical", "Hip-Hop", "Jazz", "Metal", "Pop", "Rock"],
        active=[0, 1, 2, 3, 4, 5],
        inline=True,
    )
    _genre_filter_js = CustomJS(
        args=dict(src_d=src_d, src_e=src_e, src_box=src_box, src_box_all=src_box_all, p3b=p3b),
        code="""
    if (!cb_obj.active || cb_obj.active.length === 0) {
      cb_obj.active = [0, 1, 2, 3, 4, 5];
      return;
    }
    const keys = ["classical", "hip-hop", "jazz", "metal", "pop", "rock"];
    const active = new Set(cb_obj.active.map(i => keys[i]));

    function filtScatter(src) {
      const x = [], y = [], track_name = [], artists = [], genre = [];
      const G = src.data.genre, X = src.data.x, Y = src.data.y;
      const T = src.data.track_name, A = src.data.artists;
      for (let i = 0; i < G.length; i++) {
        if (active.has(G[i])) {
          x.push(X[i]); y.push(Y[i]); track_name.push(T[i]); artists.push(A[i]); genre.push(G[i]);
        }
      }
      src.data = {x: x, y: y, track_name: track_name, artists: artists, genre: genre};
      src.change.emit();
    }
    filtScatter(src_d);
    filtScatter(src_e);

    const gk = src_box_all.data.genre_key;
    const lab = src_box_all.data.genre;
    const q1 = src_box_all.data.q1, q2 = src_box_all.data.q2, q3 = src_box_all.data.q3;
    const glab = [], gkey = [], qq1 = [], qq2 = [], qq3 = [];
    for (let i = 0; i < gk.length; i++) {
      if (active.has(gk[i])) {
        gkey.push(gk[i]); glab.push(lab[i]); qq1.push(q1[i]); qq2.push(q2[i]); qq3.push(q3[i]);
      }
    }
    src_box.data = {genre_key: gkey, genre: glab, q1: qq1, q2: qq2, q3: qq3};
    src_box.change.emit();
    p3b.y_range.factors = glab.length ? glab : ["—"];
    """,
    )
    genre_cb.js_on_change("active", _genre_filter_js)

    sec2_block = column(genre_filter_help, genre_cb, row(p2a, p2b, p2c))

    # ========== Chart 4 ==========
    if "group" in c4.columns:
        feat_bar = [c for c in c4.columns if c != "group"]
        groups = list(c4["group"].astype(str))
        hit_vals = [float(c4.loc[c4["group"] == groups[0], f].iloc[0]) for f in feat_bar]
        miss_vals = [float(c4.loc[c4["group"] == groups[1], f].iloc[0]) for f in feat_bar]
    else:
        feat_bar = list(c4.columns)
        groups = list(c4.index.astype(str))
        hit_vals = [float(c4.loc[groups[0], f]) for f in feat_bar]
        miss_vals = [float(c4.loc[groups[1], f]) for f in feat_bar]
    x = feat_bar
    src_hit = ColumnDataSource(dict(x=x, v=hit_vals))
    src_miss = ColumnDataSource(dict(x=x, v=miss_vals))
    p4 = figure(
        title="Top 10% vs bottom 10% by popularity — average audio profile",
        x_range=FactorRange(*x),
        width=820,
        height=440,
        tools="pan,wheel_zoom,box_zoom,reset,save",
        toolbar_location=None,
    )
    w = 0.35
    r_hit = p4.vbar(
        x=dodge("x", -w / 2, range=p4.x_range),
        top="v",
        width=w,
        source=src_hit,
        color="#2ca02c",
        legend_label="Top 10% popularity",
    )
    r_miss = p4.vbar(
        x=dodge("x", w / 2, range=p4.x_range),
        top="v",
        width=w,
        source=src_miss,
        color="#bdbdbd",
        legend_label="Bottom 10% popularity",
    )
    p4.x_range.range_padding = 0.05
    p4.yaxis.axis_label = "Average value in each group"
    p4.add_tools(
        HoverTool(renderers=[r_hit], tooltips=[("Group", "Top 10%"), ("Feature", "@x"), ("Average", "@v{0.000}")])
    )
    p4.add_tools(
        HoverTool(
            renderers=[r_miss], tooltips=[("Group", "Bottom 10%"), ("Feature", "@x"), ("Average", "@v{0.000}")]
        )
    )
    p4.legend.location = "top_right"
    p4.xaxis.major_label_orientation = 0.8
    p4.xaxis.major_label_overrides = {k: (PLAIN[k].split("(")[0].strip() if k in PLAIN else k) for k in x}

    # ========== Chart 5 mood map ==========
    c5 = c5.copy()
    c5["is_focus"] = c5["genre"].isin(FOCUS_GENRES)
    c5["genre_disp"] = c5["genre"].map(lambda g: FOCUS_LABELS.get(g, g.replace("-", " ").title()))
    src_bg = ColumnDataSource(c5[~c5["is_focus"]])
    src_fg = ColumnDataSource(c5[c5["is_focus"]])

    p5 = figure(
        title="Where genres sit: happy ↔ sad, calm ↔ intense",
        x_axis_label="Sounds more sad ← → more happy / positive",
        y_axis_label="Sounds calmer ← → more intense",
        width=760,
        height=540,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p5.scatter("valence", "energy", source=src_bg, size=8, color="#bbbbbb", alpha=0.55, line_color=None, marker="circle")
    p5.scatter(
        "valence",
        "energy",
        source=src_fg,
        size=14,
        color="#e6550d",
        alpha=0.9,
        line_color="#333",
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
        size=22,
        color="#111",
        line_width=2,
        legend_label="Your track",
        marker="star",
    )
    p5.legend.location = "top_right"
    p5.legend.label_text_font_size = "9pt"

    # ========== Jonas panel ==========
    explain = Div(
        text=(
            '<div style="font-size:13px;max-width:780px">'
            "<p><b>What would your song score?</b> Drag the sliders to mirror how your track sounds. "
            "The star moves on the mood map (happy/sad vs calm/intense), the dashed line on the radar compares your shape "
            "to the genre averages, and the figure below is the <i>average popularity</i> of real tracks whose features fall "
            "in the same bins — not a forecast.</p></div>"
        ),
    )
    readout = Div(text='<div style="font-size:13px;max-width:780px"><b>Matching-bin average popularity:</b> — / 100</div>')
    disclaimer = Div(
        text='<p style="color:#555;font-size:12px;max-width:780px"><i>This is the average for tracks with similar features — not a prediction.</i></p>',
    )

    sd = Slider(start=0, end=1, value=0.55, step=0.01, title="How danceable? (0 = not, 1 = very)")
    se = Slider(start=0, end=1, value=0.55, step=0.01, title="How intense / energetic?")
    sv = Slider(start=0, end=1, value=0.55, step=0.01, title="How happy / positive does it sound?")
    sa = Slider(start=0, end=1, value=0.30, step=0.01, title="How acoustic (not electronic)?")
    _bpm_lo = max(40, int(np.floor(tmin)))
    _bpm_hi = min(260, int(np.ceil(tmax)))
    # Default BPM chosen so (d,e,v,a,tempo_bin) exists in slider_lookup for typical slider defaults.
    _st_mid = int(np.clip(75, _bpm_lo, _bpm_hi))
    st = Slider(start=_bpm_lo, end=_bpm_hi, value=_st_mid, step=1, title="Tempo (BPM)")

    _lut = {}
    for _, __r in lookup.iterrows():
        _k = f"{int(__r.danceability_bin)}_{int(__r.energy_bin)}_{int(__r.valence_bin)}_{int(__r.acousticness_bin)}_{int(__r.tempo_bin)}"
        _lut[_k] = float(__r.popularity)

    _angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
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
            lut=_lut,
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
    if (pop === undefined) {
      readout.text = '<div style="font-size:13px;max-width:780px"><b>Matching-bin average popularity:</b> <i>no tracks in this exact bin combo</i> — nudge a slider.</div>';
    } else {
      readout.text = '<div style="font-size:13px;max-width:780px"><b>Matching-bin average popularity:</b> ' + Number(pop).toFixed(1) + ' / 100</div>';
    }
    """,
    )

    for _w in (sd, se, sv, sa, st):
        _w.js_on_change("value", _jonas_cb)

    panel = column(explain, row(sd, se), row(sv, sa), st, readout, disclaimer)

    _pop0 = lookup_popularity(lookup, sd.value, se.value, sv.value, sa.value, st.value)
    if _pop0 is None:
        readout.text = (
            '<div style="font-size:13px;max-width:780px"><b>Matching-bin average popularity:</b> '
            "<i>no tracks in this exact bin combo</i> — nudge a slider.</div>"
        )
    else:
        readout.text = (
            f'<div style="font-size:13px;max-width:780px"><b>Matching-bin average popularity:</b> '
            f"{_pop0:.1f} / 100</div>"
        )

    full = column(p1, sec2_block, p3, p3b, p4, p5, panel)
    return full
