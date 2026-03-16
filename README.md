# Reel Connections
[![Coverage Status](https://coveralls.io/repos/github/Shilord/Data515_MediaAnalysis_FinalProj/badge.svg?branch=main)](https://coveralls.io/github/Shilord/Data515_MediaAnalysis_FinalProj?branch=main)
![Workflow Status](https://github.com/Shilord/Data515_MediaAnalysis_FinalProj/actions/workflows/build_test.yml/badge.svg)  

**Project Members:** Owen Guo, Zach Lubarsky, Henry Shi, Daniel Yan

**Project Type:** Web App/Tool

**Questions of Interest:** Can you identify and categorize movies and television series based on their metadata alone and what kinds of connections can you find between seemingly unrelated pieces of media?

**Project Output:** An interactive web app that allows you to play game(s) involving movies and actors. Specifically, a connection based game similar to the Wiki Game (https://www.thewikigame.com) where you are required to jump from a movie to a different one by using shared metadata, inspired by the Six Degrees of Kevin Bacon.

**Data Sources:** 
- IMDb's Non-Commercial Datasets for movie and actor lists: https://developer.imdb.com/non-commercial-datasets/
- TMDb API for additional information not found on the IMDb datasets: https://developer.themoviedb.org/docs/getting-started
- Inflation Data provided by the US Bureau of Labor Statistics: https://data.bls.gov/timeseries/CUUR0000SA0L1E?output_view=pct_12mths 

---

## Setting Up the Virtual Environment

This project uses **Conda** to manage dependencies and ensure a consistent environment across all collaborators.

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download) installed on your machine.

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/Shilord/Data515_MediaAnalysis_FinalProj.git
cd Data515_MediaAnalysis_FinalProj
```

**2. Create the conda environment**

This installs Python 3.13 and all required dependencies defined in `environment.yml`:
```bash
conda env create -f environment.yml
```

**3. Activate the environment**
```bash
conda activate reel-connections
```

You should see `(reel-connections)` at the start of your terminal prompt confirming the environment is active.

**4. Run the app**
```bash
cd 515_streamlit
streamlit run app.py
```

### Updating the Environment

If dependencies change (e.g. after pulling new changes), update your local environment:
```bash
conda env update -f environment.yml --prune
```

The `--prune` flag removes any packages that are no longer needed.

### Deactivating the Environment

When you're done working:
```bash
conda deactivate
```

### Removing the Environment

If you need to start fresh:
```bash
conda remove --name reel-connections --all
```

---

## Running Tests

From the repo root with the environment active:
```bash
cd 515_streamlit
coverage run -m unittest discover -s tests -t tests
coverage report
```

## Running the Linter

```bash
pylint --recursive=y --source-roots=515_streamlit 515_streamlit/core/
pylint --recursive=y --source-roots=515_streamlit 515_streamlit/tests/
```
