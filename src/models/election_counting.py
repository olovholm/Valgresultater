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
        mandater = data.get('mandater', {}).get('antall', 0)
        fhs_stemmer = data.get('stemmer', {}).get('fhs', 0)
        fhs_forkastede = data.get('stemmer', {}).get('fhs_forkastede', 0)
        total = data.get('stemmer', {}).get('total', 0)
        totalt_forkastede = data.get('stemmer', {}).get('totalt_forkastede', 0)
        stemmegivning = data.get('stemmegivning', {}).get('antall', 0)
        fremmotte = data.get('fremmotte', {}).get('antall', 0)
        opptalt = data.get('opptalt', {}).get('prosent', 0)


        facts.append({
            'year': year,
            'total_mandates': mandater,
            'total_votes': stemmegivning,
            'total_attendance': fremmotte,
            'total_counted_percentage': opptalt
        })



fact_df = pd.DataFrame(facts)
os.makedirs('../../data/facts', exist_ok=True)
fact_df.to_csv('../../data/facts/election_counting.csv', index=False)
