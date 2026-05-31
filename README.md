# Spotify Data Story

**Group:** ad24-1-fancyproject (PODSV FS26)  
**Topic:** Why do some songs blow up on Spotify while most are never heard?

Interactive data story on **89,741 Spotify tracks** — popularity, audio features, and genre. The main product is a scrollable Quarto website with Bokeh charts and an interactive slider panel (“Try it yourself”).

---

## Where to find our deliverables

| Deliverable | Location |
|-------------|----------|
| **Live visualization** | [Open the data story](https://podsv-fs26-ad24.github.io/ad24-1-fancyproject/story.html) |
| **Documentation site** | [GitHub Pages home](https://podsv-fs26-ad24.github.io/ad24-1-fancyproject/) |
| **Project charta** (concept + personas) | [project_charta.html](https://podsv-fs26-ad24.github.io/ad24-1-fancyproject/project_charta.html) |
| **Data report** | [data_report.html](https://podsv-fs26-ad24.github.io/ad24-1-fancyproject/data_report.html) |
| **Source code & docs** | This repository |
| **Presentation slides** | [`submission pptx/ad24-1-presentation.pptx`](submission%20pptx/ad24-1-presentation.pptx) |

Start with the [landing page](https://podsv-fs26-ad24.github.io/ad24-1-fancyproject/) → **Explore the story** for the full interactive experience.

---

## What is in the visualization?

The data story (`docs/story.qmd`) walks through five sections plus a slider panel:

1. **Popularity** — how most tracks cluster at low popularity  
2. **Audio features** — scatter plots and a correlation heatmap  
3. **Genres** — radar chart and energy spread by genre  
4. **Hits vs non-hits** — comparing top and bottom tracks  
5. **Mood map** — genres positioned by valence and energy  
6. **Try it** — sliders to explore “your own track” (updates charts live)

Charts and the slider are implemented in `docs/bokeh_story.py`.

---

## Repository layout

```
docs/
  story.qmd              ← main visualization (text + embedded Bokeh figures)
  bokeh_story.py         ← all charts and slider logic
  project_charta.qmd     ← project charter (required documentation)
  data_report.qmd        ← data report (required documentation)
  index.qmd              ← landing page
data/
  chart*.csv             ← precomputed chart data (in repository)
  slider_lookup.csv      ← lookup table for slider panel
eda/                     ← scripts used to generate chart CSVs from raw data
notebooks/               ← exploratory analysis (not required to run the site)
submission pptx/
  ad24-1-presentation.pptx  ← oral presentation slides
```

The published GitHub Pages site includes **index**, **story**, **project charta**, and **data report** only. Files under `docs/reference/` are optional course-template material and are not deployed.

---

## How to run the project locally

If you want to rebuild or inspect the site on your machine:

**Requirements:** Git, [uv](https://docs.astral.sh/uv/getting-started/installation/), [Quarto](https://quarto.org/docs/get-started/)

```bash
git clone https://github.com/podsv-fs26-ad24/ad24-1-fancyproject.git
cd ad24-1-fancyproject
uv sync
curl -L -o data/dataset.csv "https://drive.switch.ch/index.php/s/Q4iQaQ3vxqzNFeY/download"
cd docs
uv run quarto preview
```

To produce a static build instead of preview:

```bash
cd docs
uv run quarto render
```

Open `docs/build/index.html` in a browser.

The raw dataset (`data/dataset.csv`, ~114k tracks) is not in the repository because of size; it is downloaded from [SwitchDrive](https://drive.switch.ch/index.php/s/Q4iQaQ3vxqzNFeY/download). Precomputed chart CSVs in `data/` are included so the charts can be inspected without the full dataset, but rendering the story executes Python that reads `dataset.csv`.

Deployment to GitHub Pages runs automatically via `.github/workflows/publish.yml` on each push to `main`.

---

## Data source

[Spotify Tracks Dataset (Kaggle)](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) — popularity score and nine audio features per track. Details on cleaning and usage are in the [data report](https://podsv-fs26-ad24.github.io/ad24-1-fancyproject/data_report.html).
