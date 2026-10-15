"""Loading and preparing national election results, shared by the Streamlit app and the notebooks."""
from pathlib import Path

import pandas as pd

FACTS_DIR = Path(__file__).resolve().parents[2] / 'data' / 'facts'

MAJORITY = 85  # of 169 mandates

# Parties that have been in parliament, ordered left to right as used when stacking mandates.
# Colours follow each party's conventional colour, adjusted in lightness so that neighbours in this
# order stay distinguishable with colour vision deficiency, on both light and dark backgrounds.
# MDG is counted on the red-green side here, although it has formally been independent of the blocks.
PARTIES = {
    'RØDT': {'label': 'Rødt', 'color': '#b21017', 'block': 'Rødgrønne'},
    'SV': {'label': 'SV', 'color': '#e06099', 'block': 'Rødgrønne'},
    'MDG': {'label': 'MDG', 'color': '#72a62b', 'block': 'Rødgrønne'},
    'A': {'label': 'Ap', 'color': '#d11e22', 'block': 'Rødgrønne'},
    'SP': {'label': 'Sp', 'color': '#08762e', 'block': 'Rødgrønne'},
    'KRF': {'label': 'KrF', 'color': '#ac8103', 'block': 'Borgerlige'},
    'V': {'label': 'V', 'color': '#008574', 'block': 'Borgerlige'},
    'H': {'label': 'H', 'color': '#488fe7', 'block': 'Borgerlige'},
    'FRP': {'label': 'FrP', 'color': '#305bad', 'block': 'Borgerlige'},
}
OTHER = {'label': 'Andre', 'color': '#b3b1aa', 'block': 'Andre'}

# Stacking order: red-green parties, then other parties, then the non-socialist parties
PARTY_ORDER = ['Rødt', 'SV', 'MDG', 'Ap', 'Sp', 'Andre', 'KrF', 'V', 'H', 'FrP']
PARTY_COLORS = {p['label']: p['color'] for p in [*PARTIES.values(), OTHER]}

# Two-series and diverging colours
TURNOUT_COLOR = '#2a78d6'
ADVANCE_COLOR = '#d95926'
GAIN_COLOR = '#2a78d6'
LOSS_COLOR = '#e34948'


def load_counting():
    """Turnout and vote totals per election, with the share of advance votes."""
    df = pd.read_csv(FACTS_DIR / 'election_counting.csv').sort_values('year').reset_index(drop=True)
    df['advance_share'] = df['advance_votes'] / df['total_votes'] * 100
    return df


def load_results():
    """Votes and mandates per party and election, with parties outside parliament grouped as 'Andre'."""
    df = pd.read_csv(FACTS_DIR / 'election_results_total.csv')
    df['party'] = df['party_code'].map(lambda code: PARTIES.get(code, OTHER)['label'])
    df = (
        df.groupby(['year', 'party'], as_index=False)
        .agg(votes_total=('votes_total', 'sum'),
             votes_percentage=('votes_percentage', 'sum'),
             mandates=('mandates', 'sum'))
    )
    df['block'] = df['party'].map(lambda label: next(
        (p['block'] for p in PARTIES.values() if p['label'] == label), OTHER['block']))
    df['color'] = df['party'].map(PARTY_COLORS)
    df['order'] = df['party'].map(PARTY_ORDER.index)

    # Change in percentage points since the previous election
    years = sorted(df['year'].unique())
    previous = df[['year', 'party', 'votes_percentage']].rename(columns={'votes_percentage': 'previous_percentage'})
    previous['year'] = previous['year'].map(dict(zip(years[:-1], years[1:])))
    previous = previous.dropna(subset=['year']).astype({'year': int})
    df = df.merge(previous, on=['year', 'party'], how='left')
    df['change'] = df['votes_percentage'] - df['previous_percentage']
    return df.sort_values(['year', 'order']).reset_index(drop=True)


def mandates_by_block(results):
    """Mandates per block and election."""
    return results.pivot_table(index='year', columns='block', values='mandates', aggfunc='sum', fill_value=0)


def text_color_on(fill):
    """White or near-black, whichever reads best on the given fill colour."""
    def luminance(hex_color):
        channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    fill_luminance = luminance(fill)
    on_white = 1.05 / (fill_luminance + 0.05)
    on_black = (fill_luminance + 0.05) / (luminance('#0b0b0b') + 0.05)
    return '#ffffff' if on_white >= on_black else '#0b0b0b'


def fmt_pct(value, decimals=1):
    return f'{value:.{decimals}f} %'.replace('.', ',')


def fmt_pp(value):
    return f'{value:+.1f}'.replace('.', ',').replace('-', '−') + ' pp'


def fmt_int(value):
    return f'{int(value):,}'.replace(',', ' ')
