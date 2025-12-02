"""Generate an interactive Plotly choropleth for a state's swing scores.

Usage:
    python -m backend.plotly_map --state PA --input outputs/PA_top20.csv

This script will download a US counties GeoJSON (if not present) and
produce an HTML file `outputs/{state}_swing_map.html`.
"""
from pathlib import Path
import argparse
import json
import sys

import pandas as pd
from .fips import format_fips

try:
    import plotly.express as px
except Exception:
    print("plotly is required. Install with: pip install plotly")
    raise

import requests


GEOJSON_URL = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"


def ensure_geojson(path: Path) -> dict:
    if path.exists():
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)

    print(f"Downloading county GeoJSON to {path} ...")
    r = requests.get(GEOJSON_URL, timeout=30)
    r.raise_for_status()
    data = r.json()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh)
    return data


def make_map(state: str, csv_path: Path, out_dir: Path) -> Path:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path, dtype={'county_fips': str})

    # Ensure FIPS are 5-char strings (robustly handle floats like 13121.0)
    df['county_fips'] = df['county_fips'].apply(format_fips)

    # Ensure a swing_score_100 column for display (either convert from swing_score or use existing)
    if 'swing_score_100' not in df.columns:
        if 'swing_score' in df.columns:
            df['swing_score_100'] = (df['swing_score'].astype(float) * 100).round(2)
        else:
            # fallback: create placeholder from 0..1 numeric swing_score if present under other name
            df['swing_score_100'] = 0

    # Load or download geojson
    geojson_path = Path(__file__).parent.parent / 'swingscorejsons' / 'counties.geojson'
    geojson = ensure_geojson(geojson_path)

    # Build choropleth
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations='county_fips',
        color='swing_score_100',
        color_continuous_scale='RdYlBu_r',
        range_color=(0, 100),
        scope='usa',
        labels={'swing_score_100': 'Swing score (0-100)'},
    hover_data=['county_name', 'swing_score_100', 'margin_change_abs', 'closeness_latest', 'turnout_latest']
    )

    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0})

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{state}_swing_map.html"
    fig.write_html(str(out_file))
    return out_file


def parse_args():
    p = argparse.ArgumentParser(description='Create Plotly choropleth for swing scores')
    p.add_argument('--state', '-s', required=True, help='Two-letter state code (e.g., PA)')
    p.add_argument('--input', '-i', default=None, help='Input CSV path (defaults to outputs/{STATE}_top20.csv)')
    p.add_argument('--out', '-o', default='outputs', help='Output directory for HTML')
    return p.parse_args()


def main():
    args = parse_args()
    state = args.state.upper()
    csv_path = Path(args.input) if args.input else Path('outputs') / f"{state}_top20.csv"
    out_dir = Path(args.out)

    try:
        out_file = make_map(state, csv_path, out_dir)
    except Exception as e:
        print('Error creating map:', e)
        sys.exit(1)

    print(f'Wrote map to: {out_file.resolve()}')


if __name__ == '__main__':
    main()
