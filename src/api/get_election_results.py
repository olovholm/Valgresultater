import requests
import os

BASE_URL = "https://valgresultat.no/api"
DATA_DIR = "../../data/raw"

os.makedirs(DATA_DIR, exist_ok=True)

metadata_resp = requests.get(f"{BASE_URL}")
metadata = metadata_resp.json()

sublinks = metadata["_sublinks"]
years = list(sublinks.keys())

election_urls = []

for year in years:
    print("Fetching URL for year:", year)
    st_items = list(filter(lambda x: x["navn"] == "st", sublinks[year]))
    if st_items:
        stortings_urls = st_items[0]["href"]
        election_urls.append(f"{BASE_URL}{stortings_urls}")


for election_url in election_urls:
    print("Fetching election data from:", election_url)
    year_data_resp = requests.get(election_url)
    year_data = year_data_resp.json()

    year = year_data["id"]["valgaar"]
    filename = os.path.join(DATA_DIR, f"election_results_{year}.json")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(year_data_resp.text)

    print(f"Saved election data for year {year} to {filename}")





