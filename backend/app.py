from flask import Flask, render_template, abort, request
from pathlib import Path
import json

from backend.json_loader import load_state_from_json
from backend import config
import pandas as pd
from backend.fips import format_fips
from backend.tier_system import add_tier_column, get_tier_summary, TIER_EMOJIS, TIER_DESCRIPTIONS

app = Flask(__name__, template_folder=Path(__file__).parent.parent / 'templates')


@app.route('/')
def index():
    states = config.DEFAULT_STATES
    
    # Calculate overall tier statistics
    all_data = []
    for state in states:
        df = load_state_from_json(state)
        if not df.empty:
            df = add_tier_column(df)
            all_data.append(df)
    
    tier_stats = None
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        tier_summary = get_tier_summary(combined)
        tier_stats = tier_summary.to_dict('records')
    
    return render_template('index.html', states=states, tier_stats=tier_stats)


@app.route('/state/<state>')
def state_view(state: str):
    state = state.upper()
    df = load_state_from_json(state)
    if df.empty:
        abort(404, f'No data for state: {state}')

    # Add tier classification
    df = add_tier_column(df)
    
    # Ensure swing_score_100 available
    if 'swing_score_100' not in df.columns:
        if 'swing_score' in df.columns:
            df['swing_score_100'] = (df['swing_score'].astype(float) * 100).round(2)
        else:
            df['swing_score_100'] = 0.0

    # Get tier filter from query params
    tier_filter = request.args.get('tier', None)
    if tier_filter:
        tier_filter = tier_filter.upper()
        df = df[df['tier'] == tier_filter]
    
    # Get tier summary
    full_df = load_state_from_json(state)
    full_df = add_tier_column(full_df)
    tier_summary = get_tier_summary(full_df)
    
    # Add emoji to tier column for display
    df['tier_display'] = df['tier'].apply(lambda t: f"{TIER_EMOJIS.get(t, '')} {t}")

    # Selected columns for display
    cols = ['tier_display', 'county_name', 'swing_score_100']
    optional_cols = ['margin_change_abs', 'closeness_latest']
    for col in optional_cols:
        if col in df.columns:
            cols.append(col)
    
    cols = [c for c in cols if c in df.columns]
    
    # Format the display dataframe
    display_df = df[cols].copy()
    
    # Round numeric columns for cleaner display
    if 'swing_score_100' in display_df.columns:
        display_df['swing_score_100'] = display_df['swing_score_100'].round(1)
    if 'margin_change_abs' in display_df.columns:
        display_df['margin_change_abs'] = (display_df['margin_change_abs'] * 100).round(2)
    if 'closeness_latest' in display_df.columns:
        display_df['closeness_latest'] = (display_df['closeness_latest'] * 100).round(1)
    
    # Rename columns for display
    column_names = {
        'tier_display': 'Tier',
        'county_name': 'County',
        'swing_score_100': 'Score',
        'margin_change_abs': 'Margin Shift %',
        'closeness_latest': 'Closeness %'
    }
    display_df = display_df.rename(columns=column_names)
    
    table_html = display_df.head(100).to_html(classes='table table-striped table-sm table-hover', index=False, border=0, escape=False)
    
    return render_template('state.html', 
                         state=state, 
                         table_html=table_html,
                         tier_summary=tier_summary.to_dict('records'),
                         current_tier=tier_filter)


@app.route('/map/<state>')
def map_view(state: str):
    state = state.upper()
    df = load_state_from_json(state)
    if df.empty:
        abort(404, f'No data for state: {state}')

    # Ensure county_fips zero-padded (json_loader already normalizes but be robust)
    if 'county_fips' in df.columns:
        df['county_fips'] = df['county_fips'].apply(format_fips)

    # Prepare swing_score_100
    if 'swing_score_100' not in df.columns and 'swing_score' in df.columns:
        df['swing_score_100'] = (df['swing_score'].astype(float) * 100).round(2)

    try:
        import plotly.express as px
    except Exception:
        abort(500, 'plotly is required to render the map')

    # Load geojson (downloaded earlier by plotly_map script)
    geojson_path = Path(__file__).parent.parent / 'swingscorejsons' / 'counties.geojson'
    if not geojson_path.exists():
        # fallback: try the online file
        GEOJSON_URL = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
        import requests
        geojson = requests.get(GEOJSON_URL, timeout=30).json()
    else:
        with open(geojson_path, 'r', encoding='utf-8') as fh:
            geojson = json.load(fh)

    # Add tier classification for hover info
    df = add_tier_column(df)
    
    # Add formatted hover text with county name and tier
    df['hover_text'] = df.apply(
        lambda row: f"<b>{row['county_name']}</b><br>" +
                    f"Tier: {TIER_EMOJIS.get(row['tier'], '')} {row['tier']}<br>" +
                    f"Score: {row['swing_score_100']:.1f}",
        axis=1
    )
    
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations='county_fips',
        color='swing_score_100',
        color_continuous_scale='RdYlBu_r',
        range_color=(0, 100),
        scope='usa',
        labels={'swing_score_100': 'Swing Score'},
        hover_name='county_name',
        hover_data={
            'county_fips': False,
            'swing_score_100': ':.1f',
            'tier': True
        }
    )

    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(
        margin={'r':0,'t':0,'l':0,'b':0},
        title=f'{state} County Swing Scores',
        title_x=0.5
    )

    # Return full HTML page containing the plotly figure
    return fig.to_html(full_html=True)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
