import pandas as pd
import json
import glob
import os

files = glob.glob('../../data/raw/election_results_*.json')
facts = []

for file in files:
    with open(file) as f:
        data = json.load(f)
    election_id = data['id']['valgaar']  # or a composite key
    for region in data['_links']['related']:
        region_id = region['nr']
        for party in data['partier']:
            party_code = party['id']['partikode']
            percent = party.get('stemmer', {}).get('resultat', {}).get('prosent', 0)
            votes = party.get('stemmer', {}).get('resultat',{}).get('antall', {}).get('total', 0)  # adjust to your metric
            facts.append({
                'valg_id': election_id,
                'region': region_id,
                'parti_kode': party_code,
                'prosent': percent,
                'stemmer': votes
            })

fact_df = pd.DataFrame(facts)
os.makedirs('../../data/facts', exist_ok=True)
fact_df.to_csv('../../data/facts/election_results_per_county.csv', index=False)
