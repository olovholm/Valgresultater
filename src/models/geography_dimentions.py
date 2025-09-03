import os
import json
import glob
import pandas as pd

raw_dir = '../../data/raw'
years = [d for d in os.listdir(raw_dir) if d.isdigit()]
counties = []
municipalities = []

for year in years:
    year_path = os.path.join(raw_dir, year)
    # County folders are named by county number (e.g., '01', '02', ...)
    county_dirs = [d for d in os.listdir(year_path) if d.isdigit()]
    for county_nr in county_dirs:
        county_path = os.path.join(year_path, county_nr)
        # Find county JSON file (e.g., '2009_st_01.json')
        county_jsons = glob.glob(os.path.join(year_path, f'*_st_{county_nr}.json'))
        for county_json in county_jsons:
            with open(county_json) as f:
                data = json.load(f)
            counties.append({'year': year, 'nr': data['id']['nr'], 'navn': data['id']['navn']})
        # Municipality JSONs (e.g., '0301.json')
        muni_jsons = glob.glob(os.path.join(county_path, '*.json'))
        for muni_json in muni_jsons:
            with open(muni_json) as f:
                data = json.load(f)
            municipalities.append({'year': year, 'county_nr': county_nr, 'nr': data['id']['nr'], 'navn': data['id']['navn']})

# Aggregate and deduplicate
county_df = pd.DataFrame(counties).drop_duplicates()
muni_df = pd.DataFrame(municipalities).drop_duplicates()

os.makedirs('../../data/dimensions', exist_ok=True)
county_df.to_csv('../../data/dimensions/counties.csv', index=False)
muni_df.to_csv('../../data/dimensions/municipalities.csv', index=False)
