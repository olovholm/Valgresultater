import os
import json
import glob
import requests

raw_dir = '../../data/raw'
files = glob.glob(os.path.join(raw_dir, 'election_results_*.json'))
base_url = 'https://valgresultat.no/api'  # Replace with the actual base URL

for file in files:
    with open(file) as f:
        data = json.load(f)
    year = data['id']['valgaar']
    year_dir = os.path.join(raw_dir, year)
    os.makedirs(year_dir, exist_ok=True)
    for region in data['_links']['related']:
        county_path = region['href'].lstrip('/')
        url = f"{base_url}/{county_path}"
        response = requests.get(url)
        if response.status_code == 200:
            out_path = os.path.join(year_dir, f"{county_path.replace('/', '_')}.json")
            with open(out_path, 'w') as out_f:
                out_f.write(response.text)
        else:
            print(f"Failed to download {url}")
