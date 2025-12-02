"""Export all counties for a given state from the precomputed JSON.

Example:
    python -m backend.export_full_state --state PA --out outputs/PA_all_counties.csv
"""
from pathlib import Path
import argparse
import json
import sys

import pandas as pd
from .fips import format_fips


def parse_args():
    p = argparse.ArgumentParser(description='Export all counties for a state from swingscore JSON')
    p.add_argument('--state', '-s', required=True, help='Two-letter state code')
    p.add_argument('--json', default='swingscorejsons/swing_scores_all_states.json', help='Path to precomputed JSON')
    p.add_argument('--out', '-o', default=None, help='Output CSV path')
    return p.parse_args()


def main():
    args = parse_args()
    state = args.state.upper()
    json_path = Path(args.json)
    if not json_path.exists():
        print('JSON file not found:', json_path)
        sys.exit(2)

    with open(json_path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    # JSON may be a dict keyed by state (e.g., {"PA": [records...]}) or a flat list
    if isinstance(data, dict):
        records = data.get(state, [])
    else:
        records = data

    df = pd.DataFrame(records)
    if df.empty:
        print(f'No records found for state {state} (or JSON empty)')
        sys.exit(1)

    # If the JSON was a flat list, filter by state_code column
    if 'state_code' in df.columns:
        df_state = df[df['state_code'] == state].copy()
    else:
        df_state = df.copy()
    if df_state.empty:
        print(f'No records found for state {state}')
        sys.exit(1)

    # Ensure county_fips is zero-padded 5-digit string
    if 'county_fips' in df_state.columns:
        df_state['county_fips'] = df_state['county_fips'].apply(format_fips)

    out_path = Path(args.out) if args.out else Path('outputs') / f"{state}_all_counties.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_state.to_csv(out_path, index=False)
    print('Wrote CSV:', out_path)


if __name__ == '__main__':
    main()
