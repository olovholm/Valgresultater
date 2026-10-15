"""Streamlit app for national results from the Norwegian parliamentary elections.

Run from the project root with: streamlit run src/app/streamlit_app.py
"""
import altair as alt
import pandas as pd
import streamlit as st

import election_data as ed

st.set_page_config(page_title='Valgresultater', layout='wide')

DARK = st.context.theme.type == 'dark'
SURFACE = '#0e1117' if DARK else '#ffffff'
INK = '#fafafa' if DARK else '#31333f'  # Streamlit's own text colours
CONTEXT = '#5b5a56' if DARK else '#c3c2b7'  # Grey for lines that give context
PARTY_SCALE = alt.Scale(domain=ed.PARTY_ORDER, range=[ed.PARTY_COLORS[p] for p in ed.PARTY_ORDER])
MAIN_PARTIES = [p for p in ed.PARTY_ORDER if p != ed.OTHER['label']]


@st.cache_data
def load_data():
    return ed.load_results(), ed.load_counting()


def with_labels(df):
    """Add formatted text columns used in labels and tooltips."""
    return df.assign(
        share_label=df['votes_percentage'].map(ed.fmt_pct),
        votes_label=df['votes_total'].map(ed.fmt_int),
        change_label=df['change'].map(lambda v: '' if pd.isna(v) else ed.fmt_pp(v)),
    )


PARTY_TOOLTIP = [
    alt.Tooltip('party:N', title='Parti'),
    alt.Tooltip('share_label:N', title='Oppslutning'),
    alt.Tooltip('votes_label:N', title='Stemmer'),
    alt.Tooltip('mandates:Q', title='Mandater'),
    alt.Tooltip('change_label:N', title='Endring'),
]


def bar_chart_height(party_sort):
    # The height includes the x-axis, not just the bars
    return 34 * len(party_sort) + 60


def share_chart(year_df, party_sort):
    base = alt.Chart(year_df).encode(
        y=alt.Y('party:N', sort=party_sort, title=None, axis=alt.Axis(ticks=False, domain=False, labelFontSize=13)),
        tooltip=PARTY_TOOLTIP,
    )
    bars = base.mark_bar(size=18, cornerRadiusEnd=4).encode(
        x=alt.X('votes_percentage:Q', title='Oppslutning (%)', scale=alt.Scale(domain=[0, 40]),
                axis=alt.Axis(values=[0, 10, 20, 30, 40])),
        color=alt.Color('party:N', scale=PARTY_SCALE, legend=None),
    )
    labels = base.mark_text(align='left', dx=5, fontSize=12, color=INK).encode(x='votes_percentage:Q', text='share_label:N')
    return (bars + labels).properties(height=bar_chart_height(party_sort))


def change_chart(year_df, party_sort):
    base = alt.Chart(year_df).encode(
        y=alt.Y('party:N', sort=party_sort, title=None, axis=alt.Axis(ticks=False, domain=False, labelFontSize=13)),
        tooltip=PARTY_TOOLTIP,
    )
    # Leave room for the value labels outside the longest bars
    low, high = min(year_df['change'].min(), 0) - 3, max(year_df['change'].max(), 0) + 3
    x = alt.X('change:Q', title='Endring (prosentpoeng)', scale=alt.Scale(domain=[low, high], nice=False))
    gains = base.transform_filter('datum.change >= 0')
    losses = base.transform_filter('datum.change < 0')
    layers = [
        gains.mark_bar(size=18, cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color=ed.GAIN_COLOR).encode(x=x),
        losses.mark_bar(size=18, cornerRadiusTopLeft=4, cornerRadiusBottomLeft=4, color=ed.LOSS_COLOR).encode(x=x),
        gains.mark_text(align='left', dx=5, fontSize=12, color=INK).encode(x='change:Q', text='change_label:N'),
        losses.mark_text(align='right', dx=-5, fontSize=12, color=INK).encode(x='change:Q', text='change_label:N'),
        alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(color='#898781').encode(x='x:Q'),
    ]
    return alt.layer(*layers).properties(height=bar_chart_height(party_sort))


