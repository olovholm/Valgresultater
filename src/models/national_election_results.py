import pandas as pd
import json
import glob
import os

files = glob.glob('../../data/raw/election_results_*.json')
facts = []

for file in files:
    with open(file) as f:
        data = json.load(f)
        year = data['id']['valgaar']
        for parti in data.get('partier', []):
            party_code = parti['id'].get('partikode')
            party_name = parti['id'].get('navn')
            votes = parti.get('stemmer', {}).get('resultat', {}).get('prosent', 0)
            mandater = parti.get('mandater', {}).get('resultat', {}).get('antall', 0)
            facts.append({
                'year': year,
                'party_code': party_code,
                'party_name': party_name,
                'votes_percentage': votes,
                'mandates': mandater
            })




fact_df = pd.DataFrame(facts)
os.makedirs('../../data/facts', exist_ok=True)
fact_df.to_csv('../../data/facts/election_results_total.csv', index=False)
