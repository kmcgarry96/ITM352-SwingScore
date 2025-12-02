"""
Small display helpers for showing ranked county swing scores and prompting
for details in a simple terminal UI.

This module intentionally avoids external UI dependencies so it stays
lightweight and easy to run in class/demo environments.
"""
from typing import Optional
import pandas as pd 


def show_ranked_counties(df: pd.DataFrame, top: int = 20) -> None:
    """Print a compact ranked table of counties with swing scores.

    Expects `df` to contain at least these columns produced by the
    existing pipeline: 'county_name', 'county_fips', 'swing_score'
    (0..1), 'margin_change_abs' (0..1), 'closeness_latest' (0..1), and
    'turnout_latest' / 'total_votes' where available.
    """
    if df is None or df.empty:
        print("No counties to show.")
        return

    # Work on a small copy and prepare display columns
    out = df.copy()
    # Format swing score as 0-100
    out['swing_score_100'] = out['swing_score'] * 100
    # margin change and margin display as percentage
    out['margin_change_pct'] = out['margin_change_abs'] * 100
    # Approximate latest absolute margin pct from closeness: abs_margin = 1 - closeness
    out['latest_abs_margin_pct'] = (1.0 - out['closeness_latest']) * 100

    rows = out.head(top)

    header = f"{'#':>3}  {'County':40} {'FIPS':8} {'Score':>7} {'ΔMargin%':>9} {'|Margin%|':>9} {'Votes':>10}"
    print(header)
    print('-' * len(header))

    for i, row in enumerate(rows.itertuples(index=False), start=1):
        county = getattr(row, 'county_name', '')
        fips = getattr(row, 'county_fips', '')
        score = getattr(row, 'swing_score_100', 0.0)
        dmargin = getattr(row, 'margin_change_pct', 0.0)
        abs_margin = getattr(row, 'latest_abs_margin_pct', 0.0)
        votes = getattr(row, 'turnout_latest', getattr(row, 'total_votes', ''))

        print(f"{i:3d}. {county:40.40} {str(fips):8.8} {score:7.2f} {dmargin:9.2f} {abs_margin:9.2f} {str(votes):>10}")


def show_state_summary(df: pd.DataFrame) -> None:
    """Print a short summary of score distribution for the state.
    """
    if df is None or df.empty:
        return
    print()
    print(f"Counties: {len(df)}")
    print(f"Score: min {df['swing_score'].min()*100:.2f}, max {df['swing_score'].max()*100:.2f}, mean {df['swing_score'].mean()*100:.2f}")
    print()


def prompt_for_county_selection(df: pd.DataFrame) -> None:
    """Simple prompt loop allowing the user to pick a county by rank/index
    to see raw component values. Enter 'q' to exit.
    """
    if df is None or df.empty:
        return

    while True:
        choice = input("Enter county # (shown left) to view details, or 'q' to quit: ").strip()
        if choice.lower() in ('q', 'quit', 'exit'):
            break
        if not choice.isdigit():
            print("Please enter a number or 'q'.")
            continue
        idx = int(choice) - 1
        if idx < 0 or idx >= len(df):
            print("Index out of range.")
            continue
        row = df.iloc[idx]
        # Prepare a small details view
        details = {
            'county_name': row.get('county_name'),
            'county_fips': row.get('county_fips'),
            'swing_score_100': float(row.get('swing_score', 0.0) * 100),
            'margin_change_pct': float(row.get('margin_change_abs', 0.0) * 100),
            'latest_abs_margin_pct': float((1.0 - row.get('closeness_latest', 0.0)) * 100),
            'turnout_latest': float(row.get('turnout_latest', row.get('total_votes', 0)))
        }
        print('\nDETAILS:')
        for k, v in details.items():
            print(f"  {k}: {v}")
        print()
