import os
import json
import glob
import requests

base_url = 'https://valgresultat.no/api'  # Replace with actual base URL
years = ['2009', '2013', '2017', '2021', '2025']
raw_dir = '../../data/raw'

for year in years:
    county_files = glob.glob(os.path.join(raw_dir, year, f'{year}_st_*.json'))
    for county_file in county_files:
        with open(county_file) as f:
            data = json.load(f)
        county_nr = data['id']['nr']
        county_dir = os.path.join(raw_dir, year, county_nr)
        os.makedirs(county_dir, exist_ok=True)
        for muni in data['_links']['related']:
            muni_path = muni['href'].lstrip('/')
            url = f"{base_url}/{muni_path}"
            response = requests.get(url)
            if response.status_code == 200:
                muni_nr = muni['nr']
                out_path = os.path.join(county_dir, f"{muni_nr}.json")
                with open(out_path, 'w') as out_f:
                    out_f.write(response.text)
            else:
                print(f"Failed to download {url}")
