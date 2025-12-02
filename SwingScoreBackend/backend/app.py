from flask import Flask, render_template, abort, request
from pathlib import Path
import json

from backend.json_loader import load_state_from_json
from backend import config
import pandas as pd
from backend.fips import format_fips

app = Flask(__name__, template_folder=Path(__file__).parent.parent / 'templates')


@app.route('/')
def index():
    states = config.DEFAULT_STATES
    return render_template('index.html', states=states)


@app.route('/state/<state>')
def state_view(state: str):
    state = state.upper()
    df = load_state_from_json(state)
    if df.empty:
        abort(404, f'No data for state: {state}')

    # Ensure swing_score_100 available
    if 'swing_score_100' not in df.columns:
        if 'swing_score' in df.columns:
            df['swing_score_100'] = (df['swing_score'].astype(float) * 100).round(2)
        else:
            df['swing_score_100'] = 0.0

    # Selected columns for display
    cols = [c for c in ['county_name', 'county_fips', 'swing_score_100', 'margin_change_abs', 'closeness_latest', 'turnout_latest'] if c in df.columns]
    table_html = df[cols].head(100).to_html(classes='table table-striped table-sm', index=False, border=0)
    return render_template('state.html', state=state, table_html=table_html)


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

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations='county_fips',
        color='swing_score_100',
        color_continuous_scale='RdYlBu_r',
        range_color=(0, 100),
        scope='usa',
        labels={'swing_score_100': 'Swing score (0-100)'}
    )

    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0})

    # Return full HTML page containing the plotly figure
    return fig.to_html(full_html=True)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
