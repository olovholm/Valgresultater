# Veikart

Mål: gjøre Valgresultater til en tjeneste der man kan utforske og finne innsikt i norske valgresultater – fra landsnivå helt ned til stemmekrets.

Fasene bygger på hverandre: innsikt er lite verdt før dataene er riktige.

## Fase 1 – Rette datafeil

- [x] **Last ned 2025-data på nytt.** `data/raw/election_results_2025.json` er et valgnattsnapshot (`rapportGenerert` 2025-09-08T21:00:45, 2 093 254 av 3 246 318 stemmer talt). Kommunefilene for 2025 er generert 2025-09-01 – før valget – og inneholder bare nuller. API-et har nå endelige tall (FrP 47 / MDG 8 / V 3, mot 49 / 7 / 2 lokalt).
  - [ ] Lagre `tidspunkt.rapportGenerert` og sjekk at opptellingen er ferdig før data tas i bruk (`opptalt.endelig == 100` for eldre år, `opptellingsStatus` fra 2025).
- [x] **Filtrer bort «Andre»/«Andre2» (`partikategori == 0`).** Samlepost for småpartier som gir dobbelttelling – mandatsummen blir 170 i 2013 og 2021.
  - [x] Blanke stemmer (`BLANKE`) er også ført som et parti, men holdes utenfor de offisielle partiprosentene. De ligger nå som `blank_votes` i `election_counting.csv`.
- [x] **Fiks feltnavn i `src/models/election_counting.py`.** `stemmegivning`, `fremmotte` og `opptalt.prosent` finnes ikke, så `election_counting.csv` er bare nuller. Riktige felt: `stemmer.total`, `stemmegiving`, `frammote.prosent`, `antallsb`. Merk at 2025 har et annet skjema (`opptellingsStatus` i stedet for `opptalt`/`prognose`).
- [ ] **Stier relativt til `__file__`.** Alle skript bruker `../../data`, så `run_scripts.py` (som kjøres fra roten) peker utenfor repoet.
- [x] **Lagre stemmetall, ikke bare prosent** (`stemmer.resultat.antall.total` og `.fhs`), slik at områder kan aggregeres og prosenter regnes ut på nytt.
- [ ] **Topp 10 per parti per år.** `src/anlysis/top_10_municipalities_per_party.py` grupperer kun på `party_code`, så årene blandes.
- [ ] **Partidimensjon per år.** Samme partikode har ulike navn over tid (SV, DEMN, KRISTNE, HELSE), og MDG bytter partikategori (2 → 1). Lag `partikode + år → navn, kategori` pluss et kanonisk navn.
- [x] **Notebook:** bruker kolonnen `'vo'`, som ikke finnes; aksetittelen sier «Mandates», men grafen viser stemmer.
- [ ] **Avhengigheter** i `requirements.txt` eller `pyproject.toml` (pandas, requests, matplotlib).
- [ ] Rydde navn: `anlysis` → `analysis`, `dimentions` → `dimensions`.

## Fase 2 – Datagrunnlag

- [ ] **Én generisk crawler** som følger `_links.related` rekursivt (land → fylke → kommune → bydel → stemmekrets) og speiler API-stien på disk. Erstatter de tre skriptene i `src/api/`. Med rate-limit, cache, og nedlasting kun når `rapportGenerert` er endret.
- [ ] **Alle valgtyper** fra `GET /api` → `_sublinks`: stortingsvalg `st` (2009–2025), kommunestyre- og fylkestingsvalg `ko`/`fy` (2011–2023) og sametingsvalg `sa` (2013–2025).
- [ ] **Lang faktatabell i DuckDB/Parquet:**
  - `results(år, valgtype, nivå, område_id, partikode, stemmer_total, stemmer_fhs, prosent, fhs_prosent, vts_prosent, endring, mandater)`
  - `areas(år, nivå, område_id, navn, forelder_id)`
  - `turnout(år, valgtype, område_id, stemmeberettigede, stemmer, frammøte_prosent)`
- [ ] **Geografi over reformer.** Kommunereformen 2020 (428 → 356 kommuner) og fylkesreformene 2020 (19 → 11) og 2024 (11 → 15) gjør sammenligning over tid misvisende. Bygg en overgangstabell fra SSB Klass (kommuner: klassifikasjon 131, fylker: 104) slik at samme område kan følges over tid.
- [ ] Vurdere [HNygard/valgresultat.no-copy](https://github.com/HNygard/valgresultat.no-copy) som kilde eller kontroll – arkiverer alle endringer i API-et med tidsstempel, ned til krets.

## Fase 3 – Første innsiktssider

- [ ] **Oslo ned på stemmekrets.** Kart over partistyrke, endring og valgdeltakelse per bydel og krets; hvordan øst/vest-skillet har utviklet seg.
- [ ] **Forhåndsstemmer.** Andelen forhåndsstemmer har gått fra 24 % (2009) til 63 % (2025). Hvilke partier vinner tidlig, og hvilke på valgdagen (`fhsProsent` mot `vtsProsent`)?
- [ ] **Kommunesammenligning** på harmonisert geografi.

## Fase 4 – Videre innsikt

- [ ] **Swing og blokker** – hvor endrer velgerne seg mest, og hvor er det jevnest mellom rødgrønn og borgerlig side?
- [ ] **Kommunevalg mot stortingsvalg** i samme område – splittstemming og lokallister.
- [ ] **«Ligner mest på Norge»** – klynging av kommuner etter stemmeprofil, bellwether-kommuner og «kommunen som ligner din».
- [ ] **Mandatsimulator** – sperregrense, Sainte-Laguë og utjevningsmandater (dataene har `utjevning.kvotient` og `mandatrang`). Hvor få stemmer manglet for et mandat til?
- [ ] **Kobling til SSB og Oslo statistikkbank** – inntekt, utdanning, alder og sentralitet mot stemmegivning.
- [ ] **Valgnatt-forløp** – hvordan resultatet endret seg utover kvelden (krever historiske snapshots).

## Leveranse

- [ ] Første versjon: DuckDB + Streamlit.
- [ ] Offentlig versjon: statisk side (Observable Framework eller Evidence) på samme DuckDB-fil.
- [ ] Kartgrunnlag: kommune-, fylkes- og kretsgrenser som GeoJSON fra Geonorge.
- [ ] Automatisk oppdatering (f.eks. GitHub Actions) rundt valg.

## Risiko

- Valgdirektoratet jobber med endringer i API-et som følge av ny valglov (2024). Sjekk at nedlastingen fungerer før neste valg.
- Resultater er tilgjengelige i API-et først fra kl. 21:00 på valgnatta, og tallene endres i dagene etterpå – ikke last ned endelige data før opptellingen er ferdig.

## Ressurser

- [valgresultat.no/api](https://valgresultat.no/api) – API-et (selvbeskrivende HAL+JSON)
- [API med valgresultater – Valgdirektoratet](https://www.valg.no/om-valgdirektoratet/om-valgdirektoratet/pressesider/API-med-valgresultater/)
- [HNygard/valgresultat.no-copy](https://github.com/HNygard/valgresultat.no-copy) – arkiv av API-et med historikk
- [thomastallaksen/valganalyse](https://github.com/thomastallaksen/valganalyse) – Oslo på stemmekretsnivå
- [FemtiGram/kart](https://github.com/FemtiGram/kart) – kartvisning av valgresultater
- [SSB Klass](https://www.ssb.no/klass/) – kommune- og fylkesendringer
