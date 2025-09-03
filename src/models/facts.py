import pandas as pd
import json
import glob

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
            votes = party.get('stemmer', None)  # adjust to your metric
            facts.append({
                'election_id': election_id,
                'region_id': region_id,
                'party_code': party_code,
                'votes': votes
            })

fact_df = pd.DataFrame(facts)
fact_df.to_csv('../../data/facts/election_results.csv', index=False)
