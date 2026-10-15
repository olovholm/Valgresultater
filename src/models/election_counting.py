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
        stemmer = data.get('stemmer', {})
        # 'opptalt' is missing from the 2025 schema, which uses 'opptellingsStatus' instead
        opptalt = data.get('opptalt') or {}

        facts.append({
            'year': year,
            'total_mandates': data.get('mandater', {}).get('antall'),
            'eligible_voters': data.get('antallsb'),
            'total_votes': stemmer.get('total'),
            'advance_votes': stemmer.get('fhs'),
            'rejected_votes': stemmer.get('totalForkastede'),
            'turnout_percentage': data.get('frammote', {}).get('prosent'),
            'counted_percentage': opptalt.get('endelig')
        })

fact_df = pd.DataFrame(facts)
os.makedirs('../../data/facts', exist_ok=True)
fact_df.to_csv('../../data/facts/election_counting.csv', index=False)
