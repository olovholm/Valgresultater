import os
import json
import glob
import pandas as pd

raw_dir = '../../data/raw'
years = [d for d in os.listdir(raw_dir) if d.isdigit()]
party_muni_votes = []

for year in years:
    year_path = os.path.join(raw_dir, year)
    county_dirs = [d for d in os.listdir(year_path) if d.isdigit()]
    for county_nr in county_dirs:
        county_path = os.path.join(year_path, county_nr)
        muni_jsons = glob.glob(os.path.join(county_path, '*.json'))
        for muni_json in muni_jsons:
            with open(muni_json) as f:
                data = json.load(f)
            muni_nr = data['id']['nr']
            muni_name = data['id']['navn']
            for party in data.get('partier', []):
                party_code = party['id'].get('partikode')
                party_name = party['id'].get('navn')
                votes = party.get('stemmer',{}).get('resultat',{}).get('prosent',0)

                if isinstance(party_code, (str, int)) and isinstance(votes, (int, float)):
                    party_muni_votes.append({
                        'year': year,
                        'county_nr': county_nr,
                        'municipality_nr': muni_nr,
                        'municipality_name': muni_name,
                        'party_code': party_code,
                        'party_name': party_name,
                        'votes': votes
                    })

df = pd.DataFrame(party_muni_votes)
top10 = (
    df.sort_values(['party_code', 'votes'], ascending=[True, False])
    .groupby('party_code')
    .head(10)
)

top10.to_csv('../../data/facts/top10_municipalities_per_party.csv', index=False)
