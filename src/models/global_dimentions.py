import pandas as pd
import json
import glob
import os

# Find all election result files
files = glob.glob('../../data/raw/election_results_*.json')

elections = []
parties = []
regions = []

for file in files:
    with open(file) as f:
        data = json.load(f)
    elections.append(data['id'])
    party_dim = pd.json_normalize(data['partier'], sep='_')
    parties.append(party_dim[['id_partikode', 'id_navn', 'id_partikategori']])
    region_dim = pd.json_normalize(data['_links']['related'])
    regions.append(region_dim[['nr', 'navn']])

# Aggregate and deduplicate
election_df = pd.DataFrame(elections).drop_duplicates()
party_df = pd.concat(parties).drop_duplicates()
region_df = pd.concat(regions).drop_duplicates()

os.makedirs('../../data/dimensions', exist_ok=True)

election_df.to_csv('../../data/dimensions/elections.csv', index=False)
party_df.to_csv('../../data/dimensions/parties.csv', index=False)
region_df.to_csv('../../data/dimensions/regions.csv', index=False)
