# Presentation assets

Extracted from `presentation.pptx` (Angelina, project root):

| File | Source | Used on |
|------|--------|---------|
| `from-pptx/spotify-notes.svg` | pptx media/image1.svg | Title & closing slide |
| `from-pptx/lena.jpeg` | pptx media/image2.jpeg | Lena persona slide |
| `from-pptx/jonas.jpeg` | pptx media/image3.jpeg | Jonas persona slide |
| `wave-accent.svg` | project | Title slide decoration |
| `findings/finding-01-popularity.png` | `export_presentation_charts.py` | Finding slide 01 |
| `findings/finding-02-correlations.png` | same | Finding slide 02 |
| `findings/finding-03-genre-radar.png` | same | Finding slide 03 |
| `findings/finding-04-hits.png` | same | Finding slide 04 |

**Regenerate finding charts** (after data changes):

```bash
cd <project-root>
uv run python docs/export_presentation_charts.py
cd docs && uv run quarto render presentation.qmd
```

To update persona images from PowerPoint: replace files in `from-pptx/`, then re-render.
