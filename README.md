# Valgresultater

This project processes and analyzes Norwegian election results data, including county, municipality, and party vote statistics. The data is organized into dimension and fact tables for further analysis.

## Directory Structure

- `data/raw/` — Raw JSON files for each election year, county, and municipality.
- `data/dimensions/` — Dimension tables for counties, municipalities, parties, regions, and elections.
- `data/facts/` — Fact tables with election results and top municipalities per party.
- `src/` — Source code for data extraction, transformation, and analysis.
- `src/app/` — Streamlit app, and `election_data.py` with data loading and party colours shared with the notebooks.

## Data Source

Election data is sourced from the official Valgdirektoratet API at [valgresultat.no](https://valgresultat.no).  
All credits for the data go to Valgdirektoratet.


## Usage
### Install dependencies
```bash
pip install -r requirements.txt
```

### Load data for analysis
Download the raw data from the API and build the dimension and fact tables:
```bash
python run_scripts.py
```
The analysis scripts in `src/anlysis/` are run separately, from their own directory.

### Explore the results
- Streamlit app with key figures, results per election, mandates, trends and turnout:
  ```bash
  streamlit run src/app/streamlit_app.py
  ```
- Notebook with the same views as static charts: `src/notebooks/national_election_results.ipynb`


## Roadmap
Planned fixes and ideas for insights are tracked in [ROADMAP.md](ROADMAP.md) (in Norwegian).