def mandates_chart(results, year):
    df = results[results['mandates'] > 0].sort_values(['year', 'order']).copy()
    df['end'] = df.groupby('year')['mandates'].cumsum()
    df['start'] = df['end'] - df['mandates']
    df['mid'] = df['start'] + df['mandates'] / 2
    df['text_color'] = df['color'].map(ed.text_color_on)
    df = with_labels(df)

    y = alt.Y('year:O', title=None, axis=alt.Axis(
        ticks=False, domain=False, labelFontSize=13,
        labelFontWeight=alt.expr(f"datum.value == {year} ? 'bold' : 'normal'")))
    base = alt.Chart(df).encode(y=y)
    bars = base.mark_bar(size=24, stroke=SURFACE, strokeWidth=2).encode(
        x=alt.X('start:Q', title='Mandater', scale=alt.Scale(domain=[0, 169]),
                axis=alt.Axis(values=[0, 40, 85, 120, 169])),
        x2='end:Q',
        color=alt.Color('party:N', scale=PARTY_SCALE, title=None,
                        legend=alt.Legend(orient='top', direction='horizontal', symbolType='square')),
        tooltip=PARTY_TOOLTIP,
    )
    # Only label segments wide enough to hold the number
    labels = base.transform_filter('datum.mandates >= 5').mark_text(fontSize=11).encode(
        x='mid:Q', text='mandates:Q', color=alt.Color('text_color:N', scale=None))
    majority = alt.Chart(pd.DataFrame({'x': [ed.MAJORITY]}))
    rule = majority.mark_rule(color='#898781', strokeWidth=1).encode(x='x:Q')
    rule_label = majority.mark_text(align='left', dx=4, dy=-10, color='#898781', fontSize=11).encode(
        x='x:Q', y=alt.value(0), text=alt.value(f'Flertall: {ed.MAJORITY}'))
    # The height includes the legend and axis, not just the bars
    return (bars + rule + labels + rule_label).properties(height=44 * df['year'].nunique() + 130)


