# Reel Connections
[![Coverage Status](https://coveralls.io/repos/github/Shilord/Data515_MediaAnalysis_FinalProj/badge.svg?branch=main)](https://coveralls.io/github/Shilord/Data515_MediaAnalysis_FinalProj?branch=main)
![Workflow Status](https://github.com/Shilord/Data515_MediaAnalysis_FinalProj/actions/workflows/build_test.yml/badge.svg)  

## Background
**Project Members:** Owen Guo, Zach Lubarsky, Henry Shi, Daniel Yan

**Project Type:** Web App/Game

**Questions of Interest:** Can you reach a target actor from a starting actor by selecting movie + actor combinations in between?

**Project Output:** 

This project aims to create a web app that allows users to test their movie and actor knowledge in the form of a game inspired by popular parlor game [Six Degrees of Kevin Bacon](https://en.wikipedia.org/wiki/Six_Degrees_of_Kevin_Bacon). In this game, users are given a random starting actor and random target actor. They then connect the starting actor to another actor through a film they both appear in, and repeat until they reach the target actor. The goal of the game is to reach the target actor in as few movie + actor combinations as possible. An alternate, more challenging game mode is featured as well, in which players once again choose movie + actor combinations to reach the target actor, but score higher the lower the total box office sales (adjusted for inflation) of their chosen movies is, incentivizing creative picks of less well-known movies over simply the shortest path to the target actor.

On the back-end of this web app, several datasets have be created, processed, and synthesized to form the necessary web of connections between actors and movies: 1) a list of actor data, 2) a comprehensive dataset of movies and cast with box office sales, and 3) a dataset containing inflation indices for the relevant time frame. The information is stored into efficient nested dictionaries and search algorithms are used calculate the optimal solution for both game modes. Scores are given to players based on how far their selections deviate from the optimal.

Through the development of this web app, we seek to enforce strong data science and software engineering practices including: 1) data acquisition, cleaning, merging, and analysis, 2) unit testing and modular programming, 3) writing code and algorithms for game/app logic, and 4) designing a smooth UI experience with all of the data science and code abstracted away. We hope to provide an engaging and seamless game for users to enjoy.

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
