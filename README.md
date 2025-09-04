# Valgresultater

This project processes and analyzes Norwegian election results data, including county, municipality, and party vote statistics. The data is organized into dimension and fact tables for further analysis.

## Directory Structure

- `data/raw/` — Raw JSON files for each election year, county, and municipality.
- `data/dimensions/` — Dimension tables for counties, municipalities, parties, regions, and elections.
- `data/facts/` — Fact tables with election results and top municipalities per party.
- `src/` — Source code for data extraction, transformation, and analysis.

## Data Source

Election data is sourced from the official Valgdirektoratet API at [valgresultat.no](https://valgresultat.no).  
All credits for the data go to Valgdirektoratet.


## Usage
### Load data for analysis
- First run the API script to download the raw data:
  ```bash
  python src/api/get_election_results.py
  python src/api/get_counties.py
  python src/api/get_municipalities.py
  ```
- Then run the scripts in models
- Finally run the analysis scripts in analysis