def trend_chart(results, year):
    """Small multiples: each party highlighted against the others in grey."""
    df = with_labels(results[results['party'].isin(MAIN_PARTIES)])
    panels = pd.concat([df.assign(panel=p, focus=df['party'] == p) for p in MAIN_PARTIES])

    base = alt.Chart().encode(
        x=alt.X('year:O', title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('votes_percentage:Q', title=None, scale=alt.Scale(domain=[0, 40])),
    )
    context = base.transform_filter('!datum.focus').mark_line(strokeWidth=1, color=CONTEXT).encode(
        detail='party:N')
    focus = base.transform_filter('datum.focus')
    line = focus.mark_line(strokeWidth=2).encode(color=alt.Color('party:N', scale=PARTY_SCALE, legend=None))
    points = focus.mark_circle(size=64, stroke=SURFACE, strokeWidth=2, opacity=1).encode(
        color=alt.Color('party:N', scale=PARTY_SCALE, legend=None), tooltip=PARTY_TOOLTIP)
    end_label = focus.transform_filter(f'datum.year == {year}').mark_text(dy=-14, fontSize=11, color=INK).encode(
        text='share_label:N')
    return alt.layer(context, line, points, end_label, data=panels).properties(width=300, height=140).facet(
        facet=alt.Facet('panel:N', sort=MAIN_PARTIES, title=None,
                        header=alt.Header(labelFontSize=14, labelAnchor='start', labelFontWeight='bold')),
        columns=3,
    )


def turnout_chart(counting, year):
    measures = {'turnout_percentage': 'Valgdeltakelse', 'advance_share': 'Andel forhåndsstemmer'}
    df = counting.melt(id_vars='year', value_vars=list(measures), var_name='measure', value_name='value')
    df['measure'] = df['measure'].map(measures)
    df['value_label'] = df['value'].map(ed.fmt_pct)
    wide = counting.assign(
        turnout_label=counting['turnout_percentage'].map(ed.fmt_pct),
        advance_label=counting['advance_share'].map(ed.fmt_pct),
    )

    color = alt.Color('measure:N', title=None, legend=alt.Legend(orient='top', symbolType='stroke'),
                      scale=alt.Scale(domain=list(measures.values()), range=[ed.TURNOUT_COLOR, ed.ADVANCE_COLOR]))
    x = alt.X('year:O', title=None, axis=alt.Axis(labelAngle=0))
    base = alt.Chart(df).encode(x=x, y=alt.Y('value:Q', title='Prosent', scale=alt.Scale(domain=[0, 100])))
    lines = base.mark_line(strokeWidth=2).encode(color=color)
    points = base.mark_circle(size=64, stroke=SURFACE, strokeWidth=2, opacity=1).encode(color=color)
    end_labels = base.transform_filter(f'datum.year == {year}').mark_text(dy=-14, fontSize=12, color=INK).encode(
        text='value_label:N')

    # Crosshair: snap to the nearest election and show both values
    hover = alt.selection_point(fields=['year'], nearest=True, on='pointerover', empty=False)
    crosshair = alt.Chart(wide).mark_rule(color='#898781').encode(
        x=x,
        opacity=alt.when(hover).then(alt.value(1)).otherwise(alt.value(0)),
        tooltip=[alt.Tooltip('year:O', title='Valg'),
                 alt.Tooltip('turnout_label:N', title='Valgdeltakelse'),
                 alt.Tooltip('advance_label:N', title='Andel forhåndsstemmer')],
    ).add_params(hover)
    return (lines + points + end_labels + crosshair).properties(height=320)


try:
    results, counting = load_data()
except FileNotFoundError:
    st.error('Fant ikke datagrunnlaget i `data/facts/`. Kjør `python run_scripts.py` fra prosjektroten først.')
    st.stop()

years = sorted(results['year'].unique())
st.title(f'Stortingsvalg {years[0]}–{years[-1]}')
st.caption('Kilde: Valgdirektoratet, [valgresultat.no](https://valgresultat.no). Landsresultater.')

year = st.segmented_control('Valgår', years, default=years[-1], required=True)
previous_year = years[years.index(year) - 1] if year != years[0] else None

# Key figures
current = counting.set_index('year').loc[year]
previous = counting.set_index('year').loc[previous_year] if previous_year else None
history = counting[counting['year'] <= year]
block_history = ed.mandates_by_block(results).loc[:year]
blocks = block_history.loc[year]
red_green_change = int(blocks['Rødgrønne'] - block_history.loc[previous_year, 'Rødgrønne']) if previous_year else None

kpi = st.columns(4)
kpi[0].metric(
    'Valgdeltakelse', ed.fmt_pct(current['turnout_percentage']),
    delta=f"{current['turnout_percentage'] - previous['turnout_percentage']:+.1f} pp".replace('.', ',') if previous_year else None,
    delta_color='off', chart_data=history['turnout_percentage'].tolist(), border=True)
kpi[1].metric(
    'Godkjente stemmer', ed.fmt_int(current['total_votes']),
    delta=f"{int(current['total_votes'] - previous['total_votes']):+,}".replace(',', ' ') if previous_year else None,
    delta_color='off', chart_data=history['total_votes'].tolist(), border=True)
kpi[2].metric(
    'Andel forhåndsstemmer', ed.fmt_pct(current['advance_share']),
    delta=f"{current['advance_share'] - previous['advance_share']:+.1f} pp".replace('.', ',') if previous_year else None,
    delta_color='off', chart_data=history['advance_share'].tolist(), border=True)
kpi[3].metric(
    'Mandater rødgrønne – borgerlige', f"{blocks['Rødgrønne']} – {blocks['Borgerlige']}",
    delta=f'{red_green_change:+d} rødgrønne' if previous_year else None,
    delta_color='off', chart_data=block_history['Rødgrønne'].tolist(), border=True,
    help=f'{ed.MAJORITY} mandater gir flertall. MDG regnes her til rødgrønn side.')

# Result for the selected year
year_df = with_labels(results[results['year'] == year])
party_sort = (year_df[year_df['party'] != ed.OTHER['label']]
              .sort_values('votes_percentage', ascending=False)['party'].tolist() + [ed.OTHER['label']])

st.subheader(f'Resultat {year}')
left, right = st.columns(2, gap='large')
with left:
    st.markdown('**Oppslutning**')
    st.altair_chart(share_chart(year_df, party_sort), width='stretch')
with right:
    if previous_year:
        st.markdown(f'**Endring fra {previous_year}**')
        st.altair_chart(change_chart(year_df, party_sort), width='stretch')
    else:
        st.info(f'{year} er det første valget i datagrunnlaget, så det finnes ingen endring å vise.')

st.subheader('Mandater')
st.caption(f'Partiene er ordnet fra venstre til høyre. Streken markerer flertall ({ed.MAJORITY} av 169).')
st.altair_chart(mandates_chart(results, year), width='stretch')

st.subheader('Oppslutning over tid')
st.caption('Hvert parti er uthevet mot de andre partiene i grått.')
st.altair_chart(trend_chart(results, year))

st.subheader('Valgdeltakelse og forhåndsstemmer')
st.altair_chart(turnout_chart(counting, year), width='stretch')

with st.expander('Tabell'):
    table = year_df.sort_values('votes_percentage', ascending=False)[
        ['party', 'votes_total', 'votes_percentage', 'change', 'mandates']]
    st.dataframe(
        table, hide_index=True,
        column_config={
            'party': st.column_config.TextColumn('Parti'),
            'votes_total': st.column_config.NumberColumn('Stemmer', format='localized'),
            'votes_percentage': st.column_config.NumberColumn('Oppslutning (%)', format='%.1f'),
            'change': st.column_config.NumberColumn(f'Endring fra {previous_year} (pp)', format='%+.1f'),
            'mandates': st.column_config.NumberColumn('Mandater'),
        },
    )
