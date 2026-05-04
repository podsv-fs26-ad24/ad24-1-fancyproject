# Spotify Data Story

An interactive data story exploring what makes Spotify tracks popular — built as a scrollable webpage with charts, plain-language insights, and no maths degree required.

**Live site:** [podsv-fs26-ad24.github.io/ad24-1-fancyproject](https://podsv-fs26-ad24.github.io/ad24-1-fancyproject/)

---

## Quickstart — Run it from scratch

Everything you need to go from a fresh clone to a running local website.

### Prerequisites

Install these once before you start:

| Tool | Install |
|------|---------|
| Git | [git-scm.com](https://git-scm.com) |
| uv (Python package manager) | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Quarto | [quarto.org/docs/get-started](https://quarto.org/docs/get-started/) |

> Python 3.12 is installed automatically by `uv sync` — you do **not** need to install it separately.

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/podsv-fs26-ad24/ad24-1-fancyproject.git
cd ad24-1-fancyproject
```

**2. Set up the Python environment**
```bash
uv sync
```
This installs Python 3.12 and all required packages (bokeh, pandas, matplotlib, seaborn, jupyter, ydata-profiling, etc.) into a local `.venv` folder.

**3. Download the dataset**

macOS / Linux:
```bash
curl -L -o data/dataset.csv "https://drive.switch.ch/index.php/s/Q4iQaQ3vxqzNFeY/download"
```

Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri "https://drive.switch.ch/index.php/s/Q4iQaQ3vxqzNFeY/download" -OutFile "data/dataset.csv"
```

Or download manually — see the [Dataset](#dataset) section below.

**4. Create your `.env` file**
```bash
# macOS / Linux
cp .env.template .env

# Windows (PowerShell)
Copy-Item .env.template .env
```

**5. Preview the documentation website**
```bash
cd docs
uv run quarto preview
```
This opens the site in your browser at a local URL (e.g. `http://localhost:4396`).

To build a static version instead: run `uv run quarto render` from the `docs` folder. The output goes to `docs/build/`.

---

## Dataset

The project uses the [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) from Kaggle (~114,000 songs, each with a popularity score and 9 audio features).

The dataset is hosted on SwitchDrive so no Kaggle account is required.

**To download the dataset:**
1. Download `dataset.csv` directly: [https://drive.switch.ch/index.php/s/Q4iQaQ3vxqzNFeY/download](https://drive.switch.ch/index.php/s/Q4iQaQ3vxqzNFeY/download)
2. Place the file in the `data/` folder: `data/dataset.csv`.

Or from the command line:

macOS / Linux:
```bash
curl -L -o data/dataset.csv "https://drive.switch.ch/index.php/s/Q4iQaQ3vxqzNFeY/download"
```

Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri "https://drive.switch.ch/index.php/s/Q4iQaQ3vxqzNFeY/download" -OutFile "data/dataset.csv"
```

The `data/` folder is already in `.gitignore` — do **not** commit the raw dataset to GitHub.

## Project Organisation
The visualization product development is organised according to the following process model:

![The visualization product development process](docs/pics/vizproductprocess.png)

Code and configurations used in the different project phases are stored in the correspoding subfolders. Documentation artefacts in the form of a Quarto project are provided in `docs`.

| Phase | Code folders | Documentation section | `docs`-File |
|:-------|:---|:---|:---|
| Project Understanding | -  | Project Charta | project_charta.qmd  |
| Data Acquisition and Exploration | `eda` | Data Report | data_report.qmd  |
| Visual Encoding and Design | `encoding-design`  | Visual Encoding and Design | viz_encoding_design.qmd  |
| Evaluation | `evaluation`  | Evaluation | evaluation.qmd  |
| Deployment | `deployment` | Deployment | deployment.qmd |

See the [Quarto Setup and Usage](#quarto-setup-and-usage) section for instructions on how to build and serve the documentation website locally.

## Python Environment Setup and Management with uv
Make sure to have uv installed: https://docs.astral.sh/uv/getting-started/installation/

After cloning the repository,  create the python environment with all dependencies based on the `.python-version`, `pyproject.toml` and `uv.lock` files by running
```bash
uv sync
```

To add new dependencies, use
```bash
uv add <package>
```
which will add the package to `pyproject.toml` and update the `uv.lock` file. You can also specify a version, e.g. `uv add pandas==2.0.3`.

Remove packages with
```bash
uv remove <package>
```

Commit changes to `pyproject.toml` and `uv.lock` files into version control.

Run `uv sync` after pulling changes to update the local environment.

Whenever the python environment is used, make sure to prefix every command that uses python with `uv run`, e.g.
```bash
uv run python script.py
```

You can also run
```bash 
source .venv/bin/activate
```
to activate the project Python environment in a terminal session in order to avoid having to prefix every command.

## Runtime Configuration with Environment Variables
The environment variables are specified in a .env-File, which is never commited into version control, as it may contain secrets. The repo just contains the file `.env.template` to demonstrate how environment variables are specified.

You have to create a local copy of `.env.template` in the project root folder and the easiest is to just rename it to `.env`.

The content of the .env-file is then read by the pypi-dependency: `python-dotenv`. Usage:
```python
import os
from dotenv import load_dotenv
```

`load_dotenv` reads the .env-file and sets the environment variables:

```python
load_dotenv()
```

which can then be accessed (assuming the file contains a line `SAMPLE_VAR=<some value>`):

```python
os.environ['SAMPLE_VAR']
```

## Quarto Setup and Usage

### Setup Quarto

1. [Install Quarto](https://quarto.org/docs/get-started/)
2. Optional: [quarto-extension for VS Code](https://marketplace.visualstudio.com/items?itemName=quarto.quarto)
3. If working with svg files and pdf output you will need to install rsvg-convert:
    * On macOS: `brew install librsvg`
    * On Windows using chocolatey:
      * [Install chocolatey](https://chocolatey.org/install#individual)
      * [Install rsvg-convert](https://community.chocolatey.org/packages/rsvg-convert): `choco install rsvg-convert`

Source `*.qmd` and configuration files are in the `docs` folder. The Quarto project configuration is in `docs/_quarto.yml`.

With embedded python code chunks that perform computations, you need to make sure that the python environment is activated when rendering. This can be done by prefixing the render command with `uv run`, e.g.:
```bash
uv run quarto render
```

### Working on the Documentation

1. Make changes to the `.qmd` source files in the `docs` folder
2. Make sure the project Python environment is activated (see Python environment setup and management)
3. Preview locally: `quarto preview` from the `docs` folder
4. Build the documentation website: `uv run quarto render` from the `docs` folder. This renders to `docs/build`
5. Check the website locally by opening `docs/build/index.html` in a browser

### Deployment of the Documentation to GitHub Pages

The documentation website is deployed to GitHub Pages via a GitHub Actions workflow (`.github/workflows/publish.yml`). Every push to `main` triggers the workflow, which renders the Quarto project and deploys the result.

The setting `execute: freeze: auto` in `_quarto.yml` ensures that Python computations are only executed locally. Results are cached in `docs/_freeze` and checked into the repository, so the GitHub Actions runner does not need Python — it uses the pre-computed results.

#### Initial Setup (once)

1. In the GitHub repository settings, go to **Settings > Pages** and set the source to **GitHub Actions**
2. Render locally so that `_freeze` contains cached computation results:
   ```bash
   cd docs && uv run quarto render
   ```
3. Push the changes to `main`

The `_freeze` directory and the workflow file `.github/workflows/publish.yml` should already be tracked in the repository.


#### Publishing Updates

1. Build the website locally: `uv run quarto render` from the `docs` folder. This updates `docs/build` (gitignored) and `docs/_freeze` (checked in)
2. Check the website locally by opening `docs/build/index.html`
3. Commit and push all updated files (including `docs/_freeze`) to `main`. The GitHub Actions workflow will render and deploy the site automatically
