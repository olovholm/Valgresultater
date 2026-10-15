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
            party_category = parti['id'].get('partikategori')
            party_code = parti['id'].get('partikode')
            # Category 0 ('Andre', 'Andre2') sums up parties that are also listed individually,
            # and blank votes ('BLANKE') are not part of the official party percentages
            if party_category == 0 or party_code == 'BLANKE':
                continue
            party_name = parti['id'].get('navn')
            resultat = parti.get('stemmer', {}).get('resultat', {})
            antall = resultat.get('antall') or {}
            mandater = parti.get('mandater', {}).get('resultat', {}).get('antall', 0)
            facts.append({
                'year': year,
                'party_code': party_code,
                'party_name': party_name,
                'party_category': party_category,
                'votes_total': antall.get('total'),
                'votes_advance': antall.get('fhs'),
                'votes_percentage': resultat.get('prosent', 0),
                'mandates': mandater
            })

fact_df = pd.DataFrame(facts)
os.makedirs('../../data/facts', exist_ok=True)
fact_df.to_csv('../../data/facts/election_results_total.csv', index=False)
